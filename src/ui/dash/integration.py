import asyncio
from typing import Optional
import logging
from pathlib import Path
import sys
import threading
import json
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.agents import SwarmCoordinator, AgentManager
from src.ui.dash import create_app, serve_app
from src.ui.dash.websocket_events import (
    emit_agent_status_change, emit_agent_created, emit_agent_deleted,
    emit_task_queued, emit_task_assigned, emit_task_completed, emit_task_failed,
    emit_performance_metrics, emit_system_alert
)
from src.config import Configuration
from src.server import Server
from src.llm_client import LLMClient
from dash import html
from dash.dependencies import Input, Output

# --- Correct and specific imports for all callbacks ---
from src.ui.dash.layouts import create_main_layout
from src.ui.dash.pages.testing_dashboard import create_layout as create_testing_layout
from src.ui.dash.callbacks.testing_callbacks import register_testing_page_callbacks

# Import cost tracking modules
from src.database.cost_tracking import CostTrackingDB
from src.core.cost_tracker import CostTracker

logger = logging.getLogger(__name__)

# Try to import TestRunnerService with fallback
try:
    from src.core.test_runner_service import TestRunnerService
except ImportError:
    logger.warning("TestRunnerService not available - test running features will be disabled")
    TestRunnerService = None


class SwarmBotDashboard:
    """Main class for running SwarmBot with Dash UI"""
    
    def __init__(self, config: Optional[Configuration] = None):
        self.config = config or Configuration()
        self.swarm_coordinator = SwarmCoordinator("MainSwarm")
        self.agent_manager = AgentManager()
        self.app = None
        self.servers = {}
        self.llm_client = None
        # --- NEW: Instantiate the TestRunnerService ---
        project_root = Path(__file__).parent.parent.parent.parent
        if TestRunnerService:
            self.test_runner_service = TestRunnerService(project_root)
        else:
            self.test_runner_service = None
            logger.warning("TestRunnerService not available in SwarmBotDashboard")
        
        # Initialize cost tracking
        if self.config.config.get('TRACK_COSTS', True):
            try:
                self.cost_tracker = CostTracker(self.config)
                self.cost_db = CostTrackingDB(self.config.config.get('DATABASE_PATH', 'data/swarmbot_chats.db'))
                logger.info("Cost tracking initialized")
            except Exception as e:
                logger.error(f"Failed to initialize cost tracking: {e}")
                self.cost_tracker = None
                self.cost_db = None
        else:
            self.cost_tracker = None
            self.cost_db = None
        
    def setup_mcp_servers(self):
        # ... (method content is correct and remains unchanged)
        try:
            server_config = self.config.load_config('config/servers_config.json')
            # Handle both 'servers' and 'mcpServers' keys for backward compatibility
            servers_dict = server_config.get('servers', server_config.get('mcpServers', {}))
            for name, srv_config in servers_dict.items():
                self.servers[name] = Server(name, srv_config, self.config)
                logger.info(f"Configured MCP server: {name}")
        except Exception as e:
            logger.error(f"Failed to setup MCP servers: {e}")

    def setup_llm_client(self):
        # ... (method content is correct and remains unchanged)
        try:
            self.llm_client = LLMClient(self.config.llm_provider, self.config.llm_api_key)
            logger.info(f"Configured LLM client: {self.config.llm_provider}")
        except Exception as e:
            logger.error(f"Failed to setup LLM client: {e}")
            
    def create_default_agents(self):
        # ... (method content is correct and remains unchanged)
        try:
            team_config = {
                "coordinator": {"template_name": "task_coordinator", "name": "MainCoordinator"},
                "workers": [{"template_name": "research_specialist", "name": "ResearchBot-1"}, {"template_name": "code_developer", "name": "CodeBot-1"}],
                "specialists": [{"template_name": "system_monitor", "name": "MonitorBot-1"}, {"template_name": "quality_validator", "name": "ValidatorBot-1"}]
            }
            agents = self.agent_manager.create_agent_team(team_config)
            for agent in agents:
                self.swarm_coordinator.register_agent(agent)
            logger.info(f"Created {len(agents)} default agents")
        except Exception as e:
            logger.error(f"Failed to create default agents: {e}")
    
    async def start_swarm(self):
        # ... (method content is correct and remains unchanged)
        try:
            await self.swarm_coordinator.start()
            logger.info("Swarm coordinator started")
        except Exception as e:
            logger.error(f"Failed to start swarm: {e}")
    
    def setup_dashboard(self):
        """Setup the Dash dashboard with WebSocket and routing."""
        try:
            self.app = create_app(swarm_coordinator=self.swarm_coordinator)
            self.app.swarm_coordinator = self.swarm_coordinator
            self.app.agent_manager = self.agent_manager
            # --- NEW: Pass the test runner service to the app context ---
            self.app.test_runner_service = self.test_runner_service
            
            self.swarm_coordinator.set_event_callbacks(
                on_agent_status_change=emit_agent_status_change,
                on_system_alert=emit_system_alert
            )
            
            self.app.layout = create_main_layout()
            register_testing_page_callbacks(self.app)
            
            # Register cost tracking callbacks if enabled
            if self.config.config.get('TRACK_COSTS', True):
                from src.ui.dash.pages.cost_tracking import register_cost_dashboard_callbacks
                register_cost_dashboard_callbacks(self.app, self)

            @self.app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
            def display_page(pathname):
                if pathname == '/testing':
                    return create_testing_layout()
                elif pathname == '/costs':
                    from src.ui.dash.pages.cost_tracking import create_cost_dashboard_layout
                    return create_cost_dashboard_layout()
                else:
                    from src.ui.dash.layouts import create_agent_monitor_layout
                    return create_agent_monitor_layout() 

            logger.info("Dashboard setup complete")
            
        except Exception as e:
            logger.error(f"Failed to setup dashboard: {e}", exc_info=True)
    
    def run(self, host: str = "127.0.0.1", port: int = 8050, debug: bool = False):
        self.setup_mcp_servers()
        self.setup_llm_client()
        self.create_default_agents()
        
        # The test runner will now be triggered by a user action in the UI.
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(self.start_swarm())
        
        self.setup_dashboard()
        
        if self.app:
            logger.info(f"Starting SwarmBot Dashboard on http://{host}:{port}")
            dash_thread = threading.Thread(
                target=serve_app,
                args=(self.app, host, port, debug),
                daemon=True
            )
            dash_thread.start()
            try:
                loop.run_forever()
            except KeyboardInterrupt:
                logger.info("Shutting down SwarmBot Dashboard...")
                loop.run_until_complete(self.shutdown())
        else:
            logger.error("Failed to create dashboard app")

    def get_cost_tracking_data(self):
        """Get cost tracking data for dashboard"""
        if not self.cost_db:
            return self._empty_cost_data()
            
        try:
            # Get today's costs
            today = datetime.now().date()
            daily_costs = self.cost_db.get_daily_costs(1)
            today_data = next((d for d in daily_costs if d['date'] == today.isoformat()), None)
            
            # Get month's costs
            month_summary = self.cost_db.get_cost_summary(
                start_date=datetime.now().replace(day=1).isoformat(),
                end_date=datetime.now().isoformat()
            )
            
            # Get all-time summary
            all_time_summary = self.cost_db.get_cost_summary()
            
            # Get budget status
            budget_threshold = self.config.config.get('COST_ALERT_THRESHOLD', 10.0)
            budget_status = self.cost_db.check_budget_threshold(budget_threshold)
            
            # Get daily costs for chart
            daily_costs_30 = self.cost_db.get_daily_costs(30)
            
            # Get model usage stats
            model_usage = self.cost_db.get_model_usage_stats()
            
            # Get top conversations
            top_conversations = self.cost_db.get_conversation_rankings(10)
            
            return {
                'today': {
                    'total_cost': today_data['total_cost'] if today_data else 0,
                    'request_count': today_data['request_count'] if today_data else 0
                },
                'month': {
                    'total_cost': month_summary['total_cost'],
                    'request_count': month_summary['total_requests']
                },
                'all_time': {
                    'total_cost': all_time_summary['total_cost'],
                    'request_count': all_time_summary['total_requests'],
                    'avg_cost_per_request': all_time_summary['average_cost_per_request']
                },
                'budget': budget_status,
                'daily_costs': daily_costs_30,
                'model_usage': model_usage,
                'top_conversations': top_conversations
            }
            
        except Exception as e:
            logger.error(f"Error getting cost tracking data: {e}")
            return self._empty_cost_data()
    
    def _empty_cost_data(self):
        """Return empty cost data structure"""
        return {
            'today': {'total_cost': 0, 'request_count': 0},
            'month': {'total_cost': 0, 'request_count': 0},
            'all_time': {'total_cost': 0, 'request_count': 0, 'avg_cost_per_request': 0},
            'budget': {
                'current_month_cost': 0,
                'budget_threshold': 10.0,
                'exceeded': False,
                'percentage_used': 0,
                'remaining_budget': 10.0
            },
            'daily_costs': [],
            'model_usage': [],
            'top_conversations': []
        }
    
    def export_cost_data_csv(self, start_date: str, end_date: str):
        """Export cost data as CSV"""
        if not self.cost_db:
            return "session_id,timestamp,model,input_tokens,output_tokens,input_cost,output_cost,total_cost\n"
            
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
                self.cost_db.export_costs_csv(f.name, start_date, end_date)
                f.seek(0)
                return open(f.name, 'r').read()
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            return "Error exporting data"
    
    def export_cost_data_json(self, start_date: str, end_date: str):
        """Export cost data as JSON"""
        if not self.cost_db:
            return json.dumps({'error': 'Cost tracking not available'})
            
        try:
            return self.cost_db.export_costs_json(start_date, end_date)
        except Exception as e:
            logger.error(f"Error exporting JSON: {e}")
            return json.dumps({'error': str(e)})

    async def shutdown(self):
        logger.info("Shutting down swarm coordinator...")
        await self.swarm_coordinator.stop()

def main():
    import argparse
    from src.logging_utils import configure_logging
    configure_logging('swarmbot_dashboard.log')
    parser = argparse.ArgumentParser(description='SwarmBot Dashboard')
    # ... (parser arguments remain unchanged)
    args = parser.parse_args()
    dashboard = SwarmBotDashboard()
    dashboard.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()