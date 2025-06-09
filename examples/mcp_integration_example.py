"""
Example: Integrating MCP Server Management with SwarmBot

This example shows how to integrate the new MCP server management
system with the main SwarmBot application.
"""

import asyncio
from src.mcp import MCPServerInventory, MCPServerManager
from src.config import Configuration


class SwarmBotWithMCP:
    """Example SwarmBot integration with MCP servers"""
    
    def __init__(self):
        self.config = Configuration()
        self.mcp_inventory = None
        self.mcp_manager = MCPServerManager()
        self.servers = {}
        
    async def initialize_mcp_servers(self):
        """Initialize and start MCP servers"""
        print("[SwarmBot] Initializing MCP servers...")
        
        # Create inventory
        self.mcp_inventory = MCPServerInventory("config/servers_config.json")
        self.servers = self.mcp_inventory.scan_servers()
        
        print(f"[SwarmBot] Found {len(self.servers)} MCP servers")
        
        # Check prerequisites
        all_ready = True
        for server_name, server_config in self.servers.items():
            ready, missing = self.mcp_inventory.check_prerequisites(server_name)
            if not ready:
                print(f"[WARNING] {server_name}: Missing {missing}")
                all_ready = False
                
        if not all_ready:
            print("[WARNING] Some servers have missing prerequisites")
            
        # Start essential servers
        essential_servers = ["memory", "filesystem", "sqlite-db"]
        
        for server_name in essential_servers:
            if server_name in self.servers:
                print(f"[SwarmBot] Starting {server_name}...")
                success = await self.mcp_manager.start_server(
                    server_name, 
                    self.servers[server_name]
                )
                if success:
                    print(f"[OK] {server_name} started")
                else:
                    print(f"[ERROR] Failed to start {server_name}")
                    
    async def shutdown_mcp_servers(self):
        """Shutdown all MCP servers"""
        print("\n[SwarmBot] Shutting down MCP servers...")
        await self.mcp_manager.stop_all_servers()
        
    async def run(self):
        """Main application run loop"""
        try:
            # Initialize MCP servers
            await self.initialize_mcp_servers()
            
            # Get server status
            running_servers = self.mcp_manager.get_all_servers()
            print(f"\n[SwarmBot] {len(running_servers)} servers running")
            
            # Your main application logic here
            print("\n[SwarmBot] Ready for commands...")
            print("Press Ctrl+C to exit")
            
            # Keep running until interrupted
            await asyncio.Event().wait()
            
        except KeyboardInterrupt:
            print("\n[SwarmBot] Interrupted by user")
        finally:
            # Clean shutdown
            await self.shutdown_mcp_servers()
            

async def main():
    """Example usage"""
    app = SwarmBotWithMCP()
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
