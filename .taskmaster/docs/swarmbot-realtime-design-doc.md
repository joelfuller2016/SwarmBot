# SwarmBot Real-Time Infrastructure Design & Development Document

## Executive Summary

This document outlines the architectural design and implementation plan for SwarmBot's real-time event infrastructure (Tasks 21 & 35). The design prioritizes modularity, extensibility, and simplicity to enable rapid feature development while maintaining system reliability.

**Key Objectives:**
- Create a reusable event infrastructure that any SwarmBot component can leverage
- Enable real-time dashboard updates as the first consumer of this infrastructure
- Design for future extensibility without over-engineering
- Implement comprehensive testing to ensure reliability
- Maintain backward compatibility during migration

## Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [Architectural Design](#architectural-design)
3. [Implementation Plan](#implementation-plan)
4. [Component Specifications](#component-specifications)
5. [Testing Strategy](#testing-strategy)
6. [Future Extensibility](#future-extensibility)
7. [Timeline & Milestones](#timeline--milestones)
8. [Risk Management](#risk-management)

## Current State Analysis

### Project Status
- **Overall Completion**: 65.71% (23/35 tasks completed)
- **Dashboard Status**: Task 20 (Dash Web Interface) ✅ COMPLETE
- **Real-Time Updates**: Tasks 21 & 35 ❌ PENDING

### Current Architecture Limitations
1. **Polling-Based Updates**: Dashboard uses 1-second interval polling
2. **Resource Inefficiency**: ~80% unnecessary server load from constant polling
3. **Latency Issues**: Up to 1-second delay for status changes
4. **Limited Scalability**: Each client polls independently
5. **No Event System**: Components cannot communicate asynchronously

### Dependencies Analysis
- Task 21 depends on: Task 20 (✅ Complete)
- Task 35 depends on: Tasks 20 (✅) and 21 (❌)
- No blocking dependencies for starting Task 21

## Architectural Design

### Design Principles

1. **Protocol Agnostic**: Support multiple transport mechanisms
2. **Type Safety**: Strongly typed events prevent runtime errors
3. **Minimal Core API**: Simple interface that's easy to understand
4. **Progressive Enhancement**: Add features without breaking existing code
5. **Fail Gracefully**: Always have fallback mechanisms

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     SwarmBot Application                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Agents    │  │  Dashboard   │  │ External Systems │  │
│  └──────┬──────┘  └──────┬───────┘  └────────┬─────────┘  │
│         │                 │                    │            │
│         ▼                 ▼                    ▼            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    Event Bus Core                     │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  │  │
│  │  │   Publish   │  │  Subscribe   │  │  Registry  │  │  │
│  │  └─────────────┘  └──────────────┘  └────────────┘  │  │
│  └─────────────────────┬────────────────────────────────┘  │
│                        │                                    │
│  ┌─────────────────────▼────────────────────────────────┐  │
│  │              Transport Abstraction Layer              │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │  │
│  │  │WebSocket │  │   SSE    │  │  Future (gRPC)   │  │  │
│  │  └──────────┘  └──────────┘  └──────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Event Flow Design

```
Agent Status Change → Event Published → Event Bus → Subscribers Notified
                                           │
                                           ├─→ Dashboard (Updates UI)
                                           ├─→ Logger (Records Event)
                                           └─→ Monitor (Tracks Metrics)
```

## Implementation Plan

### Phase 1: Core Event Infrastructure (Task 21)

#### Subtask 1.1: Event Bus Core Implementation
**Duration**: 3 days  
**Location**: `src/core/events/`

```python
# src/core/events/bus.py
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
import asyncio
import re

@dataclass
class Event:
    type: str  # e.g., "agent.status.changed"
    data: Dict
    timestamp: float
    source: Optional[str] = None

class EventBus:
    """Central event publication and subscription system."""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Subscription]] = {}
        self._lock = asyncio.Lock()
    
    async def publish(self, event: Event) -> None:
        """Publish an event to all matching subscribers."""
        async with self._lock:
            for pattern, subscriptions in self._subscribers.items():
                if self._matches_pattern(pattern, event.type):
                    for subscription in subscriptions:
                        await subscription.handler(event)
    
    def subscribe(self, pattern: str, handler: Callable) -> str:
        """Subscribe to events matching the pattern."""
        subscription_id = self._generate_id()
        subscription = Subscription(subscription_id, pattern, handler)
        
        if pattern not in self._subscribers:
            self._subscribers[pattern] = []
        self._subscribers[pattern].append(subscription)
        
        return subscription_id
    
    def unsubscribe(self, subscription_id: str) -> None:
        """Remove a subscription."""
        for pattern, subscriptions in self._subscribers.items():
            self._subscribers[pattern] = [
                s for s in subscriptions if s.id != subscription_id
            ]
```

#### Subtask 1.2: Event Registry & Standards
**Duration**: 2 days  
**Location**: `src/core/events/registry.py`

```python
# src/core/events/registry.py
from enum import Enum
from typing import Type, Dict
from pydantic import BaseModel

class EventTypes(str, Enum):
    # Agent Events
    AGENT_CREATED = "agent.created"
    AGENT_STATUS_CHANGED = "agent.status.changed"
    AGENT_TASK_ASSIGNED = "agent.task.assigned"
    AGENT_TASK_COMPLETED = "agent.task.completed"
    
    # System Events
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"
    SYSTEM_RESOURCE_ALERT = "system.resource.alert"
    
    # Task Events
    TASK_CREATED = "task.created"
    TASK_QUEUED = "task.queued"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"

class AgentStatusEvent(BaseModel):
    agent_id: str
    previous_status: str
    new_status: str
    reason: Optional[str]

class TaskEvent(BaseModel):
    task_id: str
    agent_id: Optional[str]
    status: str
    metadata: Dict

# Registry mapping event types to their schemas
EVENT_SCHEMAS: Dict[str, Type[BaseModel]] = {
    EventTypes.AGENT_STATUS_CHANGED: AgentStatusEvent,
    EventTypes.TASK_COMPLETED: TaskEvent,
    # ... more mappings
}
```

#### Subtask 1.3: Transport Abstraction Layer
**Duration**: 3 days  
**Location**: `src/core/events/transports/`

```python
# src/core/events/transports/base.py
from abc import ABC, abstractmethod
from typing import Set, Dict

class Transport(ABC):
    """Abstract base class for event transports."""
    
    @abstractmethod
    async def connect(self, client_id: str, connection: Any) -> None:
        """Register a new client connection."""
        pass
    
    @abstractmethod
    async def disconnect(self, client_id: str) -> None:
        """Remove a client connection."""
        pass
    
    @abstractmethod
    async def send(self, client_id: str, event: Event) -> None:
        """Send an event to a specific client."""
        pass
    
    @abstractmethod
    async def broadcast(self, event: Event) -> None:
        """Send an event to all connected clients."""
        pass

# src/core/events/transports/websocket.py
class WebSocketTransport(Transport):
    """WebSocket implementation of event transport."""
    
    def __init__(self):
        self._connections: Dict[str, WebSocketConnection] = {}
        self._reconnect_config = ReconnectConfig(
            initial_delay=1.0,
            max_delay=30.0,
            factor=2.0
        )
    
    async def connect(self, client_id: str, ws: WebSocket) -> None:
        connection = WebSocketConnection(
            client_id=client_id,
            websocket=ws,
            heartbeat_interval=30.0
        )
        self._connections[client_id] = connection
        await connection.start_heartbeat()
```

#### Subtask 1.4: Lifecycle & Resilience
**Duration**: 2 days  
**Location**: `src/core/events/resilience.py`

```python
# src/core/events/resilience.py
class ConnectionManager:
    """Manages connection lifecycle with resilience features."""
    
    def __init__(self, transport: Transport):
        self._transport = transport
        self._reconnect_attempts: Dict[str, int] = {}
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60.0
        )
    
    async def handle_connection_failure(self, client_id: str) -> None:
        """Handle connection failure with exponential backoff."""
        attempts = self._reconnect_attempts.get(client_id, 0)
        delay = min(2 ** attempts, 30)  # Max 30 seconds
        
        await asyncio.sleep(delay)
        
        if await self._attempt_reconnect(client_id):
            self._reconnect_attempts[client_id] = 0
        else:
            self._reconnect_attempts[client_id] = attempts + 1
```

### Phase 2: Dashboard Integration (Task 35)

#### Subtask 2.1: Dashboard Event Adapter
**Duration**: 2 days  
**Location**: `src/ui/adapters/dashboard_events.py`

```python
# src/ui/adapters/dashboard_events.py
class DashboardEventAdapter:
    """Connects the dashboard to the event infrastructure."""
    
    def __init__(self, event_bus: EventBus, dash_app: Dash):
        self.event_bus = event_bus
        self.dash_app = dash_app
        self._setup_subscriptions()
    
    def _setup_subscriptions(self):
        """Subscribe to all dashboard-relevant events."""
        # Agent events
        self.event_bus.subscribe(
            "agent.*", 
            self._handle_agent_event
        )
        
        # Task events
        self.event_bus.subscribe(
            "task.*",
            self._handle_task_event
        )
        
        # System events
        self.event_bus.subscribe(
            "system.resource.*",
            self._handle_resource_event
        )
    
    async def _handle_agent_event(self, event: Event):
        """Process agent events and update dashboard state."""
        if event.type == EventTypes.AGENT_STATUS_CHANGED:
            await self._update_agent_status(event.data)
```

#### Subtask 2.2: Frontend Event Components
**Duration**: 3 days  
**Location**: `src/ui/components/realtime/`

```python
# src/ui/components/realtime/live_status.py
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

class LiveStatusComponent:
    """Reusable component for displaying live status updates."""
    
    def __init__(self, component_id: str):
        self.id = component_id
        self._event_buffer = EventBuffer(max_size=100)
    
    def layout(self) -> html.Div:
        return html.Div([
            html.Div(id=f"{self.id}-status", children="Connecting..."),
            dcc.Store(id=f"{self.id}-event-store"),
            dcc.Interval(
                id=f"{self.id}-fallback-interval",
                interval=5000,  # 5s fallback polling
                disabled=True  # Enabled only if WebSocket fails
            )
        ])
    
    def register_callbacks(self, app: Dash):
        @app.callback(
            Output(f"{self.id}-status", "children"),
            Input(f"{self.id}-event-store", "data"),
            State(f"{self.id}-status", "children")
        )
        def update_status(event_data, current_status):
            if event_data:
                return self._render_status(event_data)
            return current_status
```

#### Subtask 2.3: Performance Optimization
**Duration**: 2 days  
**Location**: `src/ui/optimization/`

```python
# src/ui/optimization/event_batching.py
class EventBatcher:
    """Batches rapid events for efficient UI updates."""
    
    def __init__(self, batch_interval: float = 0.1):
        self.batch_interval = batch_interval
        self._pending_events: List[Event] = []
        self._batch_task: Optional[asyncio.Task] = None
    
    async def add_event(self, event: Event):
        """Add an event to the batch."""
        self._pending_events.append(event)
        
        if not self._batch_task:
            self._batch_task = asyncio.create_task(
                self._process_batch()
            )
    
    async def _process_batch(self):
        """Process accumulated events."""
        await asyncio.sleep(self.batch_interval)
        
        # Coalesce similar events
        coalesced = self._coalesce_events(self._pending_events)
        
        # Send batched update
        await self._send_batch_update(coalesced)
        
        self._pending_events.clear()
        self._batch_task = None
```

## Component Specifications

### Event Bus API

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `publish` | `event: Event` | `None` | Publishes event to all matching subscribers |
| `subscribe` | `pattern: str, handler: Callable` | `str` | Returns subscription ID |
| `unsubscribe` | `subscription_id: str` | `None` | Removes subscription |

### Event Naming Convention

Format: `domain.entity.action`

Examples:
- `agent.status.changed`
- `task.execution.started`
- `system.resource.warning`

### Transport Interface

All transports must implement:
- Connection management
- Heartbeat/keepalive
- Reconnection logic
- Error handling
- Graceful shutdown

## Testing Strategy

### Unit Tests (Task 21)

```python
# tests/core/events/test_event_bus.py
import pytest
from src.core.events import EventBus, Event

class TestEventBus:
    @pytest.mark.asyncio
    async def test_publish_subscribe_basic(self):
        """Test basic pub/sub functionality."""
        bus = EventBus()
        received_events = []
        
        # Subscribe
        sub_id = bus.subscribe(
            "test.event",
            lambda e: received_events.append(e)
        )
        
        # Publish
        event = Event(type="test.event", data={"value": 42})
        await bus.publish(event)
        
        # Verify
        assert len(received_events) == 1
        assert received_events[0].data["value"] == 42
    
    @pytest.mark.asyncio
    async def test_pattern_matching(self):
        """Test wildcard pattern subscriptions."""
        bus = EventBus()
        agent_events = []
        
        # Subscribe to all agent events
        bus.subscribe("agent.*", lambda e: agent_events.append(e))
        
        # Publish various events
        await bus.publish(Event(type="agent.created", data={}))
        await bus.publish(Event(type="agent.status.changed", data={}))
        await bus.publish(Event(type="task.created", data={}))
        
        # Only agent events should be received
        assert len(agent_events) == 2
```

### Integration Tests (Task 35)

```python
# tests/integration/test_dashboard_realtime.py
class TestDashboardRealtime:
    async def test_agent_update_flow(self, dash_app, event_bus):
        """Test complete flow from agent event to UI update."""
        # Setup
        adapter = DashboardEventAdapter(event_bus, dash_app)
        
        # Simulate agent status change
        await event_bus.publish(Event(
            type="agent.status.changed",
            data={
                "agent_id": "agent-1",
                "new_status": "active"
            }
        ))
        
        # Verify dashboard updated
        await asyncio.sleep(0.1)  # Allow for async processing
        assert dash_app.get_agent_status("agent-1") == "active"
```

### Performance Tests

```python
# tests/performance/test_event_throughput.py
class TestEventPerformance:
    async def test_high_throughput(self, event_bus):
        """Test system handles 10k events/second."""
        events_received = 0
        
        def counter(event):
            nonlocal events_received
            events_received += 1
        
        event_bus.subscribe("perf.*", counter)
        
        # Publish 10k events
        start = time.time()
        for i in range(10000):
            await event_bus.publish(
                Event(type="perf.test", data={"i": i})
            )
        duration = time.time() - start
        
        assert events_received == 10000
        assert duration < 1.0  # Should handle 10k in under 1 second
```

### Chaos Tests

```python
# tests/chaos/test_resilience.py
class TestResilience:
    async def test_reconnection_storm(self, transport):
        """Test system handles many simultaneous reconnections."""
        # Simulate 100 clients disconnecting at once
        tasks = []
        for i in range(100):
            tasks.append(
                transport.disconnect(f"client-{i}")
            )
        await asyncio.gather(*tasks)
        
        # Verify system remains responsive
        response_time = await self.measure_response_time()
        assert response_time < 100  # milliseconds
```

## Future Extensibility

### 1. Agent Collaboration System
```python
# Future feature: Agents discover and collaborate
class AgentCollaborationExtension:
    def __init__(self, event_bus: EventBus):
        # Agents announce capabilities
        event_bus.subscribe(
            "agent.capability.announced",
            self.update_capability_registry
        )
        
        # Agents request collaboration
        event_bus.subscribe(
            "agent.collaboration.requested",
            self.match_collaborators
        )
```

### 2. External Monitoring Integration
```python
# Future feature: Prometheus metrics
class PrometheusExporter:
    def __init__(self, event_bus: EventBus):
        event_bus.subscribe("*", self.export_metric)
        
    def export_metric(self, event: Event):
        metric_name = event.type.replace(".", "_")
        prometheus_client.Counter(metric_name).inc()
```

### 3. Mobile Application Support
```python
# Future feature: React Native app
class MobileTransport(Transport):
    """Uses Firebase Cloud Messaging for mobile push."""
    async def send(self, client_id: str, event: Event):
        await fcm.send_to_device(
            client_id,
            self._event_to_notification(event)
        )
```

### 4. Webhook Forwarding
```python
# Future feature: Forward events to external webhooks
class WebhookForwarder:
    def __init__(self, event_bus: EventBus):
        self.webhooks = self.load_webhook_config()
        
        for pattern, webhook_url in self.webhooks.items():
            event_bus.subscribe(
                pattern,
                lambda e: self.forward_to_webhook(e, webhook_url)
            )
```

## Timeline & Milestones

### Week 1-2: Core Infrastructure (Task 21)
- **Days 1-3**: Event Bus Core ✓
- **Days 4-5**: Event Registry ✓
- **Days 6-8**: Transport Layer ✓
- **Days 9-10**: Resilience Features ✓
- **Milestone**: Basic pub/sub working with WebSocket transport

### Week 3: Dashboard Integration (Task 35)
- **Days 11-12**: Dashboard Adapter ✓
- **Days 13-15**: Frontend Components ✓
- **Days 16-17**: Performance Optimization ✓
- **Milestone**: Dashboard shows real-time updates

### Week 4: Testing & Documentation
- **Days 18-19**: Test Suite Completion ✓
- **Days 20-21**: Documentation & Deployment Guide ✓
- **Milestone**: Production-ready with full test coverage

### Deliverables Checklist

#### Task 21 Deliverables:
- [ ] Event Bus implementation with tests
- [ ] Event Registry with standard event types
- [ ] WebSocket Transport implementation
- [ ] Connection resilience mechanisms
- [ ] API documentation
- [ ] Performance benchmarks

#### Task 35 Deliverables:
- [ ] Dashboard event adapter
- [ ] Reusable real-time UI components
- [ ] Performance optimizations (batching, throttling)
- [ ] Integration tests
- [ ] Migration guide from polling
- [ ] User documentation updates

## Risk Management

### Technical Risks

1. **WebSocket Browser Compatibility**
   - *Mitigation*: Automatic fallback to SSE or long-polling
   - *Detection*: Feature detection in client code

2. **Event Storm Overload**
   - *Mitigation*: Rate limiting, event batching, circuit breakers
   - *Detection*: Performance monitoring, alert thresholds

3. **Memory Leaks in Subscriptions**
   - *Mitigation*: Weak references, automatic cleanup
   - *Detection*: Memory profiling in tests

### Implementation Risks

1. **Breaking Existing Dashboard**
   - *Mitigation*: Progressive enhancement, feature flags
   - *Strategy*: Both polling and events work during transition

2. **Scope Creep**
   - *Mitigation*: Strict adherence to defined subtasks
   - *Strategy*: Future features tracked separately

## Success Criteria

### Task 21 Success Metrics:
- Event bus handles 10,000+ events/second
- Zero memory leaks over 24-hour test
- Reconnection succeeds within 5 seconds
- 100% unit test coverage

### Task 35 Success Metrics:
- Dashboard updates within 100ms of event
- 90% reduction in network traffic vs polling
- 80% reduction in server CPU usage
- Zero UI freezes during high event rates

## Conclusion

This design provides a solid foundation for SwarmBot's real-time capabilities while maintaining simplicity and extensibility. The modular approach ensures that future features can easily integrate with the event infrastructure, and the comprehensive testing strategy ensures reliability in production.

The phased implementation allows for incremental delivery of value, with each subtask providing tangible benefits. By following this plan, SwarmBot will have a robust, scalable real-time system that enhances user experience and enables new collaborative features.