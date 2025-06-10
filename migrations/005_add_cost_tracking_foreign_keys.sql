-- Migration: 005_add_cost_tracking_foreign_keys
-- Description: Add foreign key constraints to cost tracking tables and standardize column names
-- Date: 2025-01-06

BEGIN TRANSACTION;

-- SQLite doesn't support adding foreign keys to existing tables directly
-- We need to recreate the tables with the proper constraints

-- First, rename existing tables to temporary names
ALTER TABLE request_costs RENAME TO request_costs_old;
ALTER TABLE conversation_costs RENAME TO conversation_costs_old;

-- Create new request_costs table with proper foreign key
CREATE TABLE request_costs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,  -- Changed from conversation_id to session_id for consistency
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    model TEXT NOT NULL,
    input_tokens INTEGER NOT NULL CHECK (input_tokens >= 0),
    output_tokens INTEGER NOT NULL CHECK (output_tokens >= 0),
    input_cost REAL NOT NULL CHECK (input_cost >= 0),
    output_cost REAL NOT NULL CHECK (output_cost >= 0),
    total_cost REAL NOT NULL CHECK (total_cost >= 0),
    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE
);

-- Create new conversation_costs table with proper foreign key
CREATE TABLE conversation_costs (
    session_id TEXT PRIMARY KEY,  -- Changed from conversation_id to session_id for consistency
    start_time DATETIME NOT NULL,
    last_update DATETIME NOT NULL,
    total_cost REAL NOT NULL DEFAULT 0 CHECK (total_cost >= 0),
    request_count INTEGER NOT NULL DEFAULT 0 CHECK (request_count >= 0),
    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE
);

-- Copy data from old tables, renaming columns
INSERT INTO request_costs (id, session_id, timestamp, model, input_tokens, output_tokens, input_cost, output_cost, total_cost)
SELECT id, conversation_id, timestamp, model, input_tokens, output_tokens, input_cost, output_cost, total_cost
FROM request_costs_old;

INSERT INTO conversation_costs (session_id, start_time, last_update, total_cost, request_count)
SELECT conversation_id, start_time, last_update, total_cost, request_count
FROM conversation_costs_old;

-- Drop old tables
DROP TABLE request_costs_old;
DROP TABLE conversation_costs_old;

-- Recreate indexes with new column names
CREATE INDEX idx_request_costs_session_id ON request_costs(session_id);
CREATE INDEX idx_request_costs_timestamp ON request_costs(timestamp);
CREATE INDEX idx_request_costs_model ON request_costs(model);
CREATE INDEX idx_request_costs_session_time ON request_costs(session_id, timestamp);

CREATE INDEX idx_conversation_costs_start_time ON conversation_costs(start_time);
CREATE INDEX idx_conversation_costs_last_update ON conversation_costs(last_update);
CREATE INDEX idx_conversation_costs_total_cost ON conversation_costs(total_cost DESC);

-- Recreate trigger with new column names
DROP TRIGGER IF EXISTS update_conversation_costs_on_insert;
CREATE TRIGGER update_conversation_costs_on_insert
AFTER INSERT ON request_costs
BEGIN
    INSERT INTO conversation_costs (session_id, start_time, last_update, total_cost, request_count)
    VALUES (NEW.session_id, NEW.timestamp, NEW.timestamp, NEW.total_cost, 1)
    ON CONFLICT(session_id) DO UPDATE SET
        last_update = NEW.timestamp,
        total_cost = total_cost + NEW.total_cost,
        request_count = request_count + 1;
END;

-- Insert migration record
INSERT INTO migration_log (migration_id, applied_at, description)
VALUES ('005_add_cost_tracking_foreign_keys', datetime('now'), 'Add foreign key constraints and standardize column names to session_id');

COMMIT;
