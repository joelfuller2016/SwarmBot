# SwarmBot - AI Assistant with MCP Tools

A modular, extensible AI assistant that integrates with Model Context Protocol (MCP) tools for enhanced capabilities.

## Project Status (June 8, 2025)

**Overall Completion: 71.4%** (25 of 35 tasks complete)

### Recent Updates
- ✅ **Unified Launcher System** (June 8, 2025)
  - Single launch.py file with all functionality
  - Automatic dependency checking and installation
  - Cross-platform support (Windows, Linux, macOS)
  - Comprehensive diagnostics and error handling

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
# Clone the repository
git clone https://github.com/yourusername/SwarmBot.git
cd SwarmBot

# Launch SwarmBot (automatic dependency installation)
python launch.py

# Or use platform-specific launchers
./launch.bat    # Windows
./launch.sh     # Linux/macOS
```

The launcher will:
1. Check Python version (3.8+ required)
2. Install missing dependencies automatically
3. Create configuration files if needed
4. Run diagnostics
5. Present an interactive menu

## Installation

### Automatic Installation (Recommended)

Simply run the launcher and it will handle everything:

```bash
python launch.py
```

### Manual Installation

If you prefer to install dependencies manually:

```bash
# Install all requirements
pip install -r requirements.txt
```

### Requirements

- Python 3.8 or higher
- All dependencies listed in `requirements.txt` (automatically installed by launcher)

## Launch Options

### Interactive Menu (Recommended)

```bash
python launch.py
```

This presents a menu with all available options:
1. 🌐 Dashboard UI (Web Interface)
2. 🚀 Enhanced Chat (Auto-tools)
3. 💬 Standard Chat (Manual tools)
4. ✓ Validate Configuration
5. 🛠️ List Available Tools
6. 🔍 Run Full Diagnostics
7. 🧹 Clean Logs
8. ❌ Exit

### Direct Command-Line Usage

```bash
# Basic launch (enhanced mode by default)
python swarmbot.py

# Standard mode
python swarmbot.py standard

# Enhanced mode (explicit)
python swarmbot.py enhanced

# Dashboard UI
python swarmbot.py --ui

# Validate configuration
python swarmbot.py --validate

# List all available tools
python swarmbot.py --list-tools

# Clean log files
python swarmbot.py --clean-logs

# Debug mode
python swarmbot.py --debug

# Auto-prompt options
python swarmbot.py --auto-prompt                    # Enable auto-prompt
python swarmbot.py --auto-prompt-iterations 10     # Set max iterations

# Combine options
python swarmbot.py standard --debug --auto-prompt
```

## Configuration

1. The launcher will create a `.env` file automatically if it doesn't exist
2. Edit `.env` to add your API keys:

```env
# LLM Provider (groq, anthropic, openai)
LLM_PROVIDER=groq

# API Keys
GROQ_API_KEY=your_groq_key
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key

# Auto-prompt configuration (optional)
AUTO_PROMPT_ENABLED=true
AUTO_PROMPT_MAX_ITERATIONS=1
```

3. Configure MCP servers in `config/servers_config.json`

## Features

- **Unified Launcher**: Single entry point with automatic setup
- **Multiple Modes**: 
  - Standard: Manual tool execution with full control
  - Enhanced: Automatic tool detection from natural language
- **Auto-Prompt System**: Automatically continues multi-step tasks
- **Multi-Agent System**: Specialized agents for different tasks
- **MCP Integration**: Connect to various MCP servers and tools
- **Multiple LLM Support**: OpenAI, Anthropic, Groq
- **Real-time Dashboard**: Web-based monitoring interface
  - Real-time push updates (< 50ms latency)
  - WebSocket support with auto-reconnection
  - Support for 500+ concurrent users

## Project Structure

```
SwarmBot/
├── launch.py               # Universal launcher with auto-setup
├── launch.bat             # Windows launcher shortcut
├── launch.sh              # Unix/Linux/macOS launcher shortcut
├── swarmbot.py            # Core application entry point
├── swarmbot.ps1           # PowerShell launcher
├── swarmbot.sh            # Shell script launcher
├── requirements.txt       # All dependencies
├── .env                   # Configuration (created automatically)
├── src/                   # Source code
│   ├── core/              # Core application logic
│   ├── agents/            # Multi-agent system
│   ├── ui/                # Dashboard interface
│   └── ...                # Other modules
├── config/                # Configuration files
├── scripts/               # Utility scripts
├── tests/                 # Test suite
└── Docs/                  # Documentation
```

## Dashboard UI

The web dashboard provides real-time monitoring and control:

- **URL**: http://localhost:8050
- **Features**:
  - Real-time agent activity monitoring
  - Tool execution tracking
  - Chat history and logs
  - Performance metrics
  - WebSocket-based updates

Access via:
- Menu option 1 in `launch.py`
- `python swarmbot.py --ui`

## Troubleshooting

### Common Issues

1. **Python Version Error**
   - Solution: Install Python 3.8+ from https://python.org

2. **Import Errors**
   - Solution: Run `python launch.py` - it will install missing dependencies

3. **API Key Errors**
   - Solution: Edit `.env` and add valid API keys

4. **UI Not Loading**
   - Solution: Use menu option 6 (Run Full Diagnostics) to identify issues

### Logs

Check these log files for detailed information:
- `swarmbot.log` (standard mode)
- `swarmbot_enhanced.log` (enhanced mode)
- `logs/` directory for dated logs

### Getting Help

1. Run diagnostics: `python launch.py` → Option 6
2. Check validation: `python launch.py` → Option 4
3. View available tools: `python launch.py` → Option 5

## Development

### Adding New Features

The modular architecture makes it easy to extend:

1. Add new agents in `src/agents/`
2. Add new tools in `config/servers_config.json`
3. Extend UI in `src/ui/dash/`

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src
```

## Documentation

- **UI Manual**: `Docs/UI_MANUAL_COMPLETE.md`
- **WebSocket Guide**: `Docs/WEBSOCKET_DEPLOYMENT_GUIDE.md`
- **Validation Report**: `Docs/UI_VALIDATION_REPORT_2025_06_07_FINAL.md`

## License

[Your License Here]

---

**Note**: For the best experience, use `python launch.py` which provides automatic setup, dependency management, and an interactive menu for all SwarmBot features.
