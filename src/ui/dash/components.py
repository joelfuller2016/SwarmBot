"""
Reusable UI components for SwarmBot Dash interface
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any, Optional
from datetime import datetime
import networkx as nx


class AgentCard:
    """Component for displaying agent information"""
    
    @staticmethod
    def create(agent_data: Dict[str, Any]) -> dbc.Card:
        """Create an agent information card"""
        agent_id = agent_data.get("agent_id", "unknown")
        name = agent_data.get("name", "Unknown Agent")
        role = agent_data.get("role", "worker")
        status = agent_data.get("status", "offline")
        reliability = agent_data.get("reliability_score", 0) * 100
        load = agent_data.get("load_factor", 0) * 100
        
        # Status color mapping
        status_colors = {
            "idle": "success",
            "busy": "warning",
            "processing": "primary",
            "error": "danger",
            "offline": "secondary"
        }
        
        status_color = status_colors.get(status, "secondary")
        
        return dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.H5(name, className="mb-0"),
                    html.Small(f"ID: {agent_id[:8]}...", className="text-muted")
                ])
            ]),
            dbc.CardBody([
                html.Div([
                    html.Span("Role: ", className="text-muted"),
                    html.Span(role.capitalize(), className="text-white")
                ], className="mb-2"),
                
                html.Div([
                    html.Span("Status: ", className="text-muted"),
                    dbc.Badge(status.upper(), color=status_color, className="ms-2")
                ], className="mb-3"),
                
                html.Div([
                    html.Small("Reliability", className="text-muted"),
                    dbc.Progress(value=reliability, className="mb-2", style={"height": "10px"}),
                    
                    html.Small("Load", className="text-muted"),
                    dbc.Progress(value=load, className="mb-2", style={"height": "10px"})
                ]),
                
                html.Div([
                    dbc.ButtonGroup([
                        dbc.Button("Details", size="sm", color="primary", outline=True),
                        dbc.Button("Tasks", size="sm", color="primary", outline=True),
                        dbc.Button("Stop", size="sm", color="danger", outline=True)
                    ], className="w-100")
                ], className="mt-3")
            ])
        ], className=f"agent-card agent-status-{status} h-100")


class TaskQueue:
    """Component for displaying task queue"""
    
    @staticmethod
    def create(tasks: List[Dict[str, Any]]) -> html.Div:
        """Create a task queue display"""
        if not tasks:
            return html.Div([
                html.P("No tasks in queue", className="text-muted text-center p-4")
            ])
        
        task_items = []
        for task in tasks[:10]:  # Show max 10 tasks
            task_id = task.get("task_id", "unknown")
            task_type = task.get("task_type", "unknown")
            priority = task.get("priority", 5)
            status = task.get("status", "pending")
            
            priority_class = "high" if priority <= 3 else "medium" if priority <= 7 else "low"
            
            task_items.append(
                html.Div([
                    html.Div([
                        html.Div([
                            html.H6(f"Task {task_id}", className="mb-1"),
                            html.Small(task_type, className="text-muted")
                        ], className="flex-grow-1"),
                        html.Div([
                            dbc.Badge(status.upper(), color="primary" if status == "executing" else "secondary")
                        ])
                    ], className="d-flex justify-content-between align-items-center"),
                    html.Div([
                        html.Small(f"Priority: {priority}", className="text-muted me-3"),
                        html.Small(f"Assigned: {len(task.get('assigned_agents', []))} agents", className="text-muted")
                    ], className="mt-2")
                ], className=f"p-3 mb-2 card task-priority-{priority_class}")
            )
        
        return html.Div([
            html.Div(task_items),
            html.Div([
                html.Small(f"Showing {len(task_items)} of {len(tasks)} tasks", 
                          className="text-muted text-center d-block mt-3")
            ]) if len(tasks) > 10 else None
        ])


class SwarmMetrics:
    """Component for displaying swarm metrics"""
    
    @staticmethod
    def create(metrics: Dict[str, Any]) -> dbc.Card:
        """Create a swarm metrics display"""
        return dbc.Card([
            dbc.CardHeader("Swarm Performance"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H4(metrics.get("total_tasks", 0), className="mb-0"),
                            html.Small("Total Tasks", className="text-muted")
                        ], className="text-center")
                    ], width=3),
                    dbc.Col([
                        html.Div([
                            html.H4(metrics.get("completed_tasks", 0), className="mb-0 text-success"),
                            html.Small("Completed", className="text-muted")
                        ], className="text-center")
                    ], width=3),
                    dbc.Col([
                        html.Div([
                            html.H4(metrics.get("failed_tasks", 0), className="mb-0 text-danger"),
                            html.Small("Failed", className="text-muted")
                        ], className="text-center")
                    ], width=3),
                    dbc.Col([
                        html.Div([
                            html.H4(f"{metrics.get('average_completion_time', 0):.1f}s", className="mb-0"),
                            html.Small("Avg Time", className="text-muted")
                        ], className="text-center")
                    ], width=3),
                ])
            ])
        ])


class CommunicationGraph:
    """Component for visualizing agent communication"""
    
    @staticmethod
    def create(agents: List[Dict[str, Any]], messages: List[Dict[str, Any]]) -> dcc.Graph:
        """Create a communication network graph"""
        # Create network graph
        G = nx.Graph()
        
        # Add nodes (agents)
        for agent in agents:
            G.add_node(agent["agent_id"], 
                      name=agent["name"],
                      role=agent["role"],
                      status=agent["status"])
        
        # Add edges (communications)
        edge_counts = {}
        for msg in messages:
            sender = msg.get("sender_id")
            recipient = msg.get("recipient_id")
            if sender and recipient and sender in G.nodes and recipient in G.nodes:
                key = tuple(sorted([sender, recipient]))
                edge_counts[key] = edge_counts.get(key, 0) + 1
        
        for (node1, node2), count in edge_counts.items():
            G.add_edge(node1, node2, weight=count)
        
        # Generate layout
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # Create edge traces
        edge_traces = []
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            weight = edge[2].get('weight', 1)
            
            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=min(weight * 0.5, 5), color='#888'),
                hoverinfo='none'
            )
            edge_traces.append(edge_trace)
        
        # Create node trace
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        
        status_colors = {
            "idle": "#10b981",
            "busy": "#f59e0b", 
            "processing": "#8b5cf6",
            "error": "#ef4444",
            "offline": "#6b7280"
        }
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            node_data = G.nodes[node]
            node_text.append(f"{node_data['name']}<br>Role: {node_data['role']}<br>Status: {node_data['status']}")
            node_color.append(status_colors.get(node_data['status'], '#888'))
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=[G.nodes[node]['name'] for node in G.nodes()],
            textposition="top center",
            hoverinfo='text',
            hovertext=node_text,
            marker=dict(
                size=30,
                color=node_color,
                line=dict(width=2, color='white')
            )
        )
        
        # Create figure
        fig = go.Figure(data=edge_traces + [node_trace])
        
        fig.update_layout(
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            title="Agent Communication Network",
            title_font_color="white",
            paper_bgcolor="#161b22",
            plot_bgcolor="#161b22",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=400
        )
        
        return dcc.Graph(figure=fig, config={'displayModeBar': False})


class PerformanceChart:
    """Component for performance visualization"""
    
    @staticmethod
    def create_cpu_chart(data: List[Dict[str, Any]]) -> dcc.Graph:
        """Create CPU usage chart"""
        if not data:
            data = [{"timestamp": datetime.now(), "value": 0}]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=[d["timestamp"] for d in data],
            y=[d["value"] for d in data],
            mode='lines',
            name='CPU Usage',
            line=dict(color='#58a6ff', width=2),
            fill='tozeroy',
            fillcolor='rgba(88, 166, 255, 0.2)'
        ))
        
        fig.update_layout(
            title="CPU Usage (%)",
            title_font_color="white",
            paper_bgcolor="#161b22",
            plot_bgcolor="#161b22",
            xaxis=dict(
                showgrid=True,
                gridcolor='#30363d',
                color='#c9d1d9'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#30363d',
                color='#c9d1d9',
                range=[0, 100]
            ),
            margin=dict(l=40, r=40, t=40, b=40),
            height=300
        )
        
        return dcc.Graph(figure=fig, config={'displayModeBar': False})
    
    @staticmethod
    def create_memory_chart(data: List[Dict[str, Any]]) -> dcc.Graph:
        """Create memory usage chart"""
        if not data:
            data = [{"timestamp": datetime.now(), "value": 0}]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=[d["timestamp"] for d in data],
            y=[d["value"] for d in data],
            mode='lines',
            name='Memory Usage',
            line=dict(color='#f97316', width=2),
            fill='tozeroy',
            fillcolor='rgba(249, 115, 22, 0.2)'
        ))
        
        fig.update_layout(
            title="Memory Usage (MB)",
            title_font_color="white",
            paper_bgcolor="#161b22",
            plot_bgcolor="#161b22",
            xaxis=dict(
                showgrid=True,
                gridcolor='#30363d',
                color='#c9d1d9'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#30363d',
                color='#c9d1d9'
            ),
            margin=dict(l=40, r=40, t=40, b=40),
            height=300
        )
        
        return dcc.Graph(figure=fig, config={'displayModeBar': False})
    
    @staticmethod
    def create_task_completion_chart(data: Dict[str, Any]) -> dcc.Graph:
        """Create task completion chart"""
        labels = ['Completed', 'In Progress', 'Failed', 'Queued']
        values = [
            data.get('completed', 0),
            data.get('in_progress', 0),
            data.get('failed', 0),
            data.get('queued', 0)
        ]
        colors = ['#10b981', '#f59e0b', '#ef4444', '#6b7280']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker=dict(colors=colors),
            textfont=dict(color='white')
        )])
        
        fig.update_layout(
            title="Task Distribution",
            title_font_color="white",
            paper_bgcolor="#161b22",
            plot_bgcolor="#161b22",
            showlegend=True,
            legend=dict(font=dict(color='#c9d1d9')),
            margin=dict(l=20, r=20, t=40, b=20),
            height=300
        )
        
        return dcc.Graph(figure=fig, config={'displayModeBar': False})
    
    @staticmethod
    def create_agent_utilization_chart(agents: List[Dict[str, Any]]) -> dcc.Graph:
        """Create agent utilization chart"""
        if not agents:
            agents = [{"name": "No Agents", "load_factor": 0}]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=[agent["name"] for agent in agents],
            y=[agent["load_factor"] * 100 for agent in agents],
            marker_color='#8b5cf6'
        ))
        
        fig.update_layout(
            title="Agent Utilization (%)",
            title_font_color="white",
            paper_bgcolor="#161b22",
            plot_bgcolor="#161b22",
            xaxis=dict(
                showgrid=False,
                color='#c9d1d9'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#30363d',
                color='#c9d1d9',
                range=[0, 100]
            ),
            margin=dict(l=40, r=40, t=40, b=40),
            height=300
        )
        
        return dcc.Graph(figure=fig, config={'displayModeBar': False})
