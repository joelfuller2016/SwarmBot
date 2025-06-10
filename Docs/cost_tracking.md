# LLM API Cost Tracking System Documentation

## Overview

The LLM API Cost Tracking System (Task 96) provides comprehensive monitoring and reporting of AI API usage costs across multiple providers. This system integrates seamlessly with SwarmBot to track costs in real-time, provide budget alerts, and generate detailed reports.

## Features

### 🎯 Core Features
- **Real-time Cost Tracking**: Monitor costs as API calls are made
- **Multi-Provider Support**: Track costs for OpenAI, Anthropic, Google, and Groq
- **Budget Management**: Set monthly budgets with alerts and warnings
- **Cost Analytics**: Visualize spending patterns and trends
- **Export Capabilities**: Export data in JSON and CSV formats
- **Session-based Tracking**: Track costs per conversation session
- **Model Comparison**: Compare costs across different models and providers

### 📊 Dashboard Features
- Daily cost trends visualization
- Model usage pie charts
- Provider comparison charts
- Top cost sessions table
- Real-time metrics updates
- Export functionality

## Configuration

### Environment Variables

Add these variables to your `.env` file:

```bash
# Cost Tracking Configuration
TRACK_COSTS=true                    # Enable/disable cost tracking
COST_ALERT_THRESHOLD=10.00          # Monthly budget alert threshold (USD)
CUSTOM_COSTS_FILE=                  # Path to custom pricing file (optional)
EXPORT_COSTS_ON_EXIT=false          # Auto-export costs on shutdown

# Budget Alert Settings
DAILY_COST_LIMIT=1.00               # Daily spending limit (USD)
SESSION_COST_LIMIT=0.50             # Per-session cost limit (USD)
BUDGET_WARNING_PERCENT=80           # Percentage for warning alerts
BUDGET_CRITICAL_PERCENT=95          # Percentage for critical alerts

# Email Notifications (Optional)
ENABLE_EMAIL_ALERTS=false           # Enable email notifications
SMTP_HOST=smtp.gmail.com            # SMTP server host
SMTP_PORT=587                       # SMTP server port
SMTP_USERNAME=                      # SMTP username/email
SMTP_PASSWORD=                      # SMTP password
ALERT_FROM_EMAIL=                   # From email address
ALERT_TO_EMAILS=                    # Comma-separated recipients
```

### Custom Pricing File

You can override default pricing with a custom JSON file:

```json
{
  "openai": {
    "gpt-4": {
      "input_cost_per_1k": 0.03,
      "output_cost_per_1k": 0.06,
      "context_window": 8192
    }
  }
}
```

## Usage

### Enabling Cost Tracking

1. Set `TRACK_COSTS=true` in your `.env` file
2. Configure your budget threshold: `COST_ALERT_THRESHOLD=10.00`
3. Start SwarmBot normally - cost tracking will be automatic

### Viewing Cost Reports

#### Via Dashboard
1. Start SwarmBot with UI: `python swarmbot.py --ui`
2. Navigate to the "Cost Tracking" page
3. View real-time metrics and charts

#### Via Commands
```bash
# In SwarmBot chat
/costs                  # View current session costs
/costs summary         # View monthly summary
/costs export json     # Export cost data as JSON
/costs export csv      # Export cost data as CSV
```

### Budget Alerts

The system will automatically alert you when:
- Daily spending exceeds configured limit
- Monthly spending approaches threshold (80% warning, 95% critical)
- Individual session costs exceed limits
- Unusual spending patterns are detected

## API Reference

### Cost Tracker

```python
from src.core.cost_tracker import CostTracker

# Initialize tracker
tracker = CostTracker(config)

# Track a request
cost = tracker.track_request(
    conversation_id="session_123",
    model="gpt-4",
    input_tokens=150,
    output_tokens=250,
    provider="openai"
)

# Get summaries
session_summary = tracker.get_session_summary()
monthly_summary = tracker.get_monthly_summary()

# Export data
tracker.export_costs(format='json', output_path='costs.json')
```

### Budget Monitor

```python
from src.core.budget_monitor import BudgetMonitor

# Initialize monitor
monitor = BudgetMonitor(config, cost_db)

# Check budget status
status = monitor.check_budget_status()

# Get alerts
alerts = monitor.get_active_alerts()

# Configure custom alert
monitor.add_custom_alert(
    threshold_type="daily_cost",
    threshold_value=5.0,
    alert_level="warning"
)
```

### Database Queries

```python
from src.database.cost_tracking import CostTrackingDB

db = CostTrackingDB()

# Get conversation costs
costs = db.get_conversation_cost_summary("session_123")

# Get daily breakdown
daily = db.get_daily_costs(days=30)

# Get model usage stats
stats = db.get_model_usage_stats()

# Export data
db.export_costs_csv("report.csv", start_date="2025-01-01")
```

## Model Pricing Reference

### OpenAI
| Model | Input (per 1K tokens) | Output (per 1K tokens) | Context Window |
|-------|----------------------|------------------------|----------------|
| GPT-4 | $0.03 | $0.06 | 8,192 |
| GPT-4-Turbo | $0.01 | $0.03 | 128,000 |
| GPT-3.5-Turbo | $0.0005 | $0.0015 | 16,385 |
| GPT-4o | $0.005 | $0.015 | 128,000 |
| GPT-4o-mini | $0.00015 | $0.0006 | 128,000 |

### Anthropic
| Model | Input (per 1K tokens) | Output (per 1K tokens) | Context Window |
|-------|----------------------|------------------------|----------------|
| Claude-3-Opus | $0.015 | $0.075 | 200,000 |
| Claude-3-Sonnet | $0.003 | $0.015 | 200,000 |
| Claude-3-Haiku | $0.00025 | $0.00125 | 200,000 |

### Google
| Model | Input (per 1K tokens) | Output (per 1K tokens) | Context Window |
|-------|----------------------|------------------------|----------------|
| Gemini-Pro | $0.00125 | $0.00375 | 32,760 |
| Gemini-1.5-Pro | $0.0035 | $0.0105 | 1,048,576 |
| Gemini-1.5-Flash | $0.00035 | $0.00105 | 1,048,576 |

### Groq
| Model | Input (per 1K tokens) | Output (per 1K tokens) | Context Window |
|-------|----------------------|------------------------|----------------|
| Llama2-70B | $0.0007 | $0.0008 | 4,096 |
| Mixtral-8x7B | $0.00027 | $0.00027 | 32,768 |
| Gemma-7B | $0.0001 | $0.0001 | 8,192 |

## Troubleshooting

### Common Issues

#### Cost tracking not working
1. Verify `TRACK_COSTS=true` in `.env`
2. Check database migrations ran successfully
3. Ensure LLM provider is configured correctly
4. Check logs for error messages

#### Budget alerts not triggering
1. Verify `COST_ALERT_THRESHOLD` is set
2. Check email configuration if using email alerts
3. Ensure budget monitor service is running
4. Check `budget_alerts` table for recorded alerts

#### Export failing
1. Check write permissions for export directory
2. Verify sufficient disk space
3. Check for invalid characters in date range
4. Review logs for specific error messages

### Debug Mode

Enable debug logging for cost tracking:
```python
import logging
logging.getLogger('src.core.cost_tracker').setLevel(logging.DEBUG)
logging.getLogger('src.database.cost_tracking').setLevel(logging.DEBUG)
```

### Database Issues

Check database integrity:
```sql
-- Check tables exist
SELECT name FROM sqlite_master WHERE type='table';

-- Check recent costs
SELECT * FROM request_costs ORDER BY timestamp DESC LIMIT 10;

-- Check conversation totals
SELECT * FROM conversation_costs ORDER BY last_update DESC LIMIT 10;

-- Verify foreign keys
PRAGMA foreign_key_list(request_costs);
```

## Performance Considerations

- Cost tracking adds <5% latency to API requests
- Database queries are optimized with indexes
- Model costs are cached in memory (1-hour refresh)
- Automatic aggregation reduces query complexity
- WAL mode enabled for better concurrency

## Security

- Cost data is stored locally in SQLite database
- No cost data is sent to external services
- API keys are never stored with cost data
- Export files can be encrypted if needed
- Database supports user-level access control

## Migration Guide

### From Existing System

1. Backup your current database
2. Run migration scripts in order:
   ```bash
   python scripts/run_migrations.py
   ```
3. Verify data integrity:
   ```bash
   python scripts/verify_task_96.py
   ```
4. Update configuration files
5. Restart SwarmBot

### Rollback Procedure

If issues occur:
1. Stop SwarmBot
2. Restore database backup
3. Set `TRACK_COSTS=false`
4. Run rollback migrations
5. Restart SwarmBot

## Support

For issues or questions:
1. Check logs in `logs/cost_tracking.log`
2. Run verification script: `python scripts/verify_task_96.py`
3. Review this documentation
4. Submit issues to the SwarmBot repository

## Changelog

### Version 1.0.0 (Task 96 Completion)
- Initial implementation of cost tracking system
- Multi-provider support (OpenAI, Anthropic, Google, Groq)
- Real-time cost calculation and tracking
- Budget monitoring and alerts
- Dashboard visualization
- Export functionality
- Session-based cost tracking
- Foreign key constraints for data integrity
- Standardized session_id usage throughout system
