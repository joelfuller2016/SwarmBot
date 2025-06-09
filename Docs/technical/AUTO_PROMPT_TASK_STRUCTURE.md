# Auto-Prompt Implementation Tasks

## Task Status Update
- **Task #31**: Changed from `done` to `in-progress`
- **Task #34**: New task created for complete implementation

## Task Hierarchy

### Task #31: Add Auto-Prompt Configuration Setting (In-Progress)
Original task that was incorrectly marked as done. Currently has:
- Configuration reading implemented ✅
- AutoPromptSystem class created ✅
- Integration missing ❌

#### Subtask 31.1: Integrate AutoPromptSystem into chat sessions
- Status: Pending
- Basic integration needed before full implementation

### Task #34: Complete Auto-Prompt System Integration (Pending)
Comprehensive task to properly implement auto-prompt functionality.

#### Subtask 34.1: Initialize AutoPromptSystem in chat sessions
- Import and initialize AutoPromptSystem in ChatSession and EnhancedChatSession
- Check config.auto_prompt_enabled and create instance if enabled
- Store configuration values for use during chat

#### Subtask 34.2: Implement goal detection logic
- Analyze LLM responses for continuation indicators
- Detect incomplete task markers
- Return confidence score for task incompleteness
- Respect config.auto_prompt_goal_detection setting

#### Subtask 34.3: Add automatic continuation mechanism
- Check if task is incomplete after each response
- Generate appropriate continuation prompts
- Track iteration count vs max_iterations
- Add visual indicators for auto-prompt actions
- Handle user interruption

#### Subtask 34.4: Add command-line flags for auto-prompt
- Add `--auto-prompt` flag to enable/disable
- Add `--auto-prompt-iterations` for max iterations
- Override config values when flags provided
- Update help text and validation output

#### Subtask 34.5: Test and document auto-prompt system
- Create unit tests for goal detection
- Integration tests for complete flow
- Update README and create AUTO_PROMPT_GUIDE.md
- Document configuration options and best practices

## Implementation Order
1. First complete subtask 31.1 (basic integration)
2. Then work through task 34 subtasks in order
3. Each subtask builds on the previous one

## Expected Outcome
When complete, users will be able to:
- Enable auto-prompt via .env or command-line
- Have the bot automatically continue multi-step tasks
- Configure iteration limits for safety
- See clear indicators when auto-prompt is active
- Interrupt if needed