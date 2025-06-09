"""
Command system for SwarmBot chat interface
Follows existing pattern of simple string commands (no "/" prefix)
"""

import json
import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class Command:
    """Base command class"""
    def __init__(self, name: str, description: str, handler: Callable):
        self.name = name
        self.description = description
        self.handler = handler
        self.aliases = []
    
    def add_alias(self, alias: str):
        """Add an alias for this command"""
        self.aliases.append(alias)
        return self


class CommandParser:
    """
    Command parser following SwarmBot's existing pattern.
    Commands are simple strings without "/" prefix.
    """
    
    def __init__(self):
        self.commands: Dict[str, Command] = {}
        self._register_default_commands()
    
    def _register_default_commands(self):
        """Register default commands matching existing functionality"""
        # Help command
        self.register("help", "Show available commands", self._cmd_help)
        
        # Tools command  
        self.register("tools", "List all available tools", self._cmd_tools)
        
        # Servers command
        self.register("servers", "Show active servers", self._cmd_servers)
        
        # Exit commands with aliases
        exit_cmd = Command("quit", "Exit the application", self._cmd_quit)
        exit_cmd.add_alias("exit").add_alias("q")
        self.commands["quit"] = exit_cmd
        for alias in exit_cmd.aliases:
            self.commands[alias] = exit_cmd
        
        # New commands to add
        self.register("clear", "Clear the conversation display", self._cmd_clear)
        self.register("status", "Show system status", self._cmd_status)
        self.register("history", "Show conversation history", self._cmd_history)
        self.register("export", "Export conversation to file", self._cmd_export)
        self.register("reset", "Reset conversation context", self._cmd_reset)
        self.register("version", "Show SwarmBot version", self._cmd_version)
    
    def register(self, name: str, description: str, handler: Callable):
        """Register a new command"""
        self.commands[name.lower()] = Command(name, description, handler)
    
    def parse(self, user_input: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse user input and execute command if found.
        Returns command result or None if not a command.
        """
        input_lower = user_input.strip().lower()
        
        # Check if it's a command
        if input_lower in self.commands:
            cmd = self.commands[input_lower]
            try:
                return cmd.handler(user_input, context)
            except Exception as e:
                logger.error(f"Command '{cmd.name}' failed: {e}")
                return {
                    'type': 'error',
                    'message': f"Command failed: {str(e)}"
                }
        
        # Check for commands with arguments (e.g., "history 20")
        parts = input_lower.split()
        if parts and parts[0] in self.commands:
            cmd = self.commands[parts[0]]
            try:
                return cmd.handler(user_input, context)
            except Exception as e:
                logger.error(f"Command '{cmd.name}' failed: {e}")
                return {
                    'type': 'error', 
                    'message': f"Command failed: {str(e)}"
                }
        
        return None
    
    # Command implementations
    def _cmd_help(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Show help information"""
        lines = ["\n📚 Available Commands:"]
        
        # Get unique commands (skip aliases)
        seen = set()
        for name, cmd in self.commands.items():
            if cmd not in seen:
                seen.add(cmd)
                if cmd.aliases:
                    aliases = f" (aliases: {', '.join(cmd.aliases)})"
                else:
                    aliases = ""
                lines.append(f"  {cmd.name:<12} - {cmd.description}{aliases}")
        
        return {
            'type': 'help',
            'message': '\n'.join(lines)
        }
    
    def _cmd_tools(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """List available tools"""
        chat_session = context.get('chat_session')
        if not chat_session:
            return {'type': 'error', 'message': 'No chat session available'}
        
        # Delegate to existing show_tools method
        return {
            'type': 'delegate',
            'method': 'show_tools'
        }
    
    def _cmd_servers(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Show active servers"""
        return {
            'type': 'delegate',
            'method': 'show_servers'
        }
    
    def _cmd_quit(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Exit the application"""
        return {
            'type': 'exit',
            'message': '\n👋 Goodbye!'
        }
    
    def _cmd_clear(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Clear the screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        return {
            'type': 'clear',
            'message': '🧹 Screen cleared'
        }
    
    def _cmd_status(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Show system status"""
        chat_session = context.get('chat_session')
        if not chat_session:
            return {'type': 'error', 'message': 'No chat session available'}
        
        lines = ["\n📊 System Status:"]
        lines.append(f"  Active Servers: {len(chat_session.active_servers)}/{len(chat_session.servers)}")
        lines.append(f"  Available Tools: {len(chat_session.all_tools)}")
        lines.append(f"  Messages in History: {len(chat_session.conversation_history)}")
        
        # Add context manager info if available
        if hasattr(chat_session, 'context_manager'):
            cm = chat_session.context_manager
            lines.append(f"  Context Window: {cm.current_tokens}/{cm.max_tokens} tokens")
        
        return {
            'type': 'status',
            'message': '\n'.join(lines)
        }
    
    def _cmd_history(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Show conversation history"""
        chat_session = context.get('chat_session')
        if not chat_session:
            return {'type': 'error', 'message': 'No chat session available'}
        
        # Parse count from input
        parts = user_input.split()
        count = 10  # default
        if len(parts) > 1 and parts[1].isdigit():
            count = int(parts[1])
        
        history = chat_session.conversation_history[-count:]
        lines = [f"\n📜 Last {min(count, len(history))} messages:"]
        
        for msg in history:
            role = msg['role'].upper()
            content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            lines.append(f"\n[{role}]: {content}")
        
        return {
            'type': 'history',
            'message': '\n'.join(lines)
        }
    
    def _cmd_export(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Export conversation"""
        chat_session = context.get('chat_session')
        if not chat_session:
            return {'type': 'error', 'message': 'No chat session available'}
        
        # Parse filename from input
        parts = user_input.split()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.json" if len(parts) < 2 else parts[1]
        
        try:
            data = {
                'timestamp': timestamp,
                'messages': chat_session.conversation_history,
                'server_count': len(chat_session.active_servers),
                'tool_count': len(chat_session.all_tools)
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return {
                'type': 'export',
                'message': f'💾 Conversation exported to {filename}'
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f'Export failed: {str(e)}'
            }
    
    def _cmd_reset(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Reset conversation context"""
        return {
            'type': 'reset',
            'message': '🔄 Conversation context will be reset. Type "confirm" to proceed.'
        }
    
    def _cmd_version(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Show version information"""
        return {
            'type': 'version',
            'message': '\n🤖 SwarmBot v0.1.0\nAI Assistant with MCP Tools\n'
        }
