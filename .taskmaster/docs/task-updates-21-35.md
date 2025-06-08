# Manual Task Updates for SwarmBot Real-Time Infrastructure

## Task 21: Core Event Infrastructure

### Update Title:
FROM: "Real-Time Dashboard Updates"
TO: "Core Event Infrastructure"

### Update Description:
FROM: "Implement real-time updates for the dashboard to reflect current system state."
TO: "Implement a modular, reusable real-time event infrastructure that serves as the foundation for all real-time communication in SwarmBot, including dashboard updates, agent coordination, and external integrations."

### Update Details:
"Create a protocol-agnostic event system following these design principles:
1. **Protocol Agnostic**: Support WebSocket today, SSE/gRPC tomorrow
2. **Type Safety**: Strongly typed events with Pydantic models
3. **Minimal Core API**: publish(), subscribe(pattern, handler), unsubscribe()
4. **Progressive Enhancement**: Add features without breaking existing code
5. **Fail Gracefully**: Automatic fallback mechanisms

The infrastructure enables ANY SwarmBot component to publish/subscribe to events using patterns like 'agent.*' or '*.*.completed'. This foundation will be consumed by Task 35 (dashboard) and future features like agent collaboration, external monitoring, webhooks, and mobile apps.

Code location: src/core/events/
Performance target: 10,000+ events/second with zero memory leaks"

### Update Subtasks:

#### Subtask 1: Event Bus Core Implementation (3 days)
**Title**: "Event Bus Core Implementation"
**Description**: "Create the central publish/subscribe system with type-safe events"
**Details**: "Implement src/core/events/bus.py with:
- Event dataclass with type, data, timestamp, source
- EventBus class with publish(), subscribe(), unsubscribe()
- Pattern matching for subscriptions (e.g., 'agent.*')
- Thread-safe async operations with locks
- Memory-efficient subscription management
- Unit tests for pub/sub, pattern matching, concurrent access"

#### Subtask 2: Event Registry & Standards (2 days)
**Title**: "Event Registry & Standards"
**Description**: "Define standardized event types and validation schemas"
**Details**: "Create src/core/events/registry.py with:
- EventTypes enum following domain.entity.action pattern
- Pydantic models for each event type (AgentStatusEvent, TaskEvent, etc.)
- EVENT_SCHEMAS registry mapping types to models
- Event validation and serialization
- Documentation of all standard events
- Examples: agent.status.changed, task.execution.started"

#### Subtask 3: Transport Abstraction Layer (3 days)
**Title**: "Transport Abstraction Layer"
**Description**: "Create protocol-agnostic transport system for event delivery"
**Details**: "Implement src/core/events/transports/ with:
- Abstract Transport base class
- WebSocketTransport implementation
- Connection lifecycle management
- Heartbeat/keepalive mechanism
- Client registry with efficient lookups
- Broadcast and targeted send methods
- Future-ready for SSE, gRPC transports"

#### Subtask 4: Lifecycle & Resilience (2 days)
**Title**: "Lifecycle & Resilience"
**Description**: "Implement connection resilience and failure recovery"
**Details**: "Create src/core/events/resilience.py with:
- ConnectionManager with exponential backoff
- Circuit breaker pattern (5 failures = 60s timeout)
- Automatic reconnection (1s, 2s, 4s, 8s, max 30s)
- Connection storm prevention
- Graceful degradation strategies
- Comprehensive chaos testing"

## Task 35: Dashboard Event Integration

### Update Title:
FROM: "Implement WebSocket Support for Real-Time Dashboard Updates"
TO: "Dashboard Event Integration"

### Update Description:
FROM: "Implement WebSocket support to replace the current 1-second polling mechanism..."
TO: "Connect the SwarmBot dashboard to the core event infrastructure as its first consumer, enabling real-time updates with 90% less network traffic and 80% less CPU usage."

### Update Details:
"Create a thin adapter layer that connects the Dash dashboard to the event bus without coupling. The dashboard becomes just another event consumer, demonstrating the modularity of Task 21's infrastructure. Implementation focuses on:
- Clean separation between infrastructure and UI
- Reusable real-time components for any UI
- Performance optimization through batching
- Graceful fallback to polling if needed
- Zero changes to existing dashboard functionality during migration"

### Update Subtasks:

#### Subtask 1: Dashboard Event Adapter (2 days)
**Title**: "Dashboard Event Adapter"
**Description**: "Create adapter connecting dashboard to event infrastructure"
**Details**: "Implement src/ui/adapters/dashboard_events.py:
- DashboardEventAdapter class
- Subscribe to agent.*, task.*, system.resource.* events
- Event handlers that update dashboard state
- Clean separation from event bus internals
- No direct WebSocket code (uses Transport abstraction)
- Integration tests with mock event bus"

#### Subtask 2: Frontend Event Components (3 days)
**Title**: "Frontend Event Components"
**Description**: "Build reusable real-time UI components"
**Details**: "Create src/ui/components/realtime/ with:
- LiveStatus component with connection indicators
- EventStream component for activity feeds
- RealtimeChart for live metrics
- WebSocket store for Dash state management
- Automatic fallback to interval polling
- Visual connection status indicators"

#### Subtask 3: Performance Optimization (2 days)
**Title**: "Performance Optimization"
**Description**: "Optimize UI updates for smooth performance"
**Details**: "Implement src/ui/optimization/event_batching.py:
- EventBatcher with 100ms batching window
- Event coalescing (merge similar events)
- Request animation frame integration
- Virtual scrolling for event logs
- Throttling for high-frequency updates
- Performance benchmarks (1000 events/sec smooth UI)"

## Success Metrics

### Task 21:
- ✓ 10,000+ events/second throughput
- ✓ Zero memory leaks in 24-hour test
- ✓ Reconnection within 5 seconds
- ✓ 100% unit test coverage

### Task 35:
- ✓ Dashboard updates within 100ms
- ✓ 90% reduction in network traffic
- ✓ 80% reduction in server CPU
- ✓ Zero UI freezes at 1000 events/sec