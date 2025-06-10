# LLM API Cost Tracking System - Integration Documentation

## Task 96.3: Integration with Existing System Components

### Overview
This document describes the integration of the LLM API Cost Tracking System with SwarmBot's existing components. The integration enables real-time cost tracking and analysis across all LLM API interactions.

### Integration Points

#### 1. Context Manager Integration (`src/core/context_manager.py`)
The ConversationContext class has been enhanced with cost tracking capabilities:

- **Cost Tracker Parameter**: Accepts an optional `cost_tracker` parameter during initialization
- **Cost Metadata Tracking**: Maintains token usage metadata including:
  - `total_tokens`: Total tokens in the context
  - `input_tokens`: Cumulative input tokens from user messages
  - `output_tokens`: Cumulative output tokens from assistant messages
  - `estimated_cost`: Calculated cost estimate (when integrated with cost tracker)

- **Key Methods**:
  - `add_message()`: Updates token counts and notifies cost tracker
  - `get_cost_metadata()`: Returns current cost tracking metadata
  - `set_cost_tracker()`: Allows dynamic cost tracker assignment
  - `get_summary()`: Includes cost tracking info when enabled

#### 2. LLM Client Adapter Integration (`src/llm_client_adapter.py`)
The LLMClient class fully integrates with the IntegratedAnalyzer for comprehensive cost tracking:

- **Automatic Initialization**: Cost tracking is enabled by default if `TRACK_COSTS` is true in configuration
- **Per-Request Tracking**: Every LLM request is automatically tracked with:
  - Token counting for input and output
  - Cost calculation based on model and provider
  - Conversation ID association for detailed tracking

- **Key Features**:
  - `_track_cost()`: Internal method that tracks costs after each successful LLM request
  - `get_cost_summary()`: Returns comprehensive cost analysis from the integrated analyzer
  - `shutdown()`: Properly closes cost tracking and exports data if configured

- **Provider Detection**: Automatically detects the actual LLM provider from the client class for accurate cost attribution

#### 3. Database Integration (`src/database/cost_tracking.py`)
The CostTrackingDB extends the existing ChatDatabase with cost-specific operations:

- **Schema Extensions**: Three new tables for cost tracking:
  - `model_costs`: Stores pricing information for each model/provider
  - `request_costs`: Records individual API request costs
  - `conversation_costs`: Aggregates costs at the conversation level

- **Performance Optimizations**:
  - SQLite WAL mode for better concurrency
  - Indexed columns for efficient queries
  - Trigger-based automatic aggregation
  - In-memory caching for model costs

- **Key Methods**:
  - `log_request_cost()`: Records cost for a single API request
  - `get_conversation_cost_summary()`: Retrieves cost summary for a conversation
  - `get_model_usage_stats()`: Provides usage analytics by model
  - `check_budget_threshold()`: Monitors budget compliance

#### 4. Integrated Analyzer (`src/core/integrated_analyzer.py`)
The IntegratedAnalyzer combines token analysis with cost tracking:

- **Unified Analysis**: Single entry point for both token counting and cost calculation
- **Session Metrics**: Tracks comprehensive metrics including:
  - Total tokens and costs
  - Model-specific usage and efficiency
  - Cost breakdowns (input vs output)
  - Token efficiency trends

- **Recommendations Engine**: Provides cost optimization suggestions based on:
  - Model efficiency comparisons
  - Token usage patterns
  - Budget utilization
  - Historical trends

### Configuration Options

The cost tracking system respects the following configuration options:

```python
# Enable/disable cost tracking
TRACK_COSTS = True  # Default: True

# Monthly budget alert threshold
COST_ALERT_THRESHOLD = 10.00  # Default: $10.00

# Custom costs file for overriding default pricing
CUSTOM_COSTS_FILE = "path/to/custom_costs.json"  # Optional

# Export costs when shutting down
EXPORT_COSTS_ON_EXIT = True  # Default: False

# Database path for cost tracking tables
DATABASE_PATH = "data/swarmbot_chats.db"  # Default
```

### Usage Examples

#### Basic Usage with Context Manager
```python
from src.core.context_manager import ConversationContext
from src.core.cost_tracker import CostTracker
from src.config import Configuration

# Initialize
config = Configuration()
cost_tracker = CostTracker(config)
context = ConversationContext(cost_tracker=cost_tracker)

# Add messages
context.add_message("user", "Hello!")
context.add_message("assistant", "Hi there!")

# Get cost metadata
cost_info = context.get_cost_metadata()
print(f"Total tokens: {cost_info['total_tokens']}")
```

#### Using LLM Client with Cost Tracking
```python
from src.llm_client_adapter import LLMClient

# Cost tracking is automatic when enabled
client = LLMClient(provider="openai")

# Make requests - costs are tracked automatically
messages = [{"role": "user", "content": "Hello!"}]
response = client.get_response(messages, conversation_id="conv_123")

# Get cost summary
summary = client.get_cost_summary()
print(f"Session cost: ${summary['session']['total_cost']:.4f}")
```

#### Direct Database Queries
```python
from src.database.cost_tracking import CostTrackingDB

# Initialize database
db = CostTrackingDB()

# Get conversation costs
conv_summary = db.get_conversation_cost_summary("conv_123")

# Get model usage statistics
stats = db.get_model_usage_stats()

# Check budget status
budget_status = db.check_budget_threshold(10.0)
```

### Testing

Integration tests are provided in `tests/test_integration_96_3.py`:

1. **Context Manager Integration Test**: Verifies cost metadata tracking
2. **LLM Client Integration Test**: Tests automatic cost tracking on requests
3. **Full Integration Test**: End-to-end test of all components working together

Run tests with:
```bash
python tests/test_integration_96_3.py
```

### Migration Support

Database migrations are automatically applied on startup. Migration files:
- `001_cost_tracking_schema.sql`: Creates core tables
- `002_add_model_costs_data.sql`: Seeds initial model pricing
- `003_add_cost_tracking_views.sql`: Adds reporting views
- `004_add_query_performance_monitoring.sql`: Adds performance tracking

### Next Steps

With subtask 96.3 complete, the next tasks are:

1. **96.4**: Implement reporting and visualization
2. **96.5**: Develop alerting and budgeting system
3. **96.6**: Add configuration options
4. **96.7**: Comprehensive testing

### Troubleshooting

Common issues and solutions:

1. **Cost tracking not working**: 
   - Verify `TRACK_COSTS=true` in configuration
   - Check database migrations have run
   - Ensure model costs are populated in database

2. **Performance issues**:
   - Check SQLite indexes are created
   - Monitor slow queries in performance log
   - Consider adjusting cache sizes

3. **Incorrect costs**:
   - Verify model names match between LLM client and cost database
   - Check for custom costs file override
   - Run cost updater to refresh pricing

### API Reference

See individual module documentation:
- `src/core/context_manager.py`
- `src/llm_client_adapter.py`
- `src/core/integrated_analyzer.py`
- `src/database/cost_tracking.py`
