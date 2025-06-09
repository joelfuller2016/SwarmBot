#!/usr/bin/env python3
"""Quick test to verify the Test Executor is working"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.testing import TestExecutor, TestStatus
    print("✓ Successfully imported TestExecutor module")
    
    # Try to create an executor
    executor = TestExecutor()
    print("✓ Successfully created TestExecutor instance")
    
    # Test framework detection
    test_file = Path(__file__)
    framework = executor._detect_framework(test_file)
    print(f"✓ Framework detection working (detected: {framework})")
    
    # Test the summary generation
    summary = TestExecutor.generate_summary([])
    print("✓ Summary generation working")
    
    print("\nTest Executor module is working correctly!")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
