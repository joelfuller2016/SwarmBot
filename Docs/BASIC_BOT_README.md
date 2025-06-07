# SwarmBot Basic - Getting Started

## Quick Start

### 1. Test Your Setup
First, verify your environment is configured correctly:
```bash
python test_setup.py
```

This will check:
- Python version
- Environment variables (.env file)
- API connectivity to Groq

### 2. Run the Basic Bot
Once the test passes, run the basic chatbot:
```bash
python swarmbot_basic.py
```

### 3. Chat Commands
- Type anything to chat with SwarmBot
- Type `reset` to clear conversation history
- Type `quit` or `exit` to stop the bot

## Troubleshooting

### API Key Issues
If you get API key errors:
1. Check your `.env` file exists
2. Ensure `GROQ_API_KEY` is set correctly
3. Verify the key is valid at https://console.groq.com/

### Connection Issues
If you can't connect to Groq:
1. Check your internet connection
2. Try a different model (update in swarmbot_basic.py)
3. Check Groq service status

## Next Steps
Once the basic bot is working:
1. Move on to Task 1: Setup Development Environment
2. Begin implementing MCP server integration
3. Start the evolution journey!

## Files Created
- `swarmbot_basic.py` - Simple chatbot without MCP complexity
- `test_setup.py` - Environment and API testing script
- This README file for quick reference