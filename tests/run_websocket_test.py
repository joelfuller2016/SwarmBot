# -*- coding: utf-8 -*-
"""Verify WebSocket tests are working"""
import unittest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

# Run a simple test
from tests.test_websocket_events import TestEventBatcher

# Create test suite
loader = unittest.TestLoader()
suite = loader.loadTestsFromTestCase(TestEventBatcher)

# Run tests
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

# Print summary
print(f"\nTests run: {result.testsRun}")
print(f"Failures: {len(result.failures)}")
print(f"Errors: {len(result.errors)}")
print(f"Success: {result.wasSuccessful()}")
