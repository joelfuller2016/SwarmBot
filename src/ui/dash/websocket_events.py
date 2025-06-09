"""
WebSocket event handlers for real-time SwarmBot dashboard updates
"""

from flask_socketio import emit, join_room, leave_room, rooms
from flask import request
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from collections import defaultdict
import threading

# Configure logging
logger = logging.getLogger(__name__)

# Event batching configuration
BATCH_INTERVAL = 0.1  # seconds
MAX_BATCH_SIZE = 50

# Global event batchers
event_batchers: Dict[str, 'EventBatcher'] = {}
batch_lock = threading.Lock()


class EventBatcher:
    """Batches events to prevent overwhelming clients with rapid updates"""
    
    # --- FIX: Accept socketio instance ---
    def __init__(self, event_type: str, socketio, interval: float = BATCH_INTERVAL):
        self.event_type = event_type
        self.socketio = socketio
        self.interval = interval
        self.events: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
        self.timer: Optional[threading.Timer] = None
        
    def add_event(self, data: Dict[str, Any], room: Optional[str] = None):
        """Add an event to the batch"""
        with self.lock:
            self.events.append({
                'data': data,
                'room': room,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            if self.timer is None:
                self.timer = threading.Timer(self.interval, self._flush_events)
                self.timer.start()
            
            if len(self.events) >= MAX_BATCH_SIZE:
                self._flush_events()
    
    def _flush_events(self):
        """Flush all batched events"""
        with self.lock:
            if not self.events:
                return
                
            events_by_room = defaultdict(list)
            for event in self.events:
                room = event['room'] or 'broadcast'
                events_by_room[room].append(event['data'])
            
            # --- FIX: Use self.socketio.emit to ensure correct context ---
            for room, batch in events_by_room.items():
                payload = {
                    'type': self.event_type,
                    'batch': batch,
                    'count': len(batch),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                if room == 'broadcast':
                    # When using the socketio object, broadcasting is the default when no room is specified.
                    self.socketio.emit(f'{self.event_type}_batch', payload, namespace='/')
                else:
                    self.socketio.emit(f'{self.event_type}_batch', payload, room=room, namespace='/')
            
            self.events.clear()
            if self.timer:
                self.timer.cancel()
            self.timer = None


def init_websocket_events(socketio):
    """Initialize WebSocket event handlers"""
    
    global event_batchers
    # --- FIX: Pass socketio instance to EventBatcher ---
    event_batchers = {
        'agent_update': EventBatcher('agent_update', socketio),
        'task_update': EventBatcher('task_update', socketio),
        'metric_update': EventBatcher('metric_update', socketio, interval=0.5),
        'log_update': EventBatcher('log_update', socketio, interval=0.2)
    }
    
    @socketio.on('connect')
    def handle_connect():
        client_id = request.sid
        logger.info(f"Client connected: {client_id}")
        join_room('dashboard')
        emit('connection_established', {'client_id': client_id, 'timestamp': datetime.utcnow().isoformat(), 'rooms': list(rooms())})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        client_id = request.sid
        logger.info(f"Client disconnected: {client_id}")
        for room in list(rooms()):
            if room != client_id:
                leave_room(room)
    
    @socketio.on('join_room')
    def handle_join_room(data):
        room = data.get('room')
        if room:
            join_room(room)
            emit('room_joined', {'room': room, 'client_id': request.sid, 'timestamp': datetime.utcnow().isoformat()})
            logger.info(f"Client {request.sid} joined room: {room}")
    
    @socketio.on('leave_room')
    def handle_leave_room(data):
        room = data.get('room')
        if room:
            leave_room(room)
            emit('room_left', {'room': room, 'client_id': request.sid, 'timestamp': datetime.utcnow().isoformat()})
            logger.info(f"Client {request.sid} left room: {room}")
    
    # --- FIX: Accept optional sid argument ---
    @socketio.on('ping')
    def handle_ping(sid=None):
        """Handle ping for connection health check"""
        emit('pong', {'timestamp': datetime.utcnow().isoformat()})


# The rest of the file remains the same, as the emit calls from here are
# not in background threads and will have the correct context.

def emit_agent_status_change(agent_id: str, old_status: str, new_status: str, details: Optional[Dict] = None):
    data = {'agent_id': agent_id, 'old_status': old_status, 'new_status': new_status, 'details': details or {}, 'timestamp': datetime.utcnow().isoformat()}
    with batch_lock:
        event_batchers['agent_update'].add_event(data)
    if new_status in ['error', 'offline']:
        emit('agent_critical_update', data, broadcast=True, namespace='/')

def emit_agent_created(agent_id: str, agent_type: str, capabilities: List[str], metadata: Optional[Dict] = None):
    emit('agent_created', {'agent_id': agent_id, 'agent_type': agent_type, 'capabilities': capabilities, 'metadata': metadata or {}, 'timestamp': datetime.utcnow().isoformat()}, broadcast=True, namespace='/')

def emit_agent_deleted(agent_id: str, reason: Optional[str] = None):
    emit('agent_deleted', {'agent_id': agent_id, 'reason': reason, 'timestamp': datetime.utcnow().isoformat()}, broadcast=True, namespace='/')

def emit_task_queued(task_id: str, task_type: str, priority: str, metadata: Optional[Dict] = None):
    data = {'task_id': task_id, 'task_type': task_type, 'priority': priority, 'metadata': metadata or {}, 'timestamp': datetime.utcnow().isoformat()}
    with batch_lock:
        event_batchers['task_update'].add_event(data)

def emit_task_assigned(task_id: str, agent_id: str):
    data = {'task_id': task_id, 'agent_id': agent_id, 'event': 'assigned', 'timestamp': datetime.utcnow().isoformat()}
    with batch_lock:
        event_batchers['task_update'].add_event(data)

def emit_task_completed(task_id: str, agent_id: str, result: Optional[Dict] = None, duration_ms: Optional[int] = None):
    emit('task_completed', {'task_id': task_id, 'agent_id': agent_id, 'result': result, 'duration_ms': duration_ms, 'timestamp': datetime.utcnow().isoformat()}, broadcast=True, namespace='/')

def emit_task_failed(task_id: str, agent_id: str, error: str, traceback: Optional[str] = None):
    emit('task_failed', {'task_id': task_id, 'agent_id': agent_id, 'error': error, 'traceback': traceback, 'timestamp': datetime.utcnow().isoformat()}, broadcast=True, namespace='/')

def emit_performance_metrics(metrics: Dict[str, Any]):
    data = {'metrics': metrics, 'timestamp': datetime.utcnow().isoformat()}
    with batch_lock:
        event_batchers['metric_update'].add_event(data)

def emit_agent_metrics(agent_id: str, cpu: float, memory: float, tasks_completed: int, error_rate: float):
    data = {'agent_id': agent_id, 'cpu': cpu, 'memory': memory, 'tasks_completed': tasks_completed, 'error_rate': error_rate, 'timestamp': datetime.utcnow().isoformat()}
    with batch_lock:
        event_batchers['metric_update'].add_event(data)

def emit_system_alert(level: str, message: str, details: Optional[Dict] = None):
    emit('system_alert', {'level': level, 'message': message, 'details': details or {}, 'timestamp': datetime.utcnow().isoformat()}, broadcast=True, namespace='/')

def emit_log_message(level: str, source: str, message: str, metadata: Optional[Dict] = None):
    data = {'level': level, 'source': source, 'message': message, 'metadata': metadata or {}, 'timestamp': datetime.utcnow().isoformat()}
    with batch_lock:
        event_batchers['log_update'].add_event(data)

def broadcast_swarm_status(status: Dict[str, Any]):
    emit('swarm_status_update', {'status': status, 'timestamp': datetime.utcnow().isoformat()}, broadcast=True, namespace='/')

def broadcast_task_queue_update(queue_stats: Dict[str, Any]):
    emit('task_queue_update', {'stats': queue_stats, 'timestamp': datetime.utcnow().isoformat()}, broadcast=True, namespace='/')

def get_connected_clients() -> int:
    return 0

def flush_all_batchers():
    with batch_lock:
        for batcher in event_batchers.values():
            batcher._flush_events()