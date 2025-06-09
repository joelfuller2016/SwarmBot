"""
Test Execution Module for SwarmBot Test Suite Audit

This module provides functionality to execute test files and capture their results,
including stdout, stderr, exit codes, and execution time.
"""

import subprocess
import sys
import time
import json
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue
import re
import os


class TestStatus(Enum):
    """Test execution status"""
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"
    NOT_FOUND = "not_found"


@dataclass
class TestResult:
    """Container for test execution results"""
    file_path: str
    status: TestStatus
    exit_code: Optional[int]
    stdout: str
    stderr: str
    execution_time: float
    error_message: Optional[str] = None
    test_count: Optional[int] = None
    passed_count: Optional[int] = None
    failed_count: Optional[int] = None
    skipped_count: Optional[int] = None
    framework: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['status'] = self.status.value
        return result


class TestExecutor:
    """
    Executes test files and captures their results.
    
    Supports both pytest and unittest frameworks and provides
    detailed execution information including output capture and timing.
    """
    
    def __init__(self, project_root: Optional[str] = None, timeout: int = 300):
        """
        Initialize the test executor.
        
        Args:
            project_root: Root directory of the project (defaults to current directory)
            timeout: Maximum execution time per test file in seconds (default: 300)
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.timeout = timeout
        self.python_executable = sys.executable
        
    def _detect_framework(self, file_path: Path) -> str:
        """
        Detect which testing framework a file uses.
        
        Args:
            file_path: Path to the test file
            
        Returns:
            'pytest', 'unittest', or 'unknown'
        """
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            return 'unknown'
        
        # Check for pytest-specific imports or decorators
        pytest_patterns = [
            r'import pytest',
            r'from pytest import',
            r'@pytest\.',
            r'pytest\.',
        ]
        
        for pattern in pytest_patterns:
            if re.search(pattern, content):
                return 'pytest'
        
        # Check for unittest-specific imports or classes
        unittest_patterns = [
            r'import unittest',
            r'from unittest import',
            r'class\s+\w+\s*\(.*unittest\.TestCase\)',
            r'class\s+\w+\s*\(.*TestCase\)',
        ]
        
        for pattern in unittest_patterns:
            if re.search(pattern, content):
                return 'unittest'
        
        # Default to pytest if we see test_ functions
        if re.search(r'def\s+test_\w+', content):
            return 'pytest'
            
        return 'unknown'

    def _parse_pytest_output(self, output: str) -> Dict[str, Optional[int]]:
        """
        Parse pytest output to extract test counts.
        
        Args:
            output: The stdout from pytest execution
            
        Returns:
            Dictionary with test counts
        """
        counts = {
            'test_count': None,
            'passed_count': None,
            'failed_count': None,
            'skipped_count': None
        }
        
        # Look for pytest summary line (e.g., "1 passed, 2 failed, 3 skipped in 0.5s")
        summary_pattern = r'(\d+)\s+passed|(\d+)\s+failed|(\d+)\s+skipped|(\d+)\s+error'
        
        passed_match = re.search(r'(\d+)\s+passed', output)
        failed_match = re.search(r'(\d+)\s+failed', output)
        skipped_match = re.search(r'(\d+)\s+skipped', output)
        error_match = re.search(r'(\d+)\s+error', output)
        
        if passed_match:
            counts['passed_count'] = int(passed_match.group(1))
        if failed_match:
            counts['failed_count'] = int(failed_match.group(1))
        if skipped_match:
            counts['skipped_count'] = int(skipped_match.group(1))
        
        # Calculate total count
        total = 0
        if counts['passed_count'] is not None:
            total += counts['passed_count']
        if counts['failed_count'] is not None:
            total += counts['failed_count']
        if counts['skipped_count'] is not None:
            total += counts['skipped_count']
        if error_match:
            total += int(error_match.group(1))
            
        if total > 0:
            counts['test_count'] = total
            
        return counts
    
    def _parse_unittest_output(self, output: str) -> Dict[str, Optional[int]]:
        """
        Parse unittest output to extract test counts.
        
        Args:
            output: The stdout from unittest execution
            
        Returns:
            Dictionary with test counts
        """
        counts = {
            'test_count': None,
            'passed_count': None,
            'failed_count': None,
            'skipped_count': None
        }
        
        # Look for unittest summary line (e.g., "Ran 5 tests in 0.001s")
        ran_match = re.search(r'Ran\s+(\d+)\s+test', output)
        if ran_match:
            counts['test_count'] = int(ran_match.group(1))
        
        # Check for OK (all passed)
        if re.search(r'\nOK\s*$', output.strip()):
            counts['passed_count'] = counts['test_count']
            counts['failed_count'] = 0
            counts['skipped_count'] = 0
        else:
            # Look for FAILED (failures=X, errors=Y)
            failures_match = re.search(r'failures=(\d+)', output)
            errors_match = re.search(r'errors=(\d+)', output)
            skipped_match = re.search(r'skipped=(\d+)', output)
            
            failed_total = 0
            if failures_match:
                failed_total += int(failures_match.group(1))
            if errors_match:
                failed_total += int(errors_match.group(1))
                
            counts['failed_count'] = failed_total
            
            if skipped_match:
                counts['skipped_count'] = int(skipped_match.group(1))
            else:
                counts['skipped_count'] = 0
                
            # Calculate passed count
            if counts['test_count'] is not None and counts['failed_count'] is not None:
                passed = counts['test_count'] - counts['failed_count']
                if counts['skipped_count'] is not None:
                    passed -= counts['skipped_count']
                counts['passed_count'] = max(0, passed)
        
        return counts
    
    def _run_with_timeout(self, cmd: List[str], cwd: Path, timeout: int) -> tuple:
        """
        Run a command with timeout.
        
        Args:
            cmd: Command to execute
            cwd: Working directory
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (stdout, stderr, return_code, timed_out)
        """
        result_queue = queue.Queue()
        
        def run_command():
            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(cwd),
                    text=True,
                    env=os.environ.copy()
                )
                
                stdout, stderr = process.communicate(timeout=timeout)
                result_queue.put((stdout, stderr, process.returncode, False))
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                result_queue.put((stdout, stderr, -1, True))
            except Exception as e:
                result_queue.put(("", str(e), -1, False))
        
        thread = threading.Thread(target=run_command)
        thread.daemon = True
        thread.start()
        thread.join(timeout + 5)  # Give a bit extra time for cleanup
        
        if thread.is_alive():
            # Thread is still running, something went very wrong
            return "", "Test execution thread hung", -1, True
            
        try:
            return result_queue.get(block=False)
        except queue.Empty:
            return "", "Failed to get test results", -1, True

    def execute_test(self, test_file: Union[str, Path]) -> TestResult:
        """
        Execute a single test file and capture results.
        
        Args:
            test_file: Path to the test file to execute
            
        Returns:
            TestResult object containing execution details
        """
        test_path = Path(test_file)
        
        # Check if file exists
        if not test_path.exists():
            return TestResult(
                file_path=str(test_path),
                status=TestStatus.NOT_FOUND,
                exit_code=None,
                stdout="",
                stderr=f"Test file not found: {test_path}",
                execution_time=0.0,
                error_message=f"File not found: {test_path}"
            )
        
        # Detect testing framework
        framework = self._detect_framework(test_path)
        
        # Prepare command based on framework
        if framework == 'pytest':
            cmd = [self.python_executable, "-m", "pytest", "-v", str(test_path)]
        elif framework == 'unittest':
            cmd = [self.python_executable, "-m", "unittest", str(test_path)]
        else:
            # Try running as a regular Python script
            cmd = [self.python_executable, str(test_path)]
        
        # Record start time
        start_time = time.time()
        
        # Execute the test with timeout
        stdout, stderr, exit_code, timed_out = self._run_with_timeout(
            cmd, self.project_root, self.timeout
        )
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Determine status
        if timed_out:
            status = TestStatus.TIMEOUT
            error_message = f"Test execution timed out after {self.timeout} seconds"
        elif exit_code == 0:
            status = TestStatus.PASSED
            error_message = None
        elif exit_code == 5:  # pytest exit code for no tests collected
            status = TestStatus.SKIPPED
            error_message = "No tests found in file"
        else:
            status = TestStatus.FAILED
            error_message = f"Test execution failed with exit code {exit_code}"
        
        # Parse output for test counts
        counts = {}
        if framework == 'pytest':
            counts = self._parse_pytest_output(stdout)
        elif framework == 'unittest':
            counts = self._parse_unittest_output(stdout)
        
        # Create result object
        result = TestResult(
            file_path=str(test_path),
            status=status,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            execution_time=execution_time,
            error_message=error_message,
            framework=framework,
            **counts
        )
        
        return result
    
    def execute_tests(self, test_files: List[Union[str, Path]], 
                     progress_callback: Optional[callable] = None) -> List[TestResult]:
        """
        Execute multiple test files.
        
        Args:
            test_files: List of test files to execute
            progress_callback: Optional callback function(current, total, result)
                              called after each test execution
            
        Returns:
            List of TestResult objects
        """
        results = []
        total = len(test_files)
        
        for i, test_file in enumerate(test_files):
            result = self.execute_test(test_file)
            results.append(result)
            
            if progress_callback:
                progress_callback(i + 1, total, result)
                
        return results
    
    def execute_directory(self, directory: Union[str, Path], 
                         pattern: str = "test_*.py",
                         recursive: bool = True,
                         progress_callback: Optional[callable] = None) -> List[TestResult]:
        """
        Execute all test files in a directory matching a pattern.
        
        Args:
            directory: Directory to search for test files
            pattern: Glob pattern for test files (default: "test_*.py")
            recursive: Whether to search recursively (default: True)
            progress_callback: Optional callback function
            
        Returns:
            List of TestResult objects
        """
        dir_path = Path(directory)
        
        if not dir_path.exists():
            raise ValueError(f"Directory not found: {dir_path}")
        
        # Find all test files
        if recursive:
            test_files = list(dir_path.rglob(pattern))
        else:
            test_files = list(dir_path.glob(pattern))
        
        # Filter out __pycache__ directories
        test_files = [f for f in test_files if '__pycache__' not in str(f)]
        
        # Sort for consistent ordering
        test_files.sort()
        
        return self.execute_tests(test_files, progress_callback)
    
    @staticmethod
    def generate_summary(results: List[TestResult]) -> Dict[str, Any]:
        """
        Generate a summary of test results.
        
        Args:
            results: List of TestResult objects
            
        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'total_files': len(results),
            'passed_files': 0,
            'failed_files': 0,
            'error_files': 0,
            'timeout_files': 0,
            'skipped_files': 0,
            'not_found_files': 0,
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'total_execution_time': 0.0,
            'frameworks': {}
        }
        
        for result in results:
            # File-level counts
            if result.status == TestStatus.PASSED:
                summary['passed_files'] += 1
            elif result.status == TestStatus.FAILED:
                summary['failed_files'] += 1
            elif result.status == TestStatus.ERROR:
                summary['error_files'] += 1
            elif result.status == TestStatus.TIMEOUT:
                summary['timeout_files'] += 1
            elif result.status == TestStatus.SKIPPED:
                summary['skipped_files'] += 1
            elif result.status == TestStatus.NOT_FOUND:
                summary['not_found_files'] += 1
            
            # Test-level counts
            if result.test_count is not None:
                summary['total_tests'] += result.test_count
            if result.passed_count is not None:
                summary['passed_tests'] += result.passed_count
            if result.failed_count is not None:
                summary['failed_tests'] += result.failed_count
            if result.skipped_count is not None:
                summary['skipped_tests'] += result.skipped_count
                
            # Execution time
            summary['total_execution_time'] += result.execution_time
            
            # Framework usage
            if result.framework:
                summary['frameworks'][result.framework] = summary['frameworks'].get(result.framework, 0) + 1
        
        return summary
