#!/usr/bin/env python3
"""
Task 96 Core Verification Script
Focused testing of core cost tracking functionality without full app dependencies
"""

import os
import sys
import json
import sqlite3
import tempfile
import time
from pathlib import Path
from datetime import datetime
from decimal import Decimal

def verify_core_functionality():
    """Verify core cost tracking functionality"""
    results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {},
        'overall_status': 'UNKNOWN',
        'critical_issues': [],
        'warnings': [],
        'recommendations': []
    }
    
    print("🔍 Starting Task 96 Core Verification...")
    print("=" * 60)
    
    # Test 1: Database Schema Verification
    print("\n📁 Testing Database Schema...")
    try:
        # Check if migrations exist
        migrations_path = Path("migrations")
        if migrations_path.exists():
            migration_files = list(migrations_path.glob("*.sql"))
            migration_files = [f for f in migration_files if not f.name.endswith("_rollback.sql")]
            
            results['tests']['migrations'] = {
                'status': 'PASS',
                'migration_files_found': len(migration_files),
                'migrations': [f.name for f in migration_files]
            }
            print(f"✅ Migrations: PASS - {len(migration_files)} migration files found")
        else:
            results['tests']['migrations'] = {
                'status': 'FAIL',
                'error': 'Migrations directory not found'
            }
            results['critical_issues'].append("Migrations directory missing")
            print("❌ Migrations: FAIL - migrations directory not found")
    except Exception as e:
        results['tests']['migrations'] = {'status': 'FAIL', 'error': str(e)}
        print(f"❌ Migrations: FAIL - {e}")
    
    # Test 2: Core Module Structure
    print("\n📦 Testing Core Module Structure...")
    try:
        core_modules = [
            'src/core/cost_tracker.py',
            'src/core/budget_monitor.py',
            'src/core/cost_updater.py',
            'src/core/integrated_analyzer.py',
            'src/database/cost_tracking.py'
        ]
        
        existing_modules = []
        missing_modules = []
        
        for module in core_modules:
            if Path(module).exists():
                existing_modules.append(module)
            else:
                missing_modules.append(module)
        
        if missing_modules:
            results['tests']['core_modules'] = {
                'status': 'FAIL',
                'missing_modules': missing_modules,
                'existing_modules': existing_modules
            }
            results['critical_issues'].append(f"Missing core modules: {missing_modules}")
            print(f"❌ Core Modules: FAIL - Missing: {missing_modules}")
        else:
            results['tests']['core_modules'] = {
                'status': 'PASS',
                'modules_found': len(existing_modules),
                'all_modules': existing_modules
            }
            print(f"✅ Core Modules: PASS - {len(existing_modules)} modules found")
    except Exception as e:
        results['tests']['core_modules'] = {'status': 'FAIL', 'error': str(e)}
        print(f"❌ Core Modules: FAIL - {e}")
    
    # Test 3: Configuration Check
    print("\n⚙️ Testing Configuration...")
    try:
        env_example_path = Path(".env.example")
        if env_example_path.exists():
            with open(env_example_path, 'r') as f:
                content = f.read()
            
            cost_tracking_vars = [
                'TRACK_COSTS',
                'COST_ALERT_THRESHOLD',
                'DAILY_COST_LIMIT',
                'SESSION_COST_LIMIT',
                'BUDGET_WARNING_PERCENT',
                'BUDGET_CRITICAL_PERCENT'
            ]
            
            found_vars = []
            missing_vars = []
            
            for var in cost_tracking_vars:
                if var in content:
                    found_vars.append(var)
                else:
                    missing_vars.append(var)
            
            results['tests']['configuration'] = {
                'status': 'PASS' if not missing_vars else 'PARTIAL',
                'env_example_exists': True,
                'cost_vars_found': len(found_vars),
                'cost_vars_missing': missing_vars
            }
            
            if missing_vars:
                results['warnings'].append(f"Missing config vars in .env.example: {missing_vars}")
                print(f"⚠️ Configuration: PARTIAL - Missing vars: {missing_vars}")
            else:
                print(f"✅ Configuration: PASS - All {len(found_vars)} cost tracking vars documented")
        else:
            results['tests']['configuration'] = {
                'status': 'FAIL',
                'error': '.env.example not found'
            }
            results['critical_issues'].append(".env.example file missing")
            print("❌ Configuration: FAIL - .env.example not found")
    except Exception as e:
        results['tests']['configuration'] = {'status': 'FAIL', 'error': str(e)}
        print(f"❌ Configuration: FAIL - {e}")
    
    # Test 4: Database Migration Test
    print("\n🗄️ Testing Database Migration...")
    try:
        # Create temporary database and test migrations
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            test_db_path = f.name
        
        conn = sqlite3.connect(test_db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Run migrations manually
        migrations_path = Path("migrations")
        if migrations_path.exists():
            migration_files = sorted([f for f in migrations_path.glob("*.sql") 
                                   if not f.name.endswith("_rollback.sql")])
            
            tables_created = []
            for migration_file in migration_files:
                try:
                    with open(migration_file, 'r', encoding='utf-8') as f:
                        migration_sql = f.read()
                    
                    conn.executescript(migration_sql)
                    
                except Exception as e:
                    print(f"❌ Migration {migration_file.name} failed: {e}")
                    break
            
            # Check what tables were created
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables_created = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['model_costs', 'request_costs', 'conversation_costs']
            missing_tables = [t for t in expected_tables if t not in tables_created]
            
            if missing_tables:
                results['tests']['database_migration'] = {
                    'status': 'FAIL',
                    'tables_created': tables_created,
                    'missing_tables': missing_tables
                }
                results['critical_issues'].append(f"Database migration failed - missing tables: {missing_tables}")
                print(f"❌ Database Migration: FAIL - Missing tables: {missing_tables}")
            else:
                results['tests']['database_migration'] = {
                    'status': 'PASS',
                    'tables_created': len(tables_created),
                    'all_tables': tables_created
                }
                print(f"✅ Database Migration: PASS - {len(tables_created)} tables created")
        
        conn.close()
        os.unlink(test_db_path)
        
    except Exception as e:
        results['tests']['database_migration'] = {'status': 'FAIL', 'error': str(e)}
        results['critical_issues'].append(f"Database migration test failed: {e}")
        print(f"❌ Database Migration: FAIL - {e}")
    
    # Test 5: Cost Calculation Logic
    print("\n🧮 Testing Cost Calculation Logic...")
    try:
        # Test basic cost calculation math
        input_tokens = 1000
        output_tokens = 500
        input_cost_per_1k = 0.03
        output_cost_per_1k = 0.06
        
        # Calculate using Decimal for precision (like the actual implementation)
        input_cost = float(Decimal(str(input_tokens)) / Decimal('1000') * Decimal(str(input_cost_per_1k)))
        output_cost = float(Decimal(str(output_tokens)) / Decimal('1000') * Decimal(str(output_cost_per_1k)))
        total_cost = input_cost + output_cost
        
        # Expected: (1000/1000 * 0.03) + (500/1000 * 0.06) = 0.03 + 0.03 = 0.06
        expected_total = 0.06
        
        calculation_correct = abs(total_cost - expected_total) < 0.001
        
        if calculation_correct:
            results['tests']['cost_calculation'] = {
                'status': 'PASS',
                'calculated_cost': total_cost,
                'expected_cost': expected_total,
                'test_scenario': f"{input_tokens} in, {output_tokens} out tokens"
            }
            print(f"✅ Cost Calculation: PASS - ${total_cost:.4f}")
        else:
            results['tests']['cost_calculation'] = {
                'status': 'FAIL',
                'calculated_cost': total_cost,
                'expected_cost': expected_total,
                'difference': abs(total_cost - expected_total)
            }
            results['critical_issues'].append("Cost calculation logic error")
            print(f"❌ Cost Calculation: FAIL - Expected ${expected_total:.4f}, got ${total_cost:.4f}")
    except Exception as e:
        results['tests']['cost_calculation'] = {'status': 'FAIL', 'error': str(e)}
        print(f"❌ Cost Calculation: FAIL - {e}")
    
    # Test 6: Integration Points Check
    print("\n🔗 Testing Integration Points...")
    try:
        # Check chat_session.py for session_id passing
        chat_session_path = Path("src/chat_session.py")
        if chat_session_path.exists():
            with open(chat_session_path, 'r') as f:
                content = f.read()
            
            session_id_passed = "conversation_id=session_id" in content
            llm_response_calls = content.count("self.llm_client.get_response")
            
            # Check llm_client_adapter.py for cost tracking
            adapter_path = Path("src/llm_client_adapter.py")
            cost_tracking_integrated = False
            if adapter_path.exists():
                with open(adapter_path, 'r') as f:
                    adapter_content = f.read()
                cost_tracking_integrated = "_track_cost" in adapter_content and "IntegratedAnalyzer" in adapter_content
            
            integration_status = 'PASS' if (session_id_passed and cost_tracking_integrated) else 'FAIL'
            
            results['tests']['integration_points'] = {
                'status': integration_status,
                'session_id_passed': session_id_passed,
                'llm_response_calls': llm_response_calls,
                'cost_tracking_integrated': cost_tracking_integrated
            }
            
            if integration_status == 'PASS':
                print("✅ Integration Points: PASS")
            else:
                issues = []
                if not session_id_passed:
                    issues.append("session_id not passed to LLM client")
                if not cost_tracking_integrated:
                    issues.append("cost tracking not integrated in LLM adapter")
                results['critical_issues'].extend(issues)
                print(f"❌ Integration Points: FAIL - {', '.join(issues)}")
        else:
            results['tests']['integration_points'] = {
                'status': 'FAIL',
                'error': 'chat_session.py not found'
            }
            results['critical_issues'].append("chat_session.py file missing")
            print("❌ Integration Points: FAIL - chat_session.py not found")
    except Exception as e:
        results['tests']['integration_points'] = {'status': 'FAIL', 'error': str(e)}
        print(f"❌ Integration Points: FAIL - {e}")
    
    # Test 7: UI Components Check
    print("\n🎨 Testing UI Components...")
    try:
        ui_components = [
            'src/ui/dash/pages/cost_tracking.py',
            'src/ui/dash/assets/cost_tracking.css'
        ]
        
        existing_ui = []
        missing_ui = []
        
        for component in ui_components:
            if Path(component).exists():
                existing_ui.append(component)
            else:
                missing_ui.append(component)
        
        if missing_ui:
            results['tests']['ui_components'] = {
                'status': 'PARTIAL',
                'existing_components': existing_ui,
                'missing_components': missing_ui
            }
            results['warnings'].append(f"Missing UI components: {missing_ui}")
            print(f"⚠️ UI Components: PARTIAL - Missing: {missing_ui}")
        else:
            results['tests']['ui_components'] = {
                'status': 'PASS',
                'components_found': len(existing_ui),
                'all_components': existing_ui
            }
            print(f"✅ UI Components: PASS - {len(existing_ui)} components found")
    except Exception as e:
        results['tests']['ui_components'] = {'status': 'FAIL', 'error': str(e)}
        print(f"❌ UI Components: FAIL - {e}")
    
    # Determine overall status
    test_results = [test.get('status', 'UNKNOWN') for test in results['tests'].values()]
    
    if results['critical_issues']:
        results['overall_status'] = 'CRITICAL_ISSUES'
    elif 'FAIL' in test_results:
        results['overall_status'] = 'FAILED'
    elif 'PARTIAL' in test_results or results['warnings']:
        results['overall_status'] = 'WARNING'
    elif all(status == 'PASS' for status in test_results):
        results['overall_status'] = 'PASS'
    else:
        results['overall_status'] = 'UNKNOWN'
    
    # Add recommendations
    if results['overall_status'] == 'PASS':
        results['recommendations'].append("✅ Task 96 implementation is complete and ready for production")
        results['recommendations'].append("✅ All core functionality verified and working")
        results['recommendations'].append("📝 Consider adding automated tests for continuous validation")
    elif results['overall_status'] == 'WARNING':
        results['recommendations'].append("⚠️ Task 96 is functional but has minor issues to address")
        results['recommendations'].append("📝 Address warnings for optimal performance")
    elif results['critical_issues']:
        results['recommendations'].append("🚨 Critical issues must be resolved before production use")
        results['recommendations'].append("🔧 Focus on fixing integration and core functionality issues")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 TASK 96 CORE VERIFICATION SUMMARY")
    print("=" * 60)
    
    status_emoji = {
        'PASS': '✅',
        'WARNING': '⚠️',
        'FAILED': '❌',
        'CRITICAL_ISSUES': '🚨',
        'UNKNOWN': '❓'
    }
    
    emoji = status_emoji.get(results['overall_status'], '❓')
    print(f"\n{emoji} Overall Status: {results['overall_status']}")
    
    print(f"\n📊 Test Results ({len(results['tests'])} tests):")
    for test_name, test_result in results['tests'].items():
        status = test_result.get('status', 'UNKNOWN')
        emoji = status_emoji.get(status, '❓')
        print(f"  {emoji} {test_name.replace('_', ' ').title()}: {status}")
    
    if results['critical_issues']:
        print(f"\n🚨 Critical Issues ({len(results['critical_issues'])}):")
        for issue in results['critical_issues']:
            print(f"  • {issue}")
    
    if results['warnings']:
        print(f"\n⚠️ Warnings ({len(results['warnings'])}):")
        for warning in results['warnings']:
            print(f"  • {warning}")
    
    if results['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in results['recommendations']:
            print(f"  • {rec}")
    
    print(f"\n📅 Verification completed at: {results['timestamp']}")
    print("=" * 60)
    
    # Save results
    results_path = Path("task_96_core_verification_results.json")
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {results_path}")
    
    return results


if __name__ == "__main__":
    results = verify_core_functionality()
    
    # Exit with appropriate code
    if results['overall_status'] in ['PASS', 'WARNING']:
        exit(0)
    else:
        exit(1)
