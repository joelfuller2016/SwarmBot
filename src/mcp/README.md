# MCP Server Management Module

This module provides comprehensive management for Model Context Protocol (MCP) servers in the SwarmBot system.

## Components

### Core Classes

- **MCPServerInventory**: Discovers and validates MCP servers from configuration
- **PrerequisiteInstaller**: Checks and guides installation of dependencies
- **MCPInstallationManager**: Orchestrates server installation process
- **MCPServerManager**: Manages server lifecycle (start, stop, restart)

### Usage

```python
from src.mcp import MCPServerInventory, MCPServerManager

# Discover servers
inventory = MCPServerInventory("config/servers_config.json")
servers = inventory.scan_servers()

# Manage servers
manager = MCPServerManager()
await manager.start_server("memory", servers["memory"])
```

### CLI Tool

Run the main CLI tool for server management:

```bash
python src/mcp/install_mcp_servers.py --verify
```

Options:
- `--verify`: Check server configurations
- `--force`: Continue even if prerequisites fail
- `--skip-prerequisites`: Skip prerequisite checks

## Configuration

Servers are configured in `config/servers_config.json`. See the main documentation at `docs/mcp_server_management.md` for details.

## Testing

Tests are located in `tests/mcp/`:
- `test_inventory.py`: Test server discovery
- `test_mcp_management.py`: Full integration test
- `test_mcp_setup.py`: Quick verification

## Dependencies

- Python 3.8+
- Node.js 16+ (for Node.js-based servers)
- UV package manager (optional, for Python servers)
