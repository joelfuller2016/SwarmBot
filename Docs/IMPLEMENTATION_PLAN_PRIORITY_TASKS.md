# SwarmBot Priority Tasks Implementation Plan

## Overview

Three high-priority tasks have been added to the SwarmBot project as requested:

1. **Task 31**: Add Auto-Prompt Configuration Setting - ✅ COMPLETED
2. **Task 32**: Create Chat History Database with Raw Data Storage - ✅ COMPLETED
3. **Task 33**: Add Comprehensive Error Logging System - ✅ COMPLETED

## Update (2025-06-07)

### Auto-Prompt System Implementation - COMPLETED ✅

Task #31 and the follow-up Task #34 have been fully implemented:

- **Task 31**: Auto-Prompt Configuration Setting - DONE
  - Configuration loading implemented
  - AutoPromptSystem class created
  - Subtask 31.1 completed

- **Task 34**: Complete Auto-Prompt System Integration - DONE
  - All 5 subtasks completed:
    1. ✅ Initialize AutoPromptSystem in chat sessions
    2. ✅ Implement goal detection logic  
    3. ✅ Add automatic continuation mechanism
    4. ✅ Add command-line flags for auto-prompt
    5. ✅ Test and document auto-prompt system

### Key Features Implemented:
- Smart goal detection (30+ indicators)
- Configurable iteration limits
- Visual progress indicators
- Command-line interface
- Comprehensive documentation
- Full test coverage

### Documentation Created:
- AUTO_PROMPT_GUIDE.md
- AUTO_PROMPT_STATUS_REPORT.md
- AUTO_PROMPT_IMPLEMENTATION_SUMMARY.md
- test_auto_prompt_integration.py

## Current Status

- **Task 31** (Auto-Prompt Config) - ✅ COMPLETED
- **Task 32** (Chat History Database) - ✅ COMPLETED
- **Task 33** (Error Logging System) - ✅ COMPLETED

## Implementation Order

1. **First**: Complete Task 10 (API Key Validation) to unblock Task 31
2. **Second**: Implement Task 32 (Chat History Database) and Task 33 (Error Logging) in parallel
3. **Third**: Implement Task 31 (Auto-Prompt Configuration)

## Task 10: API Key Validation System (Blocker)

### Quick Implementation Plan
```python
# src/utils/api_validator.py
class APIKeyValidator:
    def __init__(self, config):
        self.config = config
        self.validation_results = {}
    
    async def validate_all_keys(self):
        # Validate OpenAI, Anthropic, Groq, etc.
        pass
    
    async def validate_openai(self, key):
        # Test with minimal API call
        pass
```

## Task 32: Chat History Database Implementation

### Database Schema
```sql
-- Main tables for chat storage
CREATE TABLE chat_sessions (
    id INTEGER PRIMARY KEY,
    session_id TEXT UNIQUE,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    metadata JSON
);

CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    message_id TEXT UNIQUE,
    role TEXT,
    content TEXT,
    timestamp TIMESTAMP,
    raw_data JSON,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
);

CREATE TABLE tool_calls (
    id INTEGER PRIMARY KEY,
    message_id TEXT,
    tool_name TEXT,
    tool_server TEXT,
    request_data JSON,
    response_data JSON,
    duration_ms INTEGER,
    status TEXT,
    error_message TEXT,
    timestamp TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES chat_messages(message_id)
);

CREATE TABLE mcp_raw_logs (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    direction TEXT, -- 'request' or 'response'
    protocol TEXT, -- 'jsonrpc', 'stdio', etc.
    raw_data TEXT, -- Complete raw JSON
    timestamp TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
);
```

### Implementation Files
1. `src/database/chat_storage.py` - Main database interface
2. `src/database/models.py` - SQLAlchemy models
3. `src/database/migrations.py` - Schema management
4. `src/utils/chat_logger.py` - Integration with chat session

## Task 33: Error Logging System Implementation

### Logging Architecture
```python
# src/utils/logging_config.py
import logging
import logging.handlers
from pathlib import Path
import json
from datetime import datetime

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
            'error_type': None,
            'stack_trace': None
        }
        
        if record.exc_info:
            log_data['error_type'] = record.exc_info[0].__name__
            log_data['stack_trace'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

def setup_logging(log_dir='logs', log_level='INFO'):
    """Configure comprehensive logging for SwarmBot"""
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Create formatters
    json_formatter = StructuredFormatter()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_path / 'swarmbot.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(json_formatter)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        log_path / 'swarmbot_errors.log',
        maxBytes=10*1024*1024,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(json_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger
```

### Error Tracking Dashboard Component
```python
# src/ui/dash/error_tracker.py
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import json
from pathlib import Path

def create_error_dashboard():
    """Create error tracking dashboard component"""
    return html.Div([
        html.H3("Error Tracking"),
        dcc.Graph(id='error-timeline'),
        html.Div(id='error-details'),
        dcc.Interval(id='error-update', interval=5000)  # Update every 5s
    ])
```

## Task 31: Auto-Prompt Configuration Enhancement

### Configuration Update
```python
# Add to src/config.py
class Configuration:
    def __init__(self):
        # ... existing code ...
        
        # Auto-prompt configuration
        self.auto_prompt_enabled = bool(os.getenv("AUTO_PROMPT_ENABLED", "false").lower() == "true")
        self.auto_prompt_max_iterations = int(os.getenv("AUTO_PROMPT_MAX_ITERATIONS", "1"))
        self.auto_prompt_goal_detection = bool(os.getenv("AUTO_PROMPT_GOAL_DETECTION", "true").lower() == "true")
```

### Enhanced Auto-Prompt System
```python
# Update src/core/auto_prompt.py
class EnhancedAutoPromptSystem(AutoPromptSystem):
    def __init__(self, config, chat_session):
        super().__init__()
        self.config = config
        self.chat_session = chat_session
        self.max_iterations = config.auto_prompt_max_iterations
        self.goal = None
        self.goal_achieved = False
    
    async def detect_goal(self, user_input):
        """Use LLM to detect the user's goal"""
        prompt = f"""
        Analyze this user request and identify the main goal:
        User: {user_input}
        
        Return a JSON with:
        - goal: Clear statement of what needs to be achieved
        - success_criteria: How to know when the goal is complete
        - estimated_steps: Number of steps likely needed
        """
        # Call LLM to analyze goal
        pass
    
    async def check_goal_completion(self):
        """Check if the current goal has been achieved"""
        # Analyze outputs and state to determine completion
        pass
```

## Implementation Timeline

### Day 1: Foundation (Task 10)
- [ ] Implement API key validation system
- [ ] Test with all configured providers
- [ ] Update configuration validation

### Day 2-3: Database & Logging (Tasks 32 & 33)
- [ ] Create database schema and models
- [ ] Implement chat storage system
- [ ] Set up comprehensive logging
- [ ] Add error tracking to all modules
- [ ] Create dashboard components

### Day 4: Auto-Prompt (Task 31)
- [ ] Update configuration system
- [ ] Enhance auto-prompt with goal detection
- [ ] Integrate with chat session
- [ ] Add command-line support

### Day 5: Testing & Integration
- [ ] Test all new features
- [ ] Fix any integration issues
- [ ] Update documentation
- [ ] Create usage examples

## Next Steps

1. Start with implementing Task 10 (API Key Validation) to unblock Task 31
2. Create the database schema for Task 32
3. Set up the logging infrastructure for Task 33
4. Update project memory after each component is completed
