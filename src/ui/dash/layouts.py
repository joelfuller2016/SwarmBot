"""
Layout definitions for SwarmBot Dash UI
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from typing import Optional, Dict, Any


def create_navbar() -> dbc.Navbar:
    """Create the navigation bar"""
    return dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.I(className="fas fa-robot fa-2x text-primary"),
                    html.Span("SwarmBot Control Center", 
                             className="ms-3 h3 mb-0 text-white")
                ], width="auto"),
                dbc.Col([
                    dbc.Nav([
                        dbc.NavItem(dbc.NavLink("Dashboard", href="/", active=True)),
                        dbc.NavItem(dbc.NavLink("Agents", href="/agents")),
                        dbc.NavItem(dbc.NavLink("Tasks", href="/tasks")),
                        dbc.NavItem(dbc.NavLink("Performance", href="/performance")),
                        dbc.NavItem(dbc.NavLink("Testing", href="/testing")),
                        dbc.NavItem(dbc.NavLink("Settings", href="/settings")),
                    ], navbar=True)
                ], width=True),
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-circle text-success me-2"),
                        html.Span("System Online", className="text-white")
                    ])
                ], width="auto")
            ], className="w-100 align-items-center"),
        ], fluid=True),
        className="navbar",
        dark=True,
        sticky="top"
    )


def create_sidebar() -> html.Div:
    """Create the sidebar navigation"""
    return html.Div([
        html.Div([
            html.H5("Quick Actions", className="text-white mb-3"),
            dbc.ButtonGroup([
                dbc.Button("New Agent", color="primary", size="sm", className="mb-2"),
                dbc.Button("New Task", color="primary", size="sm", className="mb-2"),
                dbc.Button("Stop All", color="danger", size="sm", className="mb-2"),
            ], vertical=True, className="w-100")
        ], className="p-3 border-bottom"),
        
        html.Div([
            html.H5("System Status", className="text-white mb-3"),
            html.Div([
                html.Div([
                    html.Span("Active Agents: ", className="text-muted"),
                    html.Span(id="active-agents-count", children="0", className="text-white")
                ], className="mb-2"),
                html.Div([
                    html.Span("Running Tasks: ", className="text-muted"),
                    html.Span(id="running-tasks-count", children="0", className="text-white")
                ], className="mb-2"),
                html.Div([
                    html.Span("CPU Usage: ", className="text-muted"),
                    html.Span(id="cpu-usage", children="0%", className="text-white")
                ], className="mb-2"),
                html.Div([
                    html.Span("Memory: ", className="text-muted"),
                    html.Span(id="memory-usage", children="0 MB", className="text-white")
                ], className="mb-2"),
            ])
        ], className="p-3 border-bottom"),
        
        html.Div([
            html.H5("Recent Activity", className="text-white mb-3"),
            html.Div(id="recent-activity", children=[
                html.Div("No recent activity", className="text-muted small")
            ])
        ], className="p-3")
    ], className="sidebar")


def create_main_layout() -> html.Div:
    """Create the main application layout"""
    return html.Div([
        # Header
        create_navbar(),
        
        # Main container
        html.Div([
            # Sidebar
            create_sidebar(),
            
            # Main content area
            html.Div([
                # Page content
                dcc.Location(id='url', refresh=False),
                html.Div(id='page-content', className="p-4"),
                
                # Update interval
                dcc.Interval(
                    id='interval-component',
                    interval=1000,  # Update every second
                    n_intervals=0
                ),
                
                # WebSocket fallback interval (disabled by default)
                dcc.Interval(
                    id='websocket-fallback-interval',
                    interval=1000,
                    n_intervals=0,
                    disabled=True
                ),
                
                # Stores for data
                dcc.Store(id='agent-data-store'),
                dcc.Store(id='task-data-store'),
                dcc.Store(id='metrics-data-store'),
                dcc.Store(id='test-results-store'),
                
                # WebSocket stores
                dcc.Store(id='websocket-connection-store', data={'status': 'disconnected'}),
                dcc.Store(id='websocket-event-store'),
                dcc.Store(id='websocket-batch-store'),
                
                # WebSocket connection status indicator
                html.Div(
                    id='websocket-status',
                    className='ws-status ws-disconnected',
                    children=[
                        html.I(className="fas fa-circle me-2"),
                        html.Span("Disconnected", id='websocket-status-text')
                    ]
                ),
            ], className="main-content")
        ])
    ])


def create_agent_monitor_layout() -> html.Div:
    """Create the agent monitoring layout"""
    return html.Div([
        html.H2("Agent Monitor", className="text-white mb-4"),
        
        # Agent overview cards
        html.Div([
            dbc.Row([
                dbc.Col([
                    create_metric_card("Total Agents", "total-agents", "fas fa-users", "primary")
                ], width=3),
                dbc.Col([
                    create_metric_card("Active", "active-agents", "fas fa-play-circle", "success")
                ], width=3),
                dbc.Col([
                    create_metric_card("Idle", "idle-agents", "fas fa-pause-circle", "warning")
                ], width=3),
                dbc.Col([
                    create_metric_card("Errors", "error-agents", "fas fa-exclamation-triangle", "danger")
                ], width=3),
            ], className="mb-4")
        ]),
        
        # Agent grid
        html.Div([
            html.H4("Active Agents", className="text-white mb-3"),
            html.Div(id="agent-grid", className="row")
        ], className="mb-4"),
        
        # Communication graph
        html.Div([
            html.H4("Agent Communication Network", className="text-white mb-3"),
            html.Div(id="communication-graph", className="graph-container")
        ])
    ])


def create_swarm_control_layout() -> html.Div:
    """Create the swarm control layout"""
    return html.Div([
        html.H2("Swarm Control", className="text-white mb-4"),
        
        # Control panels
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Agent Creation"),
                    dbc.CardBody([
                        dbc.Form([
                            dbc.Label("Agent Type"),
                            dbc.Select(
                                id="agent-type-select",
                                options=[
                                    {"label": "Research Agent", "value": "research"},
                                    {"label": "Code Agent", "value": "code"},
                                    {"label": "Task Agent", "value": "task"},
                                    {"label": "Monitor Agent", "value": "monitor"},
                                    {"label": "Validator Agent", "value": "validator"},
                                ]
                            ),
                            dbc.Label("Agent Name", className="mt-3"),
                            dbc.Input(id="agent-name-input", placeholder="Enter agent name"),
                            dbc.Button("Create Agent", id="create-agent-btn", 
                                     color="primary", className="mt-3")
                        ])
                    ])
                ], className="mb-4")
            ], width=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Task Submission"),
                    dbc.CardBody([
                        dbc.Form([
                            dbc.Label("Task Type"),
                            dbc.Input(id="task-type-input", placeholder="Task type"),
                            dbc.Label("Description", className="mt-3"),
                            dbc.Textarea(id="task-description-input", 
                                       placeholder="Task description", rows=3),
                            dbc.Label("Priority", className="mt-3"),
                            dbc.Select(
                                id="task-priority-select",
                                options=[
                                    {"label": "High", "value": "1"},
                                    {"label": "Medium", "value": "5"},
                                    {"label": "Low", "value": "10"},
                                ]
                            ),
                            dbc.Button("Submit Task", id="submit-task-btn", 
                                     color="primary", className="mt-3")
                        ])
                    ])
                ], className="mb-4")
            ], width=6)
        ]),
        
        # Swarm configuration
        html.Div([
            html.H4("Swarm Configuration", className="text-white mb-3"),
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Load Balancing"),
                            dbc.Switch(id="load-balancing-switch", value=True)
                        ], width=3),
                        dbc.Col([
                            dbc.Label("Auto Scaling"),
                            dbc.Switch(id="auto-scaling-switch", value=False)
                        ], width=3),
                        dbc.Col([
                            dbc.Label("Max Retries"),
                            dbc.Input(id="max-retries-input", type="number", value=3)
                        ], width=3),
                        dbc.Col([
                            dbc.Label("Task Timeout (s)"),
                            dbc.Input(id="task-timeout-input", type="number", value=300)
                        ], width=3),
                    ])
                ])
            ])
        ])
    ])


def create_task_management_layout() -> html.Div:
    """Create the task management layout"""
    return html.Div([
        html.H2("Task Management", className="text-white mb-4"),
        
        # Task statistics
        html.Div([
            dbc.Row([
                dbc.Col([
                    create_metric_card("Total Tasks", "total-tasks", "fas fa-tasks", "info")
                ], width=3),
                dbc.Col([
                    create_metric_card("Completed", "completed-tasks", "fas fa-check-circle", "success")
                ], width=3),
                dbc.Col([
                    create_metric_card("In Progress", "progress-tasks", "fas fa-spinner fa-spin", "warning")
                ], width=3),
                dbc.Col([
                    create_metric_card("Failed", "failed-tasks", "fas fa-times-circle", "danger")
                ], width=3),
            ], className="mb-4")
        ]),
        
        # Task queue
        html.Div([
            html.H4("Task Queue", className="text-white mb-3"),
            html.Div(id="task-queue", className="card p-3")
        ], className="mb-4"),
        
        # Task timeline
        html.Div([
            html.H4("Task Timeline", className="text-white mb-3"),
            html.Div(id="task-timeline", className="graph-container")
        ])
    ])


def create_performance_layout() -> html.Div:
    """Create the performance monitoring layout"""
    return html.Div([
        html.H2("Performance Analytics", className="text-white mb-4"),
        
        # Performance metrics
        dbc.Row([
            dbc.Col([
                html.Div(id="cpu-chart", className="graph-container")
            ], width=6),
            dbc.Col([
                html.Div(id="memory-chart", className="graph-container")
            ], width=6),
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                html.Div(id="task-completion-chart", className="graph-container")
            ], width=6),
            dbc.Col([
                html.Div(id="agent-utilization-chart", className="graph-container")
            ], width=6),
        ], className="mb-4"),
        
        # Performance table
        html.Div([
            html.H4("Agent Performance Metrics", className="text-white mb-3"),
            html.Div(id="performance-table")
        ])
    ])


def create_metric_card(title: str, value_id: str, icon: str, color: str) -> dbc.Card:
    """Create a metric display card"""
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Div([
                    html.I(className=f"{icon} fa-2x"),
                ], className=f"text-{color} mb-3"),
                html.H3(id=value_id, children="0", className="mb-1"),
                html.P(title, className="text-muted mb-0")
            ])
        ])
    ], className="metric-card text-center")
