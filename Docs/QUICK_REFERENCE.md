# SwarmBot Automatic Tools - Quick Reference

## 🚀 Start Enhanced SwarmBot
```bash
python enhanced_main.py
# or
start_enhanced.bat
```

## 📝 Natural Language Commands

### File Operations
- **Read**: "Show me config.json" / "What's in README?"
- **Write**: "Create a new test.py file"
- **List**: "What files are in this folder?"
- **Search**: "Find all Python files"

### Task Management  
- **View**: "Show all tasks" / "What todos do I have?"
- **Next**: "What should I work on next?"
- **Update**: "Mark task 5 as done"
- **Add**: "Add new task: Fix login bug"

### Git Commands
- **Status**: "What changed?" / "Show git status"
- **Commit**: "Commit with message 'bug fix'"
- **Diff**: "Show what changed in main.py"

### Search
- **Code**: "Find all TODO comments"
- **Web**: "Search for Python best practices"
- **Files**: "Where is the config file?"

## 🎮 Special Commands
- `manual` - Toggle automatic mode on/off
- `tools` - Show all available tools
- `help` - Show detailed help
- `quit` - Exit SwarmBot

## 💡 Pro Tips

### Be Natural
❌ `{"tool": "read_file", "arguments": {"path": "test.py"}}`
✅ "Show me test.py"

### Chain Actions
"Show all tasks then mark the first one as done"
"Find errors in the code and show the files"

### Use Context
"Read the config file" → SwarmBot looks for config.*
"Show the main script" → SwarmBot finds main.*

### Confidence Levels
- 🟢 High (>60%): Auto-executes
- 🟡 Medium (40-60%): AI decides  
- 🔴 Low (<40%): Normal response

## 📊 Tool Categories

**File Ops**: read_file, write_file, list_directory, search_files
**Git**: git_status, git_commit, git_diff, git_log
**Tasks**: get_tasks, add_task, set_task_status, next_task
**Search**: web_search, search_code, grep
**GitHub**: create_issue, list_issues, create_pull_request
**Analysis**: sequential_thinking, code_reasoning
**Database**: read_query, write_query

## 🔗 Example Chains

1. **Code Review Flow**
   "Find all TODO comments and create GitHub issues for them"

2. **Task Workflow**
   "Show current task, mark it done, and get the next one"

3. **Debug Flow**
   "Search for errors, show the files, and create a bug report"

4. **Git Workflow**
   "Show changes, commit them, and create a pull request"

## ⚡ Quick Patterns

| You Say | SwarmBot Does |
|---------|---------------|
| "What's in X?" | read_file(X) |
| "Show all Y" | get_Y() |
| "Find Z" | search_*(Z) |
| "Create new A" | create_A() |
| "List B" | list_B() |

## 🛠️ Customization

Edit `tool_patterns.json` to:
- Add new keywords
- Adjust confidence scores
- Create new patterns
- Define tool chains

---
🎉 Enjoy natural tool usage with SwarmBot Enhanced!