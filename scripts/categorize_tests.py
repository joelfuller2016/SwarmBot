"""
SwarmBot Test Categorization Tool
Categorizes and summarizes all test files
"""
import os
import sys
from pathlib import Path
from collections import defaultdict
import json

class TestCategorizer:
    def __init__(self, tests_dir: Path):
        self.tests_dir = tests_dir
        self.categories = defaultdict(list)
        self.test_info = {}
        
    def categorize_by_name(self, file_path: Path) -> str:
        """Categorize test file by its name"""
        name = file_path.stem
        
        # Fix verification tests
        if name.endswith('_fix') or name.startswith('test_') and 'fix' in name:
            return "fix_verification"
            
        # WebSocket tests
        elif 'websocket' in name:
            return "websocket"
            
        # AsyncIO tests
        elif 'asyncio' in name:
            return "asyncio"
            
        # Dashboard/UI tests
        elif 'dashboard' in name or 'ui' in name:
            return "dashboard"
            
        # Configuration tests
        elif 'config' in name:
            return "configuration"
            
        # LLM tests
        elif 'llm' in name:
            return "llm"
            
        # Database tests
        elif 'database' in name or 'db' in name:
            return "database"
            
        # Validation/Verification scripts
        elif name.startswith(('validate_', 'verify_')):
            return "validation"
            
        # Runner scripts
        elif name.startswith('run_'):
            return "runner"
            
        # Integration tests
        elif 'integration' in str(file_path.parent):
            return "integration"
            
        # Unit tests
        elif 'unit' in str(file_path.parent):
            return "unit"
            
        # MCP tests
        elif 'mcp' in str(file_path.parent):
            return "mcp"
            
        # Archive tests
        elif 'archive' in str(file_path.parent):
            return "archive"
            
        # Basic/Core tests
        elif any(x in name for x in ['basic', 'quick', 'minimal', 'simple']):
            return "basic"
            
        # Enhanced/Advanced tests
        elif 'enhanced' in name:
            return "enhanced"
            
        # Structure/Setup tests
        elif any(x in name for x in ['structure', 'setup']):
            return "setup"
            
        # Chat tests
        elif 'chat' in name:
            return "chat"
            
        # Task tests
        elif 'task' in name:
            return "task"
            
        # Auto-prompt tests
        elif 'auto_prompt' in name:
            return "auto_prompt"
            
        # Import tests
        elif 'import' in name:
            return "imports"
            
        # Dummy/Example tests
        elif any(x in name for x in ['dummy', 'example']):
            return "example"
            
        else:
            return "other"
            
    def analyze_test_purpose(self, file_path: Path) -> dict:
        """Analyze test file to determine its purpose"""
        info = {
            "category": self.categorize_by_name(file_path),
            "has_docstring": False,
            "docstring": "",
            "likely_working": None,
            "dependencies": []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for docstring
            if content.strip().startswith(('"""', "'''")):
                quote = '"""' if content.startswith('"""') else "'''"
                end_pos = content.find(quote, 3)
                if end_pos > 0:
                    info["has_docstring"] = True
                    info["docstring"] = content[3:end_pos].strip()
                    
            # Check for obvious issues
            if "Not implemented" in content or "TODO" in content:
                info["likely_working"] = False
            elif "if __name__ == '__main__':" in content:
                info["likely_working"] = True
                
            # Extract dependencies
            import_lines = [line for line in content.split('\n') if line.strip().startswith(('import ', 'from '))]
            for line in import_lines:
                if 'from src' in line:
                    info["dependencies"].append(line.strip())
                    
        except Exception as e:
            info["error"] = str(e)
            
        return info
        
    def run_categorization(self):
        """Run categorization on all test files"""
        # Get all Python files
        test_files = []
        for pattern in ["*.py", "*/*.py", "*/*/*.py"]:
            test_files.extend(self.tests_dir.glob(pattern))
            
        # Filter to only test files
        test_files = [f for f in test_files if (
            f.stem.startswith(('test_', 'verify_', 'validate_')) or 
            f.stem.endswith('_test') or
            f.parent.name in ['integration', 'unit', 'mcp', 'archive']
        ) and '__pycache__' not in str(f)]
        
        # Categorize each file
        for test_file in test_files:
            info = self.analyze_test_purpose(test_file)
            category = info["category"]
            relative_path = test_file.relative_to(self.tests_dir)
            
            self.categories[category].append(str(relative_path))
            self.test_info[str(relative_path)] = info
            
    def print_summary(self):
        """Print categorization summary"""
        print("=" * 60)
        print("SwarmBot Test Categorization Summary")
        print("=" * 60)
        
        # Sort categories by number of tests
        sorted_categories = sorted(self.categories.items(), key=lambda x: len(x[1]), reverse=True)
        
        total_tests = sum(len(tests) for _, tests in sorted_categories)
        print(f"\nTotal test files: {total_tests}")
        print("\nTests by category:")
        print("-" * 40)
        
        for category, tests in sorted_categories:
            print(f"\n{category.upper()} ({len(tests)} tests):")
            for test in sorted(tests):
                info = self.test_info.get(test, {})
                status = ""
                if info.get("likely_working") is False:
                    status = " [LIKELY BROKEN]"
                elif info.get("error"):
                    status = " [ERROR]"
                print(f"  - {test}{status}")
                if info.get("docstring"):
                    print(f"    Purpose: {info['docstring'][:60]}...")
                    
    def save_categorization(self):
        """Save categorization to JSON file"""
        output = {
            "total_tests": sum(len(tests) for tests in self.categories.values()),
            "categories": dict(self.categories),
            "test_info": self.test_info
        }
        
        output_file = self.tests_dir.parent / "test_categorization.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)
        print(f"\nCategorization saved to: {output_file}")
        
    def generate_recommendations(self):
        """Generate recommendations for test cleanup"""
        print("\n" + "=" * 60)
        print("RECOMMENDATIONS")
        print("=" * 60)
        
        # Archive tests
        if "archive" in self.categories:
            print(f"\n1. Archive tests ({len(self.categories['archive'])} files):")
            print("   These are old versions of tests. Consider removing them entirely.")
            
        # Example/Dummy tests
        example_count = len(self.categories.get("example", []))
        if example_count > 0:
            print(f"\n2. Example/Dummy tests ({example_count} files):")
            print("   These appear to be placeholder tests. Remove if not needed.")
            
        # Runner scripts
        runner_count = len(self.categories.get("runner", []))
        if runner_count > 0:
            print(f"\n3. Runner scripts ({runner_count} files):")
            print("   Consolidate these into a single test runner utility.")
            
        # Fix verification tests
        fix_count = len(self.categories.get("fix_verification", []))
        if fix_count > 0:
            print(f"\n4. Fix verification tests ({fix_count} files):")
            print("   These verify specific bug fixes. Keep only if fixes are still relevant.")
            
        # WebSocket tests
        ws_count = len(self.categories.get("websocket", []))
        if ws_count > 0:
            print(f"\n5. WebSocket tests ({ws_count} files):")
            print("   Large number of WebSocket tests. Consider consolidating into a test suite.")


def main():
    """Main entry point"""
    project_root = Path(__file__).parent
    tests_dir = project_root / "tests"
    
    if not tests_dir.exists():
        print(f"Error: Tests directory not found at {tests_dir}")
        return 1
        
    categorizer = TestCategorizer(tests_dir)
    categorizer.run_categorization()
    categorizer.print_summary()
    categorizer.save_categorization()
    categorizer.generate_recommendations()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
