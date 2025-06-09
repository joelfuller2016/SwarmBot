# Launcher Migration Notice

The SwarmBot launcher system has been unified! 

## Old → New Mapping

| Old Command | New Command |
|-------------|-------------|
| `python main.py` | `python swarmbot.py standard` |
| `python enhanced_main.py` | `python swarmbot.py enhanced` |
| `python run_swarmbot.py` | `python swarmbot.py` |
| `scripts/start_swarmbot.bat` | `swarmbot.bat standard` |
| `scripts/start_enhanced.bat` | `swarmbot.bat enhanced` |
| `scripts/swarmbot_enhanced.bat` | `swarmbot.bat enhanced` |

## Benefits of Unified Launcher

1. **Single Entry Point**: No more confusion about which script to run
2. **Interactive Mode**: Helpful guidance for new users
3. **Built-in Help**: `python swarmbot.py --help` shows all options
4. **Requirements Check**: `python swarmbot.py --check` validates setup
5. **Clean Logs**: `python swarmbot.py --clean` removes old logs
6. **Better Error Messages**: Clear feedback on what went wrong

## Quick Start

```bash
# Interactive mode (recommended for new users)
python swarmbot.py

# Direct mode selection
python swarmbot.py enhanced

# Windows users
swarmbot.bat
```

All old launchers still work but will redirect to the new unified launcher.
