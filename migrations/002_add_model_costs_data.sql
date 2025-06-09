-- Migration: 002_add_model_costs_data
-- Description: Insert initial model cost data for common LLM providers
-- Date: 2025-01-06

BEGIN TRANSACTION;

-- Insert initial model cost data
-- OpenAI Models
INSERT OR REPLACE INTO model_costs (model_name, provider, input_cost_per_1k, output_cost_per_1k, context_window, last_updated)
VALUES 
    ('gpt-4-turbo', 'openai', 0.01, 0.03, 128000, datetime('now')),
    ('gpt-4', 'openai', 0.03, 0.06, 8192, datetime('now')),
    ('gpt-3.5-turbo', 'openai', 0.0005, 0.0015, 16385, datetime('now')),
    ('gpt-3.5-turbo-16k', 'openai', 0.003, 0.004, 16385, datetime('now')),
    ('gpt-4-turbo-preview', 'openai', 0.01, 0.03, 128000, datetime('now')),
    ('gpt-4-1106-preview', 'openai', 0.01, 0.03, 128000, datetime('now'));

-- Anthropic Models
INSERT OR REPLACE INTO model_costs (model_name, provider, input_cost_per_1k, output_cost_per_1k, context_window, last_updated)
VALUES 
    ('claude-3-opus', 'anthropic', 0.015, 0.075, 200000, datetime('now')),
    ('claude-3-sonnet', 'anthropic', 0.003, 0.015, 200000, datetime('now')),
    ('claude-3-haiku', 'anthropic', 0.00025, 0.00125, 200000, datetime('now')),
    ('claude-2.1', 'anthropic', 0.008, 0.024, 200000, datetime('now')),
    ('claude-2', 'anthropic', 0.008, 0.024, 100000, datetime('now')),
    ('claude-instant-1.2', 'anthropic', 0.0008, 0.0024, 100000, datetime('now'));

-- Google Models
INSERT OR REPLACE INTO model_costs (model_name, provider, input_cost_per_1k, output_cost_per_1k, context_window, last_updated)
VALUES 
    ('gemini-pro', 'google', 0.0005, 0.0015, 32768, datetime('now')),
    ('gemini-1.5-pro', 'google', 0.00125, 0.00375, 1048576, datetime('now')),
    ('gemini-1.5-flash', 'google', 0.00035, 0.00105, 1048576, datetime('now'));

-- Groq Models
INSERT OR REPLACE INTO model_costs (model_name, provider, input_cost_per_1k, output_cost_per_1k, context_window, last_updated)
VALUES 
    ('llama2-70b-4096', 'groq', 0.00070, 0.00080, 4096, datetime('now')),
    ('mixtral-8x7b-32768', 'groq', 0.00027, 0.00027, 32768, datetime('now')),
    ('gemma-7b-it', 'groq', 0.00010, 0.00010, 8192, datetime('now'));

-- Insert migration record
INSERT INTO migration_log (migration_id, applied_at, description)
VALUES ('002_add_model_costs_data', datetime('now'), 'Insert initial model cost data for common LLM providers');

COMMIT;
