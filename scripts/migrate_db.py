"""
Database migration runner for SwarmBot
Manages the execution of SQL migrations for database schema updates
"""

import sqlite3
import sys
from pathlib import Path
import logging
from typing import List, Optional
import argparse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MigrationRunner:
    """Handles database migration execution"""
    
    def __init__(self, db_path: str, migrations_dir: str = None):
        self.db_path = db_path
        self.migrations_dir = Path(migrations_dir) if migrations_dir else Path(__file__).parent / "migrations"
        self.conn = None
        
    def connect(self):
        """Connect to the database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        logger.info(f"Connected to database: {self.db_path}")
        
    def disconnect(self):
        """Disconnect from the database"""
        if self.conn:
            self.conn.close()
            logger.info("Disconnected from database")
    
    def ensure_migration_table(self):
        """Ensure the migration_log table exists"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS migration_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                migration_id TEXT UNIQUE NOT NULL,
                applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
        """)
        self.conn.commit()
        
    def get_applied_migrations(self) -> List[str]:
        """Get list of already applied migrations"""
        self.ensure_migration_table()
        cursor = self.conn.cursor()
        cursor.execute("SELECT migration_id FROM migration_log ORDER BY applied_at")
        return [row['migration_id'] for row in cursor.fetchall()]
    
    def get_pending_migrations(self) -> List[Path]:
        """Get list of migrations that need to be applied"""
        applied = set(self.get_applied_migrations())
        
        # Get all migration files (excluding rollback files)
        migration_files = []
        for file in sorted(self.migrations_dir.glob("*.sql")):
            if not file.name.endswith("_rollback.sql"):
                migration_id = file.stem
                if migration_id not in applied:
                    migration_files.append(file)
        
        return migration_files
    
    def apply_migration(self, migration_file: Path) -> bool:
        """Apply a single migration"""
        migration_id = migration_file.stem
        logger.info(f"Applying migration: {migration_id}")
        
        try:
            # Read migration content
            with open(migration_file, 'r', encoding='utf-8') as f:
                migration_sql = f.read()
            
            # Execute migration
            cursor = self.conn.cursor()
            cursor.executescript(migration_sql)
            
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
            # Read rollback content
            with open(rollback_file, 'r', encoding='utf-8') as f:
                rollback_sql = f.read()
            
            # Execute rollback
            cursor = self.conn.cursor()
            cursor.executescript(rollback_sql)
            
            logger.info(f"Successfully rolled back migration: {migration_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback migration {migration_id}: {e}")
            self.conn.rollback()
            return False
    
    def run_migrations(self) -> int:
        """Run all pending migrations"""
        pending = self.get_pending_migrations()
        
        if not pending:
            logger.info("No pending migrations")
            return 0
        
        logger.info(f"Found {len(pending)} pending migration(s)")
        
        applied_count = 0
        for migration_file in pending:
            if self.apply_migration(migration_file):
                applied_count += 1
            else:
                logger.error(f"Migration failed, stopping at {migration_file.stem}")
                break
        
        logger.info(f"Applied {applied_count} migration(s)")
        return applied_count
    
    def status(self):
        """Show migration status"""
        applied = self.get_applied_migrations()
        pending = self.get_pending_migrations()
        
        print("\n=== Migration Status ===")
        print(f"Database: {self.db_path}")
        print(f"Applied migrations: {len(applied)}")
        
        if applied:
            print("\nApplied:")
            cursor = self.conn.cursor()
            for migration_id in applied:
                cursor.execute(
                    "SELECT applied_at, description FROM migration_log WHERE migration_id = ?",
                    (migration_id,)
                )
                row = cursor.fetchone()
                print(f"  - {migration_id} (applied: {row['applied_at']})")
                if row['description']:
                    print(f"    {row['description']}")
        
        print(f"\nPending migrations: {len(pending)}")
        if pending:
            print("\nPending:")
            for migration_file in pending:
                print(f"  - {migration_file.stem}")
        
        print()


def main():
    """Main entry point for the migration runner"""
    parser = argparse.ArgumentParser(description="SwarmBot Database Migration Runner")
    parser.add_argument(
        "--db", 
        default="data/swarmbot_chats.db",
        help="Path to the database file"
    )
    parser.add_argument(
        "--migrations-dir",
        default=None,
        help="Path to migrations directory (default: ./migrations)"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show migration status"
    )
    parser.add_argument(
        "--rollback",
        metavar="MIGRATION_ID",
        help="Rollback a specific migration"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply all pending migrations"
    )
    
    args = parser.parse_args()
    
    # Create runner
    runner = MigrationRunner(args.db, args.migrations_dir)
    
    try:
        runner.connect()
        
        if args.status:
            runner.status()
        elif args.rollback:
            if runner.rollback_migration(args.rollback):
                print(f"Successfully rolled back migration: {args.rollback}")
            else:
                print(f"Failed to rollback migration: {args.rollback}")
                sys.exit(1)
        elif args.apply:
            count = runner.run_migrations()
            print(f"Applied {count} migration(s)")
        else:
            # Default action is to show status
            runner.status()
            
    finally:
        runner.disconnect()


if __name__ == "__main__":
    main()
