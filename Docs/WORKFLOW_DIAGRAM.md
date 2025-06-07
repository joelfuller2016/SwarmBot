# SwarmBot Workflow Diagram

## Complete System Architecture and Workflow

```mermaid
graph TB
    subgraph "Entry Layer"
        U[User] --> |Launches| SL[swarmbot.py<br/>Unified Launcher]
        SL --> |Mode Selection| MS{Mode?}
        MS --> |Standard| SM[Standard Mode]
        MS --> |Enhanced| EM[Enhanced Mode]
        MS --> |Auto| EM
        
        SM --> UM[unified_main.py<br/>Main Entry Point]
        EM --> UM
        
        U2[User] --> |Direct Launch| BL[Batch Launchers<br/>scripts/launchers/]
        BL --> SL
    end

    subgraph "Core Application Layer"
        UM --> C[Configuration<br/>src/config.py]
        C --> |Loads| ENV[.env File<br/>API Keys]
        C --> |Loads| SC[servers_config.json<br/>MCP Servers]
        C --> |Loads| TP[tool_patterns.json<br/>Tool Matching]
        
        UM --> SM2[Server Manager<br/>src/server.py]
        SM2 --> |Creates| SS[Server Instances]
        
        UM --> LC[LLM Client<br/>src/llm_client.py]
        LC --> |Connects| LLMP{LLM Provider}
        LLMP --> OAI[OpenAI API]
        LLMP --> ANT[Anthropic API]
        LLMP --> GRQ[Groq API]
        LLMP --> AZ[Azure API]
    end

    subgraph "Session Management"
        UM --> |Standard| CS[ChatSession<br/>src/chat_session.py]
        UM --> |Enhanced| ECS[EnhancedChatSession<br/>src/enhanced_chat_session.py]
        
        CS --> |Initialize| IS[Initialize Servers]
        CS --> |Load| LT[Load Tools]
        CS --> |Handle| MH[Message Handler]
        
        ECS --> |Inherits| CS
        ECS --> |Uses| TM[ToolMatcher<br/>src/tool_matcher.py]
        TM --> |Auto-detect| TD[Tool Detection]
        TM --> |Chain| TC[Tool Chaining]
    end

    subgraph "Tool Execution Layer"
        MH --> |Execute| TE[Tool Executor<br/>src/tool.py]
        TD --> TE
        TC --> TE
        
        TE --> |Calls| MCP[MCP Servers]
    end

    subgraph "MCP Server Layer"
        MCP --> GIT[mcp-server-git<br/>Git Operations]
        MCP --> GH[github<br/>GitHub API]
        MCP --> BS[brave-search<br/>Web Search]
        MCP --> MEM[memory<br/>Knowledge Graph]
        MCP --> PUP[puppeteer<br/>Browser Control]
        MCP --> SQL[mcp-server-sqlite<br/>Database Ops]
        MCP --> FS[filesystem<br/>File Operations]
        MCP --> TK[taskmaster-ai<br/>Task Management]
        MCP --> MORE[... 20+ more servers]
    end

    subgraph "Data Flow"
        USER[User Input] --> |Query| ECS
        ECS --> |Process| NLP[NL Processing]
        NLP --> |Identify Tools| TM
        TM --> |Select Tools| TE
        TE --> |Execute| MCP
        MCP --> |Results| RES[Tool Results]
        RES --> |Format| RESP[Response Generation]
        RESP --> |Reply| USER
    end

    subgraph "Support Systems"
        LOG[Logging<br/>src/logging_utils.py] --> |Monitors| CS
        LOG --> |Monitors| ECS
        LOG --> |Monitors| TE
        
        ERR[Error Handler] --> |Catches| CS
        ERR --> |Catches| ECS
        ERR --> |Catches| TE
        
        SESS[Session State] --> |Persists| CS
        SESS --> |Persists| ECS
    end

    subgraph "Testing & Development"
        TEST[tests/] --> |Unit Tests| UT[test_*.py]
        TEST --> |Integration| IT[run_all_tests.py]
        
        DEMO[scripts/demos/] --> |Examples| DA[demo_auto_tools.py]
        
        DOC[docs/] --> |Guides| DG[Documentation]
    end

    classDef entryPoint fill:#e1f5fe,stroke:#01579b,stroke-width:3px
    classDef launcher fill:#ffeb3b,stroke:#f57c00,stroke-width:3px
    classDef coreModule fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef external fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef data fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef session fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef tool fill:#e3f2fd,stroke:#0d47a1,stroke-width:2px
    classDef support fill:#f5f5f5,stroke:#616161,stroke-width:2px

    class SL launcher
    class UM,SM,EM entryPoint
    class C,SM2,LC,TE coreModule
    class OAI,ANT,GRQ,AZ,GIT,GH,BS,MEM,PUP,SQL,FS,TK,MORE external
    class ENV,SC,TP data
    class CS,ECS,TM session
    class TD,TC tool
    class LOG,ERR,SESS support
```

## Workflow Description

### 1. Entry Flow
- User launches via `swarmbot.py` (unified launcher) or batch files
- Selects mode: Standard or Enhanced
- Launcher starts `unified_main.py` with mode parameter

### 2. Initialization Flow
1. Configuration loads environment variables and config files
2. Server Manager creates MCP server instances
3. LLM Client connects to selected provider
4. Chat Session initializes based on mode

### 3. Standard Mode Flow
- User provides explicit tool commands
- ChatSession parses and executes
- Direct tool invocation
- Results returned to user

### 4. Enhanced Mode Flow
- Natural language input from user
- EnhancedChatSession processes with ToolMatcher
- Automatic tool detection and selection
- Tool chaining for complex tasks
- Natural language response generation

### 5. Tool Execution Flow
1. Tool selected (manually or automatically)
2. Parameters extracted/generated
3. MCP server called
4. Results processed
5. Response formatted

### 6. Error Handling Flow
- All operations wrapped in try-catch
- Graceful degradation on server failures
- User-friendly error messages
- Detailed logging for debugging

## Key Components

### Entry Points
- **swarmbot.py**: Main launcher with interactive mode selection
- **unified_main.py**: Combined entry point for both modes
- **Batch files**: Windows convenience launchers

### Core Modules
- **config.py**: Central configuration management
- **server.py**: MCP server connection handling
- **llm_client.py**: Multi-provider LLM interface
- **tool.py**: Tool abstraction and execution

### Session Handlers
- **chat_session.py**: Standard mode conversation handling
- **enhanced_chat_session.py**: Enhanced mode with auto-tools
- **tool_matcher.py**: Natural language to tool mapping

### Support Systems
- **logging_utils.py**: Filtered logging system
- Error handling throughout
- Session persistence capabilities

### MCP Servers (20+ integrated)
- Development: git, github, taskmaster-ai
- Search: brave-search, exa
- Browser: puppeteer, browsermcp
- System: filesystem, desktop-commander
- Data: sqlite, memory (knowledge graph)
- AI: sequential-thinking, code-reasoning
- And many more...
