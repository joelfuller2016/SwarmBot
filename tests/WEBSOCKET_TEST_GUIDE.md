# WebSocket Test Execution Guide

## Prerequisites
Ensure all required packages are installed:
```bash
pip install flask flask-socketio dash plotly dash-bootstrap-components
```

## Running All WebSocket Tests

### Method 1: Using the Test Suite Runner
```bash
cd C:\Users\joelf\OneDrive\Joels Files\Documents\GitHub\SwarmBot
python tests\test_websocket_suite.py
```

This will:
- Load all WebSocket test modules
- Execute all tests with detailed output
- Generate a comprehensive test report
- Exit with code 0 on success, 1 on failure

### Method 2: Running Individual Test Files

#### Event Tests
```bash
python -m unittest tests.test_websocket_events -v
```
Tests covered:
- Agent creation/deletion events
- Status change batching
- Task lifecycle events
- Performance metrics batching
- System alerts
- Connection handling
- Room management
- Heartbeat mechanism

#### Resilience Tests
```bash
python -m unittest tests.test_websocket_resilience -v
```
Tests covered:
- Connection state transitions
- Exponential backoff reconnection
- Message queuing when disconnected
- Fallback mode activation
- Connection quality monitoring
- Adaptive behavior
- Heartbeat timeout detection

#### Integration Tests
```bash
python -m unittest tests.test_websocket_integration -v
```
Tests covered:
- Full SwarmBot agent integration
- Event flow from agents to dashboard
- Task lifecycle with real components
- Concurrent event handling
- Dashboard component integration

#### Performance Tests
```bash
python -m unittest tests.test_websocket_performance -v
```
Tests covered:
- 1000 events/second throughput
- Concurrent emitter handling
- Batching efficiency
- Resource usage under load

## Expected Results

### Success Criteria
All tests must pass with 100% success rate:
```
----------------------------------------------------------------------
Ran 45 tests in 15.234s

OK
✅ ALL TESTS PASSED!
```

### Performance Benchmarks
The following performance metrics should be achieved:
- Event throughput: >1000 events/second
- Event delivery latency: <100ms
- Reconnection time: <5 seconds
- Memory usage: Stable under load
- CPU usage: <10% for normal operation

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'flask_socketio'
   ```
   Solution: Install missing dependencies
   ```bash
   pip install flask-socketio
   ```

2. **Connection Timeout**
   ```
   TimeoutError: WebSocket connection timeout
   ```
   Solution: Increase test timeouts or check network settings

3. **Port Already in Use**
   ```
   OSError: [Errno 98] Address already in use
   ```
   Solution: Kill processes using port 8050 or use different port

### Debug Mode
To run tests with debug output:
```bash
python -m unittest tests.test_websocket_events -v --debug
```

Or set environment variable:
```bash
set WEBSOCKET_DEBUG=1
python tests\test_websocket_suite.py
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: WebSocket Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run WebSocket tests
      run: |
        python tests/test_websocket_suite.py
```

## Test Coverage Report

To generate a coverage report:
```bash
pip install coverage
coverage run -m unittest discover tests/test_websocket_* -v
coverage report -m
coverage html
```

Expected coverage: 100% for all WebSocket modules.
