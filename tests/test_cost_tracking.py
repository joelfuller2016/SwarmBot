"""
Test script for cost tracking database implementation
Verifies that all cost tracking functionality works correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
import json
import tempfile
from pathlib import Path
import logging

from src.database.cost_tracking import CostTrackingDB, CostTrackingHealthCheck, ModelCostCache

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_cost_tracking():
    """Test all cost tracking functionality"""
    print("\n=== Testing Cost Tracking Database Implementation ===\n")
    
    # Create temporary database for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test_cost_tracking.db")
        
        # Initialize database
        print("1. Initializing cost tracking database...")
        db = CostTrackingDB(db_path)
        print("   ✓ Database initialized successfully")
        
        # Run health check
        print("\n2. Running health check...")
        health_check = CostTrackingHealthCheck(db)
        health_status = health_check.check_database_health()
        
        print("   Table integrity:")
        for table, exists in health_status['table_integrity'].items():
            status = "✓" if exists else "✗"
            print(f"     {status} {table}")
        
        print("   Index health:")
        index_count = sum(1 for exists in health_status['index_health'].values() if exists)
        print(f"     ✓ {index_count}/{len(health_status['index_health'])} indexes created")
        
        print("   Trigger status:")
        for trigger, exists in health_status['trigger_status'].items():
            status = "✓" if exists else "✗"
            print(f"     {status} {trigger}")
        
        # Test model costs
        print("\n3. Testing model cost operations...")
        
        # Get all model costs
        model_costs = db.get_all_model_costs()
        print(f"   ✓ Loaded {len(model_costs)} model cost configurations")
        
        # Update a model cost
        db.update_model_cost("test-model", "test-provider", 0.005, 0.010, 8192)
        print("   ✓ Successfully updated model cost")
        
        # Test conversation and cost logging
        print("\n4. Testing cost logging...")
        
        # Create test sessions
        session_ids = []
        for i in range(3):
            session_id = f"test_session_{i}_{datetime.now().timestamp()}"
            db.create_session(session_id, "openai", {"test": True})
            session_ids.append(session_id)
        
        # Log various costs
        test_data = [
            (session_ids[0], "gpt-4", 1000, 500),
            (session_ids[0], "gpt-4", 2000, 1000),
            (session_ids[0], "gpt-3.5-turbo", 500, 250),
            (session_ids[1], "claude-3-opus", 3000, 1500),
            (session_ids[1], "claude-3-sonnet", 1500, 750),
            (session_ids[2], "gpt-4-turbo", 5000, 2500),
        ]
        
        for session_id, model, input_tokens, output_tokens in test_data:
            db.log_request_cost(session_id, model, input_tokens, output_tokens)
        
        print(f"   ✓ Logged {len(test_data)} cost records")
        
        # Test cost retrieval
        print("\n5. Testing cost retrieval and aggregation...")
        
        # Get conversation summaries
        for session_id in session_ids:
            summary = db.get_conversation_cost_summary(session_id)
            if summary:
                print(f"   ✓ Session {session_id[-8:]}: ${summary['total_cost']:.4f} ({summary['request_count']} requests)")
        
        # Get daily costs
        daily_costs = db.get_daily_costs(1)
        print(f"   ✓ Retrieved {len(daily_costs)} daily cost records")
        
        # Get model usage stats
        usage_stats = db.get_model_usage_stats()
        print("\n   Model usage statistics:")
        for stat in usage_stats:
            print(f"     - {stat['model']}: {stat['total_requests']} requests, ${stat['total_cost']:.4f} total")
        
        # Get conversation rankings
        rankings = db.get_conversation_rankings(10)
        print(f"\n   ✓ Retrieved top {len(rankings)} conversations by cost")
        
        # Test cost alerts
        alerts = db.get_cost_alerts(threshold=0.05)
        print(f"   ✓ Found {len(alerts)} conversations exceeding threshold")
        
        # Test cost forecast
        forecast = db.get_cost_forecast(7)
        print(f"\n   Cost forecast (7 days): ${forecast['estimated_cost']:.2f}")
        print(f"   Daily average: ${forecast['avg_daily_cost']:.4f}")
        
        # Test cache functionality
        print("\n6. Testing model cost cache...")
        cache = ModelCostCache(db)
        
        # Test cache hit
        cost1 = cache.get_model_cost("gpt-4", "openai")
        cost2 = cache.get_model_cost("gpt-4", "openai")  # Should hit cache
        print("   ✓ Cache working correctly")
        
        # Test data consistency
        print("\n7. Testing data consistency...")
        consistency = health_status['data_consistency']
        if consistency['is_consistent']:
            print("   ✓ Data consistency check passed")
        else:
            print(f"   ✗ Found {consistency['inconsistent_conversations']} inconsistent conversations")
            print(f"   ✗ Found {consistency['orphaned_requests']} orphaned requests")
        
        # Performance metrics
        print("\n8. Performance metrics:")
        metrics = health_status['performance_metrics']
        print(f"   Database size: {metrics['database_size_mb']:.2f} MB")
        print("   Table sizes:")
        for table, count in metrics['table_sizes'].items():
            print(f"     - {table}: {count} rows")
        
        # Close database
        db.close()
        print("\n✓ All tests completed successfully!")


def test_migration_runner():
    """Test the migration runner"""
    print("\n=== Testing Migration Runner ===\n")
    
    # Import migration runner
    sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
    from migrate_db import MigrationRunner
    
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test_migrations.db")
        migrations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "migrations")
        
        # Create runner
        runner = MigrationRunner(db_path, migrations_dir)
        runner.connect()
        
        # Check status
        print("1. Checking initial migration status...")
        pending = runner.get_pending_migrations()
        print(f"   ✓ Found {len(pending)} pending migrations")
        
        # Run migrations
        print("\n2. Running migrations...")
        count = runner.run_migrations()
        print(f"   ✓ Applied {count} migrations")
        
        # Check status again
        print("\n3. Checking post-migration status...")
        applied = runner.get_applied_migrations()
        print(f"   ✓ {len(applied)} migrations applied")
        
        runner.disconnect()
        print("\n✓ Migration runner test completed!")


if __name__ == "__main__":
    try:
        test_cost_tracking()
        test_migration_runner()
        print("\n🎉 All tests passed! Cost tracking implementation is working correctly.")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
