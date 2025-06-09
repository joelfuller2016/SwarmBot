# SwarmBot Priority Features Integration Guide

## Overview

This guide explains how to use the three new high-priority features added to SwarmBot:

1. **Auto-Prompt Configuration** - Allows the bot to self-prompt based on goals
2. **Chat History Database** - Stores all interactions with raw MCP data
3. **Comprehensive Error Logging** - Structured logging with error tracking

## 1. Auto-Prompt Configuration

### Configuration
Add these settings to your `.env` file:

```bash
# Auto-prompt settings
AUTO_PROMPT_ENABLED=true
AUTO_PROMPT_MAX_ITERATIONS=5
AUTO_PROMPT_GOAL_DETECTION=true
AUTO_PROMPT_SAVE_STATE=true
```

### Usage in Code
```python
from src.config import Configuration
from src.core.auto_prompt import EnhancedAutoPromptSystem

# Initialize configuration
config = Configuration()

# Check if auto-prompt is enabled
if config.auto_prompt_enabled:
    auto_prompt = EnhancedAutoPromptSystem(config, chat_session)
    auto_prompt.max_iterations = config.auto_prompt_max_iterations
    
    # Detect goal from user input
    goal = await auto_prompt.detect_goal(user_input)
    
    # Run auto-prompt system
    await auto_prompt.run()
```

## 2. Chat History Database

### Initialize Database
```python
from src.database import ChatDatabase, ChatLogger

# Create database instance
db = ChatDatabase("swarmbot_chats.db")

# Create a new session
session_id = f"session_{datetime.now().timestamp()}"
db.create_session(session_id, "openai", {"user": "example"})

# Create logger for the session
chat_logger = ChatLogger(db, session_id)
```

### Log Messages and Tool Calls
```python
# Log user message
user_msg_id = chat_logger.log_user_message("How's the weather?")

# Log tool call
import time
start_time = time.time()

# Make tool call
response = await tool.execute(params)

# Calculate duration
duration_ms = int((time.time() - start_time) * 1000)

# Log the tool call
chat_logger.log_tool_call(
    user_msg_id, 
    "weather_search", 
    "brave",
    request={"query": "weather today"},
    response=response,
    duration_ms=duration_ms
)

# Log MCP protocol data
chat_logger.log_mcp_request("brave", "search", {"query": "weather"})
chat_logger.log_mcp_response("brave", "search", response)

# Log assistant response
assistant_msg_id = chat_logger.log_assistant_message("The weather is sunny!")
```

### Query Chat History
```python
# Search messages
results = db.search_messages("weather")

# Get all messages from a session
messages = db.get_session_messages(session_id)

# Export session to JSON
db.export_session(session_id, "session_export.json")

# Get recent sessions
sessions = db.get_sessions(limit=10)
```

## 3. Comprehensive Error Logging

### Setup Logging
```python
from src.utils.logging_config import setup_logging, get_logger, log_errors

# Initialize logging system
setup_logging(
    log_level="INFO",
    log_to_file=True,
    log_to_console=True,
    log_dir="logs"
)

# Get a logger for your module
logger = get_logger(__name__)
```

### Using Logging Decorators
```python
from src.utils.logging_config import log_errors, log_async_errors

# Automatic error logging for sync functions
@log_errors()
def process_data(data):
    # Any exceptions will be automatically logged
    return data.process()

# Automatic error logging for async functions
@log_async_errors()
async def fetch_data(url):
    # Exceptions logged with full context
    async with aiohttp.ClientSession() as session:
        return await session.get(url)
```

### Using LoggingMixin
```python
from src.utils.logging_config import LoggingMixin

class MyAgent(LoggingMixin):
    def process(self):
        self.log_info("Starting process", task_id="123")
        
        try:
            # Do work
            result = self.perform_task()
            self.log_info("Task completed", result=result)
        except Exception as e:
            self.log_error("Task failed", exc_info=True, task_id="123")
            raise
```

### Error Tracking Dashboard
```python
from src.utils.logging_config import error_tracker

# Get error summary for dashboard
error_summary = error_tracker.get_error_summary()
print(f"Total errors: {error_summary['total_errors']}")
print(f"Error types: {error_summary['error_types']}")

# Get recent errors
recent_errors = error_tracker.get_recent_errors(count=10)
```

## Complete Integration Example

Here's how all three features work together:

```python
import asyncio
from datetime import datetime
from src.config import Configuration
from src.database import ChatDatabase, ChatLogger
from src.utils.logging_config import setup_logging, get_logger, log_async_errors
from src.core.auto_prompt import EnhancedAutoPromptSystem
from src.chat_session import ChatSession

# Setup logging
setup_logging(log_level="INFO")
logger = get_logger(__name__)

# Initialize components
config = Configuration()
db = ChatDatabase()
session_id = f"session_{datetime.now().timestamp()}"

@log_async_errors()
async def run_chat_with_auto_prompt():
    """Run a chat session with all new features enabled"""
    
    # Create session in database
    db.create_session(session_id, config.llm_provider, {
        "auto_prompt": config.auto_prompt_enabled,
        "started_at": datetime.utcnow().isoformat()
    })
    
    # Create chat logger
    chat_logger = ChatLogger(db, session_id)
    
    # Initialize chat session
    chat_session = ChatSession(servers, llm_client)
    await chat_session.initialize_servers()
    
    # Get user input
    user_input = "Analyze the SwarmBot codebase and create a summary report"
    
    # Log user message
    msg_id = chat_logger.log_user_message(user_input)
    logger.info("User message received", session_id=session_id, message_id=msg_id)
    
    # Check if auto-prompt is enabled
    if config.auto_prompt_enabled:
        logger.info("Auto-prompt enabled, detecting goal...")
        
        # Create auto-prompt system
        auto_prompt = EnhancedAutoPromptSystem(config, chat_session)
        
        # Detect goal
        goal = await auto_prompt.detect_goal(user_input)
        logger.info("Goal detected", goal=goal)
        
        # Run auto-prompt
        try:
            await auto_prompt.run()
            logger.info("Auto-prompt completed successfully")
        except Exception as e:
            logger.error("Auto-prompt failed", exc_info=True)
            raise
    else:
        # Normal single-prompt execution
        response = await chat_session.process_message(user_input)
        chat_logger.log_assistant_message(response)
    
    # End session
    db.end_session(session_id)
    logger.info("Session completed", session_id=session_id)

# Run the integrated system
if __name__ == "__main__":
    asyncio.run(run_chat_with_auto_prompt())
```

## Environment Variables

Add these to your `.env` file:

```bash
# Auto-prompt configuration
AUTO_PROMPT_ENABLED=true
AUTO_PROMPT_MAX_ITERATIONS=5
AUTO_PROMPT_GOAL_DETECTION=true
AUTO_PROMPT_SAVE_STATE=true

# Logging configuration
LOG_LEVEL=INFO
LOG_TO_FILE=true
LOG_TO_CONSOLE=true
LOG_DIR=logs

# Database configuration
CHAT_DB_PATH=swarmbot_chats.db
CHAT_DB_RETENTION_DAYS=30
```

## Testing the Features

### Test Auto-Prompt
```bash
python -m src.core.auto_prompt
```

### Test Database
```bash
python -m src.database.chat_storage
```

### Test Logging
```bash
python -m src.utils.logging_config
```

## Monitoring and Analysis

1. **Check Logs**: Look in the `logs/` directory for:
   - `swarmbot.json` - All structured logs
   - `swarmbot_errors.log` - Error-only logs

2. **Query Database**: Use SQLite browser or Python scripts to analyze:
   - Chat patterns
   - Tool usage statistics
   - Error frequencies
   - Performance metrics

3. **Dashboard Integration**: The error tracking data can be displayed in the existing Dash dashboard at `http://localhost:8050`

## Next Steps

1. Test the API key validator: `python -m src.utils.api_validator`
2. Integrate chat logging into existing chat session
3. Add error handling decorators to all agent classes
4. Create dashboard components for error tracking
5. Test auto-prompt with various goals
