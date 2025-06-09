# SwarmBot Token Truncation Fix

## Problem Summary
SwarmBot was experiencing context truncation at 5923 tokens despite having a hardcoded limit of 4000 tokens in `src/core/context_manager.py`. This was causing:
- Loss of conversation history
- Truncation of tool definitions
- Inability to utilize modern LLM context windows (32K-200K tokens)

## Solution Implemented

### 1. Environment Variable Configuration
Added `MAX_CONTEXT_TOKENS` to the `.env` file:
```
MAX_CONTEXT_TOKENS=16000  # Maximum tokens for conversation context (default: 16000)
```

### 2. Configuration Class Update
Updated `src/config.py` to read the environment variable:
```python
# Context management configuration
self.max_context_tokens = int(os.getenv("MAX_CONTEXT_TOKENS", "4000"))
```

### 3. ChatSession Modifications
Modified `src/chat_session.py` to:
- Accept a `config` parameter in the constructor
- Pass `max_context_tokens` to ConversationContext

```python
def __init__(self, servers: List[Server], llm_client: LLMClient, config=None) -> None:
    # ... other initialization ...
    
    # Pass max_context_tokens from config if available
    if config and hasattr(config, 'max_context_tokens'):
        self.context_manager = ConversationContext(max_tokens=config.max_context_tokens)
    else:
        self.context_manager = ConversationContext()
```

### 4. App Integration
Updated `src/core/app.py` to pass the config object when creating chat sessions:
```python
chat_session = ChatSession(self.servers, llm_client, self.config)
```

### 5. EnhancedChatSession Update
Updated `src/enhanced_chat_session.py` to accept and pass the config parameter to the parent class.

### 6. Database Verification
Confirmed that `src/database/chat_storage.py` stores full conversations without truncation. SQLite TEXT columns can handle very large strings (up to 1 billion bytes).

## Benefits

1. **Increased Context Capacity**: SwarmBot can now handle 16,000 tokens by default (4x the previous limit)
2. **User Configurable**: Users can adjust `MAX_CONTEXT_TOKENS` based on their LLM provider:
   - GPT-4: Up to 128,000 tokens
   - Claude: Up to 200,000 tokens
   - Other providers: Set based on their limits
3. **No Tool Truncation**: All 56 MCP tools can be loaded without hitting token limits
4. **Future Proof**: As LLM context windows expand, users can simply update the environment variable
5. **Better Conversations**: Longer conversation history is preserved for better context understanding

## Configuration Guide

### Setting Custom Token Limits
Edit your `.env` file and set the desired limit:
```
MAX_CONTEXT_TOKENS=32000  # For 32K context window
MAX_CONTEXT_TOKENS=128000  # For GPT-4 Turbo
MAX_CONTEXT_TOKENS=200000  # For Claude
```

### Recommended Settings by Provider
- **OpenAI GPT-3.5**: 4,000 - 16,000 tokens
- **OpenAI GPT-4**: 8,000 - 128,000 tokens
- **Anthropic Claude**: 100,000 - 200,000 tokens
- **Google Gemini**: 32,000 - 1,000,000 tokens
- **Local Models**: Varies (typically 2,000 - 32,000)

### Performance Considerations
- **Memory Usage**: Larger context windows use more memory
- **Processing Time**: Context processing scales with O(n²) complexity
- **Cost**: More tokens = higher API costs for cloud providers

## Testing

### Manual Verification
1. Check environment variable: `echo %MAX_CONTEXT_TOKENS%`
2. Run SwarmBot and observe no truncation warnings
3. Load all tools with `tools` command
4. Have extended conversations without context loss

### Automated Tests
- `tests/test_database_no_truncation.py` - Verifies database storage
- `tests/verify_token_fix.py` - Comprehensive verification script

## Troubleshooting

### Issue: Still seeing truncation at 4000 tokens
**Solution**: Ensure `.env` file is in the project root and contains `MAX_CONTEXT_TOKENS=16000`

### Issue: Out of memory errors
**Solution**: Reduce `MAX_CONTEXT_TOKENS` to a lower value like 8000 or 12000

### Issue: Slow response times
**Solution**: Large contexts take longer to process. Consider reducing token limit if performance is critical.

## Migration Notes

### For Existing Users
1. Add `MAX_CONTEXT_TOKENS=16000` to your `.env` file
2. Restart SwarmBot
3. No other changes required - the system will automatically use the new limit

### For Developers
When creating new chat session types:
1. Accept `config` parameter in constructor
2. Pass config to parent class or ConversationContext
3. Use `config.max_context_tokens` for any token-related logic

## Future Enhancements
1. Dynamic token limit adjustment based on available memory
2. Token usage analytics and reporting
3. Intelligent context pruning strategies
4. Per-session token limit configuration
5. Context compression techniques

## References
- [Understanding LLM Context Windows](https://docs.anthropic.com/claude/docs/context-windows)
- [Token Counting Best Practices](https://platform.openai.com/docs/guides/tokens)
- [Managing Large Contexts Efficiently](https://arxiv.org/abs/2310.04677)