#!/usr/bin/env python3
"""
MCP Server Installation and Testing Script
Main entry point for Task 7 implementation
"""

import asyncio
import argparse
import sys
import json
from pathlib import Path
from typing import Dict, List
import os

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import our modules
from src.mcp.server_inventory import MCPServerInventory, ServerType
from src.mcp.prerequisite_installer import PrerequisiteInstaller


class MCPInstaller:
    """Main installer class that orchestrates the entire process"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            # Use default path relative to project root
            config_path = project_root / "config" / "servers_config.json"
        self.config_path = config_path
        self.inventory = MCPServerInventory(str(config_path))
        self.prerequisite_installer = PrerequisiteInstaller()
        
    async def run(self, args):
        """Run the installation process based on command line arguments"""
        
        # Step 1: Scan servers
        print("\n🔍 Scanning MCP Server Configuration...")
        print(f"   Config file: {self.config_path}")
        
        try:
            servers = self.inventory.scan_servers()
            print(f"   Found {len(servers)} servers to configure")
            
            # Print server list
            for name, server in servers.items():
                print(f"   - {name} ({server.type.value})")
                
        except FileNotFoundError as e:
            print(f"\n❌ Error: {e}")
            print(f"   Please ensure the config file exists at: {self.config_path}")
            return False
        
        # Step 2: Check prerequisites
        if not args.skip_prerequisites:
            print("\n🔧 Checking Prerequisites...")
            all_ready = await self.check_all_prerequisites()
            
            if not all_ready and not args.force:
                print("\n❌ Prerequisites not met. Use --force to continue anyway.")
                return False
                
        # Step 3: Verify configurations
        if args.verify or args.all:
            print("\n✅ Verifying MCP Server Configurations...")
            self.verify_configurations()
            
        print("\n✅ MCP Server configuration check complete!")
        return True
    
    async def check_all_prerequisites(self) -> bool:
        """Check prerequisites for all servers"""
        all_ready = True
        missing_prerequisites = {}
        
        for server_name in self.inventory.servers:
            ready, missing = self.inventory.check_prerequisites(server_name)
            
            if not ready:
                all_ready = False
                missing_prerequisites[server_name] = missing
                print(f"\n   ❌ {server_name}: Missing prerequisites:")
                for prereq in missing:
                    print(f"      - {prereq}")
            else:
                print(f"   ✅ {server_name}: All prerequisites met")
                    
        if missing_prerequisites:
            print("\n📋 Missing Prerequisites Summary:")
            
            # Collect unique prerequisites
            all_missing = set()
            for missing_list in missing_prerequisites.values():
                all_missing.update(missing_list)
                
            # Try to install
            results = self.prerequisite_installer.install_missing_prerequisites(
                list(all_missing)
            )
            
            # Check if any were successfully installed
            if any(success for _, success in results):
                print("\n   Some prerequisites were installed. Please restart the script.")
                return False
                
        return all_ready
    
    def verify_configurations(self):
        """Verify server configurations are correct"""
        print("\n📋 Server Configuration Details:")
        
        for name, server in self.inventory.servers.items():
            print(f"\n   {name}:")
            print(f"      Type: {server.type.value}")
            print(f"      Command: {server.command}")
            if server.args:
                print(f"      Args: {' '.join(server.args)}")
            if server.env:
                print(f"      Environment Variables:")
                for key, value in server.env.items():
                    # Hide sensitive values
                    if 'KEY' in key or 'TOKEN' in key:
                        display_value = value[:10] + "..." if len(value) > 10 else value
                    else:
                        display_value = value
                    print(f"         {key}: {display_value}")
            if server.health_check:
                print(f"      Health Check: {server.health_check}")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='MCP Server Installation and Testing Tool for SwarmBot'
    )
    
    # Action arguments
    parser.add_argument('--verify', action='store_true',
                      help='Verify server configurations')
    parser.add_argument('--all', action='store_true',
                      help='Run all checks')
    
    # Options
    parser.add_argument('--config', 
                      help='Path to servers configuration file')
    parser.add_argument('--force', action='store_true',
                      help='Continue even if prerequisites fail')
    parser.add_argument('--skip-prerequisites', action='store_true',
                      help='Skip prerequisite checks')
    
    args = parser.parse_args()
    
    # Default to --all if no specific action specified
    if not args.verify:
        args.all = True
        
    # Run the installer
    installer = MCPInstaller(args.config)
    success = await installer.run(args)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    asyncio.run(main())
