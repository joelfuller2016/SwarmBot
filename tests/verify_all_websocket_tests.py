# -*- coding: utf-8 -*-
"""Run sample WebSocket tests to verify fixes"""
import unittest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

# Import test classes
from tests.test_websocket_events import TestEventBatcher, TestWebSocketEvents
from tests.test_websocket_resilience import TestWebSocketResilience
from tests.test_websocket_integration import TestWebSocketIntegration
from tests.test_websocket_performance import TestWebSocketPerformance

# Test each module with one test
test_cases = [
    (TestEventBatcher, 'test_batch_timing'),
    (TestWebSocketEvents, 'test_connection_handling'),
    (TestWebSocketResilience, 'test_initial_state'),
    (TestWebSocketIntegration, 'test_dashboard_integration'),
    (TestWebSocketPerformance, 'test_metric_batching_efficiency')
]

print("Running sample tests from each WebSocket test module...\n")

for test_class, test_method in test_cases:
    print(f"Testing {test_class.__name__}.{test_method}...")
    suite = unittest.TestSuite()
    suite.addTest(test_class(test_method))
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print(f"  [PASSED]")
    else:
        print(f"  [FAILED]")
        if result.failures:
            print(f"    Failures: {result.failures}")
        if result.errors:
            print(f"    Errors: {result.errors}")
    print()

print("Test verification complete.")
