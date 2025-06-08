# WebSocket Dependencies Update

## Changes Made to requirements.txt

### Added WebSocket Core Dependencies:
- **flask>=2.3.0** - Required base for Flask-SocketIO
- **flask-socketio>=5.3.0** - Main WebSocket server implementation
- **python-socketio>=5.10.0** - SocketIO Python client/server
- **python-engineio>=4.8.0** - Engine.IO transport layer
- **eventlet>=0.33.0** - Async networking library for WebSocket
- **dnspython>=2.4.0** - DNS toolkit required by eventlet

### Added Testing Dependencies:
- **pytest>=7.4.0** - Testing framework
- **pytest-asyncio>=0.21.0** - Async test support
- **coverage>=7.3.0** - Code coverage reporting

## Installation Instructions

### Method 1: Using Batch Script (Windows)
```bash
install_websocket_deps.bat
```

### Method 2: Using Python Script (Cross-platform)
```bash
python install_websocket_deps.py
```

### Method 3: Manual Installation
```bash
pip install -r requirements.txt
```

## Verification
After installation, verify all packages are installed:
```bash
python -c "import flask_socketio; print('flask-socketio:', flask_socketio.__version__)"
python -c "import socketio; print('python-socketio:', socketio.__version__)"
python -c "import eventlet; print('eventlet:', eventlet.__version__)"
```

## Common Issues

### Issue: eventlet installation fails on Windows
Solution: Install Microsoft C++ Build Tools first

### Issue: DNS resolution errors
Solution: Ensure dnspython is installed: `pip install dnspython`

### Issue: ImportError for flask_socketio
Solution: Install Flask first: `pip install flask flask-socketio`
