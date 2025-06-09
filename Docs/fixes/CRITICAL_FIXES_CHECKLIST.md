# SwarmBot Critical Fix Checklist

## 🚨 STOP! Fix These First (Nothing Works Without Them)

### 1. Basic Chat Loop (Task #13)
```python
# Location: src/core/chat_session.py
# Add to ChatSession class:

async def chat_loop(self):
    """Main conversation loop - THIS IS MISSING!"""
    while True:
        user_input = input("> ")
        if user_input.lower() in ['exit', 'quit']:
            break
        
        # Send to LLM (THIS DOESN'T EXIST)
        response = await self.llm_client.complete(user_input)
        
        # Display response
        print(response)
```

### 2. LLM Client Initialization (Task #11)
```python
# Location: Create new file src/llm/client_factory.py

def create_llm_client(config):
    """Create LLM client - THIS FILE DOESN'T EXIST!"""
    provider = config.get('llm_provider', 'groq')
    
    if provider == 'groq':
        from groq import Groq
        return Groq(api_key=config['GROQ_API_KEY'])
    # Add other providers...
```

### 3. MCP Server Startup (Task #7)
```python
# Location: src/mcp/server_manager.py
# Add to MCPServerManager:

async def start_servers(self):
    """Start MCP servers - THIS METHOD DOESN'T RUN!"""
    for name, config in self.servers_config.items():
        print(f"Starting {name}...")
        # This needs to actually start the process!
        process = subprocess.Popen(config['command'], config['args'])
        self.processes[name] = process
```

### 4. Wire Up Enhanced Mode (Task #14)
```python
# Location: swarmbot.py, line ~45
# CURRENT (WRONG):
session = ChatSession(config)  # Always uses basic!

# SHOULD BE:
if args.mode == 'enhanced':
    from src.enhanced_chat_session import EnhancedChatSession
    session = EnhancedChatSession(llm_client, mcp_manager, config)
else:
    session = ChatSession(config)
```

## 🧪 Quick Test Commands

### Test 1: Can it chat?
```bash
python swarmbot.py
> Hello
# Should respond, currently crashes
```

### Test 2: Are MCP servers running?
```bash
python swarmbot.py --list-tools
# Should show TaskMaster tools, currently shows nothing
```

### Test 3: Does enhanced mode work?
```bash
python swarmbot.py enhanced
> Show me all tasks
# Should auto-call get_tasks(), currently does nothing
```

## 📍 File Locations Needing Fixes

1. `swarmbot.py` - Line 45: Wrong session class
2. `src/core/chat_session.py` - Missing chat_loop()
3. `src/llm/` - Entire folder missing!
4. `src/mcp/server_manager.py` - start_servers() not called
5. `src/enhanced_chat_session.py` - Not connected to main

## ⏱️ Time Estimates

- Fix basic chat loop: 2-3 hours
- Add LLM clients: 2-3 hours  
- Start MCP servers: 3-4 hours
- Wire up enhanced mode: 1-2 hours
- Basic testing: 2-3 hours

**Total: 1-2 days to get basic functionality working**

## 🎯 Success Criteria

You'll know it's working when:
1. ✅ `python swarmbot.py` lets you chat with the bot
2. ✅ `--list-tools` shows TaskMaster-AI tools
3. ✅ Enhanced mode auto-detects "show tasks" intent
4. ✅ TaskMaster tools actually execute

## ⚠️ Don't Work On These Until Core Is Fixed

- ❌ WebSocket improvements (already works)
- ❌ Agent learning (Task #29)
- ❌ Function discovery (Task #26)  
- ❌ Editor integration (Task #28)
- ❌ Advanced testing (Task #30)

**Fix the basics first!**
