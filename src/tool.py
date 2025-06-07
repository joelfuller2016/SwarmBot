"""
Tool module for SwarmBot
Represents a tool with its properties and formatting
"""

from typing import Dict, Any


class Tool:
    """Represents a tool with its properties and formatting."""

    def __init__(self, name: str, description: str, input_schema: Dict[str, Any]) -> None:
        self.name: str = name
        self.description: str = description
        self.input_schema: Dict[str, Any] = input_schema

    def format_for_llm(self) -> str:
        """Format tool information for LLM."""
        args_desc = []
        if 'properties' in self.input_schema:
            for param_name, param_info in self.input_schema['properties'].items():
                param_type = param_info.get('type', 'any')
                param_desc = param_info.get('description', 'No description')
                required = param_name in self.input_schema.get('required', [])
                
                arg_desc = f"  - {param_name} ({param_type}): {param_desc}"
                if required:
                    arg_desc += " [REQUIRED]"
                args_desc.append(arg_desc)
        
        return f"""Tool: {self.name}
Description: {self.description}
Arguments:
{chr(10).join(args_desc) if args_desc else '  No arguments required'}"""