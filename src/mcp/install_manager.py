"""
MCP Installation Manager
Manages the installation of MCP servers for SwarmBot
"""

import asyncio
import subprocess
import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import sys

from .server_inventory import MCPServerInfo, ServerType

class MCPInstallationManager:
    """Manages the installation of MCP servers"""
    
    def __init__(self, inventory: 'MCPServerInventory', 
                 install_dir: str = "mcp_servers"):
        self.inventory = inventory
        self.install_dir = Path(install_dir)
        self.install_dir.mkdir(exist_ok=True)
        self.installation_log = []
        self.installed_servers = {}
        
    async def install_all_servers(self, parallel: bool = True) -> Dict[str, bool]:
        """Install all configured servers"""
        servers = self.inventory.get_installation_order()
        results = {}
        
        if parallel:
            # Install servers in parallel (max 3 at a time)
            semaphore = asyncio.Semaphore(3)
            
            async def install_with_semaphore(server_name):
                async with semaphore:
                    return await self.install_server(server_name)
            
            tasks = [install_with_semaphore(name) for name in servers]
            install_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for name, result in zip(servers, install_results):
                if isinstance(result, Exception):
                    results[name] = False
                    self._log(f"Failed to install {name}: {result}")
                else:
                    results[name] = result
        else:
            # Install servers sequentially
            for server_name in servers:
                try:
                    results[server_name] = await self.install_server(server_name)
                except Exception as e:
                    results[server_name] = False
                    self._log(f"Failed to install {server_name}: {e}")
                    
        # Save installation report
        await self._save_installation_report(results)
        return results
    
    async def install_server(self, server_name: str) -> bool:
        """Install a single MCP server"""
        if server_name not in self.inventory.servers:
            self._log(f"Server '{server_name}' not found in inventory", "ERROR")
            return False
            
        server = self.inventory.servers[server_name]
        self._log(f"Installing {server_name} ({server.type.value} server)...")
        
        # Check prerequisites
        ready, missing = self.inventory.check_prerequisites(server_name)
        if not ready:
            self._log(f"Prerequisites missing for {server_name}: {missing}", "ERROR")
            return False
            
        # Create server directory
        server_dir = self.install_dir / server_name
        server_dir.mkdir(exist_ok=True)
        
        # For npx-based servers, we don't need to install locally
        # They will be run directly with npx
        if server.command == "npx":
            self._log(f"✅ {server_name} will be run with npx (no local installation needed)")
            self.inventory.update_server_status(server_name, "ready")
            self.installed_servers[server_name] = {
                'install_dir': str(server_dir),
                'install_time': datetime.now().isoformat(),
                'type': server.type.value,
                'method': 'npx'
            }
            return True
            
        # For uvx-based Python servers
        elif server.command == "uvx":
            self._log(f"✅ {server_name} will be run with uvx (no local installation needed)")
            self.inventory.update_server_status(server_name, "ready")
            self.installed_servers[server_name] = {
                'install_dir': str(server_dir),
                'install_time': datetime.now().isoformat(),
                'type': server.type.value,
                'method': 'uvx'
            }
            return True
            
        # For other types, log as ready for now
        else:
            self._log(f"✅ {server_name} marked as ready (custom command: {server.command})")
            self.inventory.update_server_status(server_name, "ready")
            self.installed_servers[server_name] = {
                'install_dir': str(server_dir),
                'install_time': datetime.now().isoformat(),
                'type': server.type.value,
                'method': 'custom'
            }
            return True
    
    def _log(self, message: str, level: str = "INFO"):
        """Log installation messages"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message
        }
        self.installation_log.append(log_entry)
        print(f"[{timestamp}] [{level}] {message}")
    
    async def _save_installation_report(self, results: Dict[str, bool]):
        """Save installation report to file"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'installed_servers': self.installed_servers,
            'log': self.installation_log
        }
        
        report_path = self.install_dir / 'installation_report.json'
        
        # Use synchronous write for simplicity since we don't have aiofiles
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        self._log(f"Installation report saved to {report_path}")
