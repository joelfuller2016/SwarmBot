@echo off
echo ========================================
echo Installing SwarmBot WebSocket Dependencies
echo ========================================
echo.

echo Updating pip...
python -m pip install --upgrade pip

echo.
echo Installing all requirements...
pip install -r requirements.txt

echo.
echo Verifying WebSocket packages...
python -c "import flask_socketio; print('✓ flask-socketio version:', flask_socketio.__version__)"
python -c "import socketio; print('✓ python-socketio version:', socketio.__version__)"
python -c "import engineio; print('✓ python-engineio version:', engineio.__version__)"
python -c "import eventlet; print('✓ eventlet version:', eventlet.__version__)"
python -c "import dash; print('✓ dash version:', dash.__version__)"

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo You can now run the WebSocket tests:
echo python tests\test_websocket_suite.py
echo.
pause
