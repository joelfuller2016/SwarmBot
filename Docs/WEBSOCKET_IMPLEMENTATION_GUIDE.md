# WebSocket Implementation Guide for SwarmBot UI

## Overview
This guide provides step-by-step instructions to implement WebSocket support for real-time updates in the SwarmBot dashboard, completing Task #21.

## Current State
- Using Dash interval callbacks with 1-second polling
- All data updates happen synchronously every second
- No push notifications from backend to frontend

## Target State
- WebSocket connection for real-time push updates
- Event-driven updates when agent status changes
- Immediate task completion notifications
- Reduced server load from eliminating polling

## Implementation Steps

### 1. Install Dependencies
```bash
pip install flask-socketio>=5.3.0
```

### 2. Modify app.py to Support SocketIO
```python
# src/ui/dash/app.py
from flask_socketio import SocketIO

def create_app(swarm_coordinator=None, debug: bool = False) -> Dash:
    # ... existing code ...
    
    # Add SocketIO support
    app.server.config['SECRET_KEY'] = 'your-secret-key'
    socketio = SocketIO(app.server, cors_allowed_origins="*")
    app.socketio = socketio
    
    return app
```

### 3. Create WebSocket Event Handlers
```python
# src/ui/dash/websocket_events.py
from flask_socketio import emit, join_room, leave_room

def register_websocket_events(socketio, swarm_coordinator):
    @socketio.on('connect')
    def handle_connect():
        print(f"Client connected: {request.sid}")
        join_room('swarm_updates')
        emit('connected', {'data': 'Connected to SwarmBot'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print(f"Client disconnected: {request.sid}")
        leave_room('swarm_updates')
    
    # Agent status updates
    def emit_agent_update(agent_id, status):
        socketio.emit('agent_status_changed', {
            'agent_id': agent_id,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }, room='swarm_updates')
    
    # Task updates
    def emit_task_update(task_id, status):
        socketio.emit('task_status_changed', {
            'task_id': task_id,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }, room='swarm_updates')
    
    # Register callbacks with swarm coordinator
    swarm_coordinator.on_agent_status_change = emit_agent_update
    swarm_coordinator.on_task_complete = emit_task_update
```

### 4. Modify SwarmCoordinator to Emit Events
```python
# src/agents/swarm_coordinator.py
class SwarmCoordinator:
    def __init__(self, name: str = "SwarmCoordinator"):
        # ... existing code ...
        
        # Event callbacks
        self.on_agent_status_change = None
        self.on_task_complete = None
    
    def update_agent_status(self, agent_id: str, new_status: AgentStatus):
        """Update agent status and emit event"""
        if agent_id in self.agents:
            self.agents[agent_id].status = new_status
            
            # Emit event if callback registered
            if self.on_agent_status_change:
                self.on_agent_status_change(agent_id, new_status.value)
    
    def complete_task(self, task_id: str, result: Dict[str, Any]):
        """Complete a task and emit event"""
        # ... existing completion logic ...
        
        # Emit event if callback registered
        if self.on_task_complete:
            self.on_task_complete(task_id, "completed")
```

### 5. Update Frontend to Listen for WebSocket Events
```python
# src/ui/dash/callbacks.py
# Add WebSocket client initialization
from dash_extensions.enrich import DashProxy, WebSocket

# Modify callbacks to listen for WebSocket events
@app.callback(
    Output('agent-data-store', 'data'),
    [Input('ws', 'message'),
     Input('interval-component', 'n_intervals')]
)
def update_agent_store(ws_message, n):
    """Update agent store from WebSocket or interval"""
    ctx_triggered = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if ctx_triggered == 'ws' and ws_message:
        # Handle WebSocket message
        if ws_message.get('type') == 'agent_status_changed':
            # Update specific agent
            agent_id = ws_message['agent_id']
            # ... update logic ...
    else:
        # Fallback to interval update
        # ... existing interval logic ...
```

### 6. Add WebSocket Component to Layout
```python
# src/ui/dash/layouts.py
from dash_extensions import WebSocket

def create_main_layout() -> html.Div:
    return html.Div([
        # ... existing layout ...
        
        # Add WebSocket component
        WebSocket(id="ws", url="ws://localhost:8050/socket.io/"),
        
        # ... rest of layout ...
    ])
```

### 7. Update integration.py to Start SocketIO
```python
# src/ui/dash/integration.py
def serve_app(app: Dash, host: str = "127.0.0.1", port: int = 8050, debug: bool = False):
    """Serve the Dash application with SocketIO support"""
    if hasattr(app, 'socketio'):
        app.socketio.run(app.server, host=host, port=port, debug=debug)
    else:
        app.run(host=host, port=port, debug=debug, threaded=True)
```

## Testing WebSocket Implementation

### 1. Unit Tests
```python
# tests/test_websocket.py
import pytest
from flask_socketio import SocketIOTestClient

def test_websocket_connection(app):
    client = SocketIOTestClient(app, app.socketio)
    received = client.get_received()
    assert len(received) == 1
    assert received[0]['name'] == 'connected'

def test_agent_status_update(app, swarm_coordinator):
    client = SocketIOTestClient(app, app.socketio)
    
    # Trigger agent status change
    swarm_coordinator.update_agent_status("agent1", AgentStatus.BUSY)
    
    received = client.get_received()
    assert any(msg['name'] == 'agent_status_changed' for msg in received)
```

### 2. Integration Tests
1. Start the dashboard with WebSocket support
2. Open browser developer tools
3. Check WebSocket connection in Network tab
4. Create/modify agents and verify immediate updates
5. Submit tasks and verify real-time status changes

## Performance Improvements

### Before (Polling)
- Network requests: 60/minute (1 per second)
- Server load: Constant database queries
- Update latency: 0-1000ms (average 500ms)

### After (WebSocket)
- Network requests: Only on actual changes
- Server load: Event-driven, minimal overhead
- Update latency: <100ms typically

## Rollback Plan
If WebSocket implementation causes issues:
1. Set `use_websocket = False` in config
2. Callbacks will fallback to interval polling
3. No functionality lost, only real-time updates

## Estimated Implementation Time
- Basic WebSocket support: 2-3 hours
- Full event integration: 1-2 hours
- Testing and debugging: 1-2 hours
- **Total: 4-7 hours**

## Future Enhancements
1. Implement connection retry logic
2. Add message queuing for offline clients
3. Implement room-based updates for multi-tenant support
4. Add binary data support for file transfers
5. Implement rate limiting for event emissions

---

*Guide created for Task #21: Real-Time Dashboard Updates*
*Date: June 7, 2025*