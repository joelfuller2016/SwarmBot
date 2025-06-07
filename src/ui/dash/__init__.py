"""
SwarmBot Dash UI Components
Real-time monitoring dashboard for multi-agent system
"""

from .app import create_app, serve_app
from .layouts import (
    create_main_layout,
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
from .callbacks import register_callbacks

__all__ = [
    'create_app',
    'serve_app',
    'create_main_layout',
    'create_agent_monitor_layout',
    'create_swarm_control_layout',
    'create_task_management_layout',
    'create_performance_layout',
    'AgentCard',
    'TaskQueue',
    'SwarmMetrics',
    'CommunicationGraph',
    'PerformanceChart',
    'register_callbacks'
]
