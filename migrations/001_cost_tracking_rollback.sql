-- Rollback Migration: 001_cost_tracking_schema
-- Description: Remove cost tracking tables and related objects
-- Date: 2025-01-06

BEGIN TRANSACTION;

-- Drop the automatic update trigger
DROP TRIGGER IF EXISTS update_conversation_costs_on_insert;

-- Drop tables in reverse order of dependencies
DROP TABLE IF EXISTS conversation_costs;
DROP TABLE IF EXISTS request_costs;
DROP TABLE IF EXISTS model_costs;

-- Remove migration record
DELETE FROM migration_log WHERE migration_id = '001_cost_tracking_schema';

COMMIT;
