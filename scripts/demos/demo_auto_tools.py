#!/usr/bin/env python3
"""
SwarmBot Automatic Tools Demo
Demonstrates automatic tool detection and execution
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_main import ToolMatcher, Tool
from typing import List, Dict, Any


def create_mock_tools() -> List[Tool]:
    """Create mock tools for demonstration."""
    return [
        Tool("read_file", "Read contents of a file", {"properties": {"path": {"type": "string"}}}),
        Tool("write_file", "Write content to a file", {"properties": {"path": {"type": "string"}, "content": {"type": "string"}}}),
        Tool("list_directory", "List directory contents", {"properties": {"path": {"type": "string"}}}),
        Tool("get_tasks", "Get all tasks", {"properties": {}}),
        Tool("set_task_status", "Update task status", {"properties": {"id": {"type": "string"}, "status": {"type": "string"}}}),
        Tool("web_search", "Search the web", {"properties": {"query": {"type": "string"}}}),
        Tool("git_status", "Show git status", {"properties": {}}),
        Tool("search_code", "Search in code files", {"properties": {"pattern": {"type": "string"}}})
    ]


def demo_tool_matching():
    """Demonstrate automatic tool matching."""
    print("🚀 SwarmBot Automatic Tool Matching Demo")
    print("=" * 60)
    
    # Create matcher and mock tools
    matcher = ToolMatcher()
    tools = create_mock_tools()
    
    # Test cases
    test_cases = [
        "Show me the contents of config.json",
        "What tasks do I have?",
        "Mark task 5 as completed",
        "Search for information about Python decorators",
        "What files have changed in git?",
        "Find all TODO comments in the code",
        "Create a new file called test.py",
        "List all files in the current directory",
        "What should I work on next?",
        "Commit changes with message 'bug fix'"
    ]
    
    print("\n📝 Testing Natural Language → Tool Mapping:\n")
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"{i}. Input: '{test_input}'")
        
        # Find matching tools
        matches = matcher.find_matching_tools(test_input, tools)
        
        if matches:
            best_match = matches[0]
            print(f"   ✅ Tool: {best_match.tool_name}")
            print(f"   📊 Confidence: {best_match.confidence:.2%}")
            print(f"   📝 Arguments: {best_match.suggested_args}")
            print(f"   💡 Reasoning: {best_match.reasoning}")
            
            # Show auto-execution decision
            if best_match.confidence > 0.6:
                print(f"   🤖 Action: Would execute automatically")
            elif best_match.confidence > 0.4:
                print(f"   🤔 Action: Would suggest to LLM")
            else:
                print(f"   ⏭️  Action: Would skip (low confidence)")
        else:
            print(f"   ❌ No matching tools found")
        
        print()
    
    # Show pattern analysis
    print("\n📊 Pattern Analysis:")
    print("=" * 60)
    
    # Analyze a specific case
    test_input = "Find all Python files with error handling"
    print(f"\nDetailed analysis for: '{test_input}'")
    
    matches = matcher.find_matching_tools(test_input, tools)
    if matches:
        for i, match in enumerate(matches[:3], 1):
            print(f"\n{i}. {match.tool_name} (confidence: {match.confidence:.2%})")
            print(f"   - {match.reasoning}")


def show_chaining_examples():
    """Show examples of automatic tool chaining."""
    print("\n\n🔗 Tool Chaining Examples:")
    print("=" * 60)
    
    chaining_examples = [
        {
            "input": "Show me all tasks and then mark the completed ones as done",
            "chain": [
                {"tool": "get_tasks", "arguments": {}},
                {"tool": "set_task_status", "arguments": {"id": "[from_previous]", "status": "done"}}
            ]
        },
        {
            "input": "Find error logs and show me the most recent one",
            "chain": [
                {"tool": "search_code", "arguments": {"pattern": "error|Error|ERROR"}},
                {"tool": "read_file", "arguments": {"path": "[most_recent_from_search]"}}
            ]
        },
        {
            "input": "Check what changed and commit it with a good message",
            "chain": [
                {"tool": "git_status", "arguments": {}},
                {"tool": "git_diff", "arguments": {}},
                {"tool": "git_commit", "arguments": {"message": "[auto_generated]"}}
            ]
        }
    ]
    
    for example in chaining_examples:
        print(f"\n🧑 Input: '{example['input']}'")
        print("🤖 Tool Chain:")
        for i, step in enumerate(example['chain'], 1):
            print(f"   {i}. {step['tool']}({step['arguments']})")


def show_configuration():
    """Show configuration options."""
    print("\n\n⚙️  Configuration:")
    print("=" * 60)
    
    print("""
Confidence Thresholds:
- Auto-execute: > 60% confidence
- Suggest to LLM: 40-60% confidence  
- Ignore: < 40% confidence

Customization:
1. Edit 'tool_patterns.json' to add/modify patterns
2. Adjust confidence thresholds
3. Add new argument extractors
4. Define custom chaining patterns

Tips for Better Matching:
- Use keywords from the pattern definitions
- Include context words (file, task, git, etc.)
- Be specific with names and identifiers
- Use natural language, not commands
""")


def main():
    """Run the demonstration."""
    demo_tool_matching()
    show_chaining_examples()
    show_configuration()
    
    print("\n✨ To use automatic tools in SwarmBot, run:")
    print("   python enhanced_main.py")
    print("\nEnjoy natural language tool execution! 🎉")


if __name__ == "__main__":
    main()