"""
Enhanced callbacks for SwarmBot UI with real data integration
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
from collections import deque

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

# Global data stores with proper initialization
performance_history = {
    "cpu": deque(maxlen=60),  # Keep last 60 data points
    "memory": deque(maxlen=60),
    "timestamps": deque(maxlen=60)
}

# Activity log to track real events
activity_log = deque(maxlen=100)  # Keep last 100 activities

# Communication history
communication_history = deque(maxlen=200)  # Keep last 200 messages


def log_activity(activity_type: str, description: str, agent_id: str = None):
    """Log an activity to the activity feed"""
    activity_log.append({
        "timestamp": datetime.now(),
        "type": activity_type,
        "description": description,
        "agent_id": agent_id
    })


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
            # Return empty data if no coordinator
            return {}, {}, {}

        try:
            # Get real swarm status
            status = app.swarm_coordinator.get_swarm_status()

            # Extract real data
            agents = status.get("agents", {})
            
            # Get real task queue data
            task_queue_items = []
            if hasattr(app.swarm_coordinator, 'task_queue'):
                # Convert queue to list for display
                temp_queue = list(app.swarm_coordinator.task_queue.queue)
                task_queue_items = [
                    {
                        "task_id": task.get("task_id", f"task_{i}"),
                        "type": task.get("type", "unknown"),
                        "priority": task.get("priority", "medium"),
                        "description": task.get("description", "No description"),
                        "created_at": task.get("created_at", datetime.now())
                    }
                    for i, task in enumerate(temp_queue)
                ]
            
            tasks = {
                "queued": task_queue_items,
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
        """Update sidebar statistics with real data"""
        if not agent_data or not task_data:
            return "0", "0", "0%", "0 MB"

        # Count active agents
        active_agents = sum(1 for agent in agent_data.values()
                          if agent.get("status") != "offline")

        # Count running tasks
        running_tasks = task_data.get("active", 0)

        # Get real CPU and memory usage
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
        """Update the communication network graph with real message data"""
        if not agent_data:
            return html.Div("No communication data", className="text-muted text-center p-4")

        # Convert agent data to list format
        agents = []
        for agent_id, agent_info in agent_data.items():
            agent_info['agent_id'] = agent_id
            agents.append(agent_info)

        # Get real communication history
        messages = list(communication_history)
        
        # If no real messages yet, check if agents have message logs
        if not messages and hasattr(app, 'swarm_coordinator'):
            # Try to get message history from swarm coordinator
            if hasattr(app.swarm_coordinator, 'message_history'):
                messages = list(app.swarm_coordinator.message_history[-50:])  # Last 50 messages

        return CommunicationGraph.create(agents, messages)

    @app.callback(
        Output('task-queue', 'children'),
        Input('task-data-store', 'data')
    )
    def update_task_queue(task_data):
        """Update the task queue display with real queue data"""
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
        """Update CPU usage chart with real data"""
        import psutil

        # Add new data point
        timestamp = datetime.now()
        cpu_value = psutil.cpu_percent(interval=0.1)

        performance_history["timestamps"].append(timestamp)
        performance_history["cpu"].append({"timestamp": timestamp, "value": cpu_value})

        return PerformanceChart.create_cpu_chart(list(performance_history["cpu"]))

    @app.callback(
        Output('memory-chart', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_memory_chart(n):
        """Update memory usage chart with real data"""
        import psutil

        # Add new data point
        timestamp = datetime.now()
        memory = psutil.virtual_memory()
        memory_mb = memory.used / 1024 / 1024

        performance_history["memory"].append({"timestamp": timestamp, "value": memory_mb})

        return PerformanceChart.create_memory_chart(list(performance_history["memory"]))

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
                "queued": len(task_data.get("queued", [])) if task_data else 0
            }

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
        """Handle agent creation with real agent manager"""
        if not n_clicks or not agent_type:
            raise PreventUpdate

        try:
            if hasattr(app, 'swarm_coordinator') and hasattr(app, 'agent_manager'):
                # Create real agent
                agent = app.agent_manager.create_agent(
                    template_name=agent_type,
                    name=agent_name or f"{agent_type}-{datetime.now().strftime('%H%M%S')}"
                )
                
                # Register with coordinator
                app.swarm_coordinator.register_agent(agent)
                
                # Log activity
                log_activity("agent_created", f"Created agent {agent.name}", agent.id)
                
                logger.info(f"Created agent: {agent.name} of type {agent_type}")
            else:
                logger.warning("Agent creation requested but no coordinator/manager available")

        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            log_activity("agent_error", f"Failed to create agent: {str(e)}")

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
        """Handle task submission to real swarm coordinator"""
        if not n_clicks or not task_type:
            raise PreventUpdate

        try:
            if hasattr(app, 'swarm_coordinator'):
                # Create real task
                task = {
                    "task_id": f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "type": task_type,
                    "description": description or "No description provided",
                    "priority": priority or "medium",
                    "created_at": datetime.now(),
                    "status": "queued"
                }
                
                # Submit to coordinator
                app.swarm_coordinator.submit_task(task)
                
                # Log activity
                log_activity("task_submitted", f"Submitted {task_type} task", None)
                
                logger.info(f"Submitted task: {task['task_id']} with priority {priority}")
            else:
                logger.warning("Task submission requested but no coordinator available")

        except Exception as e:
            logger.error(f"Failed to submit task: {e}")
            log_activity("task_error", f"Failed to submit task: {str(e)}")

        # Reset button clicks
        return 0

    @app.callback(
        Output('recent-activity', 'children'),
        Input('interval-component', 'n_intervals'),
        State('agent-data-store', 'data'),
        State('task-data-store', 'data')
    )
    def update_recent_activity(n, agent_data, task_data):
        """Update recent activity feed with real events"""
        activities = []
        
        # Get last 10 activities from the activity log
        recent_activities = list(activity_log)[-10:]
        
        for activity in reversed(recent_activities):
            time_str = activity["timestamp"].strftime("%H:%M:%S")
            activity_type = activity["type"]
            description = activity["description"]
            
            # Style based on activity type
            if "error" in activity_type:
                style = "text-danger"
            elif "created" in activity_type:
                style = "text-success"
            elif "completed" in activity_type:
                style = "text-info"
            else:
                style = "text-white"
            
            activities.append(
                html.Div([
                    html.Small(time_str, className="text-muted me-2"),
                    html.Small(description, className=style)
                ], className="mb-2")
            )
        
        # If no activities, show a message
        if not activities:
            activities.append(
                html.Div(
                    html.Small("No recent activity", className="text-muted"),
                    className="text-center p-3"
                )
            )
        
        return activities

    # Import necessary modules for the components
    from dash import html

    # Add hook for swarm coordinator events
    if hasattr(app, 'swarm_coordinator'):
        # Register event handlers
        def on_agent_status_change(agent_id, old_status, new_status):
            log_activity("agent_status", f"Agent {agent_id} changed from {old_status} to {new_status}", agent_id)
        
        def on_task_completed(task_id, agent_id, success):
            status = "completed" if success else "failed"
            log_activity(f"task_{status}", f"Task {task_id} {status} by agent {agent_id}", agent_id)
        
        def on_message_sent(from_agent, to_agent, message_type):
            communication_history.append({
                "from": from_agent,
                "to": to_agent,
                "type": message_type,
                "timestamp": datetime.now()
            })
        
        # Register handlers if coordinator supports events
        if hasattr(app.swarm_coordinator, 'on_agent_status_change'):
            app.swarm_coordinator.on_agent_status_change = on_agent_status_change
        if hasattr(app.swarm_coordinator, 'on_task_completed'):
            app.swarm_coordinator.on_task_completed = on_task_completed
        if hasattr(app.swarm_coordinator, 'on_message_sent'):
            app.swarm_coordinator.on_message_sent = on_message_sent

    return app
