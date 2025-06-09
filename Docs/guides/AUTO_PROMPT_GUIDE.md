# Auto-Prompt User Guide

## Overview
The Auto-Prompt feature enables SwarmBot to automatically continue multi-step tasks without requiring manual prompts from the user. When enabled, SwarmBot detects incomplete goals and continues working until the task is complete or the iteration limit is reached.

## How It Works

### Goal Detection
SwarmBot analyzes its responses for indicators that suggest more work is needed:
- Step-by-step instructions ("Step 1", "Step 2", "Next step")
- Planning phrases ("Here's the plan", "The approach is")
- Continuation indicators ("then we need to", "after that", "furthermore")
- Questions asking for permission ("Shall I continue?", "Should I proceed?")
- Incomplete endings ("...", "etc.", "and so on")

### Automatic Continuation
When an incomplete goal is detected:
1. SwarmBot generates an appropriate continuation prompt
2. The prompt is automatically added to the conversation
3. SwarmBot continues processing without user intervention
4. Visual indicator shows auto-prompt is active: `🔄 [AUTO-PROMPT 1/3]`

### Safety Limits
- Maximum iterations prevent infinite loops (default: 1, configurable)
- Each new user message resets the iteration counter
- Users can interrupt at any time with Ctrl+C

## Configuration

### Environment Variables (.env file)
```bash
# Enable/disable auto-prompt (default: false)
AUTO_PROMPT_ENABLED=true

# Maximum iterations (default: 1)
AUTO_PROMPT_MAX_ITERATIONS=3

# Enable goal detection (default: true)
AUTO_PROMPT_GOAL_DETECTION=true

# Save state between sessions (default: true)
AUTO_PROMPT_SAVE_STATE=true
```

### Command-Line Flags
Override .env settings with command-line flags:

```bash
# Enable auto-prompt for this session
swarmbot --auto-prompt

# Disable auto-prompt for this session
swarmbot --no-auto-prompt

# Set maximum iterations
swarmbot --auto-prompt-iterations 5

# Combine flags
swarmbot --auto-prompt --auto-prompt-iterations 10
```

## Examples

### Example 1: Code Refactoring
```
User: Help me refactor this messy Python file to follow best practices

SwarmBot: I'll help you refactor this Python file. Let me start by analyzing the current code structure to identify areas for improvement.

First step is to examine the file and identify the main issues...

🔄 [AUTO-PROMPT 1/3] Please continue with the next step.

Now I'll create a refactored version with the following improvements:
1. Proper function organization
2. Better variable naming
3. Added documentation...

🔄 [AUTO-PROMPT 2/3] Please continue with the next step.

Finally, let me add comprehensive tests for the refactored code...

Task completed! I've successfully refactored your Python file with improved structure, documentation, and tests.
```

### Example 2: Project Setup
```
User: Create a new React project with TypeScript, ESLint, and a component library

SwarmBot: I'll create a new React project with TypeScript, ESLint, and a component library. Here's my plan:
1. Initialize the React project with TypeScript
2. Configure ESLint with appropriate rules
3. Set up a component library structure
4. Create example components

Let me start by creating the project...

🔄 [AUTO-PROMPT 1/3] Please execute this plan.

[Creates project structure and files]

Now I'll configure ESLint for TypeScript and React...

🔄 [AUTO-PROMPT 2/3] Please continue with the next step.

[Sets up ESLint configuration]

Next, I'll create the component library structure...

🔄 [AUTO-PROMPT 3/3] Please continue with the next step.

[Creates component library]

All done! Your React project is set up with TypeScript, ESLint, and a component library.
```

## Best Practices

### When to Enable Auto-Prompt
- Complex multi-step tasks (refactoring, project setup, data analysis)
- Repetitive operations across multiple files
- Tasks with clear sequential steps
- When you want hands-free task completion

### When to Disable Auto-Prompt
- Exploratory conversations
- When you want to review each step before proceeding
- Tasks requiring user input at each stage
- When learning or debugging

### Optimal Settings
- **Small tasks**: 1-2 iterations
- **Medium tasks**: 3-5 iterations
- **Large tasks**: 5-10 iterations
- **Very complex tasks**: 10+ iterations (use with caution)

## Troubleshooting

### Auto-Prompt Not Working
1. Check if `AUTO_PROMPT_ENABLED=true` in .env
2. Verify you're using Enhanced mode (default)
3. Check iteration limit isn't too low
4. Ensure goal detection is enabled

### Too Many Iterations
- Reduce `AUTO_PROMPT_MAX_ITERATIONS`
- Use `--no-auto-prompt` flag temporarily
- Interrupt with Ctrl+C if needed

### Not Detecting Incomplete Goals
- Check if response contains completion phrases
- Ensure `AUTO_PROMPT_GOAL_DETECTION=true`
- Some tasks may naturally complete in one step

## Advanced Usage

### Combining with Tools
Auto-prompt works seamlessly with SwarmBot's automatic tool execution:
```
User: Analyze all Python files and fix any syntax errors

SwarmBot: I'll analyze all Python files and fix syntax errors. Let me start by finding all Python files...
[Executes search_files tool]

🔄 [AUTO-PROMPT 1/5] Please continue with the next step.

Found 15 Python files. Now I'll check each for syntax errors...
[Executes validation tools]

🔄 [AUTO-PROMPT 2/5] Please continue with the next step.

[Continues until all files are processed]
```

### State Persistence
When `AUTO_PROMPT_SAVE_STATE=true`, SwarmBot saves:
- Current task queue
- Iteration count
- Partial context
- Completion status

This allows resuming interrupted sessions.

## Safety and Control

### User Interruption
- Press Ctrl+C to interrupt auto-prompt
- Type 'quit' to exit completely
- New user input cancels current auto-prompt chain

### Monitoring Progress
- Watch the iteration counter: `[AUTO-PROMPT 2/5]`
- Each step is logged for review
- Full conversation history is maintained

### Prevention of Loops
- Hard limit on iterations
- Completion phrase detection
- Automatic stop when no progress detected

## Tips for Effective Use

1. **Be Specific**: Clear initial requests lead to better auto-prompt sequences
2. **Set Appropriate Limits**: Match iteration limit to task complexity
3. **Monitor Progress**: Watch the first few iterations to ensure correct direction
4. **Interrupt When Needed**: Don't hesitate to stop and redirect if needed
5. **Review Results**: Always review the final output for completeness

## Integration with Workflow

### Development Tasks
```bash
# Enable for coding session
swarmbot --auto-prompt --auto-prompt-iterations 10

# Disable for exploration
swarmbot --no-auto-prompt
```

### Batch Operations
Perfect for repetitive tasks:
- File conversions
- Code formatting
- Documentation generation
- Test creation

### Project Management
Combine with task management tools:
- Auto-complete task sequences
- Generate reports
- Update multiple items

## Conclusion

Auto-Prompt transforms SwarmBot from a conversational assistant into an autonomous task executor. Use it wisely to boost productivity while maintaining control over the process.