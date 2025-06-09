# SwarmBot Test Executor Module

## Overview

The Test Executor module provides a comprehensive framework for executing and analyzing test files in the SwarmBot project. It supports both pytest and unittest frameworks and provides detailed execution information including output capture, timing, and test counts.

## Features

- **Multi-framework support**: Automatically detects and executes both pytest and unittest tests
- **Detailed results**: Captures stdout, stderr, exit codes, and execution time
- **Test parsing**: Extracts test counts (passed, failed, skipped) from output
- **Timeout handling**: Prevents hanging tests from blocking execution
- **Batch execution**: Execute single files, multiple files, or entire directories
- **Progress tracking**: Real-time progress updates during execution
- **Summary generation**: Comprehensive statistics and summaries
- **JSON export**: Save results in machine-readable format

## Installation

The module is part of the SwarmBot project and requires no additional installation beyond the project dependencies.

## Usage

### Python API

```python
from src.testing import TestExecutor, TestStatus

# Initialize executor
executor = TestExecutor(project_root="/path/to/project", timeout=300)

# Execute a single test
result = executor.execute_test("tests/test_example.py")
print(f"Status: {result.status.value}")
print(f"Tests run: {result.test_count}")
print(f"Execution time: {result.execution_time}s")

# Execute all tests in a directory
results = executor.execute_directory("tests/", pattern="test_*.py")

# Generate summary
summary = TestExecutor.generate_summary(results)
print(f"Total files: {summary['total_files']}")
print(f"Passed: {summary['passed_files']}")
print(f"Failed: {summary['failed_files']}")
```

### Command Line Interface

```bash
# Execute a single test file
python -m src.testing.cli tests/test_config.py

# Execute all tests in a directory
python -m src.testing.cli --directory tests/

# Execute with custom timeout
python -m src.testing.cli --timeout 60 tests/test_slow.py

# Save results to JSON
python -m src.testing.cli --output results.json tests/

# Execute with verbose output
python -m src.testing.cli -v tests/
```

### Test Audit Script

```bash
# Run complete test audit
python scripts/audit_tests.py
```

## Test Result Structure

Each test execution produces a `TestResult` object with the following attributes:

- `file_path`: Path to the test file
- `status`: Execution status (PASSED, FAILED, ERROR, TIMEOUT, SKIPPED, NOT_FOUND)
- `exit_code`: Process exit code
- `stdout`: Captured standard output
- `stderr`: Captured standard error
- `execution_time`: Execution time in seconds
- `error_message`: Human-readable error message (if applicable)
- `test_count`: Total number of tests in the file
- `passed_count`: Number of passed tests
- `failed_count`: Number of failed tests
- `skipped_count`: Number of skipped tests
- `framework`: Detected test framework (pytest, unittest, unknown)

## Test Status Types

- `PASSED`: All tests passed successfully
- `FAILED`: One or more tests failed
- `ERROR`: Test execution error (e.g., syntax error, import error)
- `TIMEOUT`: Test execution exceeded timeout limit
- `SKIPPED`: No tests were collected/run
- `NOT_FOUND`: Test file does not exist

## Configuration

The executor can be configured with:

- `project_root`: Root directory for test execution (affects import paths)
- `timeout`: Maximum execution time per test file in seconds (default: 300)

## Examples

### Running Test Audit

```python
# scripts/audit_tests.py
executor = TestExecutor()
results = executor.execute_directory("tests/", recursive=True)

# Analyze results
for result in results:
    if result.status == TestStatus.FAILED:
        print(f"Failed: {result.file_path}")
        print(f"  Error: {result.error_message}")
```

### Custom Progress Tracking

```python
def progress_callback(current, total, result):
    symbol = "✓" if result.status == TestStatus.PASSED else "✗"
    print(f"[{current}/{total}] {symbol} {result.file_path}")

results = executor.execute_tests(test_files, progress_callback=progress_callback)
```

## Integration with Task System

This module fulfills Task 100 in the SwarmBot taskmaster system: "Implement Test Execution Module". It provides the foundation for the test audit workflow by enabling systematic execution and analysis of all project tests.

## Next Steps

With the Test Executor in place, the next tasks in the test audit workflow are:

1. Task 101: Develop Test Analysis Module - Analyze failures and identify patterns
2. Task 102: Implement Test Documentation Extractor - Extract test purpose and coverage
3. Tasks 103-112: Audit specific test categories using this executor

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the project root is set correctly so Python can find project modules
2. **Timeout Issues**: Increase the timeout for slow tests or investigate why tests are hanging
3. **Framework Detection**: The module auto-detects frameworks, but you can override by using specific test runners

### Debug Mode

Enable verbose output in the CLI with `-v` flag to see detailed error messages for failed tests.
