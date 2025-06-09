"""
MCP Server Manager
Manages the lifecycle of MCP servers for SwarmBot
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
import subprocess
import sys
import os

from .server_inventory import MCPServerInfo, ServerType


class MCPServerProcess:
    """Represents a running MCP server process"""
    
    def __init__(self, name: str, process: asyncio.subprocess.Process, config: MCPServerInfo):
        self.name = name
        self.process = process
        self.config = config
        self.start_time = datetime.now()
        self.pid = process.pid
        

class MCPServerManager:
    """Manages MCP server lifecycle"""
    
    def __init__(self):
        self.servers: Dict[str, MCPServerProcess] = {}
        self.server_configs: Dict[str, MCPServerInfo] = {}
        
    async def start_server(self, server_name: str, 
                         server_config: MCPServerInfo) -> bool:
        """Start an MCP server"""
        if server_name in self.servers:
            # Already running
            print(f"[INFO] Server {server_name} is already running")
            return True
            
        try:
            # Build command based on server type
            cmd = [server_config.command] + server_config.args
            
            # Set up environment
            env = os.environ.copy()
            for key, value in server_config.env.items():
                # Handle ${VAR} style placeholders
                if value.startswith('${') and value.endswith('}'):
                    actual_var = value[2:-1]
                    actual_value = os.environ.get(actual_var, '')
                    if actual_value:
                        env[key] = actual_value
                else:
                    env[key] = value
            
            # Log the command being run
            print(f"[INFO] Starting {server_name}: {' '.join(cmd)}")
            
            # Start the process
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            # Store the server process
            self.servers[server_name] = MCPServerProcess(server_name, process, server_config)
            self.server_configs[server_name] = server_config
            
            # Give it a moment to start
            await asyncio.sleep(1)
            
            # Check if still running
            if process.returncode is not None:
                # Process already exited
                print(f"[ERROR] Server {server_name} exited immediately with code {process.returncode}")
                del self.servers[server_name]
                return False
                
            print(f"[OK] Server {server_name} started successfully (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to start {server_name}: {e}")
            return False
    
    async def stop_server(self, server_name: str, timeout: int = 5) -> bool:
        """Stop an MCP server gracefully"""
        if server_name not in self.servers:
            return True
            
        server_process = self.servers[server_name]
        process = server_process.process
        
        try:
            print(f"[INFO] Stopping {server_name}...")
            
            # Send termination signal
            process.terminate()
            
            # Wait for process to end
            await asyncio.wait_for(process.wait(), timeout=timeout)
            
            print(f"[OK] Server {server_name} stopped gracefully")
            
        except asyncio.TimeoutError:
            # Force kill if graceful shutdown fails
            print(f"[WARN] Force killing {server_name} after timeout")
            process.kill()
            await process.wait()
            
        # Clean up
        del self.servers[server_name]
        if server_name in self.server_configs:
            del self.server_configs[server_name]
            
        return True
    
    async def restart_server(self, server_name: str) -> bool:
        """Restart an MCP server"""
        # Get config before stopping
        config = None
        if server_name in self.server_configs:
            config = self.server_configs[server_name]
            
        if not config:
            print(f"[ERROR] No configuration found for {server_name}")
            return False
            
        # Stop the server
        await self.stop_server(server_name)
        
        # Wait a moment
        await asyncio.sleep(1)
        
        # Start it again
        return await self.start_server(server_name, config)
    
    async def is_server_running(self, server_name: str) -> bool:
        """Check if a server is running"""
        if server_name not in self.servers:
            return False
            
        process = self.servers[server_name].process
        return process.returncode is None
    
    async def get_server_process(self, server_name: str) -> Optional[asyncio.subprocess.Process]:
        """Get the process object for a server"""
        if server_name in self.servers:
            return self.servers[server_name].process
        return None
    
    def get_server_info(self, server_name: str) -> Optional[Dict]:
        """Get information about a server"""
        if server_name not in self.servers:
            return None
            
        server = self.servers[server_name]
        return {
            'name': server.name,
            'pid': server.pid,
            'start_time': server.start_time.isoformat(),
            'uptime': (datetime.now() - server.start_time).total_seconds(),
            'config': {
                'type': server.config.type.value,
                'command': server.config.command,
                'args': server.config.args
            }
        }
    
    def get_all_servers(self) -> Dict[str, Dict]:
        """Get information about all servers"""
        return {
            name: self.get_server_info(name)
            for name in self.servers
        }
    
    async def stop_all_servers(self):
        """Stop all running servers"""
        server_names = list(self.servers.keys())
        
        for server_name in server_names:
            await self.stop_server(server_name)
            
        print(f"[OK] All {len(server_names)} servers stopped")
