"""
SwarmBot Test Fix Tool
Automatically fixes common issues in test files
"""
import os
import sys
import re
from pathlib import Path
from typing import List, Tuple

class TestFixer:
    def __init__(self, tests_dir: Path):
        self.tests_dir = tests_dir
        self.fixes_applied = {
            "path_fixes": 0,
            "import_fixes": 0,
            "encoding_fixes": 0,
            "deprecated_fixes": 0
        }
        
    def fix_path_references(self, content: str, file_path: Path) -> Tuple[str, bool]:
        """Fix incorrect path references in test files"""
        fixed = False
        original = content
        
        # Calculate correct parent level based on file location
        relative_to_tests = file_path.relative_to(self.tests_dir)
        depth = len(relative_to_tests.parts) - 1  # -1 for the file itself
        
        # Fix path references
        if depth == 0:  # File in tests/ root
            # Fix Path(__file__).parent to Path(__file__).parent.parent
            if "Path(__file__).parent" in content and "parent.parent" not in content:
                # Check if it's not already correct
                pattern = r'Path\(__file__\)\.parent(?!\.parent)'
                if re.search(pattern, content):
                    content = re.sub(pattern, 'Path(__file__).parent.parent', content)
                    fixed = True
                    
        elif depth == 1:  # File in subdirectory like tests/integration/
            # These need three parents to get to project root
            pattern = r'Path\(__file__\)\.parent\.parent(?!\.parent)'
            if re.search(pattern, content):
                content = re.sub(pattern, 'Path(__file__).parent.parent.parent', content)
                fixed = True
                
        return content, fixed
        
    def fix_import_statements(self, content: str, file_path: Path) -> Tuple[str, bool]:
        """Fix common import issues"""
        fixed = False
        original = content
        
        # Fix sys.path insertions
        if "sys.path.insert(0, str(Path(__file__).parent))" in content:
            content = content.replace(
                "sys.path.insert(0, str(Path(__file__).parent))",
                "sys.path.insert(0, str(Path(__file__).parent.parent))"
            )
            fixed = True
            
        # Fix sys.path append statements
        if "sys.path.append(str(Path(__file__).parent))" in content:
            content = content.replace(
                "sys.path.append(str(Path(__file__).parent))",
                "sys.path.append(str(Path(__file__).parent.parent))"
            )
            fixed = True
            
        # Add missing Path import if needed
        if "Path(__file__)" in content and "from pathlib import Path" not in content:
            # Add after other imports
            import_section_end = 0
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith(('import ', 'from ')) and not line.startswith('from .'):
                    import_section_end = i + 1
                elif import_section_end > 0 and not line.strip().startswith(('import ', 'from ')):
                    break
                    
            if import_section_end > 0:
                lines.insert(import_section_end, "from pathlib import Path")
                content = '\n'.join(lines)
                fixed = True
                
        return content, fixed
        
    def fix_encoding_issues(self, content: str) -> Tuple[str, bool]:
        """Fix encoding issues in test files"""
        fixed = False
        
        # Add encoding declaration if missing
        lines = content.split('\n')
        if lines and not lines[0].startswith('#') and '# -*- coding:' not in content:
            lines.insert(0, "# -*- coding: utf-8 -*-")
            content = '\n'.join(lines)
            fixed = True
            
        return content, fixed
        
    def fix_deprecated_patterns(self, content: str) -> Tuple[str, bool]:
        """Fix deprecated patterns in test files"""
        fixed = False
        original = content
        
        # Fix old-style string formatting
        content = re.sub(r'%\s*\(([^)]+)\)s', r'{\1}', content)
        
        # Fix assertEquals to assertEqual
        content = content.replace('assertEquals', 'assertEqual')
        content = content.replace('assertNotEquals', 'assertNotEqual')
        
        # Fix print statements without parentheses (Python 2 style)
        content = re.sub(r'^(\s*)print\s+([^(].*?)$', r'\1print(\2)', content, flags=re.MULTILINE)
        
        if content != original:
            fixed = True
            
        return content, fixed
        
    def should_skip_file(self, file_path: Path) -> bool:
        """Determine if a file should be skipped"""
        skip_patterns = [
            "__pycache__",
            ".pyc",
            ".pyo",
            "__init__.py",
            "conftest.py"
        ]
        
        for pattern in skip_patterns:
            if pattern in str(file_path):
                return True
                
        return False
        
    def fix_test_file(self, file_path: Path) -> bool:
        """Fix issues in a single test file"""
        if self.should_skip_file(file_path):
            return False
            
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            any_fixed = False
            
            # Apply fixes
            content, path_fixed = self.fix_path_references(content, file_path)
            if path_fixed:
                self.fixes_applied["path_fixes"] += 1
                any_fixed = True
                
            content, import_fixed = self.fix_import_statements(content, file_path)
            if import_fixed:
                self.fixes_applied["import_fixes"] += 1
                any_fixed = True
                
            content, encoding_fixed = self.fix_encoding_issues(content)
            if encoding_fixed:
                self.fixes_applied["encoding_fixes"] += 1
                any_fixed = True
                
            content, deprecated_fixed = self.fix_deprecated_patterns(content)
            if deprecated_fixed:
                self.fixes_applied["deprecated_fixes"] += 1
                any_fixed = True
                
            # Write back if changes were made
            if any_fixed and content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"[FIXED] {file_path.relative_to(self.tests_dir.parent)}")
                return True
                
        except Exception as e:
            print(f"[ERROR] Error fixing {file_path}: {str(e)}")
            
        return False
        
    def run_fixes(self):
        """Run fixes on all test files"""
        print("=" * 60)
        print("SwarmBot Test Fix Tool")
        print("=" * 60)
        
        # Get all Python files in tests directory
        test_files = []
        for pattern in ["*.py", "*/*.py", "*/*/*.py"]:
            test_files.extend(self.tests_dir.glob(pattern))
            
        fixed_count = 0
        for test_file in test_files:
            if self.fix_test_file(test_file):
                fixed_count += 1
                
        # Print summary
        print("\n" + "=" * 60)
        print("FIX SUMMARY")
        print("=" * 60)
        print(f"Files processed: {len(test_files)}")
        print(f"Files fixed: {fixed_count}")
        print(f"Path fixes: {self.fixes_applied['path_fixes']}")
        print(f"Import fixes: {self.fixes_applied['import_fixes']}")
        print(f"Encoding fixes: {self.fixes_applied['encoding_fixes']}")
        print(f"Deprecated pattern fixes: {self.fixes_applied['deprecated_fixes']}")


def main():
    """Main entry point"""
    project_root = Path(__file__).parent
    tests_dir = project_root / "tests"
    
    if not tests_dir.exists():
        print(f"Error: Tests directory not found at {tests_dir}")
        return 1
        
    fixer = TestFixer(tests_dir)
    fixer.run_fixes()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
