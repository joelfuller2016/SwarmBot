"""
Dash callbacks for SwarmBot UI interactivity
"""

from dash import Input, Output, State, callback, ctx, ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any, Tuple
import asyncio
import logging

from .layouts import (
    create_agent_monitor_layout,
    create_swarm_control_layout,
    create_task_management_layout,
    create_performance_layout
)
from .components import (
    AgentCard,
    TaskQueue,
    SwarmMetrics,
    CommunicationGraph,
    PerformanceChart
)

logger = logging.getLogger(__name__)

# Global data stores (in production, use proper state management)
performance_history = {
    "cpu": [],
    "memory": [],
    "timestamps": []
}


def register_callbacks(app):
    """Register all callbacks for the Dash application"""
    
    @app.callback(
        Output('page-content', 'children'),
        Input('url', 'pathname')
    )
    def display_page(pathname):
        """Route to different pages based on URL"""
        if pathname == '/agents':
            return create_agent_monitor_layout()
        elif pathname == '/tasks':
            return create_task_management_layout()
        elif pathname == '/performance':
            return create_performance_layout()
        elif pathname == '/settings':
            return create_swarm_control_layout()
        else:
            # Default to agent monitor
            return create_agent_monitor_layout()
    
    @app.callback(
        [Output('agent-data-store', 'data'),
         Output('task-data-store', 'data'),
         Output('metrics-data-store', 'data')],
        Input('interval-component', 'n_intervals')
    )
    def update_data_stores(n):
        """Update data stores from SwarmCoordinator"""
        if not hasattr(app, 'swarm_coordinator') or not app.swarm_coordinator:
            # Return dummy data if no coordinator
            return {}, {}, {}
        
        try:
            # Get swarm status
            status = app.swarm_coordinator.get_swarm_status()
            
            # Extract data
            agents = status.get("agents", {})
            tasks = {
                "queued": [],
                "active": status.get("tasks", {}).get("active", 0),
                "completed": status.get("tasks", {}).get("completed", 0)
            }
            metrics = status.get("metrics", {})
            
            return agents, tasks, metrics
            
        except Exception as e:
            logger.error(f"Error updating data stores: {e}")
            return {}, {}, {}
    
    @app.callback(
        [Output('active-agents-count', 'children'),
         Output('running-tasks-count', 'children'),
         Output('cpu-usage', 'children'),
         Output('memory-usage', 'children')],
        Input('agent-data-store', 'data'),
        Input('task-data-store', 'data')
    )
    def update_sidebar_stats(agent_data, task_data):
        """Update sidebar statistics"""
        if not agent_data or not task_data:
            return "0", "0", "0%", "0 MB"
        
        # Count active agents
        active_agents = sum(1 for agent in agent_data.values() 
                          if agent.get("status") != "offline")
        
        # Count running tasks
        running_tasks = task_data.get("active", 0)
        
        # Simulate CPU and memory (in production, get from system)
        import psutil
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        memory_mb = memory.used / 1024 / 1024
        
        return (
            str(active_agents),
            str(running_tasks),
            f"{cpu_percent:.1f}%",
            f"{memory_mb:.0f} MB"
        )
    
    @app.callback(
        Output('agent-grid', 'children'),
        Input('agent-data-store', 'data')
    )
    def update_agent_grid(agent_data):
        """Update the agent display grid"""
        if not agent_data:
            return html.Div("No agents active", className="text-muted text-center p-4")
        
        agent_cards = []
        for agent_id, agent_info in agent_data.items():
            agent_info['agent_id'] = agent_id
            card = AgentCard.create(agent_info)
            agent_cards.append(
                dbc.Col([card], width=12, md=6, lg=4, xl=3, className="mb-4")
            )
        
        return agent_cards
    
    @app.callback(
        Output('communication-graph', 'children'),
        Input('agent-data-store', 'data'),
        State('metrics-data-store', 'data')
    )
    def update_communication_graph(agent_data, metrics_data):
        """Update the communication network graph"""
        if not agent_data:
            return html.Div("No communication data", className="text-muted text-center p-4")
        
        # Convert agent data to list format
        agents = []
        for agent_id, agent_info in agent_data.items():
            agent_info['agent_id'] = agent_id
            agents.append(agent_info)
        
        # Get communication history (simulated for now)
        messages = []
        
        return CommunicationGraph.create(agents, messages)
    
    @app.callback(
        Output('task-queue', 'children'),
        Input('task-data-store', 'data')
    )
    def update_task_queue(task_data):
        """Update the task queue display"""
        if not task_data or not task_data.get("queued"):
            return html.Div("No tasks in queue", className="text-muted text-center p-4")
        
        return TaskQueue.create(task_data["queued"])
    
    @app.callback(
        [Output('total-agents', 'children'),
         Output('active-agents', 'children'),
         Output('idle-agents', 'children'),
         Output('error-agents', 'children')],
        Input('agent-data-store', 'data')
    )
    def update_agent_metrics(agent_data):
        """Update agent metric cards"""
        if not agent_data:
            return "0", "0", "0", "0"
        
        total = len(agent_data)
        active = sum(1 for a in agent_data.values() if a.get("status") in ["busy", "processing"])
        idle = sum(1 for a in agent_data.values() if a.get("status") == "idle")
        error = sum(1 for a in agent_data.values() if a.get("status") == "error")
        
        return str(total), str(active), str(idle), str(error)
    
    @app.callback(
        [Output('total-tasks', 'children'),
         Output('completed-tasks', 'children'),
         Output('progress-tasks', 'children'),
         Output('failed-tasks', 'children')],
        Input('task-data-store', 'data'),
        Input('metrics-data-store', 'data')
    )
    def update_task_metrics(task_data, metrics_data):
        """Update task metric cards"""
        if not metrics_data:
            return "0", "0", "0", "0"
        
        total = metrics_data.get("total_tasks", 0)
        completed = metrics_data.get("completed_tasks", 0)
        failed = metrics_data.get("failed_tasks", 0)
        in_progress = task_data.get("active", 0) if task_data else 0
        
        return str(total), str(completed), str(in_progress), str(failed)
    
    @app.callback(
        Output('cpu-chart', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_cpu_chart(n):
        """Update CPU usage chart"""
        import psutil
        
        # Add new data point
        timestamp = datetime.now()
        cpu_value = psutil.cpu_percent(interval=0.1)
        
        performance_history["timestamps"].append(timestamp)
        performance_history["cpu"].append({"timestamp": timestamp, "value": cpu_value})
        
        # Keep only last 60 data points (1 minute at 1s intervals)
        if len(performance_history["cpu"]) > 60:
            performance_history["cpu"] = performance_history["cpu"][-60:]
            performance_history["timestamps"] = performance_history["timestamps"][-60:]
        
        return PerformanceChart.create_cpu_chart(performance_history["cpu"])
    
    @app.callback(
        Output('memory-chart', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_memory_chart(n):
        """Update memory usage chart"""
        import psutil
        
        # Add new data point
        timestamp = datetime.now()
        memory = psutil.virtual_memory()
        memory_mb = memory.used / 1024 / 1024
        
        if "memory" not in performance_history:
            performance_history["memory"] = []
        
        performance_history["memory"].append({"timestamp": timestamp, "value": memory_mb})
        
        # Keep only last 60 data points
        if len(performance_history["memory"]) > 60:
            performance_history["memory"] = performance_history["memory"][-60:]
        
        return PerformanceChart.create_memory_chart(performance_history["memory"])
    
    @app.callback(
        Output('task-completion-chart', 'children'),
        Input('task-data-store', 'data'),
        Input('metrics-data-store', 'data')
    )
    def update_task_completion_chart(task_data, metrics_data):
        """Update task completion pie chart"""
        if not metrics_data:
            data = {"completed": 0, "in_progress": 0, "failed": 0, "queued": 0}
        else:
            data = {
                "completed": metrics_data.get("completed_tasks", 0),
                "in_progress": task_data.get("active", 0) if task_data else 0,
                "failed": metrics_data.get("failed_tasks", 0),
                "queued": task_data.get("queued", []) if task_data else []
            }
            data["queued"] = len(data["queued"]) if isinstance(data["queued"], list) else 0
        
        return PerformanceChart.create_task_completion_chart(data)
    
    @app.callback(
        Output('agent-utilization-chart', 'children'),
        Input('agent-data-store', 'data')
    )
    def update_agent_utilization_chart(agent_data):
        """Update agent utilization bar chart"""
        if not agent_data:
            agents = []
        else:
            agents = []
            for agent_id, agent_info in agent_data.items():
                agents.append({
                    "name": agent_info.get("name", "Unknown"),
                    "load_factor": agent_info.get("load", 0) / 100.0  # Convert percentage
                })
        
        return PerformanceChart.create_agent_utilization_chart(agents)
    
    @app.callback(
        Output('create-agent-btn', 'n_clicks'),
        Input('create-agent-btn', 'n_clicks'),
        State('agent-type-select', 'value'),
        State('agent-name-input', 'value'),
        prevent_initial_call=True
    )
    def create_agent(n_clicks, agent_type, agent_name):
        """Handle agent creation"""
        if not n_clicks or not agent_type:
            raise PreventUpdate
        
        # In production, this would call the agent manager
        logger.info(f"Creating agent: {agent_name} of type {agent_type}")
        
        # Reset button clicks
        return 0
    
    @app.callback(
        Output('submit-task-btn', 'n_clicks'),
        Input('submit-task-btn', 'n_clicks'),
        State('task-type-input', 'value'),
        State('task-description-input', 'value'),
        State('task-priority-select', 'value'),
        prevent_initial_call=True
    )
    def submit_task(n_clicks, task_type, description, priority):
        """Handle task submission"""
        if not n_clicks or not task_type:
            raise PreventUpdate
        
        # In production, this would submit to the swarm coordinator
        logger.info(f"Submitting task: {task_type} with priority {priority}")
        
        # Reset button clicks
        return 0
    
    @app.callback(
        Output('recent-activity', 'children'),
        Input('interval-component', 'n_intervals'),
        State('agent-data-store', 'data'),
        State('task-data-store', 'data')
    )
    def update_recent_activity(n, agent_data, task_data):
        """Update recent activity feed"""
        # Simulate recent activity (in production, get from event log)
        activities = [
            html.Div([
                html.Small(datetime.now().strftime("%H:%M:%S"), className="text-muted me-2"),
                html.Small("Agent Alpha completed task", className="text-white")
            ], className="mb-2"),
            html.Div([
                html.Small((datetime.now() - timedelta(seconds=30)).strftime("%H:%M:%S"), 
                          className="text-muted me-2"),
                html.Small("New task submitted", className="text-white")
            ], className="mb-2"),
            html.Div([
                html.Small((datetime.now() - timedelta(seconds=60)).strftime("%H:%M:%S"), 
                          className="text-muted me-2"),
                html.Small("Agent Beta started", className="text-white")
            ], className="mb-2")
        ]
        
        return activities[:5]  # Show last 5 activities
    
    # Import necessary modules for the components
    from dash import html
    
    return app
