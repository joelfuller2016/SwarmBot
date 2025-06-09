# -*- coding: utf-8 -*-
"""
WebSocket Functionality Verification Script
"""
import os
import sys

# Change to the SwarmBot directory
project_root = r'C:\Users\joelf\OneDrive\Joels Files\Documents\GitHub\SwarmBot'
os.chdir(project_root)
sys.path.insert(0, project_root)

print("SwarmBot WebSocket Functionality Verification")
print("=" * 60)

# Test 1: Import WebSocket modules
print("\n1. Testing WebSocket module imports...")
try:
    from src.ui.dash.websocket_events import emit_agent_created, emit_agent_status_change
    print("   ✓ websocket_events module imported successfully")
except Exception as e:
    print(f"   ✗ websocket_events import failed: {e}")

try:
    from src.ui.dash.websocket_resilience import WebSocketResilience
    print("   ✓ websocket_resilience module imported successfully")
except Exception as e:
    print(f"   ✗ websocket_resilience import failed: {e}")

try:
    from src.ui.dash.integration import setup_swarm_event_handlers
    print("   ✓ integration module imported successfully")
except Exception as e:
    print(f"   ✗ integration import failed: {e}")

# Test 2: Check if Flask-SocketIO is installed
print("\n2. Testing Flask-SocketIO installation...")
try:
    import flask_socketio
    print(f"   ✓ Flask-SocketIO version: {flask_socketio.__version__}")
except Exception as e:
    print(f"   ✗ Flask-SocketIO not installed: {e}")

# Test 3: Check WebSocket server configuration
print("\n3. Testing WebSocket server setup...")
try:
    from src.ui.dash.app import socketio
    if socketio:
        print("   ✓ SocketIO instance found in app.py")
    else:
        print("   ✗ SocketIO instance not configured")
except Exception as e:
    print(f"   ✗ Could not verify SocketIO setup: {e}")

# Test 4: Check if event handlers are registered
print("\n4. Testing event handler registration...")
try:
    from src.ui.dash.app import app
    from flask_socketio import SocketIO
    
    # Create a test SocketIO instance
    test_socketio = SocketIO()
    test_socketio.init_app(app, async_mode='threading')
    
    print("   ✓ SocketIO can be initialized with the app")
except Exception as e:
    print(f"   ✗ Event handler registration failed: {e}")

# Test 5: Check SwarmCoordinator integration
print("\n5. Testing SwarmCoordinator WebSocket integration...")
try:
    from src.core.swarm_coordinator import SwarmCoordinator
    
    # Check if the coordinator has WebSocket callbacks
    coordinator = SwarmCoordinator(config={})
    if hasattr(coordinator, 'on_agent_created_callback'):
        print("   ✓ SwarmCoordinator has WebSocket callbacks")
    else:
        print("   ✗ SwarmCoordinator missing WebSocket callbacks")
except Exception as e:
    print(f"   ✗ SwarmCoordinator check failed: {e}")

# Test 6: Test basic WebSocket functionality
print("\n6. Testing basic WebSocket functionality...")
try:
    from flask import Flask
    from flask_socketio import SocketIO, emit
    
    # Create a minimal test app
    test_app = Flask(__name__)
    test_app.config['SECRET_KEY'] = 'test-secret'
    test_socketio = SocketIO(test_app, async_mode='threading')
    
    # Create a test client
    client = test_socketio.test_client(test_app)
    
    # Test basic emit
    @test_socketio.on('test_event')
    def handle_test(data):
        emit('test_response', {'echo': data})
    
    # Send test event
    client.emit('test_event', {'msg': 'hello'})
    
    # Check received events
    import time
    time.sleep(0.1)
    received = client.get_received()
    
    if received and any(msg.get('name') == 'test_response' for msg in received):
        print("   ✓ Basic WebSocket emit/receive working")
    else:
        print("   ✗ WebSocket emit/receive not working")
        
except Exception as e:
    print(f"   ✗ Basic functionality test failed: {e}")

# Test 7: Check dashboard WebSocket client
print("\n7. Testing dashboard WebSocket client setup...")
try:
    with open(os.path.join(project_root, 'src/ui/dash/app.py'), 'r') as f:
        app_content = f.read()
        
    if 'socketio.init_app' in app_content or 'SocketIO(' in app_content:
        print("   ✓ Dashboard app has SocketIO initialization")
    else:
        print("   ✗ Dashboard app missing SocketIO initialization")
        
    if 'socket.io.js' in app_content or 'external_scripts' in app_content:
        print("   ✓ Dashboard includes Socket.IO client script")
    else:
        print("   ✗ Dashboard missing Socket.IO client script")
        
except Exception as e:
    print(f"   ✗ Dashboard check failed: {e}")

# Summary
print("\n" + "=" * 60)
print("WebSocket Verification Summary")
print("=" * 60)

# Check if we can run the actual tests
print("\n8. Checking if WebSocket tests can be run...")
try:
    import unittest
    from tests.test_websocket_events import TestWebSocketEvents
    
    # Try to create a test instance
    test = TestWebSocketEvents()
    test.setUp()
    print("   ✓ WebSocket test setup successful")
    test.tearDown()
except Exception as e:
    print(f"   ✗ WebSocket test setup failed: {e}")

print("\nVerification complete!")
print("\nTo run the full WebSocket test suite:")
print("  python tests/test_websocket_suite.py")
print("\nTo run individual test modules:")
print("  python -m pytest tests/test_websocket_events.py -v")
print("  python -m pytest tests/test_websocket_resilience.py -v")
print("  python -m pytest tests/test_websocket_integration.py -v")
print("  python -m pytest tests/test_websocket_performance.py -v")
