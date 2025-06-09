-- Migration: 003_add_cost_tracking_views
-- Description: Add database views for common cost tracking queries
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
    c.total_cost / c.request_count as avg_cost_per_request,
    c.start_time,
    c.last_update,
    CAST((julianday(c.last_update) - julianday(c.start_time)) * 24 AS INTEGER) as duration_hours
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

-- Insert migration record
INSERT INTO migration_log (migration_id, applied_at, description)
VALUES ('003_add_cost_tracking_views', datetime('now'), 'Add database views for common cost tracking queries');

COMMIT;
