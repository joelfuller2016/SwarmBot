# SwarmBot Changelog

All notable changes to the SwarmBot project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2025-06-07 (Evening Update)

### Added
- **UI Launch Capability**: Dashboard now launches successfully
  - Created missing UI modules: `tool_browser.py`, `progress_indicator.py`, `error_display.py`
  - Added comprehensive UI documentation suite
  - Created test script `test_dashboard_launch.py` for validation
  - Dashboard accessible at http://localhost:8050

### Fixed
- **UI Import Errors**: Created all missing module files
- **Dash Export Error**: Added `serve_app` to dash package exports
- **Agent Type Error**: Fixed BaseAgent initialization with 'type' parameter
- **Dash Config Error**: Changed from `app.config.update()` to direct attributes
- **Deprecated API**: Updated `app.run_server()` to `app.run()`

### Changed
- Project completion increased from 69.7% to 72.7%
- Task #20 (Dash Web Interface) marked complete with all subtasks done
- Updated README with UI status information

### Documentation
- Created `UI_IMPLEMENTATION_PROGRESS_2025_06_07.md`
- Created `PROJECT_UPDATE_SUMMARY_2025_06_07.md`
- Updated `project_plan_updated_2025_06_07_evening.md`
- Added multiple UI fix guides for reference

## [2.1.0] - 2025-06-07

### Added
- **Auto-Prompt System**: Autonomous task continuation feature
  - Smart goal detection for incomplete tasks
  - Configurable iteration limits (default: 1, customizable)
  - Visual progress indicators `🔄 [AUTO-PROMPT 1/3]`
  - Command-line flags: `--auto-prompt`, `--no-auto-prompt`, `--auto-prompt-iterations N`
  - Environment variable configuration support
  - State persistence between sessions
  - Comprehensive test suite
- Auto-prompt documentation:
  - `AUTO_PROMPT_GUIDE.md` - Complete user guide
  - `AUTO_PROMPT_STATUS_REPORT.md` - Implementation status
  - `AUTO_PROMPT_IMPLEMENTATION_SUMMARY.md` - Technical details
- Integration tests for auto-prompt functionality

### Changed
- Enhanced `EnhancedChatSession` with auto-prompt capabilities
- Updated `src/core/app.py` with new command-line arguments
- Improved help display to show auto-prompt status
- Updated README with auto-prompt documentation

### Fixed
- Auto-prompt system now fully integrated (was previously disconnected)
- Goal detection logic properly implemented
- Iteration counter resets on new user input

## [2.0.0] - 2025-06-07

### Added
- Single entry point `swarmbot.py` (19 lines)
- Core application module `src/core/app.py`
- Comprehensive command-line interface
  - `--validate` option for configuration checking
  - `--list-tools` option to show all MCP tools
  - `--clean-logs` option for log cleanup
  - `--debug` option for verbose logging
  - `--no-validation` option to skip checks
- Configuration validation system in main app
- Asyncio warning suppression for Windows
- Complete API documentation in README
- jsonschema dependency for validation

### Changed
- **BREAKING**: Consolidated all entry points into single `swarmbot.py`
- Moved all old entry points to `scripts/deprecated/`
- Refactored entire codebase to modular architecture
- Updated all documentation files
- Replaced emoji characters with ASCII alternatives
- Improved error handling and logging

### Deprecated
- `main.py` - use `python swarmbot.py standard`
- `enhanced_main.py` - use `python swarmbot.py enhanced`
- `unified_main.py` - use `python swarmbot.py`
- `run_swarmbot.py` - use `python swarmbot.py`

### Fixed
- Unicode/emoji encoding issues on Windows
- Circular import problems
- Asyncio cleanup warnings
- Configuration validation gaps

### Security
- API keys properly managed via .env
- No hardcoded secrets in code
- Input validation implemented

## [1.5.0] - 2025-06-06

### Added
- Task 9: Configuration File Validation completed
- 25 MCP server integrations
- Multi-agent system with 5 specialized agents
- Real-time Dash dashboard
- SQLite persistent storage

### Changed
- Improved agent communication system
- Enhanced task distribution logic
- Updated project documentation

## [1.0.0] - 2025-06-01

### Added
- Initial SwarmBot implementation
- Basic chat functionality
- MCP server framework
- Agent system foundation
- Configuration management
- Logging system

## Migration Guide

### From 1.x to 2.0

The main change is the entry point consolidation:

| Old Command | New Command |
|-------------|-------------|
| `python main.py` | `python swarmbot.py standard` |
| `python enhanced_main.py` | `python swarmbot.py enhanced` |
| `python unified_main.py` | `python swarmbot.py` |
| `python run_swarmbot.py` | `python swarmbot.py` |

### New Features in 2.0

1. **Command-Line Options**
   ```bash
   python swarmbot.py --help
   python swarmbot.py --validate
   python swarmbot.py --list-tools
   ```

2. **Programmatic Usage**
   ```python
   from src.core.app import SwarmBotApp
   app = SwarmBotApp()
   app.run(['enhanced'])
   ```

3. **Module Access**
   ```python
   from src.agents.specialized_agents import ResearchAgent
   from src.config import Configuration
   ```

## Version History

| Version | Date | Status | Notes |
|---------|------|--------|-------|
| 2.0.0 | 2025-06-07 | Current | Major refactoring, single entry point |
| 1.5.0 | 2025-06-06 | Stable | Added validation, completed agent system |
| 1.0.0 | 2025-06-01 | Legacy | Initial release |

## Upgrade Instructions

### From 1.x to 2.0

1. **Update requirements:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Update scripts:**
   - Replace old entry point calls with `python swarmbot.py`
   - Update any imports from old modules

3. **Test configuration:**
   ```bash
   python swarmbot.py --validate
   ```

4. **Fix Unicode issues (optional):**
   ```bash
   python scripts/fix_unicode.py
   ```

## Contributors

- SwarmBot Development Team
- MCP Community
- Open Source Contributors

## License

[Your License Here]
