"""
Main Dash application for SwarmBot UI with WebSocket support
"""

import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash_extensions.enrich import DashProxy, MultiplexerTransform
import plotly.io as pio
from flask_socketio import SocketIO
from flask import Flask
import os
from typing import Optional
from .websocket_events import init_websocket_events
from .websocket_resilience import create_resilient_connection

# Set plotly theme
pio.templates.default = "plotly_dark"

# Global SocketIO instance
socketio = None


def create_app(swarm_coordinator=None, debug: bool = False) -> Dash:
    """
    Create and configure the Dash application with WebSocket support
    
    Args:
        swarm_coordinator: SwarmCoordinator instance to monitor
        debug: Enable debug mode
        
    Returns:
        Configured Dash application with SocketIO
    """
    global socketio
    
    # Use DashProxy with MultiplexerTransform for better callback handling
    app = DashProxy(
        __name__,
        transforms=[MultiplexerTransform()],
        external_stylesheets=[
            dbc.themes.DARKLY,  # Dark theme
            dbc.icons.FONT_AWESOME,  # Icons
            "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
        ],
        suppress_callback_exceptions=True,
        title="SwarmBot Control Center"
    )
    
    # Configure Flask server for SocketIO
    server = app.server
    server.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'swarmbot-secret-key-change-in-production')
    
    # Initialize SocketIO with the Flask server
    socketio = SocketIO(
        server,
        cors_allowed_origins="*",  # Configure appropriately for production
        async_mode='threading',
        logger=debug,
        engineio_logger=debug
    )
    
    # Initialize WebSocket event handlers
    init_websocket_events(socketio)
    
    # Create resilient connection manager
    resilience = create_resilient_connection(socketio, app)
    
    # Store references in app
    app.socketio = socketio
    app.swarm_coordinator = swarm_coordinator
    app.resilience = resilience
    app.fallback_enabled = False
    
    # Store custom configuration as app attributes
    app.app_name = "SwarmBot"
    app.update_interval = 1000  # 1 second update interval
    app.max_agents = 50
    app.max_tasks_display = 100
    app.theme = "dark"
    
    # Add custom CSS
    app.index_string = '''
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
            <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
            <style>
                body {
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    background-color: #0d1117;
                    color: #c9d1d9;
                }
                
                .card {
                    background-color: #161b22;
                    border: 1px solid #30363d;
                    border-radius: 8px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
                    transition: all 0.3s cubic-bezier(.25,.8,.25,1);
                }
                
                .card:hover {
                    box-shadow: 0 14px 28px rgba(0,0,0,0.25), 0 10px 10px rgba(0,0,0,0.22);
                    transform: translateY(-2px);
                }
                
                .metric-card {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 12px;
                    padding: 20px;
                    color: white;
                }
                
                .agent-status-idle { color: #58a6ff; }
                .agent-status-busy { color: #f97316; }
                .agent-status-processing { color: #8b5cf6; }
                .agent-status-error { color: #ef4444; }
                .agent-status-offline { color: #6b7280; }
                
                .task-priority-high { border-left: 4px solid #ef4444; }
                .task-priority-medium { border-left: 4px solid #f59e0b; }
                .task-priority-low { border-left: 4px solid #10b981; }
                
                .navbar {
                    background-color: #161b22 !important;
                    border-bottom: 1px solid #30363d;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                
                .sidebar {
                    background-color: #0d1117;
                    border-right: 1px solid #30363d;
                    height: 100vh;
                    position: fixed;
                    overflow-y: auto;
                }
                
                .main-content {
                    margin-left: 250px;
                    padding: 20px;
                }
                
                @keyframes pulse {
                    0% { opacity: 1; }
                    50% { opacity: 0.5; }
                    100% { opacity: 1; }
                }
                
                .pulse {
                    animation: pulse 2s infinite;
                }
                
                .graph-container {
                    background-color: #161b22;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                }
                
                /* Custom scrollbar */
                ::-webkit-scrollbar {
                    width: 8px;
                    height: 8px;
                }
                
                ::-webkit-scrollbar-track {
                    background: #161b22;
                }
                
                ::-webkit-scrollbar-thumb {
                    background: #30363d;
                    border-radius: 4px;
                }
                
                ::-webkit-scrollbar-thumb:hover {
                    background: #484f58;
                }
                
                /* WebSocket connection status indicator */
                .ws-status {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    padding: 10px 20px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 500;
                    z-index: 1000;
                    transition: all 0.3s ease;
                }
                
                .ws-connected {
                    background-color: #10b981;
                    color: white;
                }
                
                .ws-disconnected {
                    background-color: #ef4444;
                    color: white;
                }
                
                .ws-connecting {
                    background-color: #f59e0b;
                    color: white;
                }
            </style>
            <script>
                // Initialize Socket.IO connection with resilience
                document.addEventListener('DOMContentLoaded', function() {
                    // Connection configuration
                    const config = {
                        reconnection: true,
                        reconnectionDelay: 1000,
                        reconnectionDelayMax: 30000,
                        reconnectionAttempts: Infinity,
                        timeout: 20000,
                        transports: ['websocket', 'polling']
                    };
                    
                    // Initialize connection
                    window.swarmSocket = io(config);
                    window.wsReconnectAttempts = 0;
                    window.wsQueuedEvents = [];
                    window.wsMaxQueueSize = 100;
                    
                    // Connection event handlers
                    window.swarmSocket.on('connect', function() {
                        console.log('WebSocket connected');
                        window.wsReconnectAttempts = 0;
                        updateConnectionStatus('connected');
                        
                        // Flush queued events
                        if (window.wsQueuedEvents.length > 0) {
                            console.log('Flushing ' + window.wsQueuedEvents.length + ' queued events');
                            window.wsQueuedEvents.forEach(function(event) {
                                window.swarmSocket.emit(event.type, event.data);
                            });
                            window.wsQueuedEvents = [];
                        }
                        
                        // Send connection quality info
                        window.swarmSocket.emit('connection_quality', {
                            user_agent: navigator.userAgent,
                            timestamp: new Date().toISOString()
                        });
                    });
                    
                    window.swarmSocket.on('disconnect', function() {
                        console.log('WebSocket disconnected');
                        updateConnectionStatus('disconnected');
                    });
                    
                    window.swarmSocket.on('connect_error', function(error) {
                        console.error('WebSocket connection error:', error);
                        window.wsReconnectAttempts++;
                        updateConnectionStatus('error');
                        
                        // Switch to fallback after 5 attempts
                        if (window.wsReconnectAttempts >= 5 && !window.wsFallbackEnabled) {
                            console.log('Enabling fallback polling mode');
                            window.wsFallbackEnabled = true;
                            // Signal Dash to enable fallback interval
                            window.dispatchEvent(new CustomEvent('websocket-fallback', {
                                detail: { enabled: true }
                            }));
                        }
                    });
                    
                    window.swarmSocket.on('reconnecting', function(attemptNumber) {
                        console.log('WebSocket reconnecting (attempt ' + attemptNumber + ')');
                        updateConnectionStatus('connecting');
                    });
                    
                    window.swarmSocket.on('reconnect', function() {
                        console.log('WebSocket reconnected');
                        window.wsFallbackEnabled = false;
                        window.dispatchEvent(new CustomEvent('websocket-fallback', {
                            detail: { enabled: false }
                        }));
                    });
                    
                    // Heartbeat handling
                    window.swarmSocket.on('ping', function(data) {
                        window.swarmSocket.emit('pong', {
                            ping_id: data.ping_id,
                            timestamp: new Date().toISOString()
                        });
                    });
                    
                    // Function to update connection status indicator
                    function updateConnectionStatus(status) {
                        window.wsConnectionStatus = status;
                        
                        // Update visual indicator
                        const indicator = document.getElementById('websocket-status');
                        if (indicator) {
                            indicator.className = 'ws-status ws-' + status;
                            const text = document.getElementById('websocket-status-text');
                            if (text) {
                                switch(status) {
                                    case 'connected':
                                        text.textContent = 'Connected';
                                        break;
                                    case 'connecting':
                                        text.textContent = 'Connecting...';
                                        break;
                                    case 'disconnected':
                                        text.textContent = 'Disconnected';
                                        break;
                                    case 'error':
                                        text.textContent = 'Connection Error';
                                        break;
                                }
                            }
                        }
                    }
                    
                    // Queue event if disconnected
                    window.queueWebSocketEvent = function(eventType, data) {
                        if (window.swarmSocket.connected) {
                            window.swarmSocket.emit(eventType, data);
                        } else {
                            // Queue event for later
                            if (window.wsQueuedEvents.length < window.wsMaxQueueSize) {
                                window.wsQueuedEvents.push({
                                    type: eventType,
                                    data: data,
                                    timestamp: new Date().toISOString()
                                });
                            }
                        }
                    };
                    
                    // Monitor connection quality
                    setInterval(function() {
                        if (window.swarmSocket.connected) {
                            const startTime = Date.now();
                            window.swarmSocket.emit('ping', {
                                ping_id: 'quality_' + startTime
                            });
                            
                            // Listen for pong to measure latency
                            window.swarmSocket.once('pong', function(data) {
                                if (data.ping_id === 'quality_' + startTime) {
                                    const latency = Date.now() - startTime;
                                    window.wsLatency = latency;
                                    
                                    // Adapt behavior based on latency
                                    if (latency > 500) {
                                        console.log('High latency detected: ' + latency + 'ms');
                                    }
                                }
                            });
                        }
                    }, 30000); // Check every 30 seconds
                });
            </script>
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    '''
    
    return app


def serve_app(app: Dash, host: str = "127.0.0.1", port: int = 8050, debug: bool = False):
    """
    Serve the Dash application with WebSocket support
    
    Args:
        app: Dash application instance
        host: Host address
        port: Port number
        debug: Enable debug mode
    """
    global socketio
    
    if hasattr(app, 'socketio') and app.socketio:
        # Use SocketIO to run the server
        app.socketio.run(app.server, host=host, port=port, debug=debug)
    else:
        # Fallback to regular Dash server
        app.run(host=host, port=port, debug=debug, threaded=True)
