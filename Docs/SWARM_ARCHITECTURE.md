# SwarmBot Architecture Documentation

**Version:** 2.0  
**Updated:** June 7, 2025  
**Architecture Pattern:** Modular Monolith with Agent-Based Design

## System Overview

SwarmBot is a modular AI assistant platform that combines Model Context Protocol (MCP) servers with a multi-agent system. The architecture follows a clean, single-entry-point design with modular components for maximum extensibility and maintainability.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     SwarmBot Entry Point                      │
│                      (swarmbot.py)                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    SwarmBotApp Core                          │
│                   (src/core/app.py)                          │
├─────────────────────────────────────────────────────────────┤
│  • Environment Setup    • Argument Parsing                   │
│  • Configuration Validation • Mode Selection                 │
│  • Application Lifecycle Management                          │
└──────────┬────────────────────┬─────────────────┬──────────┘
           │                    │                  │
           ▼                    ▼                  ▼
┌──────────────────┐ ┌──────────────────┐ ┌─────────────────┐
│  Chat Sessions   │ │   Agent System   │ │  MCP Servers    │
├──────────────────┤ ├──────────────────┤ ├─────────────────┤
│ • Standard Mode  │ │ • BaseAgent      │ │ • 25 Servers    │
│ • Enhanced Mode  │ │ • 5 Specialized  │ │ • Tool Registry │
│ • Tool Matching  │ │ • Coordinator    │ │ • Async Comms   │
└──────────────────┘ └──────────────────┘ └─────────────────┘
```

## Core Components

### 1. Entry Point Layer

**File:** `swarmbot.py`
- Minimal 19-line entry point
- Delegates all logic to core application
- Handles system exit codes

### 2. Application Core

**Module:** `src/core/app.py`

**Class:** `SwarmBotApp`
- Central application controller
- Manages application lifecycle
- Coordinates all subsystems

**Key Methods:**
```python
- setup_environment()      # Environment configuration
- parse_arguments()        # CLI argument handling
- validate_configuration() # Config validation
- list_tools()            # Tool discovery
- run_chat_session()      # Main chat loop
- run()                   # Application entry
```

### 3. Configuration System

**Module:** `src/config.py`

**Features:**
- Environment variable management
- API key handling
- Server configuration loading
- LLM provider selection

**Supported Providers:**
- OpenAI
- Anthropic
- Groq
- Azure

### 4. Chat System

**Modules:**
- `src/chat_session.py` - Standard mode
- `src/enhanced_chat_session.py` - Enhanced mode

**Features:**
- Message handling
- Tool execution
- Response formatting
- Session management

### 5. Agent System

**Directory:** `src/agents/`

**Components:**
```
agents/
├── base_agent.py         # Abstract base class
├── specialized_agents.py # Concrete implementations
├── agent_manager.py      # Lifecycle management
├── communication.py      # Inter-agent messaging
└── swarm_coordinator.py  # Task orchestration
```

**Agent Types:**
1. **ResearchAgent** - Information gathering
2. **CodeAgent** - Code generation/analysis
3. **TaskAgent** - Task management
4. **MonitorAgent** - System monitoring
5. **ValidatorAgent** - Quality control

### 6. MCP Integration

**Module:** `src/server.py`

**Features:**
- Async server management
- Tool discovery
- Request/response handling
- Connection pooling

**Integrated Servers (25):**
```
1. neurolorap          14. everything
2. audio-interface     15. browsermcp
3. mcp-reasoner       16. mcp-server-sqlite
4. n8n-workflow       17. mcp-compass
5. github-project     18. server-win-cli
6. mcp-server-git     19. taskmanager
7. mcp-installer      20. mcp-npx-fetch
8. desktop-commander  21. ElevenLabs
9. github             22. claude-code
10. brave-search      23. ripgrep
11. memory            24. code-reasoning
12. puppeteer         25. taskmaster-ai
13. sequential-thinking
```

### 7. User Interface

**Directory:** `src/ui/`

**Components:**
- `chat_interface.py` - Terminal UI
- `config_panel.py` - Configuration UI
- `server_manager.py` - Server status UI
- `theme_manager.py` - UI theming
- `dash/` - Web dashboard

**Dashboard Features:**
- Real-time monitoring
- Agent status display
- Performance metrics
- System health

## Data Flow

### 1. Request Flow
```
User Input → CLI Parser → SwarmBotApp → Chat Session
    ↓                                          ↓
Response ← Response Formatter ← Agent/Tool ← Router
```

### 2. Agent Communication
```
SwarmCoordinator
    ├→ TaskQueue
    ├→ AgentManager
    └→ MessageBus
         ├→ Agent A
         ├→ Agent B
         └→ Agent C
```

### 3. Tool Execution
```
User Query → Enhanced Mode → Tool Matcher
    ↓                            ↓
Response ← Tool Result ← MCP Server ← Tool Call
```

## Design Patterns

### 1. Single Entry Point
- Simplifies usage
- Clear execution flow
- Easy debugging

### 2. Dependency Injection
- Configuration passed to components
- Testable design
- Loose coupling

### 3. Factory Pattern
- Agent creation
- Server instantiation
- Session creation

### 4. Strategy Pattern
- LLM provider selection
- Chat mode selection
- Tool execution strategies

### 5. Observer Pattern
- Agent event system
- Progress notifications
- Status updates

### 6. Command Pattern
- Task execution
- Tool invocation
- Agent commands

## Async Architecture

### Event Loop Management
```python
# Windows-specific handling
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(
        asyncio.WindowsProactorEventLoopPolicy()
    )
```

### Cleanup Strategy
- Graceful shutdown
- Task cancellation
- Resource cleanup
- Connection closing

## Security Considerations

### 1. API Key Management
- Environment variables
- .env file (gitignored)
- No hardcoded secrets

### 2. Input Validation
- Command sanitization
- Parameter validation
- Type checking

### 3. Error Handling
- Comprehensive try-catch
- Graceful degradation
- User-friendly errors

## Performance Optimization

### 1. Lazy Loading
- MCP servers on demand
- Agent creation when needed
- Module imports optimized

### 2. Resource Management
- Connection pooling
- Memory limits
- Timeout controls

### 3. Async Operations
- Non-blocking I/O
- Concurrent requests
- Efficient task scheduling

## Extensibility Points

### 1. Adding New Agents
```python
class CustomAgent(BaseAgent):
    def __init__(self, agent_id, config):
        super().__init__(agent_id, "custom", config)
    
    async def process_task(self, task):
        # Implementation
```

### 2. Adding MCP Servers
```json
{
  "mcpServers": {
    "new-server": {
      "command": "npx",
      "args": ["new-server-package"]
    }
  }
}
```

### 3. Custom Chat Modes
- Extend ChatSession class
- Override message handling
- Add to mode selection

## Deployment Architecture

### Local Deployment
```
User Machine
├── Python 3.8+
├── Node.js (for npm/npx)
├── Git (optional)
└── SwarmBot
    ├── Virtual Environment
    ├── MCP Servers
    └── Configuration
```

### Future Cloud Architecture
```
Load Balancer
    ├→ API Gateway
    ├→ Container Orchestrator
    │   ├→ SwarmBot Instance 1
    │   ├→ SwarmBot Instance 2
    │   └→ SwarmBot Instance N
    └→ Shared Services
        ├→ Redis (cache)
        ├→ PostgreSQL (state)
        └→ S3 (storage)
```

## Monitoring and Observability

### 1. Logging
- Structured logging
- Log levels (DEBUG, INFO, WARN, ERROR)
- Rotating log files

### 2. Metrics
- Performance counters
- Agent statistics
- Tool usage analytics

### 3. Health Checks
- Server connectivity
- API availability
- Resource usage

## Development Workflow

### 1. Local Development
```bash
# Setup
git clone <repo>
cd SwarmBot
pip install -r requirements.txt

# Development
python swarmbot.py --debug

# Testing
python test_structure.py
```

### 2. Adding Features
1. Create feature branch
2. Implement in appropriate module
3. Add tests
4. Update documentation
5. Submit PR

### 3. Code Standards
- PEP 8 compliance
- Type hints encouraged
- Docstrings required
- Async/await patterns

## Future Architecture Plans

### 1. Plugin System
- Dynamic agent loading
- Third-party tools
- Custom commands

### 2. Distributed Mode
- Multi-instance coordination
- Shared state management
- Load balancing

### 3. AI Enhancements
- Model fine-tuning
- Custom embeddings
- RAG implementation

## Conclusion

SwarmBot's architecture provides a solid foundation for an extensible AI assistant platform. The modular design, clean separation of concerns, and comprehensive integration capabilities make it suitable for both current use and future expansion. The single-entry-point design simplifies usage while the modular internals ensure maintainability and extensibility.
