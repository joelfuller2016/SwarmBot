# SwarmBot Immediate Action Plan - Priority Tasks

## 🚨 CRITICAL PATH TO FUNCTIONALITY

This document identifies the MINIMUM tasks required to make SwarmBot functional. Complete these in order before any other work.

## Day 1: LLM Foundation (8 hours)

### Morning (4 hours)
**Task #11: LLM Provider Connection Testing**
```bash
# Location: Create new file src/llm/client_factory.py
# Goal: Get at least ONE LLM provider working
```

1. Create LLM client factory:
```python
from groq import Groq
from anthropic import Anthropic
from openai import OpenAI

class LLMClientFactory:
    @staticmethod
    def create_client(provider: str, api_key: str):
        if provider == 'groq':
            return GroqClient(api_key)
        elif provider == 'anthropic':
            return AnthropicClient(api_key)
        elif provider == 'openai':
            return OpenAIClient(api_key)
        else:
            raise ValueError(f"Unknown provider: {provider}")
```

2. Test with simple prompt:
```python
client = LLMClientFactory.create_client('groq', os.getenv('GROQ_API_KEY'))
response = client.complete("Hello, are you working?")
print(response)
```

**Success Criteria**: Get response from at least ONE provider

### Afternoon (4 hours)
**Task #36: Create LLM Client Factory** (newly added)
- Implement proper abstraction layer
- Add error handling
- Create fallback mechanism
- Test all three providers

**Success Criteria**: All providers tested, fallback working

## Day 2: Basic Chat Loop (8 hours)

### Morning (4 hours)
**Task #13: Basic Chat Functionality**
```bash
# Location: Modify src/chat_session.py
# Goal: Create working conversation loop
```

1. Implement basic loop:
```python
async def run(self):
    print("SwarmBot ready. Type 'exit' to quit.")
    
    while True:
        user_input = input("> ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        try:
            # Process message through LLM
            response = await self.llm_client.complete(user_input)
            print(f"Bot: {response}")
        except Exception as e:
            print(f"Error: {e}")
            print("Bot: I encountered an error. Please try again.")
```

**Success Criteria**: Can have basic conversation

### Afternoon (4 hours)
**Task #37: Implement Chat Message Pipeline** (newly added)
- Add proper async handling
- Implement retry logic
- Add conversation history
- Format responses properly

**Success Criteria**: Robust chat with error recovery

## Day 3: MCP Server Activation (8 hours)

### Morning (4 hours)
**Task #7: MCP Server Installation and Testing**
```bash
# Test each server manually first
npx -y --package=task-master-ai task-master-ai
```

1. Test TaskMaster-AI server:
```python
# In a separate terminal
process = subprocess.Popen([
    'npx', '-y', '--package=task-master-ai', 'task-master-ai'
])
# Wait for it to start
time.sleep(5)
# Try to connect
```

**Success Criteria**: TaskMaster-AI server starts

### Afternoon (4 hours)
**Task #15: MCP Server Connection Management**
- Implement server startup in MCPServerManager
- Add basic connection validation
- Create server registry

**Success Criteria**: Can start and connect to MCP servers

## Day 4: Wire Everything Together (8 hours)

### Morning (4 hours)
**Task #38: Fix Enhanced Mode Routing** (newly added)
```python
# In swarmbot.py, fix this:
if args.mode == 'enhanced':
    from src.enhanced_chat_session import EnhancedChatSession
    session = EnhancedChatSession(llm_client, mcp_manager, config)
else:
    session = ChatSession(llm_client, config)
```

**Success Criteria**: Enhanced mode launches correctly

### Afternoon (4 hours)
**Task #14: Enhanced Mode with Auto-Tools**
- Connect tool matcher to enhanced session
- Test tool detection
- Verify auto-execution

**Success Criteria**: Tools detected and executed automatically

## Validation Checkpoints

### After Day 1:
```bash
python swarmbot.py
> Hello
# Should get LLM response
```

### After Day 2:
```bash
python swarmbot.py
> Tell me a joke
# Should have full conversation
```

### After Day 3:
```bash
python swarmbot.py --list-tools
# Should show TaskMaster tools
```

### After Day 4:
```bash
python swarmbot.py enhanced
> Show me all tasks
# Should auto-detect and execute get_tasks()
```

## Common Blockers & Solutions

### LLM Connection Issues
- **Problem**: API key not working
- **Solution**: Test in isolation first, check rate limits

### MCP Server Won't Start
- **Problem**: Node.js issues
- **Solution**: Test npx command manually, check PATH

### Import Errors
- **Problem**: Circular imports
- **Solution**: Use lazy imports, refactor if needed

### Enhanced Mode Crashes
- **Problem**: Missing dependencies
- **Solution**: Check all imports, verify tool matcher works

## Emergency Fallback Plan

If blocked on any task for >2 hours:
1. Skip to next task
2. Document the blocker
3. Create minimal mock/stub
4. Continue forward progress

## Success Metrics

**Minimum Viable Product (4 days)**:
- [ ] Can have basic chat conversation
- [ ] At least one LLM provider works
- [ ] TaskMaster-AI server connects
- [ ] Enhanced mode detects tools

**Full Functionality (2 weeks)**:
- [ ] All pending tasks complete
- [ ] 80%+ test coverage
- [ ] Documentation updated
- [ ] Production ready

## Daily Standup Questions

1. **What did I complete?**
   - List task numbers finished
   - Note any blockers resolved

2. **What am I working on?**
   - Current task number
   - Expected completion time

3. **What's blocking me?**
   - Technical issues
   - Missing dependencies
   - Need clarification

## Next Steps After MVP

Once basic functionality works:
1. Add comprehensive tests (Task #30)
2. Implement health checks (Task #39)
3. Add function discovery (Task #26)
4. Complete remaining features

---

**Remember**: Focus on getting SOMETHING working, not EVERYTHING perfect. Iterate and improve.