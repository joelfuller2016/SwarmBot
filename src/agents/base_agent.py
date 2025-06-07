"""
Base Agent class for SwarmBot multi-agent system
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import asyncio
import logging
import uuid

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Enumeration of agent roles in the swarm"""
    COORDINATOR = "coordinator"
    WORKER = "worker"
    SPECIALIST = "specialist"
    MONITOR = "monitor"
    RESEARCHER = "researcher"
    EXECUTOR = "executor"
    VALIDATOR = "validator"


class AgentStatus(Enum):
    """Agent operational status"""
    IDLE = "idle"
    BUSY = "busy"
    PROCESSING = "processing"
    WAITING = "waiting"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class AgentCapability:
    """Definition of an agent capability"""
    name: str
    description: str
    required_tools: List[str]
    confidence_level: float = 1.0


class BaseAgent(ABC):
    """Abstract base class for all agents in the swarm"""

    def __init__(self, 
                 agent_id: Optional[str] = None,
                 name: str = "Agent",
                 role: AgentRole = AgentRole.WORKER,
                 capabilities: Optional[List[AgentCapability]] = None):
        """
        Initialize a base agent
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
            role: Role of the agent in the swarm
            capabilities: List of agent capabilities
        """
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name
        self.role = role
        self.status = AgentStatus.IDLE
        self.capabilities = capabilities or []
        
        # Agent state
        self.created_at = datetime.now()
        self.last_active = datetime.now()
        self.task_history: List[Dict[str, Any]] = []
        self.current_task: Optional[Dict[str, Any]] = None
        
        # Communication
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.response_handlers: Dict[str, Callable] = {}
        
        # Performance metrics
        self.metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_response_time": 0,
            "total_processing_time": 0,
            "error_count": 0
        }
        
        logger.info(f"Agent {self.name} ({self.agent_id}) initialized with role {self.role.value}")

    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task assigned to the agent
        
        Args:
            task: Task definition with parameters
            
        Returns:
            Task result
        """
        pass

    @abstractmethod
    async def handle_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle incoming messages from other agents
        
        Args:
            message: Message from another agent
            
        Returns:
            Optional response message
        """
        pass

    async def start(self) -> None:
        """Start the agent's main processing loop"""
        logger.info(f"Starting agent {self.name}")
        self.status = AgentStatus.IDLE
        
        # Start message processing loop
        asyncio.create_task(self._message_loop())
        
        # Start heartbeat
        asyncio.create_task(self._heartbeat_loop())

    async def stop(self) -> None:
        """Stop the agent gracefully"""
        logger.info(f"Stopping agent {self.name}")
        self.status = AgentStatus.OFFLINE
        
        # Clear message queue
        while not self.message_queue.empty():
            try:
                self.message_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

    async def assign_task(self, task: Dict[str, Any]) -> None:
        """
        Assign a task to the agent
        
        Args:
            task: Task to be assigned
        """
        if self.status != AgentStatus.IDLE:
            raise RuntimeError(f"Agent {self.name} is not available for tasks (status: {self.status.value})")
        
        self.current_task = task
        self.status = AgentStatus.PROCESSING
        self.last_active = datetime.now()
        
        try:
            start_time = datetime.now()
            result = await self.process_task(task)
            
            # Update metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_metrics(success=True, processing_time=processing_time)
            
            # Add to history
            self.task_history.append({
                "task": task,
                "result": result,
                "timestamp": datetime.now(),
                "processing_time": processing_time
            })
            
            self.current_task = None
            self.status = AgentStatus.IDLE
            
        except Exception as e:
            logger.error(f"Agent {self.name} failed to process task: {e}")
            self._update_metrics(success=False)
            self.status = AgentStatus.ERROR
            raise

    async def send_message(self, recipient_id: str, message: Dict[str, Any]) -> None:
        """
        Send a message to another agent
        
        Args:
            recipient_id: ID of the recipient agent
            message: Message to send
        """
        # This will be implemented by the swarm coordinator
        pass

    async def receive_message(self, message: Dict[str, Any]) -> None:
        """
        Receive a message from another agent
        
        Args:
            message: Incoming message
        """
        await self.message_queue.put(message)

    def can_handle_task(self, task_type: str, requirements: Optional[List[str]] = None) -> bool:
        """
        Check if the agent can handle a specific task type
        
        Args:
            task_type: Type of task
            requirements: Required tools or capabilities
            
        Returns:
            True if agent can handle the task
        """
        # Check if any capability matches the task type
        for capability in self.capabilities:
            if capability.name == task_type:
                # Check if agent has required tools
                if requirements:
                    return all(tool in capability.required_tools for tool in requirements)
                return True
        return False

    def get_load_factor(self) -> float:
        """
        Get current load factor (0.0 - 1.0)
        
        Returns:
            Current load factor
        """
        if self.status == AgentStatus.IDLE:
            return 0.0
        elif self.status in [AgentStatus.BUSY, AgentStatus.PROCESSING]:
            return 1.0
        else:
            return 0.5

    def get_reliability_score(self) -> float:
        """
        Calculate agent reliability score based on performance
        
        Returns:
            Reliability score (0.0 - 1.0)
        """
        total_tasks = self.metrics["tasks_completed"] + self.metrics["tasks_failed"]
        if total_tasks == 0:
            return 1.0  # No history, assume reliable
        
        success_rate = self.metrics["tasks_completed"] / total_tasks
        error_penalty = min(self.metrics["error_count"] * 0.1, 0.5)
        
        return max(0.0, success_rate - error_penalty)

    async def _message_loop(self) -> None:
        """Internal message processing loop"""
        while self.status != AgentStatus.OFFLINE:
            try:
                # Wait for message with timeout
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                
                # Process message
                response = await self.handle_message(message)
                
                # Send response if needed
                if response and "sender_id" in message:
                    await self.send_message(message["sender_id"], response)
                    
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in message loop for agent {self.name}: {e}")

    async def _heartbeat_loop(self) -> None:
        """Internal heartbeat loop for status updates"""
        while self.status != AgentStatus.OFFLINE:
            await asyncio.sleep(30)  # Heartbeat every 30 seconds
            self.last_active = datetime.now()

    def _update_metrics(self, success: bool, processing_time: float = 0) -> None:
        """Update agent performance metrics"""
        if success:
            self.metrics["tasks_completed"] += 1
            self.metrics["total_processing_time"] += processing_time
            
            # Update average response time
            total_tasks = self.metrics["tasks_completed"]
            self.metrics["average_response_time"] = (
                self.metrics["total_processing_time"] / total_tasks
            )
        else:
            self.metrics["tasks_failed"] += 1
            self.metrics["error_count"] += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role.value,
            "status": self.status.value,
            "capabilities": [
                {
                    "name": cap.name,
                    "description": cap.description,
                    "confidence": cap.confidence_level
                }
                for cap in self.capabilities
            ],
            "metrics": self.metrics,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "reliability_score": self.get_reliability_score(),
            "load_factor": self.get_load_factor()
        }
