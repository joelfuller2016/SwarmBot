# TaskMaster-AI Integration Guide

This guide explains how to use TaskMaster-AI with SwarmBot for project management and task tracking.

## Overview

TaskMaster-AI is already initialized in your SwarmBot project. The `.taskmaster` directory contains:
- `config.json` - TaskMaster configuration
- `docs/` - Project documentation
- `reports/` - Analysis and complexity reports
- `tasks/` - Task files and tracking
- `templates/` - Task templates

## Using TaskMaster-AI through SwarmBot

### 1. Start SwarmBot
```bash
python main.py
# or
start_swarmbot.bat
```

### 2. Basic TaskMaster Commands

Once SwarmBot is running, you can use natural language to interact with TaskMaster:

#### Initialize a New Project (if needed)
```
You: Initialize taskmaster in my project directory
```

#### Parse a Product Requirements Document
```
You: Parse the PRD document in .taskmaster/docs/prd.txt and generate tasks
```

#### List All Tasks
```
You: Show me all tasks in the project
```

#### Get Next Task
```
You: What's the next task I should work on?
```

#### Update Task Status
```
You: Mark task 5 as completed
You: Set task 3 status to in-progress
```

#### Add New Tasks
```
You: Add a new task: Implement user authentication with JWT tokens
```

#### Expand Complex Tasks
```
You: Expand task 7 into subtasks
```

#### Analyze Project Complexity
```
You: Analyze the complexity of all pending tasks
```

## Advanced TaskMaster Features

### Task Dependencies
```
You: Add dependency - task 8 depends on task 5
You: Show me the dependency graph
```

### Research-Backed Task Generation
```
You: Use research to generate tasks for implementing a REST API with best practices
```

### Bulk Operations
```
You: Update all tasks starting from task 10 with new context about using TypeScript
You: Expand all pending tasks based on complexity analysis
```

### Progress Tracking
```
You: Show me the project progress and task completion rate
You: Generate a complexity report for all tasks
```

## TaskMaster File Structure

Your project already has TaskMaster initialized:

```
.taskmaster/
├── config.json         # TaskMaster configuration
├── docs/
│   └── prd.txt        # Place your PRD here
├── reports/
│   └── task-complexity-report.json
├── tasks/
│   ├── tasks.json     # Main task list
│   └── *.json         # Individual task files
└── templates/         # Task templates
```

## Example Workflow

1. **Create a PRD**:
   ```
   You: Create a PRD for a todo list application with user authentication, task CRUD operations, and categories
   ```

2. **Parse PRD to Generate Tasks**:
   ```
   You: Parse the PRD and generate 15 tasks for the todo list project
   ```

3. **Review and Expand Tasks**:
   ```
   You: Show me all tasks
   You: Analyze complexity of all tasks
   You: Expand tasks with complexity score above 7
   ```

4. **Start Working**:
   ```
   You: What's the next task to work on?
   You: Mark task 1 as in-progress
   ```

5. **Track Progress**:
   ```
   You: Show project progress
   You: List all completed tasks
   ```

## Tips for Effective Task Management

1. **Keep PRDs Detailed**: The more detailed your PRD, the better the task generation
2. **Use Dependencies**: Define task dependencies to ensure proper workflow
3. **Regular Updates**: Update task status as you work
4. **Expand Complex Tasks**: Break down high-complexity tasks into manageable subtasks
5. **Use Research Mode**: Enable research for technical tasks to get best practices

## Troubleshooting

If TaskMaster commands aren't working:

1. Check if the taskmaster-ai server is active:
   ```
   You: Show active servers
   ```

2. Verify TaskMaster is in the tools list:
   ```
   You: List all tools | search for task
   ```

3. Check the logs:
   - Look at `swarmbot.log` for errors
   - TaskMaster logs are in `.taskmaster/logs/`

## Integration with Other Tools

TaskMaster works well with other MCP servers:

- **GitHub**: Create issues from tasks
- **Code Reasoning**: Analyze implementation complexity
- **Sequential Thinking**: Plan task execution steps
- **Knowledge Graph**: Store project context and decisions