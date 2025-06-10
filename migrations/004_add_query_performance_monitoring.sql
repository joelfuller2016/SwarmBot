-- Migration: 004_add_query_performance_monitoring
-- Description: Add query performance monitoring table for cost tracking optimization
-- Date: 2025-01-06

BEGIN TRANSACTION;

-- Create table for query performance tracking
CREATE TABLE IF NOT EXISTS query_performance_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_hash TEXT NOT NULL,
    query_text TEXT NOT NULL,
    execution_time_ms INTEGER NOT NULL,
    rows_examined INTEGER,
    rows_returned INTEGER,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance analysis
CREATE INDEX IF NOT EXISTS idx_query_performance_timestamp ON query_performance_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_query_performance_execution_time ON query_performance_log(execution_time_ms DESC);
CREATE INDEX IF NOT EXISTS idx_query_performance_query_hash ON query_performance_log(query_hash);

-- Create view for slow query analysis
CREATE VIEW IF NOT EXISTS slow_queries AS
SELECT 
    query_hash,
    query_text,
    COUNT(*) as execution_count,
    AVG(execution_time_ms) as avg_execution_time_ms,
    MAX(execution_time_ms) as max_execution_time_ms,
    MIN(execution_time_ms) as min_execution_time_ms,
    SUM(rows_examined) as total_rows_examined,
    SUM(rows_returned) as total_rows_returned
FROM query_performance_log
WHERE execution_time_ms > 100  -- Queries taking more than 100ms
GROUP BY query_hash
ORDER BY avg_execution_time_ms DESC;

-- Insert migration record
INSERT INTO migration_log (migration_id, applied_at, description)
VALUES ('004_add_query_performance_monitoring', datetime('now'), 'Add query performance monitoring table for cost tracking optimization');

COMMIT;
