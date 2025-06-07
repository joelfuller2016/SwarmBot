# SwarmBot Automatic Tool Usage Guide

This guide explains how to get SwarmBot to automatically detect and use tools based on natural language requests.

## 🚀 Quick Start

Run the enhanced version with automatic tool detection:

```bash
python enhanced_main.py
```

## 🤖 Automatic Tool Detection

SwarmBot Enhanced includes intelligent tool matching that:
- Analyzes your natural language requests
- Automatically selects appropriate tools
- Executes them without explicit commands
- Chains multiple tools for complex tasks

## 📝 Natural Language Examples

### File Operations

Instead of: `{"tool": "read_file", "arguments": {"path": "config.json"}}`

Just say:
- "Show me config.json"
- "What's in the README file?"
- "Read main.py"
- "Display the contents of test.txt"

### Task Management

Instead of: `{"tool": "get_tasks", "arguments": {}}`

Just say:
- "Show me all tasks"
- "What tasks do I have?"
- "List my todos"
- "What should I work on next?"

### Git Operations

Instead of: `{"tool": "git_status", "arguments": {}}`

Just say:
- "What files have changed?"
- "Show git status"
- "What's modified in the repo?"
- "Commit these changes with message 'bug fix'"

### Search Operations

Instead of: `{"tool": "search_code", "arguments": {"pattern": "TODO"}}`

Just say:
- "Find all TODO comments"
- "Search for the calculate_total function"
- "Look for uses of the User class"
- "Find Python files with 'import requests'"

### Web Search

Instead of: `{"tool": "web_search", "arguments": {"query": "Python tutorials"}}`

Just say:
- "Search for Python tutorials"
- "Find information about machine learning"
- "Look up the latest AI news"
- "Google SwarmBot documentation"

## 🔗 Automatic Tool Chaining

SwarmBot can automatically chain multiple tools. Examples:

### Example 1: Code Analysis
"Find all Python files with errors and show me the first one"

This automatically:
1. Uses `search_code` to find files with "error" or "Error"
2. Uses `read_file` to display the first match

### Example 2: Task Workflow
"Show me the next task and mark the current one as done"

This automatically:
1. Uses `get_tasks` to see current status
2. Uses `set_task_status` to mark current task
3. Uses `next_task` to get the next one

### Example 3: Git Workflow
"Show what changed and commit it with a descriptive message"

This automatically:
1. Uses `git_status` to see changes
2. Uses `git_diff` to show details
3. Uses `git_commit` with an auto-generated message

## 🎯 Confidence Levels

SwarmBot uses confidence scoring:

- **High Confidence (>0.6)**: Executes automatically
- **Medium Confidence (0.4-0.6)**: Suggests to LLM
- **Low Confidence (<0.4)**: Falls back to normal LLM response

## ⚙️ Configuration Options

### Toggle Automatic Mode
```
You: manual
SwarmBot: Automatic mode: DISABLED
```

### Show Tool Categories
```
You: tools
SwarmBot: [Shows tools organized by category]
```

## 📊 Tool Matching Patterns

SwarmBot recognizes patterns like:

### Keywords
- Read/Show/Display → `read_file`
- Create/Write/Save → `write_file`
- List/Contents → `list_directory`
- Search/Find/Look → Various search tools
- Task/Todo → Task management tools

### Context Words
- File/Document → File operations
- Git/Repo/Commit → Git tools
- Task/Project → Task management
- Web/Online → Web search

### Argument Extraction
SwarmBot automatically extracts:
- File paths from quotes or extensions
- Task IDs from "task 5" patterns
- Commit messages from quotes
- Search queries by removing command words

## 💡 Pro Tips

1. **Be Natural**: Just describe what you want in plain English
2. **Use Context**: Mention specific files, task numbers, or search terms
3. **Chain Commands**: Describe multi-step workflows naturally
4. **Trust the Bot**: It will ask for clarification if needed

## 🔧 Advanced Features

### Custom Tool Patterns

Add new patterns to `ToolMatcher.tool_patterns`:

```python
'your_tool': {
    'keywords': ['action', 'words'],
    'context': ['domain', 'specific'],
    'examples': ['do something with data']
}
```

### Argument Extractors

Add custom extractors to `ToolMatcher.arg_extractors`:

```python
def _extract_your_args(self, user_input: str) -> Dict[str, Any]:
    # Custom extraction logic
    return {'arg': 'value'}
```

## 📈 Performance Tips

1. **Specific Requests**: More specific = higher confidence
2. **Include Context**: "the config file" vs "config.json"
3. **Natural Flow**: "Show me X then do Y" for chaining
4. **Keywords Help**: Use natural keywords for better matching

## 🚨 Troubleshooting

### Tools Not Auto-Executing

1. Check confidence threshold (default: 0.6)
2. Verify tool is loaded: `tools` command
3. Check if manual mode is on: `manual` to toggle
4. Look at logs for matching scores

### Wrong Tool Selected

1. Be more specific in your request
2. Use explicit tool names if needed
3. Check tool patterns configuration
4. Report ambiguous cases for improvement

## 📝 Example Session

```
🚀 SwarmBot Enhanced - Automatic Tool Mode
============================================================

✅ Initialized with 15 servers and 127 tools
🤖 Automatic tool execution: ENABLED

🧑 You: Show me what tasks I have

🤖 SwarmBot: [Auto-tool mode] 
✅ Automatically selected based on: Keywords: 2/5 | Context: 2/2

📋 Tasks:
⏳ [1] Set up authentication system
    Implement JWT-based authentication...
⏳ [2] Create user dashboard
    Design and implement the main user dashboard...
✅ [3] Database schema design
    Create initial database schema...

💬 You have 2 pending tasks. Task #1 "Set up authentication system" 
appears to be the next priority based on dependencies.

🧑 You: Read the auth config file

🤖 SwarmBot: [Auto-tool mode]
✅ Found and executed read_file tool

📄 File Content:
{
  "jwt": {
    "secret": "your-secret-key",
    "expiry": "24h"
  },
  "providers": ["local", "google", "github"]
}

💬 The authentication config shows JWT setup with 24-hour token expiry 
and support for local, Google, and GitHub auth providers.

🧑 You: Search for where jwt secret is used

🤖 SwarmBot: [Auto-tool mode]
✅ Searching for JWT secret usage...

Found 3 occurrences:
1. src/auth/jwt.js:15 - const secret = config.jwt.secret
2. src/middleware/auth.js:8 - jwt.verify(token, config.jwt.secret)
3. tests/auth.test.js:23 - mockSecret: 'test-secret'

💬 The JWT secret is used in the auth module for token creation,
in middleware for verification, and mocked in tests.
```

## 🎉 Enjoy Automatic Tool Usage!

SwarmBot Enhanced makes working with MCP tools natural and effortless. Just describe what you want, and let the AI handle the rest!