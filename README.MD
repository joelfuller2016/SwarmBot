# SwarmBot - AI Assistant with MCP Tools

A modular, extensible AI assistant that integrates with Model Context Protocol (MCP) tools for enhanced capabilities.

## Project Status (June 7, 2025)

**Overall Completion: 71.4%** (25 of 35 tasks complete)

### Recent Achievements
- ✅ **WebSocket Implementation Complete** (June 7, 2025)
  - Real-time dashboard updates with < 50ms latency
  - 90% reduction in network traffic
  - Automatic reconnection and fallback mechanisms
  - All 42 WebSocket tests passing

### Component Status
- ✅ **Core Infrastructure**: 100% Complete
- ✅ **Agent System**: 100% Complete  
- ✅ **Dashboard UI**: 87% Complete (only documentation remaining)
- ✅ **Auto-Prompt System**: 100% Complete
- ✅ **Error Logging**: 100% Complete
- 🚧 **MCP Integration**: 60% Complete
- 📋 **Testing Framework**: Pending

## Quick Start

```bash
# Install requirements
pip install -r requirements.txt

# Add jsonschema (if not already in requirements.txt)
echo "jsonschema>=4.0.0" >> requirements.txt
pip install jsonschema

# Run in enhanced mode (default - automatic tool detection)
python swarmbot.py

# Run in standard mode (manual tool control)
python swarmbot.py standard

# Run with auto-prompt enabled
python swarmbot.py --auto-prompt

# Run with auto-prompt and custom iterations
python swarmbot.py --auto-prompt --auto-prompt-iterations 5

# Launch web dashboard UI
python swarmbot.py --ui

# Dashboard UI (June 7, 2025 Update)
# Status: ~87% Complete - Fully functional with real-time WebSocket updates
# Features: Real-time push notifications, < 50ms latency, auto-reconnection
# Access: http://localhost:8050
# Documentation: See Docs/UI_MANUAL_COMPLETE.md for comprehensive guide
# WebSocket Guide: See Docs/WEBSOCKET_DEPLOYMENT_GUIDE.md
# Validation: See Docs/UI_VALIDATION_REPORT_2025_06_07_FINAL.md

# Validate configuration
python swarmbot.py --validate

# List available tools
python swarmbot.py --list-tools
```

## Installation

### Requirements

Make sure you have Python 3.8+ installed, then install the dependencies:

```bash
# Install all requirements
pip install -r requirements.txt

# Note: If you get an import error for jsonschema, add it manually:
echo "jsonschema>=4.0.0" >> requirements.txt
pip install jsonschema
```

Required packages include:
- **Core**: python-dotenv, requests, mcp, uvicorn
- **UI**: dash, plotly, dash-bootstrap-components, psutil
- **WebSocket**: flask-socketio, python-socketio, eventlet
- **LLM Providers**: openai, anthropic, groq
- **Utilities**: colorama, asyncio, jsonschema

## All Entry Points and Functions

### 1. Command-Line Usage

```bash
# Basic launch (enhanced mode by default)
python swarmbot.py

# Standard mode
python swarmbot.py standard

# Enhanced mode (explicit)
python swarmbot.py enhanced

# Validate configuration only
python swarmbot.py --validate

# List all available tools
python swarmbot.py --list-tools

# Clean log files
python swarmbot.py --clean-logs

# Debug mode
python swarmbot.py --debug

# Skip validation
python swarmbot.py --no-validation

# Auto-prompt options
python swarmbot.py --auto-prompt                    # Enable auto-prompt
python swarmbot.py --no-auto-prompt                 # Disable auto-prompt
python swarmbot.py --auto-prompt-iterations 10     # Set max iterations

# Dashboard UI
python swarmbot.py --ui                             # Launch web dashboard
python scripts/launchers/dashboard.py               # Alternative dashboard launcher
python launch_dashboard.py                          # Direct dashboard launcher

# Combine options
python swarmbot.py standard --debug
python swarmbot.py enhanced --no-validation
python swarmbot.py --auto-prompt --auto-prompt-iterations 5

# Get help
python swarmbot.py -h
python swarmbot.py --help
```

### 2. Programmatic Usage

Use SwarmBot as a module in your own code:

```python
# Import the main app class
from src.core.app import SwarmBotApp

# Create instance
app = SwarmBotApp()

# Run with arguments
app.run(['enhanced'])  # Enhanced mode
app.run(['standard'])  # Standard mode
app.run(['--validate'])  # Validate only
app.run(['--list-tools'])  # List tools

# Or use specific methods
import asyncio

# Setup environment
app.setup_environment()

# Validate configuration
is_valid = app.validate_configuration()

# Clean logs
app.clean_logs()

# List tools (async)
asyncio.run(app.list_tools())

# Run chat session (async)
asyncio.run(app.run_chat_session('enhanced'))
```

### 3. Direct Module Access

For advanced users who want to use specific components:

```python
# Configuration management
from src.config import Configuration
config = Configuration()

# Chat sessions
from src.chat_session import ChatSession
from src.enhanced_chat_session import EnhancedChatSession

# LLM client
from src.llm_client import LLMClient

# Server management
from src.server import Server

# Agent system
from src.agents.base_agent import BaseAgent
from src.agents.specialized_agents import ResearchAgent, CodeAgent
from src.agents.swarm_coordinator import SwarmCoordinator
```

### 4. Interactive Python Usage

```python
# Start Python interpreter
>>> from src.core.app import SwarmBotApp
>>> app = SwarmBotApp()
>>> 
>>> # Check configuration
>>> app.validate_configuration()
>>> 
>>> # Parse arguments
>>> args = app.parse_arguments(['enhanced', '--debug'])
>>> print(args.mode)  # 'enhanced'
>>> print(args.debug)  # True
```

### 5. Utility Scripts

```bash
# Fix Unicode issues in all Python files
python scripts/fix_unicode.py

# Test the structure
python test_structure.py

# Run all tests
python tests/run_all_tests.py

# Test setup
python tests/test_setup.py
```

## API Reference

The `SwarmBotApp` class exposes these methods:

| Method | Description | Type |
|--------|-------------|------|
| `__init__()` | Initialize the app | Sync |
| `setup_environment()` | Configure environment variables and encoding | Sync |
| `parse_arguments(args)` | Parse command-line arguments | Sync |
| `clean_logs()` | Remove old log files | Sync |
| `validate_configuration()` | Check configuration validity | Sync |
| `list_tools()` | List all available MCP tools | Async |
| `run_chat_session(mode)` | Start chat session | Async |
| `run(args)` | Main entry point | Sync |

## Project Structure

```
SwarmBot/
├── swarmbot.py              # Single entry point (19 lines)
├── src/
│   ├── core/
│   │   ├── app.py          # Main application logic
│   │   └── __init__.py     # Core module exports
│   ├── agents/             # Multi-agent system components
│   ├── ui/                 # User interface components
│   ├── config.py           # Configuration management
│   ├── server.py           # MCP server management
│   ├── chat_session.py     # Standard chat mode
│   ├── enhanced_chat_session.py  # Enhanced chat mode
│   └── llm_client.py       # LLM provider interface
├── config/
│   ├── servers_config.json # MCP server configurations
│   └── tool_patterns.json  # Tool detection patterns
├── tests/                  # Test suite
├── scripts/
│   ├── deprecated/         # Old entry points (archived)
│   └── fix_unicode.py      # Unicode fixing utility
└── .env                    # API keys and environment variables
```

## Features

- **Modular Architecture**: Clean separation of concerns with single entry point
- **Multiple Modes**: 
  - Standard: Manual tool execution with full control
  - Enhanced: Automatic tool detection from natural language
- **Auto-Prompt System**: Automatically continues multi-step tasks without manual intervention
  - Smart goal detection for incomplete tasks
  - Configurable iteration limits for safety
  - Visual progress indicators
  - Command-line and configuration file support
- **Multi-Agent System**: Specialized agents for different tasks
- **MCP Integration**: Connect to various MCP servers and tools
- **Multiple LLM Support**: OpenAI, Anthropic, Groq
- **Real-time Dashboard**: Web-based monitoring interface with WebSocket support
  - **NEW**: Real-time push updates (< 50ms latency)
  - **NEW**: 90% reduction in network traffic
  - **NEW**: Automatic reconnection with fallback
  - **NEW**: Support for 500+ concurrent users

## Configuration

1. Create `.env` file with your API keys:
```env
GROQ_API_KEY=your_groq_key
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key

# Auto-prompt configuration (optional)
AUTO_PROMPT_ENABLED=false              # Enable auto-prompt (default: false)
AUTO_PROMPT_MAX_ITERATIONS=1           # Max iterations (default: 1)
AUTO_PROMPT_GOAL_DETECTION=true        # Enable goal detection (default: true)
AUTO_PROMPT_SAVE_STATE=true            # Save state between sessions (default: true)
```

2. Configure MCP servers in `config/servers_config.json`

3. Run validation to ensure everything is set up:
```bash
python swarmbot.py --validate
```

## Development

The codebase is designed to be modular and extensible:

- **Entry Point**: `swarmbot.py` - Minimal launcher that delegates to core
- **Core Logic**: `src/core/app.py` - Main application class
- **Modular Components**: Each feature in its own module
- **Clean Imports**: All functionality accessible through proper imports

## Troubleshooting

### Unicode/Emoji Issues on Windows
```bash
python scripts/fix_unicode.py
```

### Import Errors
If you get import errors for `jsonschema`:
```bash
pip install jsonschema>=4.0.0
```

### Log Files
For detailed debugging, check:
- `swarmbot.log` (standard mode)
- `swarmbot_enhanced.log` (enhanced mode)

### Validation Issues
Run validation to identify configuration problems:
```bash
python swarmbot.py --validate
```

## License

[Your License Here]
