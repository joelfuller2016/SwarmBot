#!/usr/bin/env python3
"""
Verification script for Task 96: LLM API Cost Tracking System
This script verifies that all components of the cost tracking system are working correctly.
"""

import sys
import os
from pathlib import Path
import logging
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_imports():
    """Verify all required modules can be imported"""
    logger.info("Verifying imports...")
    try:
        from src.core.cost_tracker import CostTracker, ModelCost, RequestCost
        logger.info("✓ cost_tracker module imported successfully")
        
        from src.core.integrated_analyzer import IntegratedAnalyzer
        logger.info("✓ integrated_analyzer module imported successfully")
        
        from src.core.cost_updater import CostUpdater, STATIC_MODEL_COSTS
        logger.info("✓ cost_updater module imported successfully")
        
        from src.core.budget_monitor import BudgetMonitor, BudgetAlert
        logger.info("✓ budget_monitor module imported successfully")
        
        from src.database.cost_tracking import CostTrackingDB
        logger.info("✓ cost_tracking database module imported successfully")
        
        return True
    except ImportError as e:
        logger.error(f"✗ Import failed: {e}")
        return False

def verify_database_schema():
    """Verify database schema is correctly set up"""
    logger.info("\nVerifying database schema...")
    try:
        from src.database.cost_tracking import CostTrackingDB
        import tempfile
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            db_path = temp_db.name
        
        # Initialize database
        db = CostTrackingDB(db_path)
        
        # Check tables exist
        cursor = db.conn.cursor()
        tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        table_names = [t[0] for t in tables]
        
        required_tables = ['model_costs', 'request_costs', 'conversation_costs', 'budget_alerts']
        for table in required_tables:
            if table in table_names:
                logger.info(f"✓ Table '{table}' exists")
            else:
                logger.error(f"✗ Table '{table}' missing")
        
        # Clean up
        db.close()
        os.unlink(db_path)
        
        return all(table in table_names for table in required_tables)
    except Exception as e:
        logger.error(f"✗ Database verification failed: {e}")
        return False

def verify_pricing_data():
    """Verify pricing data is available"""
    logger.info("\nVerifying pricing data...")
    try:
        from src.core.cost_updater import STATIC_MODEL_COSTS
        
        providers = list(STATIC_MODEL_COSTS.keys())
        logger.info(f"✓ Found pricing data for {len(providers)} providers: {providers}")
        
        # Check some key models
        key_models = [
            ('openai', 'gpt-4'),
            ('anthropic', 'claude-3-opus'),
            ('google', 'gemini-pro'),
            ('groq', 'llama2-70b')
        ]
        
        for provider, model in key_models:
            if provider in STATIC_MODEL_COSTS and model in STATIC_MODEL_COSTS[provider]:
                pricing = STATIC_MODEL_COSTS[provider][model]
                logger.info(f"✓ {provider}/{model}: input=${pricing['input']}/1k, output=${pricing['output']}/1k")
            else:
                logger.error(f"✗ Missing pricing for {provider}/{model}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Pricing data verification failed: {e}")
        return False

def verify_configuration():
    """Verify configuration is set up correctly"""
    logger.info("\nVerifying configuration...")
    try:
        # Check .env.example
        env_example_path = project_root / '.env.example'
        if env_example_path.exists():
            with open(env_example_path, 'r') as f:
                content = f.read()
                
            required_vars = ['TRACK_COSTS', 'COST_ALERT_THRESHOLD', 'CUSTOM_COSTS_FILE', 'EXPORT_COSTS_ON_EXIT']
            for var in required_vars:
                if var in content:
                    logger.info(f"✓ {var} found in .env.example")
                else:
                    logger.error(f"✗ {var} missing from .env.example")
        else:
            logger.error("✗ .env.example file not found")
            
        return True
    except Exception as e:
        logger.error(f"✗ Configuration verification failed: {e}")
        return False

def verify_dashboard_components():
    """Verify dashboard components exist"""
    logger.info("\nVerifying dashboard components...")
    try:
        cost_tracking_page = project_root / 'src' / 'ui' / 'dash' / 'pages' / 'cost_tracking.py'
        if cost_tracking_page.exists():
            logger.info("✓ Cost tracking dashboard page exists")
            
            # Check for key functions
            with open(cost_tracking_page, 'r') as f:
                content = f.read()
                
            required_functions = [
                'create_cost_dashboard_layout',
                'register_cost_dashboard_callbacks',
                'update_cost_metrics',
                'update_daily_cost_chart',
                'update_model_cost_chart',
                'update_provider_comparison_chart',
                'export_cost_data'
            ]
            
            for func in required_functions:
                if func in content:
                    logger.info(f"✓ Function '{func}' found")
                else:
                    logger.error(f"✗ Function '{func}' missing")
        else:
            logger.error("✗ Cost tracking dashboard page not found")
            
        return True
    except Exception as e:
        logger.error(f"✗ Dashboard verification failed: {e}")
        return False

def verify_migrations():
    """Verify migration files exist"""
    logger.info("\nVerifying migrations...")
    try:
        migrations_dir = project_root / 'migrations'
        if migrations_dir.exists():
            migration_files = list(migrations_dir.glob('*.sql'))
            logger.info(f"✓ Found {len(migration_files)} migration files")
            
            # Check for specific migrations
            required_migrations = [
                '001_cost_tracking_schema.sql',
                '002_add_model_costs_data.sql',
                '003_add_cost_tracking_views.sql',
                '004_add_query_performance_monitoring.sql',
                '005_add_cost_tracking_foreign_keys.sql',
                '006_add_budget_alerts_table.sql'
            ]
            
            for migration in required_migrations:
                if (migrations_dir / migration).exists():
                    logger.info(f"✓ Migration '{migration}' exists")
                else:
                    logger.error(f"✗ Migration '{migration}' missing")
        else:
            logger.error("✗ Migrations directory not found")
            
        return True
    except Exception as e:
        logger.error(f"✗ Migration verification failed: {e}")
        return False

def verify_session_id_passing():
    """Verify session ID is properly passed in chat_session.py"""
    logger.info("\nVerifying session ID passing...")
    try:
        chat_session_path = project_root / 'src' / 'chat_session.py'
        if chat_session_path.exists():
            with open(chat_session_path, 'r') as f:
                content = f.read()
                
            # Check for conversation_id parameter in get_response calls
            if 'conversation_id=session_id' in content:
                logger.info("✓ Session ID is passed to LLM client")
                
                # Count occurrences
                count = content.count('conversation_id=session_id')
                logger.info(f"✓ Found {count} occurrences of session_id passing")
            else:
                logger.error("✗ Session ID not passed to LLM client")
        else:
            logger.error("✗ chat_session.py not found")
            
        return True
    except Exception as e:
        logger.error(f"✗ Session ID verification failed: {e}")
        return False

def main():
    """Run all verification tests"""
    logger.info("=" * 80)
    logger.info("Task 96: LLM API Cost Tracking System - Verification Report")
    logger.info("=" * 80)
    
    results = {
        'imports': verify_imports(),
        'database': verify_database_schema(),
        'pricing': verify_pricing_data(),
        'configuration': verify_configuration(),
        'dashboard': verify_dashboard_components(),
        'migrations': verify_migrations(),
        'session_id': verify_session_id_passing()
    }
    
    logger.info("\n" + "=" * 80)
    logger.info("SUMMARY")
    logger.info("=" * 80)
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        logger.info(f"{test_name.capitalize()}: {status}")
    
    logger.info(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("\n✓ Task 96 verification PASSED - All components are working correctly!")
        return 0
    else:
        logger.error(f"\n✗ Task 96 verification FAILED - {total_tests - passed_tests} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
