"""
WebSocket connection resilience and fallback mechanisms
"""

import asyncio
import logging
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta
import threading
from enum import Enum

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """WebSocket connection states"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RECONNECTING = "reconnecting"


class WebSocketResilience:
    """Manages WebSocket connection resilience and fallback"""
    
    def __init__(self, socketio, fallback_callback: Optional[Callable] = None):
        """
        Initialize resilience manager
        
        Args:
            socketio: SocketIO instance
            fallback_callback: Callback to trigger fallback mode
        """
        self.socketio = socketio
        self.fallback_callback = fallback_callback
        
        # Connection state
        self.state = ConnectionState.DISCONNECTED
        self.connection_attempts = 0
        self.last_connection_time = None
        self.last_disconnect_time = None
        
        # Configuration
        self.config = {
            "initial_delay": 1000,  # 1 second
            "max_delay": 30000,  # 30 seconds
            "backoff_factor": 2,
            "max_attempts": 10,
            "heartbeat_interval": 30,  # 30 seconds
            "heartbeat_timeout": 60,  # 60 seconds
            "fallback_threshold": 5,  # Switch to fallback after 5 failed attempts
            "quality_check_interval": 60  # Check connection quality every 60 seconds
        }
        
        # Message queue for offline storage
        self.message_queue = []
        self.max_queue_size = 1000
        
        # Connection quality metrics
        self.quality_metrics = {
            "latency": [],
            "packet_loss": 0,
            "reconnect_count": 0,
            "uptime": 0,
            "last_check": datetime.now()
        }
        
        # Heartbeat management
        self.heartbeat_task = None
        self.last_heartbeat = None
        self.pending_pings = {}
        
        # Setup event handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup SocketIO event handlers for resilience"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle successful connection"""
            self.state = ConnectionState.CONNECTED
            self.connection_attempts = 0
            self.last_connection_time = datetime.now()
            
            # Process queued messages
            self._flush_message_queue()
            
            # Start heartbeat
            self._start_heartbeat()
            
            logger.info("WebSocket connection established")
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle disconnection"""
            self.state = ConnectionState.DISCONNECTED
            self.last_disconnect_time = datetime.now()
            
            # Stop heartbeat
            self._stop_heartbeat()
            
            # Start reconnection process
            self._schedule_reconnection()
            
            logger.warning("WebSocket connection lost")
        
        @self.socketio.on('pong')
        def handle_pong(data):
            """Handle pong response for heartbeat"""
            ping_id = data.get('ping_id')
            if ping_id in self.pending_pings:
                # Calculate latency
                latency = (datetime.now() - self.pending_pings[ping_id]).total_seconds() * 1000
                self.quality_metrics['latency'].append(latency)
                
                # Keep only last 100 latency measurements
                if len(self.quality_metrics['latency']) > 100:
                    self.quality_metrics['latency'].pop(0)
                
                del self.pending_pings[ping_id]
                self.last_heartbeat = datetime.now()
    
    def _schedule_reconnection(self):
        """Schedule reconnection with exponential backoff"""
        if self.state == ConnectionState.RECONNECTING:
            return
        
        self.state = ConnectionState.RECONNECTING
        self.connection_attempts += 1
        
        # Calculate delay with exponential backoff
        delay = min(
            self.config['initial_delay'] * (self.config['backoff_factor'] ** (self.connection_attempts - 1)),
            self.config['max_delay']
        )
        
        # Check if we should switch to fallback
        if self.connection_attempts >= self.config['fallback_threshold']:
            logger.warning(f"Switching to fallback mode after {self.connection_attempts} failed attempts")
            if self.fallback_callback:
                self.fallback_callback(True)
        
        # Schedule reconnection
        logger.info(f"Scheduling reconnection in {delay/1000:.1f} seconds (attempt {self.connection_attempts})")
        
        timer = threading.Timer(delay / 1000, self._attempt_reconnection)
        timer.daemon = True
        timer.start()
    
    def _attempt_reconnection(self):
        """Attempt to reconnect"""
        if self.state == ConnectionState.CONNECTED:
            return
        
        self.state = ConnectionState.CONNECTING
        
        try:
            # Attempt to reconnect
            self.socketio.connect()
            self.quality_metrics['reconnect_count'] += 1
        except Exception as e:
            logger.error(f"Reconnection attempt failed: {e}")
            self._schedule_reconnection()
    
    def _start_heartbeat(self):
        """Start heartbeat mechanism"""
        if self.heartbeat_task:
            return
        
        async def heartbeat_loop():
            """Send periodic heartbeats"""
            while self.state == ConnectionState.CONNECTED:
                try:
                    # Send ping
                    ping_id = f"ping_{datetime.now().timestamp()}"
                    self.pending_pings[ping_id] = datetime.now()
                    
                    self.socketio.emit('ping', {'ping_id': ping_id})
                    
                    # Wait for interval
                    await asyncio.sleep(self.config['heartbeat_interval'])
                    
                    # Check for timeout
                    if self.last_heartbeat and (datetime.now() - self.last_heartbeat).total_seconds() > self.config['heartbeat_timeout']:
                        logger.warning("Heartbeat timeout detected")
                        self.socketio.disconnect()
                        
                except Exception as e:
                    logger.error(f"Heartbeat error: {e}")
        
        # Create task
        loop = asyncio.new_event_loop()
        self.heartbeat_task = loop.create_task(heartbeat_loop())
    
    def _stop_heartbeat(self):
        """Stop heartbeat mechanism"""
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            self.heartbeat_task = None
        self.pending_pings.clear()
    
    def _flush_message_queue(self):
        """Flush queued messages after reconnection"""
        if not self.message_queue:
            return
        
        logger.info(f"Flushing {len(self.message_queue)} queued messages")
        
        for message in self.message_queue:
            try:
                event_type = message.get('type')
                data = message.get('data')
                
                # Re-emit the message
                self.socketio.emit(event_type, data)
            except Exception as e:
                logger.error(f"Failed to flush message: {e}")
        
        self.message_queue.clear()
    
    def queue_message(self, event_type: str, data: Dict[str, Any]):
        """Queue a message for later delivery if disconnected"""
        if self.state == ConnectionState.CONNECTED:
            # Send immediately if connected
            self.socketio.emit(event_type, data)
        else:
            # Queue for later
            if len(self.message_queue) < self.max_queue_size:
                self.message_queue.append({
                    'type': event_type,
                    'data': data,
                    'timestamp': datetime.now()
                })
            else:
                # Remove oldest message to make room
                self.message_queue.pop(0)
                self.message_queue.append({
                    'type': event_type,
                    'data': data,
                    'timestamp': datetime.now()
                })
    
    def get_connection_quality(self) -> Dict[str, Any]:
        """Get connection quality metrics"""
        now = datetime.now()
        
        # Calculate average latency
        avg_latency = sum(self.quality_metrics['latency']) / len(self.quality_metrics['latency']) if self.quality_metrics['latency'] else 0
        
        # Calculate uptime
        if self.last_connection_time:
            uptime = (now - self.last_connection_time).total_seconds()
        else:
            uptime = 0
        
        return {
            'state': self.state.value,
            'average_latency': avg_latency,
            'reconnect_count': self.quality_metrics['reconnect_count'],
            'uptime_seconds': uptime,
            'queued_messages': len(self.message_queue),
            'connection_attempts': self.connection_attempts,
            'quality_score': self._calculate_quality_score()
        }
    
    def _calculate_quality_score(self) -> float:
        """Calculate connection quality score (0-100)"""
        score = 100.0
        
        # Penalize for high latency
        if self.quality_metrics['latency']:
            avg_latency = sum(self.quality_metrics['latency']) / len(self.quality_metrics['latency'])
            if avg_latency > 100:
                score -= min((avg_latency - 100) / 10, 30)
        
        # Penalize for reconnections
        score -= min(self.quality_metrics['reconnect_count'] * 5, 30)
        
        # Penalize for connection attempts
        score -= min(self.connection_attempts * 10, 40)
        
        return max(0, score)
    
    def enable_adaptive_behavior(self):
        """Enable adaptive behavior based on connection quality"""
        
        async def quality_monitor():
            """Monitor connection quality and adapt behavior"""
            while True:
                try:
                    await asyncio.sleep(self.config['quality_check_interval'])
                    
                    quality = self.get_connection_quality()
                    score = quality['quality_score']
                    
                    # Adapt based on quality score
                    if score < 30:
                        # Poor quality - increase intervals
                        logger.warning(f"Poor connection quality (score: {score:.1f}), adapting behavior")
                        
                        # Reduce update frequency
                        if hasattr(self, 'update_interval_callback'):
                            self.update_interval_callback(5000)  # 5 seconds
                        
                        # Enable aggressive batching
                        if hasattr(self, 'batching_callback'):
                            self.batching_callback(True, batch_size=100)
                    
                    elif score < 70:
                        # Medium quality - moderate intervals
                        if hasattr(self, 'update_interval_callback'):
                            self.update_interval_callback(2000)  # 2 seconds
                        
                        # Moderate batching
                        if hasattr(self, 'batching_callback'):
                            self.batching_callback(True, batch_size=50)
                    
                    else:
                        # Good quality - normal operation
                        if hasattr(self, 'update_interval_callback'):
                            self.update_interval_callback(1000)  # 1 second
                        
                        # Light batching
                        if hasattr(self, 'batching_callback'):
                            self.batching_callback(True, batch_size=20)
                    
                except Exception as e:
                    logger.error(f"Quality monitor error: {e}")
        
        # Start quality monitor
        loop = asyncio.new_event_loop()
        loop.create_task(quality_monitor())
    
    def set_callbacks(self, update_interval_callback: Optional[Callable] = None,
                     batching_callback: Optional[Callable] = None):
        """Set adaptive behavior callbacks"""
        if update_interval_callback:
            self.update_interval_callback = update_interval_callback
        if batching_callback:
            self.batching_callback = batching_callback


def create_resilient_connection(socketio, app):
    """
    Create a resilient WebSocket connection with fallback
    
    Args:
        socketio: SocketIO instance
        app: Dash app instance
        
    Returns:
        WebSocketResilience instance
    """
    
    def fallback_callback(enable_fallback: bool):
        """Callback to enable/disable fallback polling"""
        if hasattr(app, 'fallback_enabled'):
            app.fallback_enabled = enable_fallback
            logger.info(f"Fallback polling {'enabled' if enable_fallback else 'disabled'}")
    
    # Create resilience manager
    resilience = WebSocketResilience(socketio, fallback_callback)
    
    # Enable adaptive behavior
    resilience.enable_adaptive_behavior()
    
    # Set adaptive callbacks if app supports them
    if hasattr(app, 'set_update_interval'):
        resilience.set_callbacks(
            update_interval_callback=app.set_update_interval,
            batching_callback=app.set_batching_mode
        )
    
    return resilience
