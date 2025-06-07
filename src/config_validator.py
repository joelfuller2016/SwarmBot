#!/usr/bin/env python3
"""
Configuration Validation System for SwarmBot
Validates JSON configuration files and environment setup
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any
import jsonschema
from jsonschema import validate, ValidationError
from dotenv import load_dotenv


class ConfigValidator:
    """Validates SwarmBot configuration files and environment"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.errors = []
        self.warnings = []
        
        # Define JSON schemas for validation
        self.schemas = {
            'servers_config': {
                "type": "object",
                "properties": {
                    "mcpServers": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "object",
                            "required": ["command", "args"],
                            "properties": {
                                "command": {"type": "string"},
                                "args": {"type": "array", "items": {"type": "string"}},
                                "env": {"type": "object"}
                            }
                        }
                    }
                },
                "required": ["mcpServers"]
            },
            'tool_patterns': {
                "type": "object",
                "additionalProperties": {
                    "type": "object",
                    "properties": {
                        "patterns": {"type": "array", "items": {"type": "string"}},
                        "description": {"type": "string"},
                        "examples": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["patterns"]
                }
            }
        }
    
    def validate_json_file(self, file_path: Path, schema_name: str) -> bool:
        """Validate a JSON file against its schema"""
        if not file_path.exists():
            self.errors.append(f"File not found: {file_path}")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in {file_path}: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Error reading {file_path}: {e}")
            return False
        
        # Validate against schema
        if schema_name in self.schemas:
            try:
                validate(instance=data, schema=self.schemas[schema_name])
                return True
            except ValidationError as e:
                self.errors.append(f"Schema validation failed for {file_path}: {e.message}")
                return False
        else:
            self.warnings.append(f"No schema defined for {schema_name}")
            return True
    
    def validate_environment(self) -> bool:
        """Validate environment variables and .env file"""
        load_dotenv()
        
        required_vars = [
            ("GROQ_API_KEY", "Groq API key for LLM access"),
            ("ANTHROPIC_API_KEY", "Anthropic API key (optional)"),
            ("OPENAI_API_KEY", "OpenAI API key (optional)")
        ]
        
        missing_required = []
        found_vars = []
        
        for var_name, description in required_vars:
            value = os.getenv(var_name)
            if value:
                found_vars.append(var_name)
            elif "optional" not in description.lower():
                missing_required.append(f"{var_name} - {description}")
        
        # At least one LLM API key must be present
        llm_keys = ["GROQ_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"]
        if not any(os.getenv(key) for key in llm_keys):
            self.errors.append("No LLM API keys found. At least one is required (GROQ_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY)")
            return False
        
        if missing_required:
            for var in missing_required:
                self.warnings.append(f"Missing optional: {var}")
        
        return True
    
    def validate_project_structure(self) -> bool:
        """Validate required project directories and files exist"""
        required_structure = {
            "directories": [
                "config",
                "src",
                "src/agents",
                "src/ui",
                "tests",
                "logs"
            ],
            "files": [
                "requirements.txt",
                "unified_main.py",
                "enhanced_main.py",
                ".env"
            ]
        }
        
        valid = True
        
        for dir_path in required_structure["directories"]:
            path = self.project_root / dir_path
            if not path.exists() or not path.is_dir():
                self.errors.append(f"Missing directory: {dir_path}")
                valid = False
        
        for file_path in required_structure["files"]:
            path = self.project_root / file_path
            if not path.exists():
                if file_path == ".env":
                    self.warnings.append(f"Missing file: {file_path} - Please create from .env.example")
                else:
                    self.errors.append(f"Missing file: {file_path}")
                    valid = False
        
        return valid
    
    def validate_server_configs(self) -> bool:
        """Validate all server configurations"""
        config_path = self.project_root / "config" / "servers_config.json"
        
        if not self.validate_json_file(config_path, 'servers_config'):
            return False
        
        # Load and check server executables
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        for server_name, server_config in config.get("mcpServers", {}).items():
            command = server_config.get("command")
            if command in ["npx", "uvx", "python", "node"]:
                # These are common commands that should exist
                import shutil
                if not shutil.which(command):
                    self.warnings.append(f"Command '{command}' not found for server '{server_name}'")
            
        return True
    
    def validate_tool_patterns(self) -> bool:
        """Validate tool patterns configuration"""
        config_path = self.project_root / "config" / "tool_patterns.json"
        
        if not config_path.exists():
            self.warnings.append("tool_patterns.json not found - enhanced mode may not work properly")
            return True
        
        return self.validate_json_file(config_path, 'tool_patterns')
    
    def run_all_validations(self) -> Tuple[bool, List[str], List[str]]:
        """Run all validation checks"""
        self.errors = []
        self.warnings = []
        
        print("[Validation] Starting configuration validation...")
        print("-" * 60)
        
        checks = [
            ("Project Structure", self.validate_project_structure),
            ("Environment Variables", self.validate_environment),
            ("Server Configurations", self.validate_server_configs),
            ("Tool Patterns", self.validate_tool_patterns)
        ]
        
        all_valid = True
        
        for check_name, check_func in checks:
            print(f"\n[Checking] {check_name}...", end="")
            try:
                if check_func():
                    print(" [OK]")
                else:
                    print(" [FAILED]")
                    all_valid = False
            except Exception as e:
                print(f" [ERROR]")
                self.errors.append(f"Exception in {check_name}: {e}")
                all_valid = False
        
        return all_valid, self.errors, self.warnings
    
    def print_report(self):
        """Print validation report"""
        print("\n" + "=" * 60)
        print("[Validation Report]")
        print("=" * 60)
        
        if self.errors:
            print(f"\n[ERRORS] Found {len(self.errors)} error(s):")
            for error in self.errors:
                print(f"  - {error}")
        else:
            print("\n[OK] No errors found!")
        
        if self.warnings:
            print(f"\n[WARNINGS] Found {len(self.warnings)} warning(s):")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        print("\n" + "=" * 60)
        
        return len(self.errors) == 0


def main():
    """Run configuration validation"""
    validator = ConfigValidator()
    all_valid, errors, warnings = validator.run_all_validations()
    validator.print_report()
    
    if all_valid:
        print("\n[SUCCESS] All configurations are valid!")
        return 0
    else:
        print("\n[FAILED] Please fix the errors above before running SwarmBot.")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
