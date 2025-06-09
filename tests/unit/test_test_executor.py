"""
Unit tests for the Test Executor module
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import json
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.testing import TestExecutor, TestResult, TestStatus


class TestTestExecutor(unittest.TestCase):
    """Test cases for the TestExecutor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.executor = TestExecutor(project_root=self.temp_dir)
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_detect_framework_pytest(self):
        """Test framework detection for pytest files."""
        test_file = Path(self.temp_dir) / "test_pytest.py"
        test_file.write_text("""
import pytest

def test_something():
    assert True
    
@pytest.mark.skip
def test_skipped():
    pass
""")
        
        framework = self.executor._detect_framework(test_file)
        self.assertEqual(framework, 'pytest')
    
    def test_detect_framework_unittest(self):
        """Test framework detection for unittest files."""
        test_file = Path(self.temp_dir) / "test_unittest.py"
        test_file.write_text("""
import unittest

class TestExample(unittest.TestCase):
    def test_something(self):
        self.assertTrue(True)
""")
        
        framework = self.executor._detect_framework(test_file)
        self.assertEqual(framework, 'unittest')
    
    def test_detect_framework_unknown(self):
        """Test framework detection for unknown files."""
        test_file = Path(self.temp_dir) / "not_a_test.py"
        test_file.write_text("""
# Just a regular Python file
print("Hello, world!")
""")
        
        framework = self.executor._detect_framework(test_file)
        self.assertEqual(framework, 'unknown')
    
    def test_execute_passing_test(self):
        """Test executing a passing test."""
        test_file = Path(self.temp_dir) / "test_pass.py"
        test_file.write_text("""
def test_passing():
    assert 1 + 1 == 2
""")
        
        result = self.executor.execute_test(test_file)
        
        self.assertEqual(result.status, TestStatus.PASSED)
        self.assertEqual(result.exit_code, 0)
        self.assertIsNotNone(result.execution_time)
        self.assertGreater(result.execution_time, 0)
    
    def test_execute_failing_test(self):
        """Test executing a failing test."""
        test_file = Path(self.temp_dir) / "test_fail.py"
        test_file.write_text("""
def test_failing():
    assert 1 + 1 == 3  # This will fail
""")
        
        result = self.executor.execute_test(test_file)
        
        self.assertEqual(result.status, TestStatus.FAILED)
        self.assertNotEqual(result.exit_code, 0)
        self.assertTrue(result.stderr or result.stdout)  # Should have error output
    
    def test_execute_nonexistent_file(self):
        """Test executing a non-existent file."""
        test_file = Path(self.temp_dir) / "does_not_exist.py"
        
        result = self.executor.execute_test(test_file)
        
        self.assertEqual(result.status, TestStatus.NOT_FOUND)
        self.assertIsNone(result.exit_code)
        self.assertIn("not found", result.error_message.lower())
    
    def test_parse_pytest_output(self):
        """Test parsing pytest output."""
        output = """
============================= test session starts ==============================
collected 3 items

test_example.py::test_one PASSED                                         [ 33%]
test_example.py::test_two FAILED                                         [ 66%]
test_example.py::test_three SKIPPED                                      [100%]

=========================== short test summary info ============================
FAILED test_example.py::test_two - assert False
=================== 1 failed, 1 passed, 1 skipped in 0.05s ====================
"""
        
        counts = self.executor._parse_pytest_output(output)
        
        self.assertEqual(counts['test_count'], 3)
        self.assertEqual(counts['passed_count'], 1)
        self.assertEqual(counts['failed_count'], 1)
        self.assertEqual(counts['skipped_count'], 1)
    
    def test_parse_unittest_output(self):
        """Test parsing unittest output."""
        output = """
..F.s
======================================================================
FAIL: test_example (test_module.TestCase)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test_module.py", line 10, in test_example
    self.assertEqual(1, 2)
AssertionError: 1 != 2

----------------------------------------------------------------------
Ran 5 tests in 0.001s

FAILED (failures=1, skipped=1)
"""
        
        counts = self.executor._parse_unittest_output(output)
        
        self.assertEqual(counts['test_count'], 5)
        self.assertEqual(counts['failed_count'], 1)
        self.assertEqual(counts['skipped_count'], 1)
        self.assertEqual(counts['passed_count'], 3)  # 5 total - 1 failed - 1 skipped
    
    def test_generate_summary(self):
        """Test summary generation."""
        results = [
            TestResult(
                file_path="test1.py",
                status=TestStatus.PASSED,
                exit_code=0,
                stdout="",
                stderr="",
                execution_time=1.5,
                test_count=3,
                passed_count=3,
                failed_count=0,
                skipped_count=0,
                framework="pytest"
            ),
            TestResult(
                file_path="test2.py",
                status=TestStatus.FAILED,
                exit_code=1,
                stdout="",
                stderr="Error",
                execution_time=2.0,
                test_count=2,
                passed_count=1,
                failed_count=1,
                skipped_count=0,
                framework="unittest"
            )
        ]
        
        summary = TestExecutor.generate_summary(results)
        
        self.assertEqual(summary['total_files'], 2)
        self.assertEqual(summary['passed_files'], 1)
        self.assertEqual(summary['failed_files'], 1)
        self.assertEqual(summary['total_tests'], 5)
        self.assertEqual(summary['passed_tests'], 4)
        self.assertEqual(summary['failed_tests'], 1)
        self.assertEqual(summary['total_execution_time'], 3.5)
        self.assertEqual(summary['frameworks']['pytest'], 1)
        self.assertEqual(summary['frameworks']['unittest'], 1)


if __name__ == '__main__':
    unittest.main()
