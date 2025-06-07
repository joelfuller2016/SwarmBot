"""
Agent Manager for creating and managing different types of agents
"""

from typing import Dict, List, Optional, Type, Any
import logging
import json
from pathlib import Path

from .base_agent import BaseAgent, AgentRole, AgentCapability
from .specialized_agents import (
    ResearchAgent,
    CodeAgent,
    TaskAgent,
    MonitorAgent,
    ValidatorAgent
)

logger = logging.getLogger(__name__)


class AgentManager:
    """Manages the creation and lifecycle of agents in the swarm"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the agent manager
        
        Args:
            config_path: Path to agent configuration file
        """
        self.agent_registry: Dict[str, Type[BaseAgent]] = {
            "research": ResearchAgent,
            "code": CodeAgent,
            "task": TaskAgent,
            "monitor": MonitorAgent,
            "validator": ValidatorAgent
        }
        
        self.active_agents: Dict[str, BaseAgent] = {}
        self.agent_templates: Dict[str, Dict[str, Any]] = {}
        
        # Load configuration if provided
        if config_path:
            self.load_config(config_path)
        else:
            self._load_default_templates()
        
        logger.info("AgentManager initialized")

    def _load_default_templates(self) -> None:
        """Load default agent templates"""
        self.agent_templates = {
            "research_specialist": {
                "type": "research",
                "name": "Research Specialist",
                "role": AgentRole.SPECIALIST,
                "capabilities": [
                    {
                        "name": "web_research",
                        "description": "Conduct web research and analysis",
                        "required_tools": ["brave-search", "exa", "fetch"],
                        "confidence_level": 0.9
                    },
                    {
                        "name": "document_analysis",
                        "description": "Analyze documents and extract insights",
                        "required_tools": ["google_drive_search", "google_drive_fetch"],
                        "confidence_level": 0.85
                    }
                ]
            },
            "code_developer": {
                "type": "code",
                "name": "Code Developer",
                "role": AgentRole.WORKER,
                "capabilities": [
                    {
                        "name": "code_generation",
                        "description": "Generate code based on requirements",
                        "required_tools": ["filesystem", "mcp-server-git"],
                        "confidence_level": 0.9
                    },
                    {
                        "name": "code_review",
                        "description": "Review and improve existing code",
                        "required_tools": ["github", "code-reasoning"],
                        "confidence_level": 0.85
                    }
                ]
            },
            "task_coordinator": {
                "type": "task",
                "name": "Task Coordinator",
                "role": AgentRole.COORDINATOR,
                "capabilities": [
                    {
                        "name": "task_planning",
                        "description": "Plan and organize tasks",
                        "required_tools": ["taskmaster-ai"],
                        "confidence_level": 0.95
                    },
                    {
                        "name": "task_distribution",
                        "description": "Distribute tasks to appropriate agents",
                        "required_tools": [],
                        "confidence_level": 0.9
                    }
                ]
            },
            "system_monitor": {
                "type": "monitor",
                "name": "System Monitor",
                "role": AgentRole.MONITOR,
                "capabilities": [
                    {
                        "name": "performance_monitoring",
                        "description": "Monitor system and agent performance",
                        "required_tools": [],
                        "confidence_level": 0.95
                    },
                    {
                        "name": "error_detection",
                        "description": "Detect and report errors",
                        "required_tools": [],
                        "confidence_level": 0.9
                    }
                ]
            },
            "quality_validator": {
                "type": "validator",
                "name": "Quality Validator",
                "role": AgentRole.VALIDATOR,
                "capabilities": [
                    {
                        "name": "result_validation",
                        "description": "Validate task results and outputs",
                        "required_tools": [],
                        "confidence_level": 0.9
                    },
                    {
                        "name": "quality_assessment",
                        "description": "Assess quality of work products",
                        "required_tools": [],
                        "confidence_level": 0.85
                    }
                ]
            }
        }

    def load_config(self, config_path: str) -> None:
        """
        Load agent configuration from file
        
        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            # Load agent templates
            if "agent_templates" in config:
                self.agent_templates.update(config["agent_templates"])
            
            # Load custom agent types
            if "custom_agents" in config:
                # This would load custom agent classes
                pass
            
            logger.info(f"Loaded agent configuration from {config_path}")
            
        except Exception as e:
            logger.error(f"Failed to load agent configuration: {e}")
            self._load_default_templates()

    def register_agent_type(self, type_name: str, agent_class: Type[BaseAgent]) -> None:
        """
        Register a custom agent type
        
        Args:
            type_name: Name for the agent type
            agent_class: Agent class
        """
        self.agent_registry[type_name] = agent_class
        logger.info(f"Registered agent type: {type_name}")

    def create_agent(self, 
                    template_name: Optional[str] = None,
                    agent_type: Optional[str] = None,
                    **kwargs) -> BaseAgent:
        """
        Create a new agent instance
        
        Args:
            template_name: Name of template to use
            agent_type: Type of agent to create (if not using template)
            **kwargs: Additional agent parameters
            
        Returns:
            Created agent instance
        """
        # Use template if provided
        if template_name:
            if template_name not in self.agent_templates:
                raise ValueError(f"Unknown agent template: {template_name}")
            
            template = self.agent_templates[template_name]
            agent_type = template["type"]
            
            # Merge template with kwargs
            agent_params = template.copy()
            agent_params.update(kwargs)
        else:
            if not agent_type:
                raise ValueError("Either template_name or agent_type must be provided")
            agent_params = kwargs
        
        # Get agent class
        if agent_type not in self.agent_registry:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_class = self.agent_registry[agent_type]
        
        # Process capabilities
        if "capabilities" in agent_params:
            capabilities = []
            for cap_data in agent_params["capabilities"]:
                capabilities.append(AgentCapability(**cap_data))
            agent_params["capabilities"] = capabilities
        
        # Create agent
        agent = agent_class(**agent_params)
        
        # Track active agent
        self.active_agents[agent.agent_id] = agent
        
        logger.info(f"Created agent {agent.name} ({agent.agent_id}) of type {agent_type}")
        return agent

    def create_agent_team(self, team_config: Dict[str, Any]) -> List[BaseAgent]:
        """
        Create a team of agents based on configuration
        
        Args:
            team_config: Team configuration with agent specifications
            
        Returns:
            List of created agents
        """
        agents = []
        
        # Create coordinator if specified
        if "coordinator" in team_config:
            coordinator = self.create_agent(**team_config["coordinator"])
            agents.append(coordinator)
        
        # Create workers
        if "workers" in team_config:
            for worker_config in team_config["workers"]:
                worker = self.create_agent(**worker_config)
                agents.append(worker)
        
        # Create specialists
        if "specialists" in team_config:
            for specialist_config in team_config["specialists"]:
                specialist = self.create_agent(**specialist_config)
                agents.append(specialist)
        
        logger.info(f"Created agent team with {len(agents)} agents")
        return agents

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Get an active agent by ID
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent instance or None
        """
        return self.active_agents.get(agent_id)

    def list_active_agents(self) -> List[Dict[str, Any]]:
        """
        List all active agents
        
        Returns:
            List of agent information
        """
        return [agent.to_dict() for agent in self.active_agents.values()]

    def remove_agent(self, agent_id: str) -> bool:
        """
        Remove an agent from active tracking
        
        Args:
            agent_id: Agent ID to remove
            
        Returns:
            True if agent was removed
        """
        if agent_id in self.active_agents:
            agent = self.active_agents.pop(agent_id)
            logger.info(f"Removed agent {agent.name} ({agent_id})")
            return True
        return False

    def get_agents_by_capability(self, capability_name: str) -> List[BaseAgent]:
        """
        Find agents with a specific capability
        
        Args:
            capability_name: Name of capability
            
        Returns:
            List of agents with the capability
        """
        capable_agents = []
        
        for agent in self.active_agents.values():
            if any(cap.name == capability_name for cap in agent.capabilities):
                capable_agents.append(agent)
        
        return capable_agents

    def get_agents_by_role(self, role: AgentRole) -> List[BaseAgent]:
        """
        Find agents with a specific role
        
        Args:
            role: Agent role
            
        Returns:
            List of agents with the role
        """
        return [agent for agent in self.active_agents.values() if agent.role == role]

    def save_agent_templates(self, path: str) -> None:
        """
        Save current agent templates to file
        
        Args:
            path: Path to save templates
        """
        try:
            # Convert capabilities to serializable format
            templates_data = {}
            for name, template in self.agent_templates.items():
                template_copy = template.copy()
                if "capabilities" in template_copy:
                    template_copy["capabilities"] = [
                        {
                            "name": cap.name,
                            "description": cap.description,
                            "required_tools": cap.required_tools,
                            "confidence_level": cap.confidence_level
                        }
                        for cap in template_copy["capabilities"]
                        if isinstance(cap, AgentCapability)
                    ]
                templates_data[name] = template_copy
            
            with open(path, 'w') as f:
                json.dump({"agent_templates": templates_data}, f, indent=2)
            
            logger.info(f"Saved agent templates to {path}")
            
        except Exception as e:
            logger.error(f"Failed to save agent templates: {e}")

    def get_manager_stats(self) -> Dict[str, Any]:
        """Get statistics about the agent manager"""
        role_distribution = {}
        capability_distribution = {}
        
        for agent in self.active_agents.values():
            # Count roles
            role_name = agent.role.value
            role_distribution[role_name] = role_distribution.get(role_name, 0) + 1
            
            # Count capabilities
            for cap in agent.capabilities:
                capability_distribution[cap.name] = capability_distribution.get(cap.name, 0) + 1
        
        return {
            "total_active_agents": len(self.active_agents),
            "registered_types": list(self.agent_registry.keys()),
            "available_templates": list(self.agent_templates.keys()),
            "role_distribution": role_distribution,
            "capability_distribution": capability_distribution
        }
