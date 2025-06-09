"""
Prerequisite Installer Module
Handles installation of missing prerequisites for MCP servers
"""

import subprocess
import sys
import os
from typing import List, Tuple
import platform

class PrerequisiteInstaller:
    """Handles installation of missing prerequisites"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        
    def install_missing_prerequisites(self, missing: List[str]) -> List[Tuple[str, bool]]:
        """Attempt to install missing prerequisites"""
        results = []
        
        for prerequisite in missing:
            if "Node.js" in prerequisite:
                success = self._install_nodejs()
                results.append(("Node.js", success))
                
            elif "npm" in prerequisite:
                success = self._install_npm()
                results.append(("npm", success))
                
            elif "UV package manager" in prerequisite:
                success = self._install_uv()
                results.append(("UV", success))
                
            elif "Environment variable" in prerequisite:
                # Can't auto-install, provide guidance
                var_name = prerequisite.split(": ")[1]
                print(f"\n⚠️  Missing environment variable: {var_name}")
                print(f"   Please set this in your .env file or system environment")
                results.append((prerequisite, False))
                
        return results
    
    def _install_nodejs(self) -> bool:
        """Provide instructions for Node.js installation"""
        print("\n📦 Node.js Installation Required")
        print("=" * 50)
        
        if self.platform == "windows":
            print("Option 1: Download from https://nodejs.org/")
            print("Option 2: Using Chocolatey:")
            print("  choco install nodejs")
            print("\nOption 3: Using winget:")
            print("  winget install OpenJS.NodeJS")
            
        elif self.platform == "darwin":  # macOS
            print("Option 1: Download from https://nodejs.org/")
            print("Option 2: Using Homebrew:")
            print("  brew install node")
            
        elif self.platform == "linux":
            print("Option 1: Using package manager:")
            print("  Ubuntu/Debian: sudo apt-get install nodejs npm")
            print("  Fedora: sudo dnf install nodejs npm")
            print("  Arch: sudo pacman -S nodejs npm")
            
        print("\nAfter installation, restart your terminal and run this script again.")
        return False
    
    def _install_npm(self) -> bool:
        """NPM usually comes with Node.js"""
        print("\n📦 npm is typically installed with Node.js")
        print("If you have Node.js but not npm, try:")
        print("  Windows: Reinstall Node.js")
        print("  macOS/Linux: sudo apt-get install npm")
        return False
    
    def _install_uv(self) -> bool:
        """Install UV package manager"""
        print("\n📦 Installing UV package manager...")
        
        try:
            # UV can be installed via pip
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', 'uv'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ UV package manager installed successfully")
                return True
            else:
                print(f"❌ Failed to install UV: {result.stderr}")
                print("\nManual installation:")
                print("  pip install uv")
                print("  or")
                print("  pipx install uv")
                return False
                
        except Exception as e:
            print(f"❌ Error installing UV: {e}")
            return False
