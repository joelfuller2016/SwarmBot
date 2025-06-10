-- Migration: 006_add_budget_alerts_table
-- Description: Create table for tracking budget alerts and notifications
-- Date: 2025-01-06

BEGIN TRANSACTION;

-- Create budget_alerts table
CREATE TABLE IF NOT EXISTS budget_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id TEXT UNIQUE NOT NULL,
    alert_type TEXT NOT NULL,
    level TEXT NOT NULL CHECK (level IN ('info', 'warning', 'critical')),
    message TEXT NOT NULL,
    current_value REAL NOT NULL,
    threshold REAL NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,
    acknowledged BOOLEAN NOT NULL DEFAULT 0,
    acknowledged_at DATETIME,
    acknowledged_by TEXT
);

-- Create indexes for budget_alerts
CREATE INDEX IF NOT EXISTS idx_budget_alerts_timestamp ON budget_alerts(timestamp);
CREATE INDEX IF NOT EXISTS idx_budget_alerts_type ON budget_alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_budget_alerts_level ON budget_alerts(level);
CREATE INDEX IF NOT EXISTS idx_budget_alerts_acknowledged ON budget_alerts(acknowledged);

-- Create budget_rules table for storing dynamic budget configurations
CREATE TABLE IF NOT EXISTS budget_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_name TEXT UNIQUE NOT NULL,
    rule_type TEXT NOT NULL,
    rule_value JSON NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_budget_rules_timestamp
AFTER UPDATE ON budget_rules
BEGIN
    UPDATE budget_rules SET updated_at = datetime('now')
    WHERE id = NEW.id;
END;

-- Insert default budget rules
INSERT OR IGNORE INTO budget_rules (rule_name, rule_type, rule_value) VALUES
    ('monthly_budget_default', 'budget_limit', '{"amount": 10.0, "currency": "USD"}'),
    ('daily_limit_default', 'budget_limit', '{"amount": 1.0, "currency": "USD"}'),
    ('session_limit_default', 'budget_limit', '{"amount": 0.5, "currency": "USD"}'),
    ('warning_threshold', 'alert_threshold', '{"percentage": 80}'),
    ('critical_threshold', 'alert_threshold', '{"percentage": 95}'),
    ('alert_cooldown', 'alert_config', '{"minutes": 60}'),
    ('spending_spike_multiplier', 'anomaly_detection', '{"multiplier": 3.0}');

-- Create notification_queue table for managing alert notifications
CREATE TABLE IF NOT EXISTS notification_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id TEXT NOT NULL,
    notification_type TEXT NOT NULL CHECK (notification_type IN ('email', 'webhook', 'dashboard')),
    recipient TEXT NOT NULL,
    payload JSON NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed', 'cancelled')),
    attempts INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sent_at DATETIME,
    error_message TEXT,
    FOREIGN KEY (alert_id) REFERENCES budget_alerts(alert_id)
);

-- Create indexes for notification_queue
CREATE INDEX IF NOT EXISTS idx_notification_queue_status ON notification_queue(status);
CREATE INDEX IF NOT EXISTS idx_notification_queue_alert_id ON notification_queue(alert_id);
CREATE INDEX IF NOT EXISTS idx_notification_queue_created_at ON notification_queue(created_at);

-- Insert migration record
INSERT INTO migration_log (migration_id, applied_at, description)
VALUES ('006_add_budget_alerts_table', datetime('now'), 'Create budget alerts and notification system tables');

COMMIT;
