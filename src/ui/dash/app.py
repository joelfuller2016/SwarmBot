"""
Main Dash application for SwarmBot UI
"""

import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash_extensions.enrich import DashProxy, MultiplexerTransform
import plotly.io as pio
from typing import Optional

# Set plotly theme
pio.templates.default = "plotly_dark"


def create_app(swarm_coordinator=None, debug: bool = False) -> Dash:
    """
    Create and configure the Dash application
    
    Args:
        swarm_coordinator: SwarmCoordinator instance to monitor
        debug: Enable debug mode
        
    Returns:
        Configured Dash application
    """
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
    
    # Store swarm coordinator reference
    app.swarm_coordinator = swarm_coordinator
    
    # Configure app
    app.config.update({
        "app_name": "SwarmBot",
        "update_interval": 1000,  # 1 second update interval
        "max_agents": 50,
        "max_tasks_display": 100,
        "theme": "dark"
    })
    
    # Add custom CSS
    app.index_string = '''
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
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
            </style>
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
    Serve the Dash application
    
    Args:
        app: Dash application instance
        host: Host address
        port: Port number
        debug: Enable debug mode
    """
    app.run_server(host=host, port=port, debug=debug, threaded=True)
