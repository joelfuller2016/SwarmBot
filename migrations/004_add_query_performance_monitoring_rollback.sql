-- Rollback Migration: 004_add_query_performance_monitoring
-- Description: Remove query performance monitoring table and related objects
-- Date: 2025-01-06

BEGIN TRANSACTION;

-- Drop the slow queries view
DROP VIEW IF EXISTS slow_queries;

-- Drop the query performance log table
DROP TABLE IF EXISTS query_performance_log;

-- Remove migration record
DELETE FROM migration_log WHERE migration_id = '004_add_query_performance_monitoring';

COMMIT;
