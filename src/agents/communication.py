"""
Agent Communication System for SwarmBot
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, Callable, List
import asyncio
import logging
import json
import uuid

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages in the agent communication system"""
    TASK_ASSIGNMENT = "task_assignment"
    TASK_RESULT = "task_result"
    STATUS_UPDATE = "status_update"
    CAPABILITY_QUERY = "capability_query"
    CAPABILITY_RESPONSE = "capability_response"
    COORDINATION = "coordination"
    HEARTBEAT = "heartbeat"
    ERROR = "error"
    REQUEST = "request"
    RESPONSE = "response"


@dataclass
class Message:
    """Message structure for inter-agent communication"""
    message_id: str
    sender_id: str
    recipient_id: str
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: datetime
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    ttl: Optional[int] = None  # Time to live in seconds

    @classmethod
    def create(cls, 
               sender_id: str,
               recipient_id: str,
               message_type: MessageType,
               content: Dict[str, Any],
               correlation_id: Optional[str] = None,
               reply_to: Optional[str] = None,
               ttl: Optional[int] = None) -> 'Message':
        """Create a new message with auto-generated ID and timestamp"""
        return cls(
            message_id=str(uuid.uuid4()),
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=message_type,
            content=content,
            timestamp=datetime.now(),
            correlation_id=correlation_id,
            reply_to=reply_to,
            ttl=ttl
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "message_type": self.message_type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "reply_to": self.reply_to,
            "ttl": self.ttl
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary"""
        return cls(
            message_id=data["message_id"],
            sender_id=data["sender_id"],
            recipient_id=data["recipient_id"],
            message_type=MessageType(data["message_type"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            correlation_id=data.get("correlation_id"),
            reply_to=data.get("reply_to"),
            ttl=data.get("ttl")
        )


class MessageRouter:
    """Routes messages between agents"""

    def __init__(self):
        self.routes: Dict[str, Callable] = {}
        self.message_history: List[Message] = []
        self.pending_responses: Dict[str, asyncio.Future] = {}

    def register_handler(self, agent_id: str, handler: Callable) -> None:
        """Register a message handler for an agent"""
        self.routes[agent_id] = handler
        logger.debug(f"Registered handler for agent {agent_id}")

    def unregister_handler(self, agent_id: str) -> None:
        """Unregister a message handler"""
        if agent_id in self.routes:
            del self.routes[agent_id]
            logger.debug(f"Unregistered handler for agent {agent_id}")

    async def route_message(self, message: Message) -> Optional[Message]:
        """Route a message to its recipient"""
        # Store in history
        self.message_history.append(message)
        
        # Check if message has expired
        if message.ttl:
            age = (datetime.now() - message.timestamp).total_seconds()
            if age > message.ttl:
                logger.warning(f"Message {message.message_id} expired (TTL: {message.ttl}s)")
                return None
        
        # Route to recipient
        if message.recipient_id in self.routes:
            handler = self.routes[message.recipient_id]
            try:
                response = await handler(message.to_dict())
                
                # Handle response if correlation ID exists
                if message.correlation_id and response:
                    if message.correlation_id in self.pending_responses:
                        self.pending_responses[message.correlation_id].set_result(response)
                
                return response
            except Exception as e:
                logger.error(f"Error routing message to {message.recipient_id}: {e}")
                return None
        else:
            logger.warning(f"No handler found for recipient {message.recipient_id}")
            return None

    async def send_and_wait(self, message: Message, timeout: float = 30.0) -> Optional[Message]:
        """Send a message and wait for response"""
        # Create future for response
        correlation_id = message.correlation_id or str(uuid.uuid4())
        message.correlation_id = correlation_id
        
        future = asyncio.Future()
        self.pending_responses[correlation_id] = future
        
        try:
            # Send message
            await self.route_message(message)
            
            # Wait for response
            response = await asyncio.wait_for(future, timeout=timeout)
            return Message.from_dict(response) if response else None
            
        except asyncio.TimeoutError:
            logger.warning(f"Timeout waiting for response to message {message.message_id}")
            return None
        finally:
            # Clean up
            self.pending_responses.pop(correlation_id, None)


class BroadcastChannel:
    """Channel for broadcasting messages to multiple agents"""

    def __init__(self, channel_id: str):
        self.channel_id = channel_id
        self.subscribers: Dict[str, Callable] = {}

    def subscribe(self, agent_id: str, handler: Callable) -> None:
        """Subscribe an agent to the channel"""
        self.subscribers[agent_id] = handler
        logger.debug(f"Agent {agent_id} subscribed to channel {self.channel_id}")

    def unsubscribe(self, agent_id: str) -> None:
        """Unsubscribe an agent from the channel"""
        if agent_id in self.subscribers:
            del self.subscribers[agent_id]
            logger.debug(f"Agent {agent_id} unsubscribed from channel {self.channel_id}")

    async def broadcast(self, message: Message) -> Dict[str, Any]:
        """Broadcast a message to all subscribers"""
        results = {}
        
        # Send to all subscribers in parallel
        tasks = []
        for agent_id, handler in self.subscribers.items():
            # Skip sender
            if agent_id != message.sender_id:
                tasks.append(self._send_to_subscriber(agent_id, handler, message))
        
        # Wait for all to complete
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        for agent_id, response in zip(
            [aid for aid in self.subscribers if aid != message.sender_id], 
            responses
        ):
            if isinstance(response, Exception):
                results[agent_id] = {"error": str(response)}
            else:
                results[agent_id] = response
        
        return results

    async def _send_to_subscriber(self, agent_id: str, handler: Callable, message: Message) -> Any:
        """Send message to a single subscriber"""
        try:
            # Create copy with updated recipient
            broadcast_msg = Message(
                message_id=str(uuid.uuid4()),
                sender_id=message.sender_id,
                recipient_id=agent_id,
                message_type=message.message_type,
                content=message.content,
                timestamp=datetime.now(),
                correlation_id=message.correlation_id,
                reply_to=message.message_id,
                ttl=message.ttl
            )
            
            return await handler(broadcast_msg.to_dict())
        except Exception as e:
            logger.error(f"Error broadcasting to {agent_id}: {e}")
            raise


class AgentCommunication:
    """Main communication system for agent interactions"""

    def __init__(self):
        self.router = MessageRouter()
        self.channels: Dict[str, BroadcastChannel] = {}
        
        # Create default channels
        self.channels["coordination"] = BroadcastChannel("coordination")
        self.channels["status"] = BroadcastChannel("status")
        self.channels["emergency"] = BroadcastChannel("emergency")

    def register_agent(self, agent_id: str, handler: Callable) -> None:
        """Register an agent with the communication system"""
        self.router.register_handler(agent_id, handler)

    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the communication system"""
        self.router.unregister_handler(agent_id)
        
        # Unsubscribe from all channels
        for channel in self.channels.values():
            channel.unsubscribe(agent_id)

    def create_channel(self, channel_id: str) -> BroadcastChannel:
        """Create a new broadcast channel"""
        if channel_id not in self.channels:
            self.channels[channel_id] = BroadcastChannel(channel_id)
        return self.channels[channel_id]

    def get_channel(self, channel_id: str) -> Optional[BroadcastChannel]:
        """Get a broadcast channel"""
        return self.channels.get(channel_id)

    async def send_message(self, message: Message) -> Optional[Message]:
        """Send a point-to-point message"""
        return await self.router.route_message(message)

    async def send_request(self, 
                          sender_id: str,
                          recipient_id: str,
                          request_type: str,
                          content: Dict[str, Any],
                          timeout: float = 30.0) -> Optional[Message]:
        """Send a request and wait for response"""
        message = Message.create(
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=MessageType.REQUEST,
            content={
                "request_type": request_type,
                **content
            }
        )
        
        return await self.router.send_and_wait(message, timeout)

    async def broadcast_to_channel(self,
                                  channel_id: str,
                                  sender_id: str,
                                  message_type: MessageType,
                                  content: Dict[str, Any]) -> Dict[str, Any]:
        """Broadcast a message to a channel"""
        if channel_id not in self.channels:
            raise ValueError(f"Channel {channel_id} does not exist")
        
        message = Message.create(
            sender_id=sender_id,
            recipient_id=f"channel:{channel_id}",
            message_type=message_type,
            content=content
        )
        
        return await self.channels[channel_id].broadcast(message)

    def get_message_history(self, 
                           agent_id: Optional[str] = None,
                           message_type: Optional[MessageType] = None,
                           limit: int = 100) -> List[Message]:
        """Get message history with optional filters"""
        history = self.router.message_history
        
        # Apply filters
        if agent_id:
            history = [msg for msg in history 
                      if msg.sender_id == agent_id or msg.recipient_id == agent_id]
        
        if message_type:
            history = [msg for msg in history if msg.message_type == message_type]
        
        # Return limited results
        return history[-limit:]

    def get_communication_stats(self) -> Dict[str, Any]:
        """Get communication statistics"""
        total_messages = len(self.router.message_history)
        
        # Message type distribution
        type_distribution = {}
        for msg in self.router.message_history:
            msg_type = msg.message_type.value
            type_distribution[msg_type] = type_distribution.get(msg_type, 0) + 1
        
        # Agent activity
        agent_activity = {}
        for msg in self.router.message_history:
            # Sender activity
            if msg.sender_id not in agent_activity:
                agent_activity[msg.sender_id] = {"sent": 0, "received": 0}
            agent_activity[msg.sender_id]["sent"] += 1
            
            # Recipient activity
            if msg.recipient_id not in agent_activity:
                agent_activity[msg.recipient_id] = {"sent": 0, "received": 0}
            agent_activity[msg.recipient_id]["received"] += 1
        
        return {
            "total_messages": total_messages,
            "type_distribution": type_distribution,
            "agent_activity": agent_activity,
            "channels": list(self.channels.keys()),
            "active_agents": len(self.router.routes)
        }
