"""
Cost tracking database module for LLM API usage
Extends the existing database infrastructure to track and analyze API costs
"""

import sqlite3
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from functools import lru_cache, wraps
import logging
from pathlib import Path
from decimal import Decimal

from .chat_storage import ChatDatabase

logger = logging.getLogger(__name__)


class CostTrackingDB(ChatDatabase):
    """Extension of ChatDatabase for cost tracking operations"""
    
    def __init__(self, db_path: str = "data/swarmbot_chats.db"):
        """Initialize cost tracking database with migrations"""
        super().__init__(db_path)
        self._model_costs_cache = {}
        self._cache_last_refresh = None
        self._cache_refresh_interval = timedelta(hours=1)
        self._configure_sqlite_optimizations()
        self._run_migrations()
        self._load_model_costs_cache()
    
    def _configure_sqlite_optimizations(self):
        """Configure SQLite for optimal performance with cost tracking"""
        cursor = self.conn.cursor()
        
        # Enable Write-Ahead Logging for better concurrency
        cursor.execute("PRAGMA journal_mode = WAL")
        
        # Set synchronous mode for balance between safety and performance
        cursor.execute("PRAGMA synchronous = NORMAL")
        
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Set cache size (negative value = KB)
        cursor.execute("PRAGMA cache_size = -10000")
        
        # Enable query planner optimizations
        cursor.execute("PRAGMA optimize")
        
        logger.info("SQLite optimizations configured for cost tracking")
    
    def monitor_query(self, func):
        """Decorator to monitor query performance"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Get the SQL query from the function arguments
            query_text = None
            if args and isinstance(args[0], str):
                query_text = args[0]
            elif 'query' in kwargs:
                query_text = kwargs['query']
            
            # Execute the query
            result = func(*args, **kwargs)
            
            # Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Log slow queries
            if execution_time_ms > 100 and query_text:
                self._log_query_performance(query_text, execution_time_ms)
            
            return result
        return wrapper
    
    def _log_query_performance(self, query_text: str, execution_time_ms: int, 
                              rows_examined: Optional[int] = None, 
                              rows_returned: Optional[int] = None):
        """Log query performance metrics"""
        # Generate query hash for grouping similar queries
        query_hash = hashlib.md5(query_text.encode()).hexdigest()
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO query_performance_log 
                (query_hash, query_text, execution_time_ms, rows_examined, rows_returned)
                VALUES (?, ?, ?, ?, ?)
            """, (query_hash, query_text, execution_time_ms, rows_examined, rows_returned))
            self.conn.commit()
        except sqlite3.OperationalError:
            # Table might not exist yet if migrations haven't run
            pass
    
    def _run_migrations(self):
        """Run database migrations for cost tracking"""
        migrations_path = Path(__file__).parent.parent.parent / "migrations"
        if not migrations_path.exists():
            logger.warning(f"Migrations directory not found at {migrations_path}")
            return
        
        # Get list of migration files
        migration_files = sorted([f for f in migrations_path.glob("*.sql") if not f.name.endswith("_rollback.sql")])
        
        for migration_file in migration_files:
            migration_id = migration_file.stem
            
            # Check if migration already applied
            cursor = self.conn.cursor()
            cursor.execute("SELECT 1 FROM migration_log WHERE migration_id = ?", (migration_id,))
            if cursor.fetchone():
                continue
            
            # Run migration
            try:
                with open(migration_file, 'r', encoding='utf-8') as f:
                    migration_sql = f.read()
                
                # Execute migration
                cursor.executescript(migration_sql)
                logger.info(f"Applied migration: {migration_id}")
                
            except Exception as e:
                logger.error(f"Failed to apply migration {migration_id}: {e}")
                raise
    
    def _load_model_costs_cache(self):
        """Load model costs into memory cache"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM model_costs")
            
            for row in cursor.fetchall():
                key = f"{row['provider']}:{row['model_name']}"
                self._model_costs_cache[key] = {
                    'input_cost_per_1k': row['input_cost_per_1k'],
                    'output_cost_per_1k': row['output_cost_per_1k'],
                    'context_window': row['context_window'],
                    'last_updated': row['last_updated']
                }
            
            self._cache_last_refresh = datetime.now()
            logger.info(f"Loaded {len(self._model_costs_cache)} model costs into cache")
            
        except sqlite3.OperationalError as e:
            if "no such table: model_costs" in str(e):
                logger.warning("model_costs table not found - migrations may not have run yet")
            else:
                raise
    
    def _get_model_costs(self, model: str, provider: Optional[str] = None) -> Dict[str, float]:
        """Get model costs with automatic cache refresh"""
        # Refresh cache if needed
        if (not self._cache_last_refresh or 
            datetime.now() - self._cache_last_refresh > self._cache_refresh_interval):
            self._load_model_costs_cache()
        
        # Try to find model costs
        if provider:
            key = f"{provider}:{model}"
            if key in self._model_costs_cache:
                return self._model_costs_cache[key]
        
        # Try to find by model name alone
        for key, costs in self._model_costs_cache.items():
            if key.endswith(f":{model}"):
                return costs
        
        # Default costs if not found
        logger.warning(f"Model costs not found for {model}, using defaults")
        return {
            'input_cost_per_1k': 0.001,
            'output_cost_per_1k': 0.002,
            'context_window': 4096
        }
    
    def log_request_cost(self, conversation_id: str, model: str, 
                        input_tokens: int, output_tokens: int,
                        provider: Optional[str] = None) -> None:
        """Log the cost of a single API request"""
        model_costs = self._get_model_costs(model, provider)
        
        # Calculate costs using Decimal for precision
        input_cost = float(Decimal(str(input_tokens)) / Decimal('1000') * 
                          Decimal(str(model_costs['input_cost_per_1k'])))
        output_cost = float(Decimal(str(output_tokens)) / Decimal('1000') * 
                           Decimal(str(model_costs['output_cost_per_1k'])))
        total_cost = float(Decimal(str(input_cost)) + Decimal(str(output_cost)))
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO request_costs 
            (conversation_id, model, input_tokens, output_tokens, 
             input_cost, output_cost, total_cost)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (conversation_id, model, input_tokens, output_tokens,
              input_cost, output_cost, total_cost))
        self.conn.commit()
        
        logger.debug(f"Logged cost for {model}: {input_tokens} in, {output_tokens} out, ${total_cost:.4f}")
    
    def get_conversation_cost_summary(self, conversation_id: str) -> Optional[Dict]:
        """Get cost summary for a specific conversation"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                total_cost,
                request_count,
                start_time,
                last_update
            FROM conversation_costs
            WHERE conversation_id = ?
        """, (conversation_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_daily_costs(self, days: int = 30) -> List[Dict]:
        """Get daily cost breakdown for the last N days"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                DATE(timestamp) as date,
                model,
                COUNT(*) as request_count,
                SUM(input_tokens) as total_input_tokens,
                SUM(output_tokens) as total_output_tokens,
                SUM(total_cost) as total_cost
            FROM request_costs
            WHERE timestamp >= date('now', '-' || ? || ' days')
            GROUP BY DATE(timestamp), model
            ORDER BY date DESC, total_cost DESC
        """, (days,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_model_usage_stats(self) -> List[Dict]:
        """Get usage statistics for all models"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                r.model,
                COUNT(DISTINCT r.conversation_id) as conversation_count,
                COUNT(*) as total_requests,
                SUM(r.input_tokens) as total_input_tokens,
                SUM(r.output_tokens) as total_output_tokens,
                SUM(r.total_cost) as total_cost,
                AVG(r.total_cost) as avg_cost_per_request
            FROM request_costs r
            GROUP BY r.model
            ORDER BY total_cost DESC
        """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_conversation_rankings(self, limit: int = 100) -> List[Dict]:
        """Get conversations ranked by cost"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                c.conversation_id,
                c.total_cost,
                c.request_count,
                c.total_cost / c.request_count as avg_cost_per_request,
                c.start_time,
                c.last_update,
                CAST((julianday(c.last_update) - julianday(c.start_time)) * 24 AS INTEGER) as duration_hours
            FROM conversation_costs c
            ORDER BY c.total_cost DESC
            LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def update_model_cost(self, model_name: str, provider: str,
                         input_cost_per_1k: float, output_cost_per_1k: float,
                         context_window: int) -> None:
        """Update or insert model cost information"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO model_costs 
            (model_name, provider, input_cost_per_1k, output_cost_per_1k, context_window, last_updated)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (model_name, provider, input_cost_per_1k, output_cost_per_1k, context_window))
        self.conn.commit()
        
        # Refresh cache
        self._load_model_costs_cache()
    
    def get_all_model_costs(self) -> List[Dict]:
        """Get all model cost configurations"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM model_costs 
            ORDER BY provider, model_name
        """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_cost_alerts(self, threshold: float = 10.0) -> List[Dict]:
        """Get conversations that exceed cost threshold"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                conversation_id,
                total_cost,
                request_count,
                start_time,
                last_update
            FROM conversation_costs
            WHERE total_cost > ?
            ORDER BY total_cost DESC
        """, (threshold,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_cost_forecast(self, days_ahead: int = 7) -> Dict[str, float]:
        """Forecast costs based on recent usage patterns"""
        # Get average daily cost from last 30 days
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                AVG(daily_cost) as avg_daily_cost,
                MAX(daily_cost) as max_daily_cost,
                MIN(daily_cost) as min_daily_cost
            FROM (
                SELECT DATE(timestamp) as date, SUM(total_cost) as daily_cost
                FROM request_costs
                WHERE timestamp >= date('now', '-30 days')
                GROUP BY DATE(timestamp)
            )
        """)
        
        row = cursor.fetchone()
        if row and row['avg_daily_cost']:
            return {
                'estimated_cost': row['avg_daily_cost'] * days_ahead,
                'max_estimated': row['max_daily_cost'] * days_ahead,
                'min_estimated': row['min_daily_cost'] * days_ahead,
                'avg_daily_cost': row['avg_daily_cost']
            }
        
        return {
            'estimated_cost': 0.0,
            'max_estimated': 0.0,
            'min_estimated': 0.0,
            'avg_daily_cost': 0.0
        }
    
    def export_costs_json(self, start_date: Optional[str] = None, 
                         end_date: Optional[str] = None) -> str:
        """Export cost data as JSON"""
        data = {
            'export_date': datetime.now().isoformat(),
            'date_range': {
                'start': start_date or 'all',
                'end': end_date or 'current'
            },
            'summary': self.get_cost_summary(start_date, end_date),
            'daily_costs': self.get_daily_costs(30),
            'model_usage': self.get_model_usage_stats(),
            'top_conversations': self.get_conversation_rankings(50)
        }
        return json.dumps(data, indent=2, default=str)
    
    def export_costs_csv(self, output_path: str, start_date: Optional[str] = None,
                        end_date: Optional[str] = None) -> None:
        """Export cost data as CSV"""
        import csv
        
        cursor = self.conn.cursor()
        query = """
            SELECT 
                conversation_id,
                timestamp,
                model,
                input_tokens,
                output_tokens,
                input_cost,
                output_cost,
                total_cost
            FROM request_costs
        """
        
        params = []
        if start_date or end_date:
            conditions = []
            if start_date:
                conditions.append("timestamp >= ?")
                params.append(start_date)
            if end_date:
                conditions.append("timestamp <= ?")
                params.append(end_date)
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY timestamp DESC"
        cursor.execute(query, params)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['conversation_id', 'timestamp', 'model', 'input_tokens',
                           'output_tokens', 'input_cost', 'output_cost', 'total_cost'])
            writer.writerows(cursor.fetchall())
        
        logger.info(f"Exported cost data to {output_path}")
    
    def get_cost_summary(self, start_date: Optional[str] = None,
                        end_date: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive cost summary"""
        cursor = self.conn.cursor()
        
        query = "SELECT SUM(total_cost) as total, COUNT(*) as requests FROM request_costs"
        params = []
        
        if start_date or end_date:
            conditions = []
            if start_date:
                conditions.append("timestamp >= ?")
                params.append(start_date)
            if end_date:
                conditions.append("timestamp <= ?")
                params.append(end_date)
            query += " WHERE " + " AND ".join(conditions)
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        
        return {
            'total_cost': result['total'] or 0,
            'total_requests': result['requests'] or 0,
            'average_cost_per_request': (result['total'] / result['requests']) if result['requests'] else 0
        }
    
    def check_budget_threshold(self, threshold: float) -> Dict[str, Any]:
        """Check if current month's costs exceed threshold"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT SUM(total_cost) as month_total
            FROM request_costs
            WHERE timestamp >= date('now', 'start of month')
        """)
        
        result = cursor.fetchone()
        month_total = result['month_total'] or 0
        
        return {
            'current_month_cost': month_total,
            'budget_threshold': threshold,
            'exceeded': month_total > threshold,
            'percentage_used': (month_total / threshold * 100) if threshold > 0 else 0,
            'remaining_budget': max(0, threshold - month_total)
        }
    
    def get_slow_queries(self, min_execution_time_ms: int = 100) -> List[Dict]:
        """Get slow queries from performance log"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                query_hash,
                query_text,
                COUNT(*) as execution_count,
                AVG(execution_time_ms) as avg_execution_time_ms,
                MAX(execution_time_ms) as max_execution_time_ms,
                MIN(execution_time_ms) as min_execution_time_ms
            FROM query_performance_log
            WHERE execution_time_ms > ?
            GROUP BY query_hash
            ORDER BY avg_execution_time_ms DESC
            LIMIT 20
        """, (min_execution_time_ms,))
        
        return [dict(row) for row in cursor.fetchall()]


class CostTrackingHealthCheck:
    """Database health monitoring for cost tracking"""
    
    def __init__(self, db: CostTrackingDB):
        self.db = db
    
    def check_database_health(self) -> Dict[str, Any]:
        """Comprehensive health check for cost tracking database"""
        return {
            'table_integrity': self._check_table_integrity(),
            'index_health': self._check_index_health(),
            'trigger_status': self._check_trigger_status(),
            'data_consistency': self._check_data_consistency(),
            'performance_metrics': self._get_performance_metrics()
        }
    
    def _check_table_integrity(self) -> Dict[str, bool]:
        """Verify all cost tracking tables exist"""
        tables = ['model_costs', 'request_costs', 'conversation_costs', 'migration_log']
        results = {}
        
        cursor = self.db.conn.cursor()
        for table in tables:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (table,))
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
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index'
        """)
        
        existing_indexes = {row['name'] for row in cursor.fetchall()}
        return {idx: idx in existing_indexes for idx in expected_indexes}
    
    def _check_trigger_status(self) -> Dict[str, bool]:
        """Check if triggers are properly configured"""
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='trigger' AND name='update_conversation_costs_on_insert'
        """)
        
        return {
            'update_conversation_costs_on_insert': cursor.fetchone() is not None
        }
    
    def _check_data_consistency(self) -> Dict[str, Any]:
        """Verify data consistency between tables"""
        cursor = self.db.conn.cursor()
        
        # Check if conversation_costs matches sum of request_costs
        cursor.execute("""
            SELECT 
                COUNT(*) as inconsistent_conversations
            FROM conversation_costs c
            WHERE ABS(c.total_cost - (
                SELECT COALESCE(SUM(r.total_cost), 0)
                FROM request_costs r
                WHERE r.conversation_id = c.conversation_id
            )) > 0.001
        """)
        
        result = cursor.fetchone()
        
        # Check for orphaned records
        cursor.execute("""
            SELECT COUNT(*) as orphaned_requests
            FROM request_costs r
            WHERE NOT EXISTS (
                SELECT 1 FROM conversation_costs c
                WHERE c.conversation_id = r.conversation_id
            )
        """)
        
        orphaned = cursor.fetchone()
        
        return {
            'inconsistent_conversations': result['inconsistent_conversations'],
            'orphaned_requests': orphaned['orphaned_requests'],
            'is_consistent': result['inconsistent_conversations'] == 0 and orphaned['orphaned_requests'] == 0
        }
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get database performance metrics"""
        cursor = self.db.conn.cursor()
        
        # Get table sizes
        cursor.execute("""
            SELECT 
                name,
                COUNT(*) as row_count
            FROM (
                SELECT 'model_costs' as name, COUNT(*) as count FROM model_costs
                UNION ALL
                SELECT 'request_costs', COUNT(*) FROM request_costs
                UNION ALL
                SELECT 'conversation_costs', COUNT(*) FROM conversation_costs
            )
            GROUP BY name
        """)
        
        table_sizes = {row['name']: row['row_count'] for row in cursor.fetchall()}
        
        # Get database file size
        db_path = Path(self.db.db_path)
        db_size = db_path.stat().st_size if db_path.exists() else 0
        
        return {
            'table_sizes': table_sizes,
            'database_size_mb': db_size / (1024 * 1024),
            'cache_status': {
                'model_costs_cached': len(self.db._model_costs_cache),
                'cache_age_minutes': (
                    (datetime.now() - self.db._cache_last_refresh).total_seconds() / 60
                    if self.db._cache_last_refresh else None
                )
            }
        }


class ModelCostCache:
    """Cache for frequently accessed model costs with LRU eviction"""
    
    def __init__(self, db: CostTrackingDB, cache_size: int = 128):
        self.db = db
        self._cache = {}
        self._last_refresh = datetime.now()
        self._refresh_interval = timedelta(hours=1)
        self.get_model_cost = lru_cache(maxsize=cache_size)(self._get_model_cost_uncached)
    
    def _get_model_cost_uncached(self, model_name: str, provider: str) -> Dict:
        """Get model cost without caching"""
        if datetime.now() - self._last_refresh > self._refresh_interval:
            self._refresh_cache()
        
        key = f"{provider}:{model_name}"
        return self._cache.get(key, self._fetch_and_cache(model_name, provider))
    
    def _refresh_cache(self):
        """Refresh entire cache from database"""
        costs = self.db.get_all_model_costs()
        self._cache = {f"{c['provider']}:{c['model_name']}": c for c in costs}
        self._last_refresh = datetime.now()
        self.get_model_cost.cache_clear()
    
    def _fetch_and_cache(self, model_name: str, provider: str) -> Dict:
        """Fetch model cost from database and cache it"""
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT * FROM model_costs 
            WHERE model_name = ? AND provider = ?
        """, (model_name, provider))
        
        row = cursor.fetchone()
        if row:
            cost_data = dict(row)
            key = f"{provider}:{model_name}"
            self._cache[key] = cost_data
            return cost_data
        
        # Return default if not found
        return {
            'model_name': model_name,
            'provider': provider,
            'input_cost_per_1k': 0.001,
            'output_cost_per_1k': 0.002,
            'context_window': 4096
        }


# Test the implementation
if __name__ == "__main__":
    import tempfile
    
    # Create temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        test_db_path = f.name
    
    # Initialize database
    db = CostTrackingDB(test_db_path)
    
    # Create a test session
    session_id = f"test_cost_session_{datetime.now().timestamp()}"
    db.create_session(session_id, "openai", {"test": True})
    
    # Log some costs
    db.log_request_cost(session_id, "gpt-4", 1000, 500, "openai")
    db.log_request_cost(session_id, "gpt-3.5-turbo", 2000, 1000, "openai")
    
    # Get cost summary
    summary = db.get_conversation_cost_summary(session_id)
    print(f"Conversation cost summary: {summary}")
    
    # Get daily costs
    daily = db.get_daily_costs(7)
    print(f"Daily costs: {daily}")
    
    # Get model usage stats
    stats = db.get_model_usage_stats()
    print(f"Model usage stats: {stats}")
    
    # Run health check
    health_check = CostTrackingHealthCheck(db)
    health_status = health_check.check_database_health()
    print(f"Health status: {json.dumps(health_status, indent=2)}")
    
    # Close database
    db.close()
    
    # Clean up
    Path(test_db_path).unlink()
