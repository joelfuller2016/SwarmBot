"""
Tool Matcher module for SwarmBot Enhanced
Provides intelligent tool matching based on natural language
"""

import re
from typing import Dict, List, Any
from dataclasses import dataclass

from .tool import Tool


@dataclass
class ToolMatch:
    """Represents a matched tool with confidence score."""
    tool_name: str
    server_name: str
    confidence: float
    suggested_args: Dict[str, Any]
    reasoning: str


class ToolMatcher:
    """Intelligent tool matching based on natural language."""
    
    def __init__(self):
        # Define tool patterns and keywords
        self.tool_patterns = {
            # File operations
            'read_file': {
                'keywords': ['read', 'show', 'display', 'view', 'open', 'look at', 'see', 'check'],
                'context': ['file', 'document', 'code', 'content'],
                'examples': ['read main.py', 'show me the config file', 'what\'s in test.txt']
            },
            'write_file': {
                'keywords': ['write', 'create', 'save', 'make', 'generate'],
                'context': ['file', 'document', 'script'],
                'examples': ['create a new python file', 'write a config.json']
            },
            'list_directory': {
                'keywords': ['list', 'show', 'what\'s in', 'contents of', 'files in'],
                'context': ['directory', 'folder', 'path'],
                'examples': ['list files in the current directory', 'what\'s in the src folder']
            },
            
            # Git operations
            'git_status': {
                'keywords': ['git status', 'changes', 'modified', 'uncommitted'],
                'context': ['git', 'repository', 'repo'],
                'examples': ['show git status', 'what files have changed']
            },
            'git_commit': {
                'keywords': ['commit', 'save changes'],
                'context': ['git'],
                'examples': ['commit these changes', 'git commit with message "fix bug"']
            },
            
            # Task management
            'get_tasks': {
                'keywords': ['tasks', 'todos', 'show tasks', 'list tasks', 'what to do'],
                'context': ['task', 'todo', 'project'],
                'examples': ['show me all tasks', 'what tasks do I have']
            },
            'next_task': {
                'keywords': ['next', 'what should I do', 'next task', 'priority'],
                'context': ['task', 'work'],
                'examples': ['what\'s next', 'what should I work on']
            },
            'set_task_status': {
                'keywords': ['complete', 'done', 'finish', 'mark', 'update status'],
                'context': ['task'],
                'examples': ['mark task 5 as done', 'complete task 3']
            },
            
            # Search operations
            'web_search': {
                'keywords': ['search', 'find', 'look up', 'google', 'web'],
                'context': ['online', 'internet', 'web'],
                'examples': ['search for python tutorials', 'find information about AI']
            },
            'search_code': {
                'keywords': ['search', 'find', 'grep', 'look for'],
                'context': ['code', 'function', 'variable', 'class'],
                'examples': ['find all uses of calculate_total', 'search for TODO comments']
            },
            
            # GitHub operations
            'create_issue': {
                'keywords': ['create issue', 'new issue', 'report bug'],
                'context': ['github', 'issue'],
                'examples': ['create a github issue for the login bug']
            },
            'list_issues': {
                'keywords': ['issues', 'bugs', 'show issues'],
                'context': ['github'],
                'examples': ['show all open issues', 'list github issues']
            }
        }
        
        # Tool argument extractors
        self.arg_extractors = {
            'read_file': self._extract_file_path,
            'write_file': self._extract_file_write_args,
            'git_commit': self._extract_commit_message,
            'set_task_status': self._extract_task_status,
            'web_search': self._extract_search_query,
            'search_code': self._extract_code_search_args
        }
    
    def find_matching_tools(self, user_input: str, available_tools: List[Tool]) -> List[ToolMatch]:
        """Find tools that match the user's intent."""
        matches = []
        input_lower = user_input.lower()
        
        # Create a map of tool names to tool objects
        tool_map = {tool.name: tool for tool in available_tools}
        
        for tool_name, patterns in self.tool_patterns.items():
            if tool_name not in tool_map:
                continue
                
            confidence = 0.0
            reasoning = []
            
            # Check keywords
            keyword_matches = sum(1 for kw in patterns['keywords'] if kw in input_lower)
            if keyword_matches > 0:
                confidence += 0.4 * (keyword_matches / len(patterns['keywords']))
                reasoning.append(f"Keywords: {keyword_matches}/{len(patterns['keywords'])}")
            
            # Check context
            context_matches = sum(1 for ctx in patterns.get('context', []) if ctx in input_lower)
            if context_matches > 0:
                confidence += 0.3 * (context_matches / len(patterns.get('context', [1])))
                reasoning.append(f"Context: {context_matches}/{len(patterns.get('context', []))}")
            
            # Check examples similarity
            for example in patterns.get('examples', []):
                similarity = self._calculate_similarity(input_lower, example.lower())
                if similarity > 0.5:
                    confidence += 0.3 * similarity
                    reasoning.append(f"Similar to: '{example}'")
                    break
            
            if confidence > 0.3:  # Threshold for considering a match
                # Extract arguments
                args = {}
                if tool_name in self.arg_extractors:
                    args = self.arg_extractors[tool_name](user_input)
                
                matches.append(ToolMatch(
                    tool_name=tool_name,
                    server_name=next((t.name for t in available_tools if t.name == tool_name), "unknown"),
                    confidence=confidence,
                    suggested_args=args,
                    reasoning=" | ".join(reasoning)
                ))
        
        # Sort by confidence
        matches.sort(key=lambda x: x.confidence, reverse=True)
        return matches
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings."""
        words1 = set(str1.split())
        words2 = set(str2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _extract_file_path(self, user_input: str) -> Dict[str, Any]:
        """Extract file path from user input."""
        # Look for quoted paths
        quoted = re.findall(r'["\']([^"\']+)["\']', user_input)
        if quoted:
            return {'path': quoted[0]}
        
        # Look for file extensions
        file_pattern = r'(\S+\.\w+)'
        matches = re.findall(file_pattern, user_input)
        if matches:
            return {'path': matches[0]}
        
        # Look for path-like structures
        path_pattern = r'(\S+[/\\]\S+)'
        matches = re.findall(path_pattern, user_input)
        if matches:
            return {'path': matches[0]}
        
        return {}
    
    def _extract_file_write_args(self, user_input: str) -> Dict[str, Any]:
        """Extract file write arguments."""
        args = self._extract_file_path(user_input)
        
        # Extract content if provided
        content_match = re.search(r'with content[:\s]+(.+)', user_input, re.IGNORECASE)
        if content_match:
            args['content'] = content_match.group(1).strip()
        
        return args
    
    def _extract_commit_message(self, user_input: str) -> Dict[str, Any]:
        """Extract git commit message."""
        # Look for quoted message
        quoted = re.findall(r'["\']([^"\']+)["\']', user_input)
        if quoted:
            return {'message': quoted[0]}
        
        # Look for message after keywords
        message_match = re.search(r'(?:message|msg|commit)[:\s]+(.+)', user_input, re.IGNORECASE)
        if message_match:
            return {'message': message_match.group(1).strip()}
        
        return {'message': 'Update from SwarmBot'}
    
    def _extract_task_status(self, user_input: str) -> Dict[str, Any]:
        """Extract task ID and status."""
        args = {}
        
        # Extract task ID
        id_match = re.search(r'task\s+(\d+)', user_input, re.IGNORECASE)
        if id_match:
            args['id'] = id_match.group(1)
        
        # Extract status
        if any(word in user_input.lower() for word in ['done', 'complete', 'finished']):
            args['status'] = 'done'
        elif 'progress' in user_input.lower():
            args['status'] = 'in-progress'
        elif 'cancel' in user_input.lower():
            args['status'] = 'cancelled'
        
        return args
    
    def _extract_search_query(self, user_input: str) -> Dict[str, Any]:
        """Extract search query."""
        # Remove command keywords
        query = user_input.lower()
        for keyword in ['search for', 'find', 'look up', 'google']:
            query = query.replace(keyword, '').strip()
        
        return {'query': query}
    
    def _extract_code_search_args(self, user_input: str) -> Dict[str, Any]:
        """Extract code search arguments."""
        args = self._extract_search_query(user_input)
        
        # Extract file pattern if specified
        pattern_match = re.search(r'in\s+(\*\.\w+)\s+files', user_input, re.IGNORECASE)
        if pattern_match:
            args['file_pattern'] = pattern_match.group(1)
        
        return args