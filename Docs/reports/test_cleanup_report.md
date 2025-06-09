# SwarmBot Test Cleanup Report

Generated: 2025-06-09 16:25:42

Total tests analyzed: 60

## Summary
- Files to delete: 4
- Files to fix: 11
- Files to keep: 3
- Files to consolidate: 10

## Files to Delete

### archive\test_websocket_events_old.py
**Reason:** Archived WebSocket test - use newer version

### archive\test_websocket_integration_old.py
**Reason:** Archived WebSocket test - use newer version

### archive\test_websocket_performance_old.py
**Reason:** Archived WebSocket test - use newer version

### archive\test_websocket_resilience_old.py
**Reason:** Archived WebSocket test - use newer version

## Files to Fix

### test_asyncio_cleanup_fix.py
**Reason:** Fix verification test needs documentation
**Action:** Add docstring explaining what fix is being verified

### test_asyncio_fix.py
**Reason:** Fix verification test needs documentation
**Action:** Add docstring explaining what fix is being verified

### test_circular_import_fix.py
**Reason:** Fix verification test needs documentation
**Action:** Add docstring explaining what fix is being verified

### test_config_key_fix.py
**Reason:** Fix verification test needs documentation
**Action:** Add docstring explaining what fix is being verified

### test_fixes.py
**Reason:** Fix verification test needs documentation
**Action:** Add docstring explaining what fix is being verified

### test_list_tools_fix.py
**Reason:** Fix verification test needs documentation
**Action:** Add docstring explaining what fix is being verified

### test_logging_fix.py
**Reason:** Fix verification test needs documentation
**Action:** Add docstring explaining what fix is being verified

### test_token_fix.py
**Reason:** Fix verification test needs documentation
**Action:** Add docstring explaining what fix is being verified

### test_tool_object_fix.py
**Reason:** Fix verification test needs documentation
**Action:** Add docstring explaining what fix is being verified

### verify_token_fix.py
**Reason:** Fix verification test needs documentation
**Action:** Add docstring explaining what fix is being verified

### mcp/__init__.py
**Reason:** Conflicts with 'mcp' package imports
**Action:** Rename mcp directory to test_mcp or mcp_tests

## Files to Keep

### test_chat_basic.py
**Reason:** Core functionality test

### test_minimal.py
**Reason:** Core functionality test

### test_swarmbot_basic.py
**Reason:** Core functionality test

## Files to Consolidate

### manual_websocket_test.py
**Reason:** Covered by test_websocket_suite.py
**Action:** Verify coverage in suite then delete

### run_websocket_test.py
**Reason:** Covered by test_websocket_suite.py
**Action:** Verify coverage in suite then delete

### test_websocket_events.py
**Reason:** Covered by test_websocket_suite.py
**Action:** Verify coverage in suite then delete

### test_websocket_integration.py
**Reason:** Covered by test_websocket_suite.py
**Action:** Verify coverage in suite then delete

### test_websocket_performance.py
**Reason:** Covered by test_websocket_suite.py
**Action:** Verify coverage in suite then delete

### test_websocket_resilience.py
**Reason:** Covered by test_websocket_suite.py
**Action:** Verify coverage in suite then delete

### run_all_tests.py
**Reason:** Multiple runner scripts - consolidate into single test runner
**Action:** Create unified test_runner.py then delete

### run_websocket_test.py
**Reason:** Multiple runner scripts - consolidate into single test runner
**Action:** Create unified test_runner.py then delete

### run_websocket_tests.py
**Reason:** Multiple runner scripts - consolidate into single test runner
**Action:** Create unified test_runner.py then delete

### run_ui_test.py
**Reason:** Multiple runner scripts - consolidate into single test runner
**Action:** Create unified test_runner.py then delete

## Recommendations

1. **Rename mcp directory**: Rename `tests/mcp/` to `tests/mcp_tests/` to avoid import conflicts
2. **Create unified test runner**: Replace multiple run_*.py scripts with single test_runner.py
3. **Add pytest configuration**: Create pytest.ini for consistent test execution
4. **Document test purpose**: Add docstrings to all test files explaining their purpose
5. **Consolidate WebSocket tests**: Merge individual WebSocket tests into the test suite