# Circular Import Fix for SwarmBot

## Issue
There was a circular import between:
- `src/core/app.py` → imports `EnhancedChatSession`
- `src/enhanced_chat_session.py` → imports from `src.core.auto_prompt`
- `src/__init__.py` → imports `EnhancedChatSession`

## Solution Applied

1. **Moved import to function level in `app.py`**:
   - Removed `EnhancedChatSession` from top-level imports
   - Import it only when needed inside the `run_chat_session` method

2. **Temporarily disabled import in `src/__init__.py`**:
   - Commented out the `EnhancedChatSession` import
   - This prevents the circular dependency at package initialization

## How to Run

### Option 1: Regular SwarmBot (Chat Mode)
```bash
python swarmbot.py
```

### Option 2: Dashboard UI
```bash
# Using the --ui flag
python swarmbot.py --ui

# Or using the direct launcher
python scripts/launchers/dashboard.py

# Or using the new launcher script
python launch_dashboard.py
```

## Dashboard Access
Once launched, open your browser to: http://localhost:8050

## If Issues Persist
1. Ensure all dependencies are installed:
   ```bash
   pip install dash plotly dash-bootstrap-components dash-extensions psutil
   ```

2. Use the `launch_dashboard.py` script which bypasses the import issues entirely

## Next Steps
A more permanent fix would involve restructuring the imports to avoid the circular dependency, possibly by:
- Moving `AutoPromptSystem` to a different module
- Using lazy imports throughout
- Restructuring the package hierarchy
