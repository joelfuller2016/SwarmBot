#!/bin/bash
# SwarmBot Unified Launcher for Unix/Linux/macOS
# Single entry point for all modes

# Set UTF-8 encoding
export PYTHONIOENCODING=utf-8
export PYTHONWARNINGS=ignore::ResourceWarning

# Check if we're in scripts directory and move to parent
if [ -f ../swarmbot.py ]; then
    cd ..
fi

# Check if swarmbot.py exists
if [ ! -f swarmbot.py ]; then
    echo
    echo "❌ ERROR: swarmbot.py not found!"
    echo "Please run this script from the SwarmBot directory."
    echo
    exit 1
fi

# Activate virtual environment if it exists
if [ -f venv/bin/activate ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
elif [ -f .venv/bin/activate ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Display header
echo
echo "============================================================"
echo "                 🤖 SwarmBot Launcher                      "
echo "============================================================"
echo

# Run SwarmBot with all arguments
python swarmbot.py "$@"

# Store exit code
EXIT_CODE=$?

# Check exit code
if [ $EXIT_CODE -ne 0 ]; then
    echo
    echo "❌ SwarmBot exited with an error."
    echo
fi

# Return the exit code
exit $EXIT_CODE
