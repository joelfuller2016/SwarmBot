"""
Swarm Coordinator for managing multi-agent collaboration
"""

import asyncio
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime
import logging
import json

from .base_agent import BaseAgent, AgentRole, AgentStatus
from .communication import AgentCommunication, Message, MessageType

logger = logging.getLogger(__name__)


@dataclass
class SwarmTask:
    """Task to be executed by the swarm"""
    task_id: str
    task_type: str
    description: str
    requirements: List[str]
    priority: int = 5
    dependencies: List[str] = None
    assigned_agents: List[str] = None
    status: str = "pending"
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.dependencies is None:
            self.dependencies = []
        if self.assigned_agents is None:
            self.assigned_agents = []


class SwarmCoordinator:
    """Coordinates agent activities and task distribution in the swarm"""

    def __init__(self, name: str = "SwarmCoordinator"):
        self.name = name
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.active_tasks: Dict[str, SwarmTask] = {}
        self.completed_tasks: Dict[str, SwarmTask] = {}
        self.communication: AgentCommunication = AgentCommunication()
        
        # Swarm configuration
        self.config = {
            "max_retries": 3,
            "task_timeout": 300,  # 5 minutes
            "load_balancing": True,
            "auto_scaling": False,
            "min_agents": 1,
            "max_agents": 10
        }
        
        # Performance tracking
        self.metrics = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "average_completion_time": 0,
            "agent_utilization": {}
        }
        
        self._running = False
        self._task_processor = None
        
        logger.info(f"SwarmCoordinator {self.name} initialized")

    def register_agent(self, agent: BaseAgent) -> None:
        """
        Register an agent with the swarm
        
        Args:
            agent: Agent to register
        """
        if agent.agent_id in self.agents:
            logger.warning(f"Agent {agent.agent_id} already registered")
            return
        
        self.agents[agent.agent_id] = agent
        self.communication.register_agent(agent.agent_id, agent.receive_message)
        
        # Initialize agent metrics
        self.metrics["agent_utilization"][agent.agent_id] = {
            "tasks_assigned": 0,
            "tasks_completed": 0,
            "total_processing_time": 0,
            "current_load": 0.0
        }
        
        logger.info(f"Registered agent {agent.name} ({agent.agent_id}) with role {agent.role.value}")

    def unregister_agent(self, agent_id: str) -> None:
        """
        Unregister an agent from the swarm
        
        Args:
            agent_id: ID of agent to unregister
        """
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not found in swarm")
            return
        
        agent = self.agents.pop(agent_id)
        self.communication.unregister_agent(agent_id)
        
        logger.info(f"Unregistered agent {agent.name} ({agent_id})")

    async def submit_task(self, task: SwarmTask) -> str:
        """
        Submit a task to the swarm for execution
        
        Args:
            task: Task to submit
            
        Returns:
            Task ID
        """
        # Add to queue with priority (lower number = higher priority)
        await self.task_queue.put((task.priority, task))
        self.metrics["total_tasks"] += 1
        
        logger.info(f"Task {task.task_id} submitted to swarm")
        return task.task_id

    async def start(self) -> None:
        """Start the swarm coordinator"""
        if self._running:
            logger.warning("SwarmCoordinator already running")
            return
        
        self._running = True
        logger.info("Starting SwarmCoordinator")
        
        # Start all registered agents
        for agent in self.agents.values():
            await agent.start()
        
        # Start task processor
        self._task_processor = asyncio.create_task(self._process_tasks())
        
        # Start monitoring
        asyncio.create_task(self._monitor_swarm())

    async def stop(self) -> None:
        """Stop the swarm coordinator"""
        if not self._running:
            return
        
        self._running = False
        logger.info("Stopping SwarmCoordinator")
        
        # Cancel task processor
        if self._task_processor:
            self._task_processor.cancel()
            try:
                await self._task_processor
            except asyncio.CancelledError:
                pass
        
        # Stop all agents
        for agent in self.agents.values():
            await agent.stop()

    async def _process_tasks(self) -> None:
        """Main task processing loop"""
        while self._running:
            try:
                # Get next task with timeout
                priority, task = await asyncio.wait_for(
                    self.task_queue.get(), 
                    timeout=1.0
                )
                
                # Check dependencies
                if not await self._check_dependencies(task):
                    # Re-queue task if dependencies not met
                    await self.task_queue.put((priority, task))
                    await asyncio.sleep(1)
                    continue
                
                # Find suitable agent(s)
                agents = await self._find_suitable_agents(task)
                if not agents:
                    logger.warning(f"No suitable agents found for task {task.task_id}")
                    # Re-queue with lower priority
                    await self.task_queue.put((priority + 1, task))
                    await asyncio.sleep(5)
                    continue
                
                # Assign task to agent(s)
                task.assigned_agents = [agent.agent_id for agent in agents]
                task.status = "assigned"
                self.active_tasks[task.task_id] = task
                
                # Execute task
                asyncio.create_task(self._execute_task(task, agents))
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in task processor: {e}")

    async def _execute_task(self, task: SwarmTask, agents: List[BaseAgent]) -> None:
        """
        Execute a task with assigned agents
        
        Args:
            task: Task to execute
            agents: Assigned agents
        """
        start_time = datetime.now()
        task.status = "executing"
        
        try:
            # Single agent execution
            if len(agents) == 1:
                agent = agents[0]
                await agent.assign_task({
                    "task_id": task.task_id,
                    "type": task.task_type,
                    "description": task.description,
                    "requirements": task.requirements
                })
                
                # Update metrics
                self._update_agent_metrics(agent.agent_id, task, start_time)
                
            # Multi-agent collaboration
            else:
                # Coordinate agents for collaborative execution
                results = await self._coordinate_agents(task, agents)
                task.result = {"collaborative_results": results}
            
            # Mark task as completed
            task.status = "completed"
            task.completed_at = datetime.now()
            self.completed_tasks[task.task_id] = self.active_tasks.pop(task.task_id)
            
            # Update swarm metrics
            completion_time = (task.completed_at - start_time).total_seconds()
            self._update_swarm_metrics(success=True, completion_time=completion_time)
            
            logger.info(f"Task {task.task_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {e}")
            task.status = "failed"
            task.result = {"error": str(e)}
            
            # Handle retry logic
            if hasattr(task, "retry_count"):
                task.retry_count += 1
            else:
                task.retry_count = 1
            
            if task.retry_count < self.config["max_retries"]:
                # Re-queue for retry
                await self.task_queue.put((task.priority + 1, task))
            else:
                # Mark as permanently failed
                self.completed_tasks[task.task_id] = self.active_tasks.pop(task.task_id)
                self._update_swarm_metrics(success=False)

    async def _find_suitable_agents(self, task: SwarmTask) -> List[BaseAgent]:
        """
        Find agents suitable for executing a task
        
        Args:
            task: Task to be executed
            
        Returns:
            List of suitable agents
        """
        suitable_agents = []
        
        for agent in self.agents.values():
            # Check if agent is available
            if agent.status not in [AgentStatus.IDLE, AgentStatus.WAITING]:
                continue
            
            # Check if agent can handle the task
            if agent.can_handle_task(task.task_type, task.requirements):
                suitable_agents.append(agent)
        
        # Apply load balancing if enabled
        if self.config["load_balancing"] and suitable_agents:
            # Sort by load factor and reliability
            suitable_agents.sort(
                key=lambda a: (a.get_load_factor(), -a.get_reliability_score())
            )
        
        # Return best agent(s) based on task requirements
        if task.task_type.startswith("collaborative_"):
            # Return multiple agents for collaborative tasks
            return suitable_agents[:3]  # Max 3 agents
        else:
            # Return single best agent
            return suitable_agents[:1] if suitable_agents else []

    async def _coordinate_agents(self, task: SwarmTask, agents: List[BaseAgent]) -> List[Dict[str, Any]]:
        """
        Coordinate multiple agents for collaborative task execution
        
        Args:
            task: Task to execute
            agents: Agents to coordinate
            
        Returns:
            Results from all agents
        """
        results = []
        
        # Create sub-tasks for each agent
        sub_tasks = self._split_task(task, len(agents))
        
        # Execute sub-tasks in parallel
        tasks = []
        for agent, sub_task in zip(agents, sub_tasks):
            tasks.append(agent.assign_task(sub_task))
        
        # Wait for all to complete
        await asyncio.gather(*tasks)
        
        # Collect results
        for agent in agents:
            if agent.task_history:
                results.append(agent.task_history[-1]["result"])
        
        return results

    def _split_task(self, task: SwarmTask, num_agents: int) -> List[Dict[str, Any]]:
        """
        Split a task into sub-tasks for multiple agents
        
        Args:
            task: Task to split
            num_agents: Number of agents
            
        Returns:
            List of sub-tasks
        """
        # Basic task splitting - can be made more sophisticated
        base_sub_task = {
            "task_id": task.task_id,
            "parent_task": task.task_id,
            "type": task.task_type,
            "requirements": task.requirements
        }
        
        sub_tasks = []
        for i in range(num_agents):
            sub_task = base_sub_task.copy()
            sub_task["sub_task_id"] = f"{task.task_id}_sub_{i}"
            sub_task["description"] = f"{task.description} (Part {i+1}/{num_agents})"
            sub_tasks.append(sub_task)
        
        return sub_tasks

    async def _check_dependencies(self, task: SwarmTask) -> bool:
        """
        Check if task dependencies are satisfied
        
        Args:
            task: Task to check
            
        Returns:
            True if all dependencies are satisfied
        """
        if not task.dependencies:
            return True
        
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return False
        
        return True

    async def _monitor_swarm(self) -> None:
        """Monitor swarm health and performance"""
        while self._running:
            await asyncio.sleep(30)  # Check every 30 seconds
            
            # Update agent utilization metrics
            for agent_id, agent in self.agents.items():
                self.metrics["agent_utilization"][agent_id]["current_load"] = agent.get_load_factor()
            
            # Check for stuck tasks
            current_time = datetime.now()
            for task_id, task in self.active_tasks.items():
                if task.status == "executing":
                    elapsed_time = (current_time - task.created_at).total_seconds()
                    if elapsed_time > self.config["task_timeout"]:
                        logger.warning(f"Task {task_id} exceeded timeout")
                        # Could implement task cancellation here
            
            # Log swarm status
            active_agents = sum(1 for agent in self.agents.values() 
                              if agent.status != AgentStatus.OFFLINE)
            logger.info(f"Swarm status: {active_agents} active agents, "
                       f"{len(self.active_tasks)} active tasks, "
                       f"{len(self.completed_tasks)} completed tasks")

    def _update_agent_metrics(self, agent_id: str, task: SwarmTask, start_time: datetime) -> None:
        """Update metrics for a specific agent"""
        if agent_id not in self.metrics["agent_utilization"]:
            return
        
        metrics = self.metrics["agent_utilization"][agent_id]
        metrics["tasks_assigned"] += 1
        metrics["tasks_completed"] += 1
        
        processing_time = (datetime.now() - start_time).total_seconds()
        metrics["total_processing_time"] += processing_time

    def _update_swarm_metrics(self, success: bool, completion_time: float = 0) -> None:
        """Update overall swarm metrics"""
        if success:
            self.metrics["completed_tasks"] += 1
            
            # Update average completion time
            total_tasks = self.metrics["completed_tasks"]
            current_avg = self.metrics["average_completion_time"]
            self.metrics["average_completion_time"] = (
                (current_avg * (total_tasks - 1) + completion_time) / total_tasks
            )
        else:
            self.metrics["failed_tasks"] += 1

    def get_swarm_status(self) -> Dict[str, Any]:
        """Get current swarm status and metrics"""
        return {
            "name": self.name,
            "agents": {
                agent_id: {
                    "name": agent.name,
                    "role": agent.role.value,
                    "status": agent.status.value,
                    "reliability": agent.get_reliability_score(),
                    "load": agent.get_load_factor()
                }
                for agent_id, agent in self.agents.items()
            },
            "tasks": {
                "queued": self.task_queue.qsize(),
                "active": len(self.active_tasks),
                "completed": len(self.completed_tasks)
            },
            "metrics": self.metrics,
            "config": self.config
        }
