"""
SwarmBot UI Package
Modular UI system for SwarmBot with advanced configuration options
"""

from .base import SwarmBotUI, UIComponent
from .config_panel import ConfigurationPanel
from .chat_interface import ChatInterface
from .server_manager import ServerManagerPanel
from .tool_browser import ToolBrowser
from .theme_manager import ThemeManager, Theme
from .progress_indicator import ProgressIndicator
from .error_display import ErrorDisplay

__all__ = [
    'SwarmBotUI',
    'UIComponent',
    'ConfigurationPanel',
    'ChatInterface',
    'ServerManagerPanel',
    'ToolBrowser',
    'ThemeManager',
    'Theme',
    'ProgressIndicator',
    'ErrorDisplay'
]
