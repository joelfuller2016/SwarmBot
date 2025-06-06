# SwarmBot Quick Start Guide

## Prerequisites
- Python 3.10+
- Node.js 18+ (for MCP servers)
- Git
- API Keys: Anthropic, OpenAI, and/or Groq

## Initial Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
npm install -g @modelcontextprotocol/server-puppeteer
```

### 2. Configure Environment
Create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
```

### 3. Initialize Taskmaster
The project has already been initialized with taskmaster. Tasks have been generated from the PRD.

### 4. View Project Tasks
To see all generated tasks:
```bash
npx task-master-ai list
```

### 5. Start Development
To begin with the first task:
```bash
npx task-master-ai next
```

## Project Structure
```
SwarmBot/
├── .taskmaster/
│   ├── docs/
│   │   ├── prd.txt           # Product Requirements Document
│   │   └── project_plan.md   # Detailed Project Plan
│   ├── tasks/
│   │   └── tasks.json        # Generated task list
│   └── reports/              # Evolution logs and reports
├── main.py                   # Current MCP chatbot implementation
├── genesis_bootstrap_starter.py  # Self-evolution framework
├── servers_config.json       # MCP server configuration
└── requirements.txt          # Python dependencies
```

## Next Steps
1. Review the generated tasks in `.taskmaster/tasks/tasks.json`
2. Start with Task 1: Setup Development Environment
3. Use the genesis_bootstrap_starter.py as a reference for self-evolution
4. Follow the daily evolution cycle outlined in the project plan

## Daily Workflow
1. Check current task: `npx task-master-ai next`
2. Implement the task requirements
3. Mark complete: `npx task-master-ai complete [task-id]`
4. Generate evolution report
5. Plan next day's objectives

## Getting Help
- Review `.taskmaster/docs/project_plan.md` for detailed guidance
- Check task dependencies before starting new tasks
- Use chain-of-thought reasoning for complex decisions
- Maintain evolution logs for tracking progress