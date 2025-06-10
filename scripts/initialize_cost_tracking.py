#!/usr/bin/env python3
"""
Run database migrations for cost tracking system
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.cost_tracking import CostTrackingDB
from src.core.cost_updater import CostUpdater
from src.config import Configuration

def main():
    """Run migrations and initialize cost data"""
    print("🚀 Running cost tracking database migrations...")
    
    # Initialize configuration
    config = Configuration()
    
    # Initialize database (this will run migrations)
    db_path = config.get('DATABASE_PATH', 'data/swarmbot_chats.db')
    print(f"Database path: {db_path}")
    
    # Ensure data directory exists
    data_dir = Path(db_path).parent
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize cost tracking database
    db = CostTrackingDB(db_path)
    print("✅ Database initialized and migrations run")
    
    # Initialize cost updater and load initial costs
    updater = CostUpdater(config, db)
    
    # Update costs from static data
    print("📊 Loading initial model cost data...")
    for provider in updater.STATIC_COSTS.keys():
        updater._update_from_static(provider)
        print(f"   ✓ Loaded costs for {provider}")
    
    # Validate the data
    validation = updater.validate_costs()
    print(f"\n📋 Validation Results:")
    print(f"   Valid entries: {len(validation['valid'])}")
    print(f"   Warnings: {len(validation['warnings'])}")
    
    if validation['warnings']:
        print("\n⚠️  Warnings:")
        for warning in validation['warnings'][:5]:  # Show first 5 warnings
            print(f"   - {warning['model']} ({warning['provider']}): {warning['issue']}")
    
    # Run health check
    from src.database.cost_tracking import CostTrackingHealthCheck
    health_check = CostTrackingHealthCheck(db)
    health = health_check.check_database_health()
    
    print(f"\n🏥 Health Check Results:")
    print(f"   Tables: {all(health['table_integrity'].values())}")
    print(f"   Indexes: {all(health['index_health'].values())}")
    print(f"   Triggers: {all(health['trigger_status'].values())}")
    print(f"   Data Consistency: {health['data_consistency']['is_consistent']}")
    
    # Close database
    db.close()
    
    print("\n✅ Cost tracking system initialized successfully!")
    print("   - Database migrations completed")
    print("   - Model costs loaded")
    print("   - System health verified")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
