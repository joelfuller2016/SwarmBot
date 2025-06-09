# SwarmBot Configuration Analysis

## Actually Used Environment Variables

### Core LLM Configuration (src/config.py)
- `LLM_PROVIDER` - Default: "openai"
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- `GROQ_API_KEY`
- `AZURE_API_KEY`

### Auto-Prompt Settings (src/config.py)
- `AUTO_PROMPT_ENABLED` - Default: "false"
- `AUTO_PROMPT_MAX_ITERATIONS` - Default: "1"
- `AUTO_PROMPT_GOAL_DETECTION` - Default: "true"
- `AUTO_PROMPT_SAVE_STATE` - Default: "true"

### MCP Server API Keys (src/config.py)
- `GITHUB_PERSONAL_ACCESS_TOKEN` (also as `GITHUB_TOKEN`)
- `BRAVE_API_KEY`
- `N8N_HOST`
- `N8N_API_KEY`
- `ELEVENLABS_API_KEY`
- `EXA_API_KEY`

### Additional API Keys (referenced in code)
- `PERPLEXITY_API_KEY` (in .env.example but not in config.py)
- `AZURE_OPENAI_ENDPOINT` (in src/utils/api_validator.py)

## Hardcoded Settings (Not Configurable)

### Database Settings
- Database path: `"swarmbot_chats.db"` (src/database/chat_storage.py:19)
- No retention days configuration
- No backup settings

### Logging Settings
- Log directory: `"logs/"` (src/utils/logging_config.py:16)
- No log level configuration via env
- No log rotation settings

### Enhanced Mode Settings
- Tool chain limit: `5` (src/enhanced_chat_session.py:26)
- Auto-execute confidence: `0.6` (src/enhanced_chat_session.py:129)
- Suggestion confidence: `0.4` (src/enhanced_chat_session.py:142)
- Default mode: `'enhanced'` (src/core/app.py:40)

### Other Hardcoded Values
- Session timeout: Not configured
- Rate limiting: Not implemented
- Debug mode: Only via command line `--debug`
- Performance profiling: Not implemented
- Security settings: Not configurable

## Settings That Were Added But Not Used
The following were in my proposed .env.example but are NOT used:
- LOG_LEVEL, LOG_TO_FILE, LOG_TO_CONSOLE, LOG_DIR
- LOG_MAX_SIZE, LOG_BACKUP_COUNT
- CHAT_DB_PATH, CHAT_DB_RETENTION_DAYS
- CHAT_DB_BACKUP_ENABLED, CHAT_DB_BACKUP_INTERVAL
- DEFAULT_MODE
- TOOL_CHAIN_LIMIT, TOOL_CONFIDENCE_THRESHOLD, TOOL_SUGGESTION_THRESHOLD
- MAX_ACTIVE_AGENTS, AGENT_TIMEOUT_SECONDS, AGENT_RETRY_ATTEMPTS
- MCP_SERVER_TIMEOUT, MCP_SERVER_RETRY_ATTEMPTS, MCP_SERVER_HEALTH_CHECK_INTERVAL
- DEBUG_MODE, SHOW_TOOL_CALLS, SHOW_LLM_TOKENS, PROFILE_PERFORMANCE
- ENABLE_RATE_LIMITING, RATE_LIMIT_REQUESTS
- SANITIZE_INPUTS, MASK_SENSITIVE_DATA

## Recommendations

1. **Use the simplified .env.example** - It only includes settings that are actually used
2. **For production use** - Consider making the hardcoded values configurable:
   - Database path and retention
   - Log levels and rotation
   - Confidence thresholds
   - Timeouts and limits
3. **Current state** - The app works fine with the existing configuration approach