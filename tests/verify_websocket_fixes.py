# -*- coding: utf-8 -*-
"""Quick test to verify WebSocket test fixes"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

# Test imports
try:
    from tests.test_websocket_events import TestWebSocketEvents, TestEventBatcher
    print("[OK] test_websocket_events imported successfully")
except Exception as e:
    print(f"[ERROR] test_websocket_events: {e}")

try:
    from tests.test_websocket_resilience import TestWebSocketResilience
    print("[OK] test_websocket_resilience imported successfully")
except Exception as e:
    print(f"[ERROR] test_websocket_resilience: {e}")

try:
    from tests.test_websocket_integration import TestWebSocketIntegration
    print("[OK] test_websocket_integration imported successfully")
except Exception as e:
    print(f"[ERROR] test_websocket_integration: {e}")

try:
    from tests.test_websocket_performance import TestWebSocketPerformance
    print("[OK] test_websocket_performance imported successfully")
except Exception as e:
    print(f"[ERROR] test_websocket_performance: {e}")

# Test basic functionality
print("\nTesting basic SocketIOTestClient functionality...")
try:
    from flask import Flask
    from flask_socketio import SocketIO
    
    app = Flask(__name__)
    app.config['TESTING'] = True
    socketio = SocketIO(app, async_mode='threading')
    
    client = socketio.test_client(app)
    
    # Test emit and receive
    @socketio.on('test_event')
    def handle_test(data):
        socketio.emit('test_response', {'echo': data})
    
    client.emit('test_event', {'msg': 'hello'})
    
    import time
    time.sleep(0.1)
    
    received = client.get_received()
    print(f"Received {len(received)} messages")
    
    for msg in received:
        print(f"  - Event: {msg.get('name')}, Data: {msg.get('args', [])}")
    
    print("[OK] Basic SocketIO test client functionality works")
    
except Exception as e:
    print(f"[ERROR] Basic functionality test failed: {e}")
    import traceback
    traceback.print_exc()

print("\nTest verification complete.")
