# LLM API Cost Tracking Database Schema
## Task 96.2 Implementation Guide

### Overview
This document provides the complete database schema implementation for the LLM API Cost Tracking System in the SwarmBot project. It includes SQL table definitions, SQLite-specific considerations, migration strategies, and integration guidelines.

## 1. SQL Table Definitions

### 1.1 model_costs Table
Stores the cost information for different LLM models.

```sql
CREATE TABLE model_costs (
    model_name TEXT NOT NULL,
    provider TEXT NOT NULL,
    input_cost_per_1k REAL NOT NULL CHECK (input_cost_per_1k >= 0),
    output_cost_per_1k REAL NOT NULL CHECK (output_cost_per_1k >= 0),
    context_window INTEGER NOT NULL CHECK (context_window > 0),
    last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (model_name, provider)
);

-- Create indexes for fast lookups
CREATE INDEX idx_model_costs_provider ON model_costs(provider);
CREATE INDEX idx_model_costs_last_updated ON model_costs(last_updated);
```

### 1.2 request_costs Table
Tracks individual API request costs.

```sql
CREATE TABLE request_costs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    model TEXT NOT NULL,
    input_tokens INTEGER NOT NULL CHECK (input_tokens >= 0),
    output_tokens INTEGER NOT NULL CHECK (output_tokens >= 0),
    input_cost REAL NOT NULL CHECK (input_cost >= 0),
    output_cost REAL NOT NULL CHECK (output_cost >= 0),
    total_cost REAL NOT NULL CHECK (total_cost >= 0),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

-- Create indexes for performance
CREATE INDEX idx_request_costs_conversation_id ON request_costs(conversation_id);
CREATE INDEX idx_request_costs_timestamp ON request_costs(timestamp);
CREATE INDEX idx_request_costs_model ON request_costs(model);
CREATE INDEX idx_request_costs_conv_time ON request_costs(conversation_id, timestamp);
```

### 1.3 conversation_costs Table
Aggregates costs per conversation.

```sql
CREATE TABLE conversation_costs (
    conversation_id TEXT PRIMARY KEY,
    start_time DATETIME NOT NULL,
    last_update DATETIME NOT NULL,
    total_cost REAL NOT NULL DEFAULT 0 CHECK (total_cost >= 0),
    request_count INTEGER NOT NULL DEFAULT 0 CHECK (request_count >= 0)
);

-- Create indexes for time-based queries
CREATE INDEX idx_conversation_costs_start_time ON conversation_costs(start_time);
CREATE INDEX idx_conversation_costs_last_update ON conversation_costs(last_update);
CREATE INDEX idx_conversation_costs_total_cost ON conversation_costs(total_cost DESC);
```

## 2. SQLite Implementation Considerations

### 2.1 Data Type Mappings
- **TEXT**: Used for all VARCHAR fields (model_name, provider, conversation_id)
- **REAL**: Used for DECIMAL values (costs) with application-level precision handling
- **INTEGER**: Used for token counts and context window
- **DATETIME**: Stored as TEXT in ISO8601 format

### 2.2 Database Configuration
```sql
-- Enable Write-Ahead Logging for better concurrency
PRAGMA journal_mode = WAL;

-- Set synchronous mode for balance between safety and performance
PRAGMA synchronous = NORMAL;

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Set cache size (negative value = KB)
PRAGMA cache_size = -10000;

-- Enable query planner optimizations
PRAGMA optimize;
```

### 2.3 Automatic Update Trigger
```sql
-- Trigger to automatically update conversation_costs when request_costs are inserted
CREATE TRIGGER update_conversation_costs_on_insert
AFTER INSERT ON request_costs
BEGIN
    INSERT INTO conversation_costs (conversation_id, start_time, last_update, total_cost, request_count)
    VALUES (NEW.conversation_id, NEW.timestamp, NEW.timestamp, NEW.total_cost, 1)
    ON CONFLICT(conversation_id) DO UPDATE SET
        last_update = NEW.timestamp,
        total_cost = total_cost + NEW.total_cost,
        request_count = request_count + 1;
END;
```

## 3. Migration Strategy

### 3.1 Migration File Structure
```
migrations/
├── 001_cost_tracking_schema.sql
├── 001_cost_tracking_rollback.sql
├── 002_add_model_costs_data.sql
└── migration_log.json
```

### 3.2 Migration Script (001_cost_tracking_schema.sql)
```sql
-- Migration: 001_cost_tracking_schema
-- Description: Create cost tracking tables for LLM API usage
-- Date: 2025-01-06

BEGIN TRANSACTION;

-- Create model_costs table
CREATE TABLE IF NOT EXISTS model_costs (
    model_name TEXT NOT NULL,
    provider TEXT NOT NULL,
    input_cost_per_1k REAL NOT NULL CHECK (input_cost_per_1k >= 0),
    output_cost_per_1k REAL NOT NULL CHECK (output_cost_per_1k >= 0),
    context_window INTEGER NOT NULL CHECK (context_window > 0),
    last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (model_name, provider)
);

-- Create request_costs table
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

-- Create conversation_costs table
CREATE TABLE IF NOT EXISTS conversation_costs (
    conversation_id TEXT PRIMARY KEY,
    start_time DATETIME NOT NULL,
    last_update DATETIME NOT NULL,
    total_cost REAL NOT NULL DEFAULT 0 CHECK (total_cost >= 0),
    request_count INTEGER NOT NULL DEFAULT 0 CHECK (request_count >= 0)
);

-- Create all indexes
CREATE INDEX IF NOT EXISTS idx_model_costs_provider ON model_costs(provider);
CREATE INDEX IF NOT EXISTS idx_model_costs_last_updated ON model_costs(last_updated);
CREATE INDEX IF NOT EXISTS idx_request_costs_conversation_id ON request_costs(conversation_id);
CREATE INDEX IF NOT EXISTS idx_request_costs_timestamp ON request_costs(timestamp);
CREATE INDEX IF NOT EXISTS idx_request_costs_model ON request_costs(model);
CREATE INDEX IF NOT EXISTS idx_request_costs_conv_time ON request_costs(conversation_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_conversation_costs_start_time ON conversation_costs(start_time);
CREATE INDEX IF NOT EXISTS idx_conversation_costs_last_update ON conversation_costs(last_update);
CREATE INDEX IF NOT EXISTS idx_conversation_costs_total_cost ON conversation_costs(total_cost DESC);

-- Create automatic update trigger
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

-- Insert migration record
INSERT INTO migration_log (migration_id, applied_at, description)
VALUES ('001_cost_tracking_schema', datetime('now'), 'Create cost tracking tables for LLM API usage');

COMMIT;
```

### 3.3 Rollback Script (001_cost_tracking_rollback.sql)
```sql
-- Rollback Migration: 001_cost_tracking_schema
BEGIN TRANSACTION;

DROP TRIGGER IF EXISTS update_conversation_costs_on_insert;
DROP TABLE IF EXISTS conversation_costs;
DROP TABLE IF EXISTS request_costs;
DROP TABLE IF EXISTS model_costs;

DELETE FROM migration_log WHERE migration_id = '001_cost_tracking_schema';

COMMIT;
```

### 3.4 Initial Data Seeding (002_add_model_costs_data.sql)
```sql
-- Insert initial model cost data
INSERT OR REPLACE INTO model_costs (model_name, provider, input_cost_per_1k, output_cost_per_1k, context_window, last_updated)
VALUES 
    ('gpt-4-turbo', 'openai', 0.01, 0.03, 128000, datetime('now')),
    ('gpt-4', 'openai', 0.03, 0.06, 8192, datetime('now')),
    ('gpt-3.5-turbo', 'openai', 0.0005, 0.0015, 16385, datetime('now')),
    ('claude-3-opus', 'anthropic', 0.015, 0.075, 200000, datetime('now')),
    ('claude-3-sonnet', 'anthropic', 0.003, 0.015, 200000, datetime('now')),
    ('claude-3-haiku', 'anthropic', 0.00025, 0.00125, 200000, datetime('now'));
```

## 4. Performance Optimizations

### 4.1 Database Views for Common Aggregations
```sql
-- Daily cost summary view
CREATE VIEW daily_cost_summary AS
SELECT 
    DATE(timestamp) as date,
    model,
    COUNT(*) as request_count,
    SUM(input_tokens) as total_input_tokens,
    SUM(output_tokens) as total_output_tokens,
    SUM(total_cost) as total_cost
FROM request_costs
GROUP BY DATE(timestamp), model;

-- Conversation cost ranking view
CREATE VIEW conversation_cost_ranking AS
SELECT 
    c.conversation_id,
    c.total_cost,
    c.request_count,
    c.total_cost / c.request_count as avg_cost_per_request,
    c.start_time,
    c.last_update,
    julianday(c.last_update) - julianday(c.start_time) as duration_days
FROM conversation_costs c
ORDER BY c.total_cost DESC;

-- Model usage statistics view
CREATE VIEW model_usage_stats AS
SELECT 
    r.model,
    COUNT(DISTINCT r.conversation_id) as conversation_count,
    COUNT(*) as total_requests,
    SUM(r.input_tokens) as total_input_tokens,
    SUM(r.output_tokens) as total_output_tokens,
    SUM(r.total_cost) as total_cost,
    AVG(r.total_cost) as avg_cost_per_request
FROM request_costs r
GROUP BY r.model;
```

### 4.2 Query Performance Monitoring
```sql
-- Create table for query performance tracking
CREATE TABLE query_performance_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_hash TEXT NOT NULL,
    query_text TEXT NOT NULL,
    execution_time_ms INTEGER NOT NULL,
    rows_examined INTEGER,
    rows_returned INTEGER,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_query_performance_timestamp ON query_performance_log(timestamp);
CREATE INDEX idx_query_performance_execution_time ON query_performance_log(execution_time_ms DESC);
```

## 5. Integration Points

### 5.1 DatabaseLogger Extension (src/database/logger.py)
```python
class CostTrackingDB(DatabaseLogger):
    """Extension of DatabaseLogger for cost tracking operations"""
    
    def __init__(self, db_path: str):
        super().__init__(db_path)
        self._initialize_cost_tracking_schema()
        self._load_model_costs_cache()
    
    def log_request_cost(self, conversation_id: str, model: str, 
                        input_tokens: int, output_tokens: int) -> None:
        """Log the cost of a single API request"""
        model_costs = self._get_model_costs(model)
        input_cost = (input_tokens / 1000) * model_costs['input_cost_per_1k']
        output_cost = (output_tokens / 1000) * model_costs['output_cost_per_1k']
        total_cost = input_cost + output_cost
        
        self._execute_insert("""
            INSERT INTO request_costs 
            (conversation_id, model, input_tokens, output_tokens, 
             input_cost, output_cost, total_cost)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (conversation_id, model, input_tokens, output_tokens,
              input_cost, output_cost, total_cost))
    
    def get_conversation_cost_summary(self, conversation_id: str) -> dict:
        """Get cost summary for a specific conversation"""
        return self._execute_query("""
            SELECT 
                total_cost,
                request_count,
                start_time,
                last_update
            FROM conversation_costs
            WHERE conversation_id = ?
        """, (conversation_id,)).fetchone()
    
    def get_daily_costs(self, days: int = 30) -> list:
        """Get daily cost breakdown for the last N days"""
        return self._execute_query("""
            SELECT * FROM daily_cost_summary
            WHERE date >= date('now', '-' || ? || ' days')
            ORDER BY date DESC
        """, (days,)).fetchall()
```

### 5.2 Caching Layer Implementation
```python
from functools import lru_cache
from datetime import datetime, timedelta

class ModelCostCache:
    """Cache for frequently accessed model costs"""
    
    def __init__(self, db: CostTrackingDB):
        self.db = db
        self._cache = {}
        self._last_refresh = datetime.now()
        self._refresh_interval = timedelta(hours=1)
    
    @lru_cache(maxsize=128)
    def get_model_cost(self, model_name: str, provider: str) -> dict:
        """Get cached model cost with automatic refresh"""
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
```

### 5.3 Health Check Implementation
```python
class CostTrackingHealthCheck:
    """Database health monitoring for cost tracking"""
    
    def __init__(self, db: CostTrackingDB):
        self.db = db
    
    def check_database_health(self) -> dict:
        """Comprehensive health check"""
        return {
            'table_integrity': self._check_table_integrity(),
            'index_health': self._check_index_health(),
            'trigger_status': self._check_trigger_status(),
            'data_consistency': self._check_data_consistency(),
            'performance_metrics': self._get_performance_metrics()
        }
    
    def _check_table_integrity(self) -> dict:
        """Verify all tables exist with correct schema"""
        tables = ['model_costs', 'request_costs', 'conversation_costs']
        results = {}
        for table in tables:
            results[table] = self.db.table_exists(table)
        return results
    
    def _check_data_consistency(self) -> dict:
        """Verify data consistency between tables"""
        # Check if conversation_costs matches sum of request_costs
        consistency_check = self.db.execute_query("""
            SELECT 
                COUNT(*) as inconsistent_conversations
            FROM conversation_costs c
            WHERE ABS(c.total_cost - (
                SELECT COALESCE(SUM(r.total_cost), 0)
                FROM request_costs r
                WHERE r.conversation_id = c.conversation_id
            )) > 0.001
        """).fetchone()
        
        return {
            'inconsistent_conversations': consistency_check['inconsistent_conversations'],
            'is_consistent': consistency_check['inconsistent_conversations'] == 0
        }
```

## 6. Testing Strategy

### 6.1 Unit Tests
```python
import unittest
from datetime import datetime

class TestCostTracking(unittest.TestCase):
    def setUp(self):
        self.db = CostTrackingDB(':memory:')
        self.db.initialize_schema()
    
    def test_request_cost_calculation(self):
        """Test accurate cost calculation"""
        self.db.add_model_cost('gpt-4', 'openai', 0.03, 0.06, 8192)
        self.db.log_request_cost('test_conv', 'gpt-4', 1000, 500)
        
        cost = self.db.get_request_cost('test_conv')
        self.assertAlmostEqual(cost['input_cost'], 0.03)
        self.assertAlmostEqual(cost['output_cost'], 0.03)
        self.assertAlmostEqual(cost['total_cost'], 0.06)
    
    def test_conversation_aggregation(self):
        """Test conversation cost aggregation"""
        # Add multiple requests
        for i in range(5):
            self.db.log_request_cost('test_conv', 'gpt-4', 100, 50)
        
        summary = self.db.get_conversation_cost_summary('test_conv')
        self.assertEqual(summary['request_count'], 5)
        self.assertAlmostEqual(summary['total_cost'], 0.045)
```

## 7. Monitoring and Alerts

### 7.1 Cost Alert Queries
```sql
-- High-cost conversations (top 10%)
SELECT 
    conversation_id,
    total_cost,
    request_count
FROM conversation_costs
WHERE total_cost > (
    SELECT PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY total_cost)
    FROM conversation_costs
)
ORDER BY total_cost DESC;

-- Unusual token usage patterns
SELECT 
    model,
    AVG(input_tokens) as avg_input,
    AVG(output_tokens) as avg_output,
    STDDEV(input_tokens) as input_stddev,
    STDDEV(output_tokens) as output_stddev
FROM request_costs
GROUP BY model
HAVING input_stddev > 2 * avg_input
    OR output_stddev > 2 * avg_output;
```

## 8. Future Enhancements

1. **Time-based partitioning**: Implement table partitioning for request_costs by month
2. **Cost budgeting**: Add budget_limits table and alerting
3. **User attribution**: Link costs to specific users or departments
4. **Real-time dashboards**: Implement WebSocket updates for live cost monitoring
5. **Cost optimization**: Add recommendations based on usage patterns

---

This completes the comprehensive database schema implementation for Task 96.2 of the LLM API Cost Tracking System.