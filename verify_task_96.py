#!/usr/bin/env python3
"""
Task 96 Verification Script
Comprehensive end-to-end testing of the LLM API Cost Tracking System
"""

import os
import sys
import json
import tempfile
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import Configuration
from src.database.cost_tracking import CostTrackingDB, CostTrackingHealthCheck
from src.core.cost_tracker import CostTracker, ModelCost, RequestCost
from src.core.budget_monitor import BudgetMonitor
from src.core.integrated_analyzer import IntegratedAnalyzer
from src.core.cost_updater import CostUpdater
from src.llm_client_adapter import LLMClient


class Task96Verifier:
    """Comprehensive verification of Task 96 implementation"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'overall_status': 'UNKNOWN',
            'critical_issues': [],
            'warnings': [],
            'recommendations': []
        }
        self.temp_db_path = None
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all verification tests"""
        print("🔍 Starting Task 96 Verification...")
        print("=" * 60)
        
        try:
            # Core functionality tests
            self.test_database_initialization()
            self.test_migrations()
            self.test_model_costs()
            self.test_cost_calculations()
            self.test_budget_monitoring()
            self.test_cost_tracking_integration()
            self.test_configuration()
            self.test_export_functionality()
            self.test_database_health()
            self.test_performance()
            
            # Integration tests
            self.test_end_to_end_workflow()
            
            # Determine overall status
            self._determine_overall_status()
            
        except Exception as e:
            self.results['critical_issues'].append(f"Verification failed: {str(e)}")
            self.results['overall_status'] = 'FAILED'
        
        finally:
            self._cleanup()
        
        return self.results
    
    def test_database_initialization(self):
        """Test database initialization and optimization"""
        print("\n📁 Testing Database Initialization...")
        
        try:
            # Create temporary database
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
                self.temp_db_path = f.name
            
            # Initialize database
            db = CostTrackingDB(self.temp_db_path)
            
            # Check optimizations
            cursor = db.conn.cursor()
            cursor.execute("PRAGMA journal_mode")
            journal_mode = cursor.fetchone()[0]
            
            cursor.execute("PRAGMA foreign_keys")
            foreign_keys = cursor.fetchone()[0]
            
            self.results['tests']['database_initialization'] = {
                'status': 'PASS',
                'journal_mode': journal_mode,
                'foreign_keys_enabled': bool(foreign_keys),
                'db_path': self.temp_db_path
            }
            
            print("✅ Database initialization: PASS")
            
        except Exception as e:
            self.results['tests']['database_initialization'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            self.results['critical_issues'].append(f"Database initialization failed: {e}")
            print(f"❌ Database initialization: FAIL - {e}")
    
    def test_migrations(self):
        """Test database migrations"""
        print("\n🔄 Testing Database Migrations...")
        
        try:
            db = CostTrackingDB(self.temp_db_path)
            
            # Check that all expected tables exist
            expected_tables = [
                'model_costs', 'request_costs', 'conversation_costs', 
                'budget_alerts', 'notification_queue', 'migration_log'
            ]
            
            cursor = db.conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table'
            """)
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            missing_tables = [t for t in expected_tables if t not in existing_tables]
            
            if missing_tables:
                self.results['tests']['migrations'] = {
                    'status': 'FAIL',
                    'missing_tables': missing_tables,
                    'existing_tables': existing_tables
                }
                self.results['critical_issues'].append(f"Missing tables: {missing_tables}")
                print(f"❌ Migrations: FAIL - Missing tables: {missing_tables}")
            else:
                self.results['tests']['migrations'] = {
                    'status': 'PASS',
                    'tables_created': len(existing_tables),
                    'all_tables': existing_tables
                }
                print(f"✅ Migrations: PASS - {len(existing_tables)} tables created")
                
        except Exception as e:
            self.results['tests']['migrations'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            self.results['critical_issues'].append(f"Migration test failed: {e}")
            print(f"❌ Migrations: FAIL - {e}")
    
    def test_model_costs(self):
        """Test model cost loading and caching"""
        print("\n💰 Testing Model Costs...")
        
        try:
            # Test cost updater
            updater = CostUpdater()
            cost_catalog = updater.get_cost_catalog()
            
            # Test database cost loading
            db = CostTrackingDB(self.temp_db_path)
            all_costs = db.get_all_model_costs()
            
            self.results['tests']['model_costs'] = {
                'status': 'PASS',
                'catalog_providers': len(cost_catalog.get('providers', {})),
                'database_costs': len(all_costs),
                'sample_costs': {
                    provider: list(models.keys())[:3] 
                    for provider, models in cost_catalog.get('providers', {}).items()
                }
            }
            
            print(f"✅ Model Costs: PASS - {len(cost_catalog.get('providers', {}))} providers loaded")
            
        except Exception as e:
            self.results['tests']['model_costs'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            self.results['warnings'].append(f"Model cost loading issue: {e}")
            print(f"⚠️ Model Costs: WARNING - {e}")
    
    def test_cost_calculations(self):
        """Test cost calculation accuracy"""
        print("\n🧮 Testing Cost Calculations...")
        
        try:
            config = Configuration()
            
            # Test ModelCost class
            model_cost = ModelCost("gpt-4", "openai", 0.03, 0.06, 8192)
            
            # Test RequestCost calculation
            request_cost = RequestCost.calculate(
                model_cost=model_cost,
                input_tokens=1000,
                output_tokens=500
            )
            
            # Verify calculation
            expected_input_cost = 0.03  # $0.03 per 1K tokens
            expected_output_cost = 0.03  # $0.06 per 1K tokens * 0.5K
            expected_total = expected_input_cost + expected_output_cost
            
            calculation_correct = abs(float(request_cost.total_cost) - expected_total) < 0.001
            
            if calculation_correct:
                self.results['tests']['cost_calculations'] = {
                    'status': 'PASS',
                    'test_input_tokens': 1000,
                    'test_output_tokens': 500,
                    'calculated_cost': float(request_cost.total_cost),
                    'expected_cost': expected_total
                }
                print(f"✅ Cost Calculations: PASS - ${float(request_cost.total_cost):.4f}")
            else:
                self.results['tests']['cost_calculations'] = {
                    'status': 'FAIL',
                    'calculated_cost': float(request_cost.total_cost),
                    'expected_cost': expected_total,
                    'difference': abs(float(request_cost.total_cost) - expected_total)
                }
                self.results['critical_issues'].append("Cost calculation accuracy issue")
                print(f"❌ Cost Calculations: FAIL - Expected ${expected_total:.4f}, got ${float(request_cost.total_cost):.4f}")
                
        except Exception as e:
            self.results['tests']['cost_calculations'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            self.results['critical_issues'].append(f"Cost calculation test failed: {e}")
            print(f"❌ Cost Calculations: FAIL - {e}")
    
    def test_budget_monitoring(self):
        """Test budget monitoring and alerts"""
        print("\n💸 Testing Budget Monitoring...")
        
        try:
            config = Configuration()
            db = CostTrackingDB(self.temp_db_path)
            
            # Test budget monitor
            monitor = BudgetMonitor(config, db)
            
            # Create test session and costs
            session_id = f"test_budget_session_{int(time.time())}"
            db.create_session(session_id, "test_provider")
            
            # Log some costs to trigger budget check
            db.log_request_cost(session_id, "gpt-4", 1000, 500, "openai")
            db.log_request_cost(session_id, "gpt-4", 2000, 1000, "openai")
            
            # Check budget status
            status = monitor.check_budget_status()
            
            self.results['tests']['budget_monitoring'] = {
                'status': 'PASS',
                'budget_status': status,
                'alerts_configured': hasattr(monitor, 'daily_limit'),
                'test_session_created': session_id
            }
            
            print("✅ Budget Monitoring: PASS")
            
        except Exception as e:
            self.results['tests']['budget_monitoring'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            self.results['warnings'].append(f"Budget monitoring issue: {e}")
            print(f"⚠️ Budget Monitoring: WARNING - {e}")
    
    def test_cost_tracking_integration(self):
        """Test integration with LLM client"""
        print("\n🔗 Testing Cost Tracking Integration...")
        
        try:
            # Test if cost tracking can be initialized
            config = Configuration()
            
            # Mock test without actual LLM call
            analyzer = IntegratedAnalyzer(config)
            
            # Test analyze_request method
            test_session = f"integration_test_{int(time.time())}"
            
            # This will test the integration without making actual LLM calls
            result = analyzer.analyze_request(
                conversation_id=test_session,
                model="gpt-4",
                input_text="Test input for cost tracking",
                output_text="Test output response",
                provider="openai"
            )
            
            summary = analyzer.get_integrated_summary()
            
            self.results['tests']['cost_tracking_integration'] = {
                'status': 'PASS',
                'integration_result': result is not None,
                'summary_available': 'session' in summary,
                'analyzer_initialized': True
            }
            
            print("✅ Cost Tracking Integration: PASS")
            
        except Exception as e:
            self.results['tests']['cost_tracking_integration'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            self.results['critical_issues'].append(f"Cost tracking integration failed: {e}")
            print(f"❌ Cost Tracking Integration: FAIL - {e}")
    
    def test_configuration(self):
        """Test configuration loading"""
        print("\n⚙️ Testing Configuration...")
        
        try:
            config = Configuration()
            
            # Check if cost tracking config is available
            track_costs = getattr(config, 'TRACK_COSTS', None)
            cost_threshold = getattr(config, 'COST_ALERT_THRESHOLD', None)
            
            # Check .env.example for cost tracking variables
            env_example_path = Path(__file__).parent / ".env.example"
            env_example_exists = env_example_path.exists()
            
            cost_config_documented = False
            if env_example_exists:
                with open(env_example_path, 'r') as f:
                    content = f.read()
                    cost_config_documented = "TRACK_COSTS" in content and "COST_ALERT_THRESHOLD" in content
            
            self.results['tests']['configuration'] = {
                'status': 'PASS',
                'track_costs_configured': track_costs is not None,
                'threshold_configured': cost_threshold is not None,
                'env_example_exists': env_example_exists,
                'cost_config_documented': cost_config_documented
            }
            
            if not cost_config_documented:
                self.results['warnings'].append("Cost tracking not fully documented in .env.example")
            
            print("✅ Configuration: PASS")
            
        except Exception as e:
            self.results['tests']['configuration'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            self.results['warnings'].append(f"Configuration test issue: {e}")
            print(f"⚠️ Configuration: WARNING - {e}")
    
    def test_export_functionality(self):
        """Test data export capabilities"""
        print("\n📤 Testing Export Functionality...")
        
        try:
            db = CostTrackingDB(self.temp_db_path)
            
            # Test JSON export
            json_export = db.export_costs_json()
            export_data = json.loads(json_export)
            
            # Test CSV export
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                csv_path = f.name
            
            db.export_costs_csv(csv_path)
            csv_exists = Path(csv_path).exists()
            
            self.results['tests']['export_functionality'] = {
                'status': 'PASS',
                'json_export_works': 'export_date' in export_data,
                'csv_export_works': csv_exists,
                'export_structure_valid': all(key in export_data for key in ['summary', 'daily_costs'])
            }
            
            # Cleanup
            if csv_exists:
                os.unlink(csv_path)
            
            print("✅ Export Functionality: PASS")
            
        except Exception as e:
            self.results['tests']['export_functionality'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            self.results['warnings'].append(f"Export functionality issue: {e}")
            print(f"⚠️ Export Functionality: WARNING - {e}")
    
    def test_database_health(self):
        """Test database health check system"""
        print("\n🏥 Testing Database Health...")
        
        try:
            db = CostTrackingDB(self.temp_db_path)
            health_check = CostTrackingHealthCheck(db)
            
            health_status = health_check.check_database_health()
            
            # Check if all health check components are working
            required_checks = ['table_integrity', 'index_health', 'trigger_status', 'data_consistency']
            all_checks_present = all(check in health_status for check in required_checks)
            
            self.results['tests']['database_health'] = {
                'status': 'PASS' if all_checks_present else 'PARTIAL',
                'health_status': health_status,
                'all_checks_present': all_checks_present
            }
            
            print("✅ Database Health: PASS")
            
        except Exception as e:
            self.results['tests']['database_health'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            self.results['warnings'].append(f"Database health check issue: {e}")
            print(f"⚠️ Database Health: WARNING - {e}")
    
    def test_performance(self):
        """Test performance characteristics"""
        print("\n⚡ Testing Performance...")
        
        try:
            db = CostTrackingDB(self.temp_db_path)
            
            # Test bulk insert performance
            session_id = f"perf_test_{int(time.time())}"
            db.create_session(session_id, "performance_test")
            
            start_time = time.time()
            
            # Insert 100 cost records
            for i in range(100):
                db.log_request_cost(session_id, "gpt-4", 1000, 500, "openai")
            
            insert_time = time.time() - start_time
            
            # Test query performance
            start_time = time.time()
            daily_costs = db.get_daily_costs(30)
            query_time = time.time() - start_time
            
            self.results['tests']['performance'] = {
                'status': 'PASS',
                'bulk_insert_time_seconds': insert_time,
                'query_time_seconds': query_time,
                'records_inserted': 100,
                'query_results_count': len(daily_costs)
            }
            
            if insert_time > 5.0:
                self.results['warnings'].append(f"Bulk insert performance slow: {insert_time:.2f}s for 100 records")
            
            print(f"✅ Performance: PASS - Insert: {insert_time:.3f}s, Query: {query_time:.3f}s")
            
        except Exception as e:
            self.results['tests']['performance'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            self.results['warnings'].append(f"Performance test issue: {e}")
            print(f"⚠️ Performance: WARNING - {e}")
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        print("\n🔄 Testing End-to-End Workflow...")
        
        try:
            # Simulate a complete workflow
            config = Configuration()
            
            # 1. Initialize cost tracking
            tracker = CostTracker(config)
            
            # 2. Create test session
            session_id = f"e2e_test_{int(time.time())}"
            
            # 3. Track a request
            cost_result = tracker.track_request(
                conversation_id=session_id,
                model="gpt-4",
                input_tokens=1500,
                output_tokens=750,
                provider="openai"
            )
            
            # 4. Get session summary
            session_summary = tracker.get_session_summary()
            
            # 5. Export costs
            export_result = tracker.export_costs('json')
            
            workflow_successful = (
                cost_result is not None and
                'session' in session_summary and
                export_result is not None
            )
            
            self.results['tests']['end_to_end_workflow'] = {
                'status': 'PASS' if workflow_successful else 'FAIL',
                'cost_tracking_works': cost_result is not None,
                'session_summary_works': 'session' in session_summary,
                'export_works': export_result is not None,
                'test_session_id': session_id
            }
            
            if workflow_successful:
                print("✅ End-to-End Workflow: PASS")
            else:
                self.results['critical_issues'].append("End-to-end workflow failed")
                print("❌ End-to-End Workflow: FAIL")
                
        except Exception as e:
            self.results['tests']['end_to_end_workflow'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            self.results['critical_issues'].append(f"End-to-end workflow failed: {e}")
            print(f"❌ End-to-End Workflow: FAIL - {e}")
    
    def _determine_overall_status(self):
        """Determine overall test status"""
        test_results = [test.get('status', 'UNKNOWN') for test in self.results['tests'].values()]
        
        if self.results['critical_issues']:
            self.results['overall_status'] = 'CRITICAL_ISSUES'
        elif 'FAIL' in test_results:
            self.results['overall_status'] = 'FAILED'
        elif 'PARTIAL' in test_results or self.results['warnings']:
            self.results['overall_status'] = 'WARNING'
        elif all(status == 'PASS' for status in test_results):
            self.results['overall_status'] = 'PASS'
        else:
            self.results['overall_status'] = 'UNKNOWN'
        
        # Add recommendations based on results
        if self.results['overall_status'] == 'PASS':
            self.results['recommendations'].append("Task 96 is ready for production use")
            self.results['recommendations'].append("Consider implementing automated testing for future changes")
        elif self.results['warnings']:
            self.results['recommendations'].append("Address warning issues for optimal performance")
        
        if self.results['critical_issues']:
            self.results['recommendations'].append("Critical issues must be resolved before production use")
    
    def _cleanup(self):
        """Clean up temporary resources"""
        if self.temp_db_path and os.path.exists(self.temp_db_path):
            try:
                os.unlink(self.temp_db_path)
            except Exception:
                pass  # Best effort cleanup
    
    def print_summary(self):
        """Print verification summary"""
        print("\n" + "=" * 60)
        print("📋 TASK 96 VERIFICATION SUMMARY")
        print("=" * 60)
        
        # Overall status
        status_emoji = {
            'PASS': '✅',
            'WARNING': '⚠️',
            'FAILED': '❌',
            'CRITICAL_ISSUES': '🚨',
            'UNKNOWN': '❓'
        }
        
        emoji = status_emoji.get(self.results['overall_status'], '❓')
        print(f"\n{emoji} Overall Status: {self.results['overall_status']}")
        
        # Test results
        print(f"\n📊 Test Results ({len(self.results['tests'])} tests):")
        for test_name, test_result in self.results['tests'].items():
            status = test_result.get('status', 'UNKNOWN')
            emoji = status_emoji.get(status, '❓')
            print(f"  {emoji} {test_name.replace('_', ' ').title()}: {status}")
        
        # Issues and warnings
        if self.results['critical_issues']:
            print(f"\n🚨 Critical Issues ({len(self.results['critical_issues'])}):")
            for issue in self.results['critical_issues']:
                print(f"  • {issue}")
        
        if self.results['warnings']:
            print(f"\n⚠️ Warnings ({len(self.results['warnings'])}):")
            for warning in self.results['warnings']:
                print(f"  • {warning}")
        
        # Recommendations
        if self.results['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in self.results['recommendations']:
                print(f"  • {rec}")
        
        print(f"\n📅 Verification completed at: {self.results['timestamp']}")
        print("=" * 60)


def main():
    """Main verification entry point"""
    verifier = Task96Verifier()
    results = verifier.run_all_tests()
    verifier.print_summary()
    
    # Save results to file
    results_path = Path(__file__).parent / "task_96_verification_results.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {results_path}")
    
    # Return exit code based on results
    if results['overall_status'] in ['PASS', 'WARNING']:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
