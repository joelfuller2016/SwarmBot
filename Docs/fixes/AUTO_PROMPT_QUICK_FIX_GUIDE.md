# How to Enable Auto-Prompt Functionality

## Current Status
**Auto-prompt is NOT working** even if you set `AUTO_PROMPT_ENABLED=true` in your .env file.

## Quick Fix Example

To make auto-prompt minimally functional, you would need to modify `src/enhanced_chat_session.py`:

### 1. Add imports at the top:
```python
from src.core.auto_prompt import AutoPromptSystem
```

### 2. In the `__init__` method, add:
```python
# Initialize auto-prompt if enabled
self.auto_prompt = None
if hasattr(servers[0].config, 'auto_prompt_enabled'):
    if servers[0].config.auto_prompt_enabled:
        self.auto_prompt = AutoPromptSystem()
        self.auto_iterations = 0
        self.max_iterations = servers[0].config.auto_prompt_max_iterations
```

### 3. In the `process_message` method, after getting LLM response:
```python
# Auto-prompt logic
if self.auto_prompt and self.auto_iterations < self.max_iterations:
    # Simple goal detection - check if response indicates more work needed
    continue_indicators = [
        "next step", "then we need to", "after that",
        "following this", "additionally", "furthermore"
    ]
    
    should_continue = any(indicator in llm_response.lower() 
                         for indicator in continue_indicators)
    
    if should_continue:
        self.auto_iterations += 1
        print(f"\n[AUTO-PROMPT] Continuing automatically ({self.auto_iterations}/{self.max_iterations})...")
        
        # Create continuation prompt
        continuation = "Continue with the next step of the task."
        
        # Process as if user said it
        self.conversation_history.append({"role": "user", "content": continuation})
        
        # Recursive call to process the continuation
        return await self.process_message(continuation)
```

## Why It Doesn't Work Now

1. **No Integration**: The `AutoPromptSystem` class exists but is never imported or used in chat sessions
2. **No Goal Detection**: There's no logic to determine if a task is complete
3. **No Continuation**: The bot doesn't know how to prompt itself

## Temporary Workaround

Until properly integrated, you can manually prompt the bot to continue:
- User: "Help me create a website"
- Bot: [provides first steps]
- User: "Continue" or "What's next?"
- Bot: [provides next steps]

## Full Implementation Requirements

For a production-ready auto-prompt system, you would need:
1. Sophisticated goal detection using NLP
2. Task state tracking
3. Context preservation between iterations  
4. Safety limits and user interruption handling
5. Progress indicators for the user
6. Integration with the task management system

## Summary

The auto-prompt configuration in `.env` currently does nothing because the feature isn't connected to the main chat flow. The code above shows the minimum changes needed to make it work at a basic level.