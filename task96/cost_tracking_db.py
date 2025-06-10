"""
Cost Tracking Database Extension for SwarmBot
Implements Task 96.2: Database schema for LLM API cost tracking
"""

import sqlite3
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Optional, Tuple, Any
import os
import json
from pathlib import Path

# Assuming DatabaseLogger exists in the project
from src.database.logger import DatabaseLogger


class ModelCostCache:
    """Cache for frequently accessed model costs"""
    
    def __init__(self, db: 'CostTrackingDB'):
        self.db = db
        self._cache: Dict[str, Dict] = {}
        self._last_refresh = datetime.now()
        self._refresh_interval = timedelta(hours=1)
    
    @lru_cache(maxsize=128)
    def get_model_cost(self, model_name: str, provider: str) -> Optional[Dict]:
        """Get cached model cost with automatic refresh"""
        if datetime.now() - self._last_refresh > self._refresh_interval:
            self._refresh_cache()
        
        key = f"{provider}:{model_name}"
        return self._cache.get(key, self._fetch_and_cache(model_name, provider))
    
    def _fetch_and_cache(self, model_name: str, provider: str) -> Optional[Dict]:
        """Fetch model cost from database and cache it"""
        cost = self.db.get_model_cost(model_name, provider)
        if cost:
            key = f"{provider}:{model_name}"
            self._cache[key] = cost
        return cost
    
    def _refresh_cache(self):
        """Refresh entire cache from database"""
        costs = self.db.get_all_model_costs()
        self._cache = {f"{c['provider']}:{c['model_name']}": c for c in costs}
        self._last_refresh = datetime.now()
        self.get_model_cost.cache_clear()


class CostTrackingDB(DatabaseLogger):
    """Extension of DatabaseLogger for cost tracking operations"""
    
    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.cost_cache = ModelCostCache(self)
        self._initialize_cost_tracking_schema()
        self._ensure_sqlite_optimizations()
    
    def _initialize_cost_tracking_schema(self):
        """Initialize the cost tracking schema by running migrations"""
        migrations_dir = Path(__file__).parent / "migrations"
        if not migrations_dir.exists():
            # If migrations directory doesn't exist in the expected location,
            # run the schema creation directly
            self._run_direct_schema_creation()
        else:
            self._run_migrations(migrations_dir)
    
    def _run_direct_schema_creation(self):
        """Run schema creation directly if migrations directory is not available"""
        # This is the same as 001_cost_tracking_schema.sql
        schema_sql = """
        CREATE TABLE IF NOT EXISTS migration_log (
            migration_id TEXT PRIMARY KEY,
            applied_at DATETIME NOT NULL,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS model_costs (
            model_name TEXT NOT NULL,
            provider TEXT NOT NULL,
            input_cost_per_1k REAL NOT NULL CHECK (input_cost_per_1k >= 0),
            output_cost_per_1k REAL NOT NULL CHECK (output_cost_per_1k >= 0),
            context_window INTEGER NOT NULL CHECK (context_window > 0),
            last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (model_name, provider)
        );

        CREATE TABLE IF NOT EXISTS request_costs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            model TEXT NOT NULL,
            input_tokens INTEGER NOT NULL CHECK (input_tokens >= 0),
            output_tokens INTEGER NOT NULL CHECK (output_tokens >= 0),
            input_cost REAL NOT NULL CHECK (input_cost >= 0),
            output_cost REAL NOT NULL CHECK (output_cost >= 0),
            total_cost REAL NOT NULL CHECK (total_cost >= 0)
        );

        CREATE TABLE IF NOT EXISTS conversation_costs (
            conversation_id TEXT PRIMARY KEY,
            start_time DATETIME NOT NULL,
            last_update DATETIME NOT NULL,
            total_cost REAL NOT NULL DEFAULT 0 CHECK (total_cost >= 0),
            request_count INTEGER NOT NULL DEFAULT 0 CHECK (request_count >= 0)
        );

        CREATE INDEX IF NOT EXISTS idx_model_costs_provider ON model_costs(provider);
        CREATE INDEX IF NOT EXISTS idx_model_costs_last_updated ON model_costs(last_updated);
        CREATE INDEX IF NOT EXISTS idx_request_costs_conversation_id ON request_costs(conversation_id);
        CREATE INDEX IF NOT EXISTS idx_request_costs_timestamp ON request_costs(timestamp);
        CREATE INDEX IF NOT EXISTS idx_request_costs_model ON request_costs(model);
        CREATE INDEX IF NOT EXISTS idx_request_costs_conv_time ON request_costs(conversation_id, timestamp);
        CREATE INDEX IF NOT EXISTS idx_conversation_costs_start_time ON conversation_costs(start_time);
        CREATE INDEX IF NOT EXISTS idx_conversation_costs_last_update ON conversation_costs(last_update);
        CREATE INDEX IF NOT EXISTS idx_conversation_costs_total_cost ON conversation_costs(total_cost DESC);

        CREATE TRIGGER IF NOT EXISTS update_conversation_costs_on_insert
        AFTER INSERT ON request_costs
        BEGIN
            INSERT INTO conversation_costs (conversation_id, start_time, last_update, total_cost, request_count)
            VALUES (NEW.conversation_id, NEW.timestamp, NEW.timestamp, NEW.total_cost, 1)
            ON CONFLICT(conversation_id) DO UPDATE SET
                last_update = NEW.timestamp,
                total_cost = total_cost + NEW.total_cost,
                request_count = request_count + 1;
        END;
        """
        
        with self.get_connection() as conn:
            conn.executescript(schema_sql)
    
    def _ensure_sqlite_optimizations(self):
        """Apply SQLite optimizations for better performance"""
        optimizations = [
            "PRAGMA journal_mode = WAL",
            "PRAGMA synchronous = NORMAL",
            "PRAGMA foreign_keys = ON",
            "PRAGMA cache_size = -10000",  # 10MB cache
            "PRAGMA optimize"
        ]
        
        with self.get_connection() as conn:
            for pragma in optimizations:
                conn.execute(pragma)
    
    def _run_migrations(self, migrations_dir: Path):
        """Run database migrations from the migrations directory"""
        with self.get_connection() as conn:
            # Create migration log table if it doesn't exist
            conn.execute("""
                CREATE TABLE IF NOT EXISTS migration_log (
                    migration_id TEXT PRIMARY KEY,
                    applied_at DATETIME NOT NULL,
                    description TEXT
                )
            """)
            
            # Get applied migrations
            applied = set(row[0] for row in conn.execute(
                "SELECT migration_id FROM migration_log"
            ).fetchall())
            
            # Find and apply pending migrations
            migration_files = sorted(migrations_dir.glob("*.sql"))
            for migration_file in migration_files:
                if migration_file.stem.endswith("_rollback"):
                    continue
                    
                migration_id = migration_file.stem
                if migration_id not in applied:
                    print(f"Applying migration: {migration_id}")
                    with open(migration_file, 'r') as f:
                        conn.executescript(f.read())
    
    def log_request_cost(self, conversation_id: str, model: str, 
                        input_tokens: int, output_tokens: int,
                        provider: str = None) -> None:
        """Log the cost of a single API request"""
        # Try to determine provider from model name if not provided
        if not provider:
            provider = self._infer_provider(model)
        
        model_costs = self.cost_cache.get_model_cost(model, provider)
        if not model_costs:
            # If model costs not found, log with zero cost
            input_cost = output_cost = total_cost = 0.0
        else:
            input_cost = (input_tokens / 1000) * model_costs['input_cost_per_1k']
            output_cost = (output_tokens / 1000) * model_costs['output_cost_per_1k']
            total_cost = input_cost + output_cost
        
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO request_costs 
                (conversation_id, model, input_tokens, output_tokens, 
                 input_cost, output_cost, total_cost)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (conversation_id, model, input_tokens, output_tokens,
                  input_cost, output_cost, total_cost))
    
    def get_model_cost(self, model_name: str, provider: str) -> Optional[Dict]:
        """Get cost information for a specific model"""
        with self.get_connection() as conn:
            row = conn.execute("""
                SELECT model_name, provider, input_cost_per_1k, output_cost_per_1k,
                       context_window, last_updated
                FROM model_costs
                WHERE model_name = ? AND provider = ?
            """, (model_name, provider)).fetchone()
            
            if row:
                return {
                    'model_name': row[0],
                    'provider': row[1],
                    'input_cost_per_1k': row[2],
                    'output_cost_per_1k': row[3],
                    'context_window': row[4],
                    'last_updated': row[5]
                }
        return None
    
    def get_all_model_costs(self) -> List[Dict]:
        """Get all model costs from the database"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT model_name, provider, input_cost_per_1k, output_cost_per_1k,
                       context_window, last_updated
                FROM model_costs
                ORDER BY provider, model_name
            """).fetchall()
            
            return [
                {
                    'model_name': row[0],
                    'provider': row[1],
                    'input_cost_per_1k': row[2],
                    'output_cost_per_1k': row[3],
                    'context_window': row[4],
                    'last_updated': row[5]
                }
                for row in rows
            ]
    
    def get_conversation_cost_summary(self, conversation_id: str) -> Optional[Dict]:
        """Get cost summary for a specific conversation"""
        with self.get_connection() as conn:
            row = conn.execute("""
                SELECT 
                    total_cost,
                    request_count,
                    start_time,
                    last_update
                FROM conversation_costs
                WHERE conversation_id = ?
            """, (conversation_id,)).fetchone()
            
            if row:
                return {
                    'total_cost': row[0],
                    'request_count': row[1],
                    'start_time': row[2],
                    'last_update': row[3]
                }
        return None
    
    def get_daily_costs(self, days: int = 30) -> List[Dict]:
        """Get daily cost breakdown for the last N days"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM daily_cost_summary
                WHERE date >= date('now', '-' || ? || ' days')
                ORDER BY date DESC
            """, (days,)).fetchall()
            
            return [
                {
                    'date': row[0],
                    'model': row[1],
                    'request_count': row[2],
                    'total_input_tokens': row[3],
                    'total_output_tokens': row[4],
                    'total_cost': row[5]
                }
                for row in rows
            ]
    
    def get_model_usage_stats(self) -> List[Dict]:
        """Get usage statistics per model"""
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM model_usage_stats").fetchall()
            
            return [
                {
                    'model': row[0],
                    'conversation_count': row[1],
                    'total_requests': row[2],
                    'total_input_tokens': row[3],
                    'total_output_tokens': row[4],
                    'total_cost': row[5],
                    'avg_cost_per_request': row[6]
                }
                for row in rows
            ]
    
    def get_high_cost_conversations(self, limit: int = 10) -> List[Dict]:
        """Get conversations with unusually high costs"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM high_cost_conversations
                LIMIT ?
            """, (limit,)).fetchall()
            
            return [
                {
                    'conversation_id': row[0],
                    'total_cost': row[1],
                    'request_count': row[2],
                    'start_time': row[3],
                    'last_update': row[4]
                }
                for row in rows
            ]
    
    def update_model_cost(self, model_name: str, provider: str,
                         input_cost_per_1k: float, output_cost_per_1k: float,
                         context_window: int) -> None:
        """Update or insert model cost information"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO model_costs 
                (model_name, provider, input_cost_per_1k, output_cost_per_1k, 
                 context_window, last_updated)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            """, (model_name, provider, input_cost_per_1k, output_cost_per_1k,
                  context_window))
        
        # Clear the cache after updating
        self.cost_cache._refresh_cache()
    
    def _infer_provider(self, model_name: str) -> str:
        """Infer provider from model name"""
        model_lower = model_name.lower()
        
        if 'gpt' in model_lower:
            return 'openai'
        elif 'claude' in model_lower:
            return 'anthropic'
        elif 'gemini' in model_lower or 'palm' in model_lower:
            return 'google'
        elif 'llama' in model_lower or 'mixtral' in model_lower or 'gemma' in model_lower:
            return 'groq'
        else:
            return 'unknown'
    
    def export_cost_report(self, start_date: str = None, end_date: str = None,
                          format: str = 'json') -> str:
        """Export cost report in specified format"""
        with self.get_connection() as conn:
            query = """
                SELECT 
                    r.conversation_id,
                    r.timestamp,
                    r.model,
                    r.input_tokens,
                    r.output_tokens,
                    r.total_cost,
                    c.total_cost as conversation_total_cost,
                    c.request_count as conversation_request_count
                FROM request_costs r
                JOIN conversation_costs c ON r.conversation_id = c.conversation_id
            """
            params = []
            
            if start_date and end_date:
                query += " WHERE r.timestamp BETWEEN ? AND ?"
                params = [start_date, end_date]
            elif start_date:
                query += " WHERE r.timestamp >= ?"
                params = [start_date]
            elif end_date:
                query += " WHERE r.timestamp <= ?"
                params = [end_date]
            
            query += " ORDER BY r.timestamp DESC"
            
            rows = conn.execute(query, params).fetchall()
        
        data = [
            {
                'conversation_id': row[0],
                'timestamp': row[1],
                'model': row[2],
                'input_tokens': row[3],
                'output_tokens': row[4],
                'request_cost': row[5],
                'conversation_total_cost': row[6],
                'conversation_request_count': row[7]
            }
            for row in rows
        ]
        
        if format == 'json':
            return json.dumps(data, indent=2)
        elif format == 'csv':
            import csv
            import io
            output = io.StringIO()
            if data:
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}")


class CostTrackingHealthCheck:
    """Database health monitoring for cost tracking"""
    
    def __init__(self, db: CostTrackingDB):
        self.db = db
    
    def check_database_health(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        return {
            'table_integrity': self._check_table_integrity(),
            'index_health': self._check_index_health(),
            'trigger_status': self._check_trigger_status(),
            'data_consistency': self._check_data_consistency(),
            'performance_metrics': self._get_performance_metrics()
        }
    
    def _check_table_integrity(self) -> Dict[str, bool]:
        """Verify all tables exist with correct schema"""
        tables = ['model_costs', 'request_costs', 'conversation_costs', 
                  'query_performance_log', 'migration_log']
        results = {}
        
        with self.db.get_connection() as conn:
            for table in tables:
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    (table,)
                )
                results[table] = cursor.fetchone() is not None
        
        return results
    
    def _check_index_health(self) -> Dict[str, bool]:
        """Check if all indexes exist"""
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
        
        results = {}
        with self.db.get_connection() as conn:
            for index in expected_indexes:
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='index' AND name=?",
                    (index,)
                )
                results[index] = cursor.fetchone() is not None
        
        return results
    
    def _check_trigger_status(self) -> Dict[str, bool]:
        """Check if triggers are properly set up"""
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='trigger' AND name=?",
                ('update_conversation_costs_on_insert',)
            )
            return {
                'update_conversation_costs_on_insert': cursor.fetchone() is not None
            }
    
    def _check_data_consistency(self) -> Dict[str, Any]:
        """Verify data consistency between tables"""
        with self.db.get_connection() as conn:
            # Check if conversation_costs matches sum of request_costs
            consistency_check = conn.execute("""
                SELECT 
                    COUNT(*) as inconsistent_conversations
                FROM conversation_costs c
                WHERE ABS(c.total_cost - (
                    SELECT COALESCE(SUM(r.total_cost), 0)
                    FROM request_costs r
                    WHERE r.conversation_id = c.conversation_id
                )) > 0.001
            """).fetchone()
            
            # Check for orphaned request_costs
            orphaned_check = conn.execute("""
                SELECT COUNT(DISTINCT r.conversation_id) as orphaned_requests
                FROM request_costs r
                LEFT JOIN conversation_costs c ON r.conversation_id = c.conversation_id
                WHERE c.conversation_id IS NULL
            """).fetchone()
        
        return {
            'inconsistent_conversations': consistency_check[0],
            'orphaned_requests': orphaned_check[0],
            'is_consistent': consistency_check[0] == 0 and orphaned_check[0] == 0
        }
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get database performance metrics"""
        with self.db.get_connection() as conn:
            # Get database size
            page_count = conn.execute("PRAGMA page_count").fetchone()[0]
            page_size = conn.execute("PRAGMA page_size").fetchone()[0]
            db_size_mb = (page_count * page_size) / (1024 * 1024)
            
            # Get table statistics
            table_stats = {}
            for table in ['model_costs', 'request_costs', 'conversation_costs']:
                count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                table_stats[table] = count
            
            # Get cache statistics
            cache_stats = conn.execute("PRAGMA cache_stats").fetchone()
        
        return {
            'database_size_mb': round(db_size_mb, 2),
            'table_row_counts': table_stats,
            'cache_hit_rate': cache_stats[0] if cache_stats else None
        }