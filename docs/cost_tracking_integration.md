# Cost Tracking System Integration

## Overview

This document describes the integration of the LLM API Cost Tracking System (Task 96) into SwarmBot. The system tracks API usage costs across multiple LLM providers in real-time.

## Architecture

### Core Components

1. **Cost Tracker** (`src/core/cost_tracker.py`)
   - Main cost tracking logic with ModelCost and RequestCost classes
   - Manages session-level cost aggregation
   - Handles budget alerts and thresholds

2. **Integrated Analyzer** (`src/core/integrated_analyzer.py`)
   - Combines token analysis with cost tracking
   - Provides comprehensive usage monitoring
   - Generates optimization recommendations

3. **Cost Updater** (`src/core/cost_updater.py`)
   - Fetches and updates model pricing from provider APIs
   - Maintains static fallback pricing data
   - Validates cost data integrity

4. **Database Layer** (`src/database/cost_tracking.py`)
   - Extends ChatDatabase for cost-specific operations
   - Implements SQLite optimizations (WAL mode, indexing)
   - Provides caching for frequently accessed model costs

### Integration Points

1. **LLM Client Adapter** (`src/llm_client_adapter.py`)
   - Modified to track costs after each LLM request
   - Added optional conversation_id parameter
   - Integrated with IntegratedAnalyzer for real-time tracking

2. **Context Manager** (`src/core/context_manager.py`)
   - Enhanced to track token usage by message role
   - Provides cost metadata for analysis
   - Supports optional cost tracker integration

## Database Schema

### Tables

1. **model_costs**
   ```sql
   CREATE TABLE model_costs (
       model_name TEXT NOT NULL,
       provider TEXT NOT NULL,
       input_cost_per_1k REAL NOT NULL,
       output_cost_per_1k REAL NOT NULL,
       context_window INTEGER NOT NULL,
       last_updated DATETIME NOT NULL,
       PRIMARY KEY (model_name, provider)
   );
   ```

2. **request_costs**
   ```sql
   CREATE TABLE request_costs (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       conversation_id TEXT NOT NULL,
       timestamp DATETIME NOT NULL,
       model TEXT NOT NULL,
       input_tokens INTEGER NOT NULL,
       output_tokens INTEGER NOT NULL,
       input_cost REAL NOT NULL,
       output_cost REAL NOT NULL,
       total_cost REAL NOT NULL
   );
   ```

3. **conversation_costs**
   ```sql
   CREATE TABLE conversation_costs (
       conversation_id TEXT PRIMARY KEY,
       start_time DATETIME NOT NULL,
       last_update DATETIME NOT NULL,
       total_cost REAL NOT NULL,
       request_count INTEGER NOT NULL
   );
   ```

### Indexes and Triggers

- Multiple indexes for efficient querying
- Automatic trigger to update conversation_costs on request insertion
- Query performance monitoring table

## Configuration

The system uses the following configuration options:

- `TRACK_COSTS` (default: true) - Enable/disable cost tracking
- `COST_ALERT_THRESHOLD` (default: 10.0) - Monthly budget alert threshold
- `CUSTOM_COSTS_FILE` - Path to custom pricing JSON file
- `EXPORT_COSTS_ON_EXIT` (default: false) - Auto-export costs on shutdown
- `COST_UPDATE_INTERVAL_HOURS` (default: 24) - Pricing update frequency

## Usage

### Basic Usage

```python
from src.llm_client_adapter import LLMClient

# Initialize client with cost tracking
client = LLMClient()

# Send request with conversation tracking
response = client.get_response(
    messages=[
        {"role": "user", "content": "Hello!"}
    ],
    conversation_id="conv_123"
)

# Get cost summary
summary = client.get_cost_summary()
print(f"Total cost: ${summary['session']['total_cost']:.4f}")
```

### Advanced Features

1. **Budget Monitoring**
   ```python
   # Check monthly budget status
   budget_status = cost_tracker.db.check_budget_threshold(10.0)
   if budget_status['exceeded']:
       print(f"Budget exceeded! Current: ${budget_status['current_month_cost']:.2f}")
   ```

2. **Cost Forecasting**
   ```python
   # Get 30-day cost forecast
   forecast = cost_tracker.db.get_cost_forecast(30)
   print(f"Projected 30-day cost: ${forecast['estimated_cost']:.2f}")
   ```

3. **Model Comparison**
   ```python
   # Get model usage statistics
   stats = cost_tracker.db.get_model_usage_stats()
   for stat in stats:
       print(f"{stat['model']}: ${stat['avg_cost_per_request']:.4f} per request")
   ```

## Initialization

To initialize the cost tracking system:

```bash
python scripts/initialize_cost_tracking.py
```

This script:
1. Runs database migrations
2. Loads initial model pricing data
3. Validates the system configuration
4. Performs health checks

## Testing

To test the integration:

```bash
python scripts/test_cost_tracking.py
```

This verifies:
- LLM client initialization with cost tracking
- Request tracking and cost calculation
- Database persistence
- Cost summary generation

## Performance Considerations

1. **Caching**: Model costs are cached in memory with 1-hour refresh
2. **Async Logging**: Cost tracking runs asynchronously to minimize latency
3. **SQLite Optimizations**: WAL mode, proper indexing, connection pooling
4. **Batch Operations**: Supports bulk cost data exports

## Monitoring and Alerts

The system provides:
- Real-time cost tracking per request
- Monthly budget threshold alerts
- High cost conversation detection
- Cost spike notifications
- Daily/weekly/monthly cost reports

## Future Enhancements

1. **Webhook Integration**: Send cost alerts to external systems
2. **Dashboard UI**: Web-based cost visualization
3. **Multi-Currency Support**: Handle international deployments
4. **Advanced Analytics**: ML-based cost optimization recommendations
5. **Provider API Integration**: Real-time pricing updates

## Troubleshooting

### Common Issues

1. **Cost tracking not working**
   - Check TRACK_COSTS configuration
   - Verify database migrations have run
   - Check logs for initialization errors

2. **Missing model costs**
   - Run cost updater to refresh pricing
   - Check custom costs file if configured
   - Verify provider names match expected values

3. **Performance degradation**
   - Check database size and run VACUUM
   - Verify indexes are properly created
   - Review query performance logs

### Debug Commands

```python
# Check database health
from src.database.cost_tracking import CostTrackingHealthCheck
health_check = CostTrackingHealthCheck(db)
health = health_check.check_database_health()
print(health)

# Validate costs
from src.core.cost_updater import CostUpdater
updater = CostUpdater(config, db)
validation = updater.validate_costs()
print(validation)
```

## Security Considerations

1. **Data Privacy**: Cost data is stored locally only
2. **API Keys**: Provider API keys are not stored in cost database
3. **Access Control**: Database file permissions should be restricted
4. **Audit Trail**: All cost updates are logged with timestamps

## API Reference

See individual module documentation:
- [Cost Tracker API](src/core/cost_tracker.py)
- [Integrated Analyzer API](src/core/integrated_analyzer.py)
- [Database API](src/database/cost_tracking.py)
