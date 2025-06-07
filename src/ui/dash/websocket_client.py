"""
WebSocket client integration for Dash callbacks
"""

from dash import Input, Output, State, callback, clientside_callback, ClientsideFunction, ctx
import json
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


# Clientside callback for WebSocket connection management
clientside_callback(
    """
    function(n_intervals, connection_store) {
        // Initialize WebSocket connection status updates
        if (typeof window.wsConnectionStatus !== 'undefined') {
            return {
                'status': window.wsConnectionStatus,
                'timestamp': new Date().toISOString()
            };
        }
        return connection_store || {'status': 'disconnected'};
    }
    """,
    Output('websocket-connection-store', 'data'),
    Input('interval-component', 'n_intervals'),
    State('websocket-connection-store', 'data')
)


# Clientside callback for WebSocket status indicator
clientside_callback(
    """
    function(connection_store) {
        if (!connection_store) return ['ws-status ws-disconnected', 'Disconnected'];
        
        const status = connection_store.status;
        let className, text;
        
        switch(status) {
            case 'connected':
                className = 'ws-status ws-connected';
                text = 'Connected';
                break;
            case 'connecting':
                className = 'ws-status ws-connecting';
                text = 'Connecting...';
                break;
            case 'error':
                className = 'ws-status ws-disconnected';
                text = 'Connection Error';
                break;
            default:
                className = 'ws-status ws-disconnected';
                text = 'Disconnected';
        }
        
        return [className, text];
    }
    """,
    [Output('websocket-status', 'className'),
     Output('websocket-status-text', 'children')],
    Input('websocket-connection-store', 'data')
)


# Clientside callback for WebSocket event listener setup
clientside_callback(
    """
    function(n_intervals) {
        if (typeof window.swarmSocket === 'undefined' || !window.swarmSocket) {
            return window.dash_clientside.no_update;
        }
        
        // Only set up listeners once
        if (!window.wsListenersSetup) {
            window.wsListenersSetup = true;
            window.wsEventQueue = [];
            window.wsBatchQueue = [];
            
            // Agent update events
            window.swarmSocket.on('agent_update_batch', function(data) {
                window.wsBatchQueue.push({
                    type: 'agent_update_batch',
                    data: data,
                    timestamp: new Date().toISOString()
                });
            });
            
            window.swarmSocket.on('agent_created', function(data) {
                window.wsEventQueue.push({
                    type: 'agent_created',
                    data: data,
                    timestamp: new Date().toISOString()
                });
            });
            
            window.swarmSocket.on('agent_deleted', function(data) {
                window.wsEventQueue.push({
                    type: 'agent_deleted',
                    data: data,
                    timestamp: new Date().toISOString()
                });
            });
            
            window.swarmSocket.on('agent_critical_update', function(data) {
                window.wsEventQueue.push({
                    type: 'agent_critical_update',
                    data: data,
                    timestamp: new Date().toISOString()
                });
            });
            
            // Task update events
            window.swarmSocket.on('task_update_batch', function(data) {
                window.wsBatchQueue.push({
                    type: 'task_update_batch',
                    data: data,
                    timestamp: new Date().toISOString()
                });
            });
            
            window.swarmSocket.on('task_completed', function(data) {
                window.wsEventQueue.push({
                    type: 'task_completed',
                    data: data,
                    timestamp: new Date().toISOString()
                });
            });
            
            window.swarmSocket.on('task_failed', function(data) {
                window.wsEventQueue.push({
                    type: 'task_failed',
                    data: data,
                    timestamp: new Date().toISOString()
                });
            });
            
            // Performance metric events
            window.swarmSocket.on('metric_update_batch', function(data) {
                window.wsBatchQueue.push({
                    type: 'metric_update_batch',
                    data: data,
                    timestamp: new Date().toISOString()
                });
            });
            
            // System events
            window.swarmSocket.on('system_alert', function(data) {
                window.wsEventQueue.push({
                    type: 'system_alert',
                    data: data,
                    timestamp: new Date().toISOString()
                });
            });
            
            window.swarmSocket.on('swarm_status_update', function(data) {
                window.wsEventQueue.push({
                    type: 'swarm_status_update',
                    data: data,
                    timestamp: new Date().toISOString()
                });
            });
        }
        
        return window.dash_clientside.no_update;
    }
    """,
    Output('websocket-event-store', 'data'),
    Input('interval-component', 'n_intervals'),
    prevent_initial_call=True
)


# Clientside callback to process WebSocket event queue
clientside_callback(
    """
    function(n_intervals, current_events) {
        if (typeof window.wsEventQueue === 'undefined' || window.wsEventQueue.length === 0) {
            return window.dash_clientside.no_update;
        }
        
        // Get all queued events
        const events = window.wsEventQueue.splice(0);
        return events;
    }
    """,
    Output('websocket-event-store', 'data'),
    Input('interval-component', 'n_intervals'),
    State('websocket-event-store', 'data')
)


# Clientside callback to process WebSocket batch queue
clientside_callback(
    """
    function(n_intervals, current_batches) {
        if (typeof window.wsBatchQueue === 'undefined' || window.wsBatchQueue.length === 0) {
            return window.dash_clientside.no_update;
        }
        
        // Get all queued batches
        const batches = window.wsBatchQueue.splice(0);
        return batches;
    }
    """,
    Output('websocket-batch-store', 'data'),
    Input('interval-component', 'n_intervals'),
    State('websocket-batch-store', 'data')
)


# Clientside callback for WebSocket fallback control
clientside_callback(
    """
    function(connection_store) {
        if (!connection_store) return true;
        
        // Enable fallback interval if disconnected
        return connection_store.status !== 'connected';
    }
    """,
    Output('websocket-fallback-interval', 'disabled'),
    Input('websocket-connection-store', 'data')
)


# Clientside callback to handle fallback events
clientside_callback(
    """
    function(n_intervals) {
        // Listen for fallback events
        if (!window.wsFallbackListenerSetup) {
            window.wsFallbackListenerSetup = true;
            
            window.addEventListener('websocket-fallback', function(event) {
                const enabled = event.detail.enabled;
                console.log('WebSocket fallback mode:', enabled ? 'enabled' : 'disabled');
                
                // Update fallback interval state
                const fallbackInterval = document.getElementById('websocket-fallback-interval');
                if (fallbackInterval) {
                    // Trigger update through Dash
                    window.dash_clientside.set_props('websocket-fallback-interval', {
                        disabled: !enabled
                    });
                }
            });
        }
        
        return window.dash_clientside.no_update;
    }
    """,
    Output('websocket-event-store', 'data'),
    Input('interval-component', 'n_intervals'),
    prevent_initial_call=True
)


def process_websocket_events(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Process WebSocket events and return updated data
    
    Args:
        events: List of WebSocket events
        
    Returns:
        Dictionary with updated data for various stores
    """
    if not events:
        return {}
    
    updates = {
        'agents': {},
        'tasks': {},
        'metrics': {},
        'alerts': []
    }
    
    for event in events:
        event_type = event.get('type')
        data = event.get('data', {})
        
        if event_type == 'agent_created':
            agent_id = data.get('agent_id')
            updates['agents'][agent_id] = {
                'status': 'idle',
                'type': data.get('agent_type'),
                'capabilities': data.get('capabilities', []),
                'created_at': data.get('timestamp')
            }
            
        elif event_type == 'agent_deleted':
            agent_id = data.get('agent_id')
            updates['agents'][agent_id] = None  # Mark for deletion
            
        elif event_type == 'agent_critical_update':
            agent_id = data.get('agent_id')
            if agent_id:
                updates['agents'][agent_id] = {
                    'status': data.get('new_status'),
                    'error': data.get('details', {}).get('error')
                }
                
        elif event_type == 'task_completed':
            task_id = data.get('task_id')
            updates['tasks'][task_id] = {
                'status': 'completed',
                'completed_at': data.get('timestamp'),
                'duration_ms': data.get('duration_ms')
            }
            
        elif event_type == 'task_failed':
            task_id = data.get('task_id')
            updates['tasks'][task_id] = {
                'status': 'failed',
                'error': data.get('error'),
                'failed_at': data.get('timestamp')
            }
            
        elif event_type == 'system_alert':
            updates['alerts'].append({
                'level': data.get('level'),
                'message': data.get('message'),
                'timestamp': data.get('timestamp')
            })
            
        elif event_type == 'swarm_status_update':
            updates['swarm_status'] = data.get('status', {})
    
    return updates


def process_websocket_batches(batches: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Process WebSocket batch events and return updated data
    
    Args:
        batches: List of WebSocket batch events
        
    Returns:
        Dictionary with updated data for various stores
    """
    if not batches:
        return {}
    
    updates = {
        'agents': {},
        'tasks': {},
        'metrics': {}
    }
    
    for batch_event in batches:
        batch_type = batch_event.get('type')
        batch_data = batch_event.get('data', {})
        
        if batch_type == 'agent_update_batch':
            for item in batch_data.get('batch', []):
                agent_id = item.get('agent_id')
                if agent_id:
                    updates['agents'][agent_id] = {
                        'status': item.get('new_status'),
                        'updated_at': item.get('timestamp')
                    }
                    
        elif batch_type == 'task_update_batch':
            for item in batch_data.get('batch', []):
                task_id = item.get('task_id')
                if task_id:
                    updates['tasks'][task_id] = {
                        'status': item.get('event', 'updated'),
                        'agent_id': item.get('agent_id'),
                        'updated_at': item.get('timestamp')
                    }
                    
        elif batch_type == 'metric_update_batch':
            for item in batch_data.get('batch', []):
                metrics = item.get('metrics', {})
                agent_id = item.get('agent_id')
                
                if agent_id:
                    updates['metrics'][agent_id] = {
                        'cpu': item.get('cpu'),
                        'memory': item.get('memory'),
                        'tasks_completed': item.get('tasks_completed'),
                        'error_rate': item.get('error_rate')
                    }
                else:
                    # System-wide metrics
                    updates['metrics']['system'] = metrics
    
    return updates
