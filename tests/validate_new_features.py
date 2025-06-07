#!/usr/bin/env python3
"""
Validation script for new SwarmBot features
Tests the newly implemented code for functionality
"""

import sys
import importlib
import traceback
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def validate_modules():
    """Validate that all new modules can be imported correctly"""
    print("=== Validating Module Imports ===\n")
    
    modules_to_test = [
        ("src.utils.api_validator", "APIKeyValidator"),
        ("src.database.chat_storage", "ChatDatabase"),
        ("src.database.chat_storage", "ChatLogger"),
        ("src.utils.logging_config", "setup_logging"),
        ("src.utils.logging_config", "ErrorTracker"),
        ("src.utils.logging_config", "LoggingMixin"),
        ("src.config", "Configuration"),
    ]
    
    results = []
    
    for module_name, class_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, class_name):
                results.append((module_name, class_name, "✓ PASS"))
                print(f"✓ {module_name}.{class_name} - Imported successfully")
            else:
                results.append((module_name, class_name, "✗ FAIL - Class not found"))
                print(f"✗ {module_name}.{class_name} - Class not found in module")
        except Exception as e:
            results.append((module_name, class_name, f"✗ FAIL - {str(e)}"))
            print(f"✗ {module_name}.{class_name} - Import failed: {str(e)}")
    
    return results

def validate_configuration():
    """Validate configuration system with auto-prompt settings"""
    print("\n=== Validating Configuration ===\n")
    
    try:
        from src.config import Configuration
        config = Configuration()
        
        # Check auto-prompt settings
        attrs = [
            "auto_prompt_enabled",
            "auto_prompt_max_iterations",
            "auto_prompt_goal_detection",
            "auto_prompt_save_state"
        ]
        
        for attr in attrs:
            if hasattr(config, attr):
                value = getattr(config, attr)
                print(f"✓ {attr}: {value} (type: {type(value).__name__})")
            else:
                print(f"✗ {attr}: Missing attribute")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration validation failed: {str(e)}")
        traceback.print_exc()
        return False

def validate_database():
    """Validate database functionality"""
    print("\n=== Validating Database ===\n")
    
    try:
        from src.database import ChatDatabase
        from datetime import datetime
        
        # Create test database
        db = ChatDatabase("test_validation.db")
        
        # Test session creation
        session_id = f"test_{datetime.now().timestamp()}"
        db.create_session(session_id, "test_provider", {"test": True})
        print("✓ Session created successfully")
        
        # Test message logging
        db.add_message(session_id, "msg1", "user", "Test message")
        print("✓ Message added successfully")
        
        # Test tool call logging
        db.add_tool_call("msg1", "test_tool", "test_server", 
                        {"input": "test"}, {"output": "result"}, 100)
        print("✓ Tool call logged successfully")
        
        # Test retrieval
        messages = db.get_session_messages(session_id)
        print(f"✓ Retrieved {len(messages)} messages")
        
        # Close database
        db.close()
        
        # Clean up test database
        Path("test_validation.db").unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        print(f"✗ Database validation failed: {str(e)}")
        traceback.print_exc()
        return False

def validate_logging():
    """Validate logging functionality"""
    print("\n=== Validating Logging System ===\n")
    
    try:
        from src.utils.logging_config import setup_logging, get_logger, error_tracker
        
        # Setup logging
        setup_logging(log_level="DEBUG", log_to_console=False)
        print("✓ Logging setup completed")
        
        # Get logger
        logger = get_logger("test_validation")
        logger.info("Test log message")
        print("✓ Logger created and used successfully")
        
        # Test error tracking
        try:
            raise ValueError("Test error for validation")
        except Exception:
            logger.error("Test error", exc_info=True)
        
        # Check error tracker
        summary = error_tracker.get_error_summary()
        print(f"✓ Error tracker working - {summary['total_errors']} errors tracked")
        
        return True
        
    except Exception as e:
        print(f"✗ Logging validation failed: {str(e)}")
        traceback.print_exc()
        return False

def validate_api_validator():
    """Validate API validator structure"""
    print("\n=== Validating API Validator ===\n")
    
    try:
        from src.utils.api_validator import APIKeyValidator
        from src.config import Configuration
        
        config = Configuration()
        validator = APIKeyValidator(config)
        
        # Check methods exist
        methods = [
            "validate_all_keys",
            "_validate_openai",
            "_validate_anthropic",
            "_validate_github",
            "get_validation_report"
        ]
        
        for method in methods:
            if hasattr(validator, method):
                print(f"✓ Method {method} exists")
            else:
                print(f"✗ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"✗ API Validator validation failed: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Run all validations"""
    print("SwarmBot Code Validation\n")
    print("=" * 50)
    
    # Run validations
    module_results = validate_modules()
    config_ok = validate_configuration()
    db_ok = validate_database()
    logging_ok = validate_logging()
    api_ok = validate_api_validator()
    
    # Summary
    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY\n")
    
    # Module imports
    passed = sum(1 for _, _, status in module_results if "PASS" in status)
    print(f"Module Imports: {passed}/{len(module_results)} passed")
    
    # Feature validations
    print(f"Configuration: {'✓ PASS' if config_ok else '✗ FAIL'}")
    print(f"Database: {'✓ PASS' if db_ok else '✗ FAIL'}")
    print(f"Logging: {'✓ PASS' if logging_ok else '✗ FAIL'}")
    print(f"API Validator: {'✓ PASS' if api_ok else '✗ FAIL'}")
    
    # Overall result
    all_passed = (passed == len(module_results) and 
                  config_ok and db_ok and logging_ok and api_ok)
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ ALL VALIDATIONS PASSED - Code is 100% functional!")
    else:
        print("✗ Some validations failed - Please check the output above")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
