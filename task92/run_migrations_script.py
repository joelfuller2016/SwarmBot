#!/usr/bin/env python3
"""
Database Migration Runner for SwarmBot Cost Tracking
Applies SQL migrations in order and tracks applied migrations
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime
import argparse
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MigrationRunner:
    """Handles database migrations for the cost tracking system"""
    
    def __init__(self, db_path: str, migrations_dir: str):
        self.db_path = db_path
        self.migrations_dir = Path(migrations_dir)
        self.conn = None
        
    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
    
    def ensure_migration_table(self):
        """Create migration tracking table if it doesn't exist"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS migration_log (
                migration_id TEXT PRIMARY KEY,
                applied_at DATETIME NOT NULL,
                description TEXT
            )
        """)
        self.conn.commit()
    
    def get_applied_migrations(self) -> set:
        """Get set of already applied migration IDs"""
        cursor = self.conn.execute("SELECT migration_id FROM migration_log")
        return {row['migration_id'] for row in cursor}
    
    def get_pending_migrations(self) -> list:
        """Get list of migrations that haven't been applied yet"""
        applied = self.get_applied_migrations()
        
        # Find all SQL files that aren't rollback scripts
        migration_files = []
        for file in sorted(self.migrations_dir.glob("*.sql")):
            if not file.stem.endswith("_rollback"):
                migration_id = file.stem
                if migration_id not in applied:
                    migration_files.append(file)
        
        return migration_files
    
    def apply_migration(self, migration_file: Path) -> bool:
        """Apply a single migration file"""
        migration_id = migration_file.stem
        logger.info(f"Applying migration: {migration_id}")
        
        try:
            # Read and execute the migration
            with open(migration_file, 'r', encoding='utf-8') as f:
                sql = f.read()
            
            # Execute the migration in a transaction
            self.conn.executescript(sql)
            
            logger.info(f"Successfully applied migration: {migration_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply migration {migration_id}: {e}")
            self.conn.rollback()
            return False
    
    def rollback_migration(self, migration_id: str) -> bool:
        """Rollback a specific migration"""
        rollback_file = self.migrations_dir / f"{migration_id}_rollback.sql"
        
        if not rollback_file.exists():
            logger.error(f"Rollback file not found: {rollback_file}")
            return False
        
        logger.info(f"Rolling back migration: {migration_id}")
        
        try:
            with open(rollback_file, 'r', encoding='utf-8') as f:
                sql = f.read()
            
            self.conn.executescript(sql)
            logger.info(f"Successfully rolled back migration: {migration_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback migration {migration_id}: {e}")
            self.conn.rollback()
            return False
    
    def run_all_pending(self) -> tuple:
        """Run all pending migrations"""
        self.ensure_migration_table()
        pending = self.get_pending_migrations()
        
        if not pending:
            logger.info("No pending migrations to apply")
            return 0, 0
        
        logger.info(f"Found {len(pending)} pending migrations")
        
        success_count = 0
        for migration_file in pending:
            if self.apply_migration(migration_file):
                success_count += 1
            else:
                logger.error(f"Migration failed, stopping at {migration_file.stem}")
                break
        
        return success_count, len(pending) - success_count
    
    def list_migrations(self):
        """List all migrations and their status"""
        self.ensure_migration_table()
        applied = self.get_applied_migrations()
        
        print("\nMigration Status:")
        print("-" * 60)
        
        # Get all migration files
        all_migrations = []
        for file in sorted(self.migrations_dir.glob("*.sql")):
            if not file.stem.endswith("_rollback"):
                all_migrations.append(file.stem)
        
        # Also include applied migrations that might not have files anymore
        for migration_id in applied:
            if migration_id not in all_migrations:
                all_migrations.append(migration_id)
        
        # Sort and display
        for migration_id in sorted(all_migrations):
            status = "✓ Applied" if migration_id in applied else "⏳ Pending"
            print(f"{migration_id:<40} {status}")
        
        print("-" * 60)
        print(f"Total: {len(all_migrations)} migrations, "
              f"{len(applied)} applied, "
              f"{len(all_migrations) - len(applied)} pending")
    
    def verify_schema(self):
        """Verify that all expected tables and indexes exist"""
        print("\nSchema Verification:")
        print("-" * 60)
        
        # Check tables
        expected_tables = [
            'migration_log',
            'model_costs', 
            'request_costs', 
            'conversation_costs',
            'query_performance_log'
        ]
        
        cursor = self.conn.execute("""
            SELECT name FROM sqlite_master WHERE type='table'
        """)
        existing_tables = {row['name'] for row in cursor}
        
        print("\nTables:")
        for table in expected_tables:
            status = "✓" if table in existing_tables else "✗"
            print(f"  {status} {table}")
        
        # Check indexes
        expected_indexes = [
            'idx_model_costs_provider',
            'idx_model_costs_last_updated',
            'idx_request_costs_conversation_id',
            'idx_request_costs_timestamp',
            'idx_request_costs_model',
            'idx_request_costs_conv_time',
            'idx_conversation_costs_start_time',
            'idx_conversation_costs_last_update',
            'idx_conversation_costs_total_cost'
        ]
        
        cursor = self.conn.execute("""
            SELECT name FROM sqlite_master WHERE type='index'
        """)
        existing_indexes = {row['name'] for row in cursor}
        
        print("\nIndexes:")
        for index in expected_indexes:
            status = "✓" if index in existing_indexes else "✗"
            print(f"  {status} {index}")
        
        # Check views
        expected_views = [
            'daily_cost_summary',
            'conversation_cost_ranking',
            'model_usage_stats',
            'high_cost_conversations',
            'token_usage_patterns'
        ]
        
        cursor = self.conn.execute("""
            SELECT name FROM sqlite_master WHERE type='view'
        """)
        existing_views = {row['name'] for row in cursor}
        
        print("\nViews:")
        for view in expected_views:
            status = "✓" if view in existing_views else "✗"
            print(f"  {status} {view}")
        
        # Check triggers
        cursor = self.conn.execute("""
            SELECT name FROM sqlite_master WHERE type='trigger'
        """)
        existing_triggers = {row['name'] for row in cursor}
        
        print("\nTriggers:")
        trigger_name = 'update_conversation_costs_on_insert'
        status = "✓" if trigger_name in existing_triggers else "✗"
        print(f"  {status} {trigger_name}")


def main():
    parser = argparse.ArgumentParser(
        description="Database migration runner for SwarmBot cost tracking"
    )
    parser.add_argument(
        'command',
        choices=['migrate', 'rollback', 'list', 'verify'],
        help='Command to execute'
    )
    parser.add_argument(
        '--db-path',
        default='swarmbot.db',
        help='Path to the SQLite database file'
    )
    parser.add_argument(
        '--migrations-dir',
        default='migrations',
        help='Directory containing migration files'
    )
    parser.add_argument(
        '--migration-id',
        help='Specific migration ID for rollback command'
    )
    
    args = parser.parse_args()
    
    # Validate migrations directory
    migrations_dir = Path(args.migrations_dir)
    if not migrations_dir.exists():
        logger.error(f"Migrations directory not found: {migrations_dir}")
        sys.exit(1)
    
    # Execute command
    with MigrationRunner(args.db_path, args.migrations_dir) as runner:
        if args.command == 'migrate':
            success, failed = runner.run_all_pending()
            if failed > 0:
                sys.exit(1)
                
        elif args.command == 'rollback':
            if not args.migration_id:
                logger.error("--migration-id required for rollback command")
                sys.exit(1)
            if not runner.rollback_migration(args.migration_id):
                sys.exit(1)
                
        elif args.command == 'list':
            runner.list_migrations()
            
        elif args.command == 'verify':
            runner.verify_schema()


if __name__ == '__main__':
    main()