"""
MCP Server Inventory Module
Manages the discovery and cataloging of MCP servers for SwarmBot
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class ServerType(Enum):
    NODEJS = "nodejs"
    PYTHON = "python"
    UNKNOWN = "unknown"

@dataclass
class MCPServerInfo:
    name: str
    type: ServerType
    command: str
    args: List[str]
    env: Dict[str, str]
    health_check: Optional[Dict[str, any]]
    status: str = "unknown"
    
class MCPServerInventory:
    """Manages the inventory of MCP servers configured for SwarmBot"""
    
    def __init__(self, config_path: str = "config/servers_config.json"):
        self.config_path = Path(config_path)
        self.servers: Dict[str, MCPServerInfo] = {}
        self.prerequisites_cache = {}
        
    def scan_servers(self) -> Dict[str, MCPServerInfo]:
        """Scan and catalog all configured MCP servers"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Server config not found: {self.config_path}")
            
        with open(self.config_path, 'r') as f:
            config = json.load(f)
            
        for name, server_config in config.get('servers', {}).items():
            server_type = self._determine_server_type(server_config)
            
            self.servers[name] = MCPServerInfo(
                name=name,
                type=server_type,
                command=server_config.get('command', ''),
                args=server_config.get('args', []),
                env=server_config.get('env', {}),
                health_check=server_config.get('health_check'),
                status='not_installed'
            )
            
        return self.servers
    
    def _determine_server_type(self, config: Dict) -> ServerType:
        """Determine the type of MCP server from its configuration"""
        command = config.get('command', '').lower()
        
        if 'node' in command or 'npm' in command or 'npx' in command:
            return ServerType.NODEJS
        elif 'python' in command or 'uv' in command or 'pip' in command:
            return ServerType.PYTHON
        else:
            # Check file extension if command points to a file
            if Path(command).suffix in ['.js', '.mjs', '.ts']:
                return ServerType.NODEJS
            elif Path(command).suffix in ['.py']:
                return ServerType.PYTHON
                
        return ServerType.UNKNOWN
    
    def check_prerequisites(self, server_name: str) -> Tuple[bool, List[str]]:
        """Check if server prerequisites are met"""
        if server_name not in self.servers:
            return False, [f"Server '{server_name}' not found in inventory"]
            
        server = self.servers[server_name]
        missing = []
        
        # Check common prerequisites
        if server.type == ServerType.NODEJS:
            if not self._check_nodejs():
                missing.append("Node.js (16+ required)")
            if not self._check_npm():
                missing.append("npm package manager")
                
        elif server.type == ServerType.PYTHON:
            if not self._check_python():
                missing.append("Python 3.8+")
            if server.command == "uvx" and not self._check_uv():
                missing.append("UV package manager")
                
        # Check server-specific requirements
        specific_reqs = self._check_specific_requirements(server)
        missing.extend(specific_reqs)
        
        return len(missing) == 0, missing
    
    def _check_nodejs(self) -> bool:
        """Check if Node.js is installed and meets version requirements"""
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                # Extract major version number
                major = int(version.split('.')[0].replace('v', ''))
                return major >= 16
        except:
            pass
        return False
    
    def _check_npm(self) -> bool:
        """Check if npm is installed"""
        try:
            result = subprocess.run(['npm', '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _check_python(self) -> bool:
        """Check if Python 3.8+ is installed"""
        try:
            result = subprocess.run([sys.executable, '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                # Extract version numbers
                parts = version.split()[1].split('.')
                major, minor = int(parts[0]), int(parts[1])
                return major == 3 and minor >= 8
        except:
            pass
        return False
    
    def _check_uv(self) -> bool:
        """Check if UV package manager is installed"""
        try:
            result = subprocess.run(['uv', '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _check_specific_requirements(self, server: MCPServerInfo) -> List[str]:
        """Check server-specific requirements"""
        missing = []
        
        # Check for required environment variables
        for env_var in server.env.keys():
            if env_var.endswith('_API_KEY') or env_var.endswith('_TOKEN'):
                # Check if the env var is set in environment or starts with ${
                env_value = os.environ.get(env_var, '')
                config_value = server.env[env_var]
                
                if config_value.startswith('${') and config_value.endswith('}'):
                    # It's a placeholder, check actual env var
                    actual_var = config_value[2:-1]
                    if not os.environ.get(actual_var):
                        missing.append(f"Environment variable: {actual_var}")
                elif not env_value and not config_value:
                    missing.append(f"Environment variable: {env_var}")
                    
        return missing
    
    def get_installation_order(self) -> List[str]:
        """Determine optimal installation order based on dependencies"""
        # For now, return alphabetical order
        # TODO: Implement dependency graph analysis
        return sorted(self.servers.keys())
    
    def update_server_status(self, server_name: str, status: str):
        """Update the status of a server"""
        if server_name in self.servers:
            self.servers[server_name].status = status
    
    def export_inventory(self, output_path: str = "mcp_inventory.json"):
        """Export the current inventory to a JSON file"""
        inventory_data = {
            name: {
                'type': server.type.value,
                'command': server.command,
                'args': server.args,
                'env': server.env,
                'health_check': server.health_check,
                'status': server.status
            }
            for name, server in self.servers.items()
        }
        
        with open(output_path, 'w') as f:
            json.dump(inventory_data, f, indent=2)
