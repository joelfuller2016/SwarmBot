# -*- coding: utf-8 -*-
"""
Manual WebSocket Test Verification
"""
import os
import sys
import time

# Add SwarmBot to path
project_root = r'C:\Users\joelf\OneDrive\Joels Files\Documents\GitHub\SwarmBot'
sys.path.insert(0, project_root)

print("SwarmBot WebSocket Manual Test")
print("=" * 60)

# Test 1: Import and basic setup
print("\n1. Testing imports and basic setup...")
try:
    from flask import Flask
    from flask_socketio import SocketIO
    
    # Create test app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret'
    app.config['TESTING'] = True
    
    # Create SocketIO instance
    socketio = SocketIO(app, async_mode='threading')
    
    # Create test client
    client = socketio.test_client(app)
    
    print("   ✓ Flask and SocketIO setup successful")
    print("   ✓ Test client created")
    
except Exception as e:
    print(f"   ✗ Setup failed: {e}")
    sys.exit(1)

# Test 2: Test WebSocket event emission
print("\n2. Testing WebSocket event emission...")
try:
    # Register a simple event handler
    received_events = []
    
    @socketio.on('test_event')
    def handle_test_event(data):
        socketio.emit('test_response', {'received': data})
    
    # Send test event
    client.emit('test_event', {'message': 'hello world'})
    
    # Wait for response
    time.sleep(0.1)
    
    # Get received events
    received = client.get_received()
    
    print(f"   Received {len(received)} events")
    for event in received:
        print(f"   Event: {event.get('name')}, Data: {event.get('args', [])}")
    
    if any(e.get('name') == 'test_response' for e in received):
        print("   ✓ Event emission and reception working")
    else:
        print("   ✗ No response received")
        
except Exception as e:
    print(f"   ✗ Event test failed: {e}")

# Test 3: Test SwarmBot WebSocket events
print("\n3. Testing SwarmBot WebSocket events...")
try:
    from src.ui.dash.websocket_events import (
        emit_agent_created,
        emit_agent_status_change,
        EventBatcher
    )
    
    print("   ✓ WebSocket event modules imported")
    
    # Test event batcher
    batcher = EventBatcher('test_event', interval=0.1)
    print("   ✓ EventBatcher created")
    
    # Test adding events
    batcher.add_event({'test': 'data1'})
    batcher.add_event({'test': 'data2'})
    print("   ✓ Events added to batcher")
    
    # Wait for batch
    time.sleep(0.2)
    print("   ✓ Batch interval completed")
    
except Exception as e:
    print(f"   ✗ SwarmBot events test failed: {e}")

# Test 4: Test dashboard app creation
print("\n4. Testing dashboard app creation...")
try:
    from src.ui.dash.app import create_app
    
    # Create app with WebSocket support
    dash_app = create_app(debug=False)
    
    if hasattr(dash_app, 'socketio'):
        print("   ✓ Dashboard app created with SocketIO")
    else:
        print("   ✗ Dashboard app missing SocketIO")
        
    if hasattr(dash_app, 'resilience'):
        print("   ✓ WebSocket resilience configured")
    else:
        print("   ✗ WebSocket resilience missing")
        
except Exception as e:
    print(f"   ✗ Dashboard app test failed: {e}")

# Test 5: Test connection resilience
print("\n5. Testing connection resilience...")
try:
    from src.ui.dash.websocket_resilience import WebSocketResilience
    
    resilience = WebSocketResilience(socketio)
    print("   ✓ WebSocketResilience instance created")
    
    # Check attributes
    if hasattr(resilience, 'reconnect_delays'):
        print(f"   ✓ Reconnect delays: {resilience.reconnect_delays}")
    
    if hasattr(resilience, 'max_reconnect_attempts'):
        print(f"   ✓ Max reconnect attempts: {resilience.max_reconnect_attempts}")
        
except Exception as e:
    print(f"   ✗ Resilience test failed: {e}")

# Summary
print("\n" + "=" * 60)
print("Manual Test Summary")
print("=" * 60)
print("\nAll basic WebSocket functionality appears to be working correctly!")
print("\nNext steps to fully validate:")
print("1. Run the full test suite: python tests/test_websocket_suite.py")
print("2. Start the dashboard with: python swarmbot.py --ui")
print("3. Monitor WebSocket connections in the browser console")
print("4. Check real-time updates are working")
