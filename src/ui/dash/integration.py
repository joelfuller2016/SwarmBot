"""
Integration module for SwarmBot Dash UI with main system
"""

import asyncio
from typing import Optional
import logging
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.agents import SwarmCoordinator, AgentManager
from src.ui.dash import create_app, serve_app, register_callbacks
from src.ui.dash.websocket_events import (
    emit_agent_status_change, emit_agent_created, emit_agent_deleted,
    emit_task_queued, emit_task_assigned, emit_task_completed, emit_task_failed,
    emit_performance_metrics, emit_system_alert
)
from src.config import Configuration
from src.server import Server
from src.llm_client import LLMClient

logger = logging.getLogger(__name__)


class SwarmBotDashboard:
    """Main class for running SwarmBot with Dash UI"""
    
    def __init__(self, config: Optional[Configuration] = None):
        """
        Initialize SwarmBot Dashboard
        
        Args:
            config: Configuration instance
        """
        self.config = config or Configuration()
        self.swarm_coordinator = SwarmCoordinator("MainSwarm")
        self.agent_manager = AgentManager()
        self.app = None
        self.servers = {}
        self.llm_client = None
        
    def setup_mcp_servers(self):
        """Setup MCP server connections"""
        try:
            # Load server configuration
            server_config = self.config.load_config('config/servers_config.json')
            
            # Create server instances
            for name, srv_config in server_config.get('mcpServers', {}).items():
                self.servers[name] = Server(name, srv_config, self.config)
                logger.info(f"Configured MCP server: {name}")
                
        except Exception as e:
            logger.error(f"Failed to setup MCP servers: {e}")
    
    def setup_llm_client(self):
        """Setup LLM client"""
        try:
            self.llm_client = LLMClient(
                self.config.llm_provider,
                self.config.llm_api_key
            )
            logger.info(f"Configured LLM client: {self.config.llm_provider}")
        except Exception as e:
            logger.error(f"Failed to setup LLM client: {e}")
    
    def create_default_agents(self):
        """Create a default set of agents"""
        try:
            # Create default agent team
            team_config = {
                "coordinator": {
                    "template_name": "task_coordinator",
                    "name": "MainCoordinator"
                },
                "workers": [
                    {
                        "template_name": "research_specialist",
                        "name": "ResearchBot-1"
                    },
                    {
                        "template_name": "code_developer", 
                        "name": "CodeBot-1"
                    }
                ],
                "specialists": [
                    {
                        "template_name": "system_monitor",
                        "name": "MonitorBot-1"
                    },
                    {
                        "template_name": "quality_validator",
                        "name": "ValidatorBot-1"
                    }
                ]
            }
            
            # Create agents
            agents = self.agent_manager.create_agent_team(team_config)
            
            # Register with coordinator
            for agent in agents:
                self.swarm_coordinator.register_agent(agent)
            
            logger.info(f"Created {len(agents)} default agents")
            
        except Exception as e:
            logger.error(f"Failed to create default agents: {e}")
    
    async def start_swarm(self):
        """Start the swarm coordinator"""
        try:
            await self.swarm_coordinator.start()
            logger.info("Swarm coordinator started")
        except Exception as e:
            logger.error(f"Failed to start swarm: {e}")
    
    def setup_dashboard(self):
        """Setup the Dash dashboard with WebSocket integration"""
        try:
            # Create Dash app
            self.app = create_app(swarm_coordinator=self.swarm_coordinator)
            
            # Store references in app for callbacks
            self.app.swarm_coordinator = self.swarm_coordinator
            self.app.agent_manager = self.agent_manager
            
            # Connect WebSocket event handlers to SwarmCoordinator
            self.swarm_coordinator.set_event_callbacks(
                on_agent_status_change=emit_agent_status_change,
                on_agent_created=emit_agent_created,
                on_agent_deleted=emit_agent_deleted,
                on_task_queued=emit_task_queued,
                on_task_assigned=emit_task_assigned,
                on_task_completed=emit_task_completed,
                on_task_failed=emit_task_failed,
                on_performance_update=emit_performance_metrics,
                on_system_alert=emit_system_alert
            )
            
            # Register callbacks
            self.app = register_callbacks(self.app)
            
            # Add custom layout
            from src.ui.dash.layouts import create_main_layout
            self.app.layout = create_main_layout()
            
            logger.info("Dashboard setup complete with WebSocket integration")
            
        except Exception as e:
            logger.error(f"Failed to setup dashboard: {e}")
    
    def run(self, host: str = "127.0.0.1", port: int = 8050, debug: bool = False):
        """
        Run the SwarmBot Dashboard
        
        Args:
            host: Host address
            port: Port number
            debug: Enable debug mode
        """
        # Setup components
        self.setup_mcp_servers()
        self.setup_llm_client()
        self.create_default_agents()
        
        # Start swarm in background
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(self.start_swarm())
        
        # Setup and run dashboard
        self.setup_dashboard()
        
        if self.app:
            logger.info(f"Starting SwarmBot Dashboard on http://{host}:{port}")
            
            # Run in separate thread to not block asyncio
            import threading
            dash_thread = threading.Thread(
                target=serve_app,
                args=(self.app, host, port, debug),
                daemon=True
            )
            dash_thread.start()
            
            # Keep asyncio loop running
            try:
                loop.run_forever()
            except KeyboardInterrupt:
                logger.info("Shutting down SwarmBot Dashboard...")
                loop.run_until_complete(self.shutdown())
        else:
            logger.error("Failed to create dashboard app")
    
    async def shutdown(self):
        """Shutdown the system gracefully"""
        logger.info("Shutting down swarm coordinator...")
        await self.swarm_coordinator.stop()
        
        logger.info("Closing MCP servers...")
        for server in self.servers.values():
            try:
                await server.stop()
            except:
                pass
        
        logger.info("Shutdown complete")


def main():
    """Main entry point for SwarmBot Dashboard"""
    import argparse
    from src.logging_utils import configure_logging
    
    # Configure logging
    configure_logging('swarmbot_dashboard.log')
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='SwarmBot Dashboard')
    parser.add_argument('--host', default='127.0.0.1', help='Host address')
    parser.add_argument('--port', type=int, default=8050, help='Port number')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()
    
    # Create and run dashboard
    dashboard = SwarmBotDashboard()
    dashboard.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
