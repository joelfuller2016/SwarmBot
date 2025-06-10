#!/usr/bin/env python3
"""
Implementation script for Task 96.2: Create database schema for cost tracking
This script creates all necessary files and directories for the cost tracking system
"""

import os
import sys
from pathlib import Path
import shutil


# SQL Migration files content
MIGRATION_001_SCHEMA = """-- Migration: 001_cost_tracking_schema
-- Description: Create cost tracking tables for LLM API usage
-- Date: 2025-01-06

BEGIN TRANSACTION;

-- Create migration_log table if it doesn't exist
CREATE TABLE IF NOT EXISTS migration_log (
    migration_id TEXT PRIMARY KEY,
    applied_at DATETIME NOT NULL,
    description TEXT
);

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

COMMIT;"""

MIGRATION_001_ROLLBACK = """-- Rollback Migration: 001_cost_tracking_schema
-- Description: Remove cost tracking tables and related objects
-- Date: 2025-01-06

BEGIN TRANSACTION;

-- Drop trigger
DROP TRIGGER IF EXISTS update_conversation_costs_on_insert;

-- Drop views
DROP VIEW IF EXISTS daily_cost_summary;
DROP VIEW IF EXISTS conversation_cost_ranking;
DROP VIEW IF EXISTS model_usage_stats;

-- Drop tables
DROP TABLE IF EXISTS conversation_costs;
DROP TABLE IF EXISTS request_costs;
DROP TABLE IF EXISTS model_costs;

-- Remove migration record
DELETE FROM migration_log WHERE migration_id = '001_cost_tracking_schema';

COMMIT;"""

MIGRATION_002_DATA = """-- Migration: 002_add_model_costs_data
-- Description: Insert initial model cost data for common LLM providers
-- Date: 2025-01-06

BEGIN TRANSACTION;

-- Insert initial model cost data
-- OpenAI Models
INSERT OR REPLACE INTO model_costs (model_name, provider, input_cost_per_1k, output_cost_per_1k, context_window, last_updated)
VALUES 
    -- GPT-4 Models
    ('gpt-4-turbo-preview', 'openai', 0.01, 0.03, 128000, datetime('now')),
    ('gpt-4-1106-preview', 'openai', 0.01, 0.03, 128000, datetime('now')),
    ('gpt-4', 'openai', 0.03, 0.06, 8192, datetime('now')),
    ('gpt-4-32k', 'openai', 0.06, 0.12, 32768, datetime('now')),
    
    -- GPT-3.5 Models
    ('gpt-3.5-turbo', 'openai', 0.0005, 0.0015, 16385, datetime('now')),
    ('gpt-3.5-turbo-16k', 'openai', 0.003, 0.004, 16385, datetime('now')),
    ('gpt-3.5-turbo-1106', 'openai', 0.001, 0.002, 16385, datetime('now')),
    
    -- Anthropic Claude Models
    ('claude-3-opus-20240229', 'anthropic', 0.015, 0.075, 200000, datetime('now')),
    ('claude-3-sonnet-20240229', 'anthropic', 0.003, 0.015, 200000, datetime('now')),
    ('claude-3-haiku-20240307', 'anthropic', 0.00025, 0.00125, 200000, datetime('now')),
    ('claude-2.1', 'anthropic', 0.008, 0.024, 200000, datetime('now')),
    ('claude-2.0', 'anthropic', 0.008, 0.024, 100000, datetime('now')),
    ('claude-instant-1.2', 'anthropic', 0.0008, 0.0024, 100000, datetime('now')),
    
    -- Google Models
    ('gemini-pro', 'google', 0.00025, 0.0005, 30720, datetime('now')),
    ('gemini-pro-vision', 'google', 0.00025, 0.0005, 12288, datetime('now')),
    
    -- Groq Models (very fast inference)
    ('llama-3.1-70b-versatile', 'groq', 0.00059, 0.00079, 131072, datetime('now')),
    ('llama-3.1-8b-instant', 'groq', 0.00005, 0.00008, 131072, datetime('now')),
    ('mixtral-8x7b-32768', 'groq', 0.00024, 0.00024, 32768, datetime('now')),
    ('gemma-7b-it', 'groq', 0.00007, 0.00007, 8192, datetime('now'));

-- Insert migration record
INSERT INTO migration_log (migration_id, applied_at, description)
VALUES ('002_add_model_costs_data', datetime('now'), 'Insert initial model cost data');

COMMIT;"""

MIGRATION_003_VIEWS = """-- Migration: 003_create_performance_views
-- Description: Create performance optimization views and monitoring tables
-- Date: 2025-01-06

BEGIN TRANSACTION;

-- Daily cost summary view
CREATE VIEW IF NOT EXISTS daily_cost_summary AS
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
CREATE VIEW IF NOT EXISTS conversation_cost_ranking AS
SELECT 
    c.conversation_id,
    c.total_cost,
    c.request_count,
    CASE 
        WHEN c.request_count > 0 THEN c.total_cost / c.request_count 
        ELSE 0 
    END as avg_cost_per_request,
    c.start_time,
    c.last_update,
    CAST(julianday(c.last_update) - julianday(c.start_time) AS REAL) as duration_days
FROM conversation_costs c
ORDER BY c.total_cost DESC;

-- Model usage statistics view
CREATE VIEW IF NOT EXISTS model_usage_stats AS
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

CREATE INDEX IF NOT EXISTS idx_query_performance_timestamp ON query_performance_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_query_performance_execution_time ON query_performance_log(execution_time_ms DESC);

-- High cost alert view (conversations exceeding threshold)
CREATE VIEW IF NOT EXISTS high_cost_conversations AS
SELECT 
    conversation_id,
    total_cost,
    request_count,
    start_time,
    last_update
FROM conversation_costs
WHERE total_cost > (
    SELECT AVG(total_cost) + 2 * 
    CASE 
        WHEN COUNT(*) > 1 THEN 
            SQRT(SUM((total_cost - (SELECT AVG(total_cost) FROM conversation_costs)) * 
                     (total_cost - (SELECT AVG(total_cost) FROM conversation_costs))) / (COUNT(*) - 1))
        ELSE 0
    END
    FROM conversation_costs
)
ORDER BY total_cost DESC;

-- Token usage patterns view
CREATE VIEW IF NOT EXISTS token_usage_patterns AS
SELECT 
    model,
    AVG(input_tokens) as avg_input_tokens,
    AVG(output_tokens) as avg_output_tokens,
    MAX(input_tokens) as max_input_tokens,
    MAX(output_tokens) as max_output_tokens,
    MIN(input_tokens) as min_input_tokens,
    MIN(output_tokens) as min_output_tokens,
    COUNT(*) as sample_count
FROM request_costs
GROUP BY model
HAVING sample_count > 10;

-- Insert migration record
INSERT INTO migration_log (migration_id, applied_at, description)
VALUES ('003_create_performance_views', datetime('now'), 'Create performance optimization views and monitoring tables');

COMMIT;"""


def create_file(filepath, content, description=""):
    """Create a file with the given content"""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if file exists
    if filepath.exists():
        print(f"⚠️  File already exists: {filepath}")
        response = input("Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Skipping...")
            return
    
    filepath.write_text(content)
    print(f"✅ Created: {filepath}")
    if description:
        print(f"   {description}")


def main():
    """Main implementation function"""
    # Get project root
    project_root = Path.cwd()
    
    # Verify we're in the SwarmBot project
    if not (project_root / "swarmbot.py").exists():
        print("❌ Error: This doesn't appear to be the SwarmBot project root.")
        print("   Please run this script from the SwarmBot project directory.")
        sys.exit(1)
    
    print("🚀 Implementing Cost Tracking Database Schema (Task 96.2)")
    print("=" * 60)
    
    # Create migration files
    print("\n📁 Creating migration files...")
    migrations = [
        ("migrations/001_cost_tracking_schema.sql", MIGRATION_001_SCHEMA, "Main schema creation"),
        ("migrations/001_cost_tracking_rollback.sql", MIGRATION_001_ROLLBACK, "Rollback script"),
        ("migrations/002_add_model_costs_data.sql", MIGRATION_002_DATA, "Initial model cost data"),
        ("migrations/003_create_performance_views.sql", MIGRATION_003_VIEWS, "Performance views"),
    ]
    
    for filepath, content, desc in migrations:
        create_file(project_root / filepath, content, desc)
    
    # Create documentation
    print("\n📄 Creating documentation...")
    doc_content = """# Cost Tracking Database Schema

## Overview
This directory contains the database schema and migrations for the LLM API Cost Tracking System (Task 96.2).

## Migration Files

1. **001_cost_tracking_schema.sql** - Creates the core tables:
   - `model_costs` - Stores cost information for different LLM models
   - `request_costs` - Tracks individual API request costs
   - `conversation_costs` - Aggregates costs per conversation

2. **002_add_model_costs_data.sql** - Seeds initial model cost data for:
   - OpenAI (GPT-4, GPT-3.5)
   - Anthropic (Claude 3 family)
   - Google (Gemini)
   - Groq (Llama, Mixtral)

3. **003_create_performance_views.sql** - Creates performance monitoring views:
   - `daily_cost_summary` - Daily cost breakdown
   - `conversation_cost_ranking` - Top conversations by cost
   - `model_usage_stats` - Usage statistics per model
   - `high_cost_conversations` - Anomaly detection
   - `token_usage_patterns` - Token usage analysis

## Running Migrations

Use the migration runner script:
```bash
python scripts/run_migrations.py migrate --db-path swarmbot.db --migrations-dir migrations
```

## Integration

The cost tracking system integrates with:
- `src/database/cost_tracking_db.py` - Main database interface
- `src/core/cost_tracker.py` - Cost calculation logic
- Token analyzer for real-time tracking

## Testing

Run the test suite:
```bash
python -m pytest tests/database/test_cost_tracking.py -v
```
"""
    
    create_file(project_root / "migrations/README.md", doc_content, "Migration documentation")
    
    # Create migration runner script
    print("\n🔧 Creating migration runner script...")
    runner_path = project_root / "scripts/run_migrations.py"
    if not runner_path.exists():
        # Get the content from the artifact we created earlier
        print("   Note: Please copy the run_migrations.py script from the artifacts to scripts/")
    
    # Create cost tracking database module
    print("\n💾 Creating database module...")
    db_module_path = project_root / "src/database/cost_tracking_db.py"
    if not db_module_path.exists():
        print("   Note: Please copy the cost_tracking_db.py from the artifacts to src/database/")
    
    # Create test file
    print("\n🧪 Creating test file...")
    test_path = project_root / "tests/database/test_cost_tracking.py"
    if not test_path.exists():
        print("   Note: Please copy the test_cost_tracking.py from the artifacts to tests/database/")
    
    print("\n✨ Implementation complete!")
    print("\nNext steps:")
    print("1. Copy the Python files from the artifacts to their respective locations")
    print("2. Run the migrations: python scripts/run_migrations.py migrate")
    print("3. Run the tests: python -m pytest tests/database/test_cost_tracking.py -v")
    print("4. Update src/llm_client_adapter.py to integrate cost tracking")
    print("5. Update task status in taskmaster")


if __name__ == "__main__":
    main()