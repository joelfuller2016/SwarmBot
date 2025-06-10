"""
Test script for cost tracking database schema implementation
Verifies that all migrations run correctly and the schema functions as expected
"""

import sys
import os
import sqlite3
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.cost_tracking import CostTrackingDB, CostTrackingHealthCheck
from src.core.cost_tracker import CostTracker, ModelCost, RequestCost
from src.config import Configuration


def test_database_creation():
    """Test database creation and migration execution"""
    print("Testing database creation and migrations...")
    
    # Create test database
    test_db_path = "test_cost_tracking.db"
    if Path(test_db_path).exists():
        Path(test_db_path).unlink()
    
    # Initialize database
    db = CostTrackingDB(test_db_path)
    
    # Check if tables were created
    cursor = db.conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        ORDER BY name
    """)
    
    tables = [row[0] for row in cursor.fetchall()]
    expected_tables = ['chat_messages', 'chat_sessions', 'conversation_costs', 
                      'migration_log', 'model_costs', 'query_performance_log', 'request_costs']
    
    print(f"Created tables: {tables}")
    
    # Verify all expected tables exist
    for table in expected_tables:
        if table in tables:
            print(f"✓ Table '{table}' created successfully")
        else:
            print(f"✗ Table '{table}' missing!")
    
    # Check migrations
    cursor.execute("SELECT * FROM migration_log ORDER BY applied_at")
    migrations = cursor.fetchall()
    print(f"\nApplied migrations: {len(migrations)}")
    for migration in migrations:
        print(f"  - {migration['migration_id']}: {migration['description']}")
    
    return db


def test_model_costs(db: CostTrackingDB):
    """Test model cost operations"""
    print("\n\nTesting model cost operations...")
    
    # Check if initial data was loaded
    costs = db.get_all_model_costs()
    print(f"Loaded {len(costs)} model costs")
    
    # Display a few examples
    for cost in costs[:3]:
        print(f"  - {cost['provider']}:{cost['model_name']} - "
              f"Input: ${cost['input_cost_per_1k']}/1k, "
              f"Output: ${cost['output_cost_per_1k']}/1k")
    
    # Test updating a model cost
    db.update_model_cost(
        model_name="test-model",
        provider="test-provider",
        input_cost_per_1k=0.01,
        output_cost_per_1k=0.02,
        context_window=4096
    )
    print("✓ Successfully added test model cost")
    
    # Verify the update
    test_cost = db._get_model_costs("test-model", "test-provider")
    print(f"✓ Retrieved test model: {test_cost}")


def test_request_logging(db: CostTrackingDB):
    """Test request cost logging"""
    print("\n\nTesting request cost logging...")
    
    # Create a test conversation
    conversation_id = f"test_conv_{datetime.now().timestamp()}"
    db.create_session(conversation_id, "openai", {"test": True})
    
    # Log some requests
    test_requests = [
        ("gpt-4", 1000, 500),
        ("gpt-3.5-turbo", 2000, 1000),
        ("gpt-4-turbo", 1500, 750)
    ]
    
    for model, input_tokens, output_tokens in test_requests:
        db.log_request_cost(
            conversation_id=conversation_id,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            provider="openai"
        )
        print(f"✓ Logged request for {model}: {input_tokens} in, {output_tokens} out")
    
    # Check conversation summary
    summary = db.get_conversation_cost_summary(conversation_id)
    print(f"\nConversation summary:")
    print(f"  - Total cost: ${summary['total_cost']:.4f}")
    print(f"  - Request count: {summary['request_count']}")
    print(f"  - Duration: {summary['start_time']} to {summary['last_update']}")
    
    return conversation_id


def test_analytics(db: CostTrackingDB):
    """Test analytics and reporting functions"""
    print("\n\nTesting analytics functions...")
    
    # Daily costs
    daily_costs = db.get_daily_costs(7)
    print(f"\nDaily costs (last 7 days): {len(daily_costs)} entries")
    for day in daily_costs[:3]:
        print(f"  - {day['date']}: ${day['total_cost']:.4f} ({day['request_count']} requests)")
    
    # Model usage stats
    usage_stats = db.get_model_usage_stats()
    print(f"\nModel usage statistics:")
    for stat in usage_stats[:3]:
        print(f"  - {stat['model']}: {stat['total_requests']} requests, "
              f"${stat['total_cost']:.4f} total, "
              f"${stat['avg_cost_per_request']:.4f} avg")
    
    # Cost rankings
    rankings = db.get_conversation_rankings(5)
    print(f"\nTop conversations by cost:")
    for rank in rankings:
        print(f"  - {rank['conversation_id']}: ${rank['total_cost']:.4f} "
              f"({rank['request_count']} requests)")
    
    # Cost forecast
    forecast = db.get_cost_forecast(30)
    print(f"\nCost forecast (30 days):")
    print(f"  - Estimated: ${forecast['estimated_cost']:.2f}")
    print(f"  - Daily average: ${forecast['avg_daily_cost']:.2f}")


def test_health_check(db: CostTrackingDB):
    """Test database health check"""
    print("\n\nTesting database health check...")
    
    health_check = CostTrackingHealthCheck(db)
    health = health_check.check_database_health()
    
    print("Database health status:")
    print(f"  - Table integrity: {json.dumps(health['table_integrity'], indent=4)}")
    print(f"  - Data consistency: {health['data_consistency']}")
    print(f"  - Performance metrics: {json.dumps(health['performance_metrics'], indent=4)}")


def test_cost_tracker():
    """Test the CostTracker class"""
    print("\n\nTesting CostTracker class...")
    
    # Create config
    config = Configuration()
    config.config['TRACK_COSTS'] = True
    config.config['COST_ALERT_THRESHOLD'] = 1.0  # Low threshold for testing
    
    # Initialize tracker
    tracker = CostTracker(config)
    
    # Track some requests
    conversation_id = f"tracker_test_{datetime.now().timestamp()}"
    
    for i in range(5):
        request_cost = tracker.track_request(
            conversation_id=conversation_id,
            model="gpt-4",
            input_tokens=100 + i * 50,
            output_tokens=200 + i * 100,
            provider="openai"
        )
        
        if request_cost:
            print(f"✓ Tracked request {i+1}: ${request_cost.total_cost:.4f}")
    
    # Get session summary
    summary = tracker.get_session_summary()
    print(f"\nSession summary:")
    print(f"  - Total cost: ${summary['session_total']:.4f}")
    print(f"  - Request count: {summary['request_count']}")
    print(f"  - Average cost: ${summary['average_cost']:.4f}")
    
    # Get monthly summary
    monthly = tracker.get_monthly_summary()
    print(f"\nMonthly summary:")
    print(f"  - Current month cost: ${monthly['current_month_cost']:.4f}")
    print(f"  - Budget used: {monthly['percentage_used']:.1f}%")
    
    return tracker


def test_exports(db: CostTrackingDB, tracker: CostTracker):
    """Test export functionality"""
    print("\n\nTesting export functions...")
    
    # Test JSON export
    json_export = db.export_costs_json()
    export_data = json.loads(json_export)
    print(f"✓ JSON export successful: {len(json_export)} characters")
    print(f"  - Contains {len(export_data['daily_costs'])} daily cost entries")
    print(f"  - Contains {len(export_data['model_usage'])} model usage entries")
    
    # Test CSV export
    csv_path = "test_costs_export.csv"
    db.export_costs_csv(csv_path)
    if Path(csv_path).exists():
        print(f"✓ CSV export successful: {csv_path}")
        Path(csv_path).unlink()  # Clean up
    
    # Test tracker export
    tracker_export = tracker.export_costs('json')
    print(f"✓ Tracker JSON export successful: {len(tracker_export)} characters")


def cleanup(db_path: str):
    """Clean up test database"""
    print("\n\nCleaning up...")
    if Path(db_path).exists():
        Path(db_path).unlink()
        print(f"✓ Removed test database: {db_path}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Cost Tracking Database Schema Test")
    print("=" * 60)
    
    try:
        # Test database creation
        db = test_database_creation()
        
        # Test model costs
        test_model_costs(db)
        
        # Test request logging
        conversation_id = test_request_logging(db)
        
        # Test analytics
        test_analytics(db)
        
        # Test health check
        test_health_check(db)
        
        # Test cost tracker
        tracker = test_cost_tracker()
        
        # Test exports
        test_exports(db, tracker)
        
        # Clean up
        db.close()
        cleanup("test_cost_tracking.db")
        
        print("\n" + "=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        
        # Clean up on error
        try:
            cleanup("test_cost_tracking.db")
        except:
            pass


if __name__ == "__main__":
    main()
