"""
Core cost tracking module for LLM API usage
Provides classes and utilities for tracking API costs in real-time
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from decimal import Decimal
import logging
from pathlib import Path

from ..database.cost_tracking import CostTrackingDB
from ..config import Configuration
from .budget_monitor import BudgetMonitor, BudgetAlert

logger = logging.getLogger(__name__)


class ModelCost:
    """Represents the cost structure for a specific LLM model"""
    
    def __init__(self, model_name: str, provider: str, 
                 input_cost_per_1k: float, output_cost_per_1k: float,
                 context_window: int):
        self.model_name = model_name
        self.provider = provider
        self.input_cost_per_1k = Decimal(str(input_cost_per_1k))
        self.output_cost_per_1k = Decimal(str(output_cost_per_1k))
        self.context_window = context_window
        self.last_updated = datetime.now()
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> Dict[str, float]:
        """Calculate the cost for a specific token count"""
        input_cost = float((Decimal(str(input_tokens)) / Decimal('1000')) * self.input_cost_per_1k)
        output_cost = float((Decimal(str(output_tokens)) / Decimal('1000')) * self.output_cost_per_1k)
        total_cost = input_cost + output_cost
        
        return {
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': total_cost
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'model_name': self.model_name,
            'provider': self.provider,
            'input_cost_per_1k': float(self.input_cost_per_1k),
            'output_cost_per_1k': float(self.output_cost_per_1k),
            'context_window': self.context_window,
            'last_updated': self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelCost':
        """Create ModelCost from dictionary"""
        return cls(
            model_name=data['model_name'],
            provider=data['provider'],
            input_cost_per_1k=data['input_cost_per_1k'],
            output_cost_per_1k=data['output_cost_per_1k'],
            context_window=data['context_window']
        )


class RequestCost:
    """Represents the cost of a single API request"""
    
    def __init__(self, session_id: str, model: str,
                 input_tokens: int, output_tokens: int,
                 input_cost: float, output_cost: float,
                 timestamp: Optional[datetime] = None):
        self.session_id = session_id
        self.model = model
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.input_cost = input_cost
        self.output_cost = output_cost
        self.total_cost = input_cost + output_cost
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'session_id': self.session_id,
            'model': self.model,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'input_cost': self.input_cost,
            'output_cost': self.output_cost,
            'total_cost': self.total_cost,
            'timestamp': self.timestamp.isoformat()
        }


class CostTracker:
    """Main cost tracking manager"""
    
    def __init__(self, config: Configuration):
        self.config = config
        self.enabled = config.get('TRACK_COSTS', True)
        self.alert_threshold = config.get('COST_ALERT_THRESHOLD', 10.0)
        self.custom_costs_file = config.get('CUSTOM_COSTS_FILE', None)
        self.export_on_exit = config.get('EXPORT_COSTS_ON_EXIT', False)
        
        # Initialize database
        db_path = config.get('DATABASE_PATH', 'data/swarmbot_chats.db')
        self.db = CostTrackingDB(db_path)
        
        # Load custom costs if provided
        if self.custom_costs_file and Path(self.custom_costs_file).exists():
            self._load_custom_costs()
        
        # Track current session costs
        self.session_costs = {
            'total': 0.0,
            'by_model': {},
            'by_conversation': {},
            'request_count': 0
        }
    
    def _load_custom_costs(self):
        """Load custom model costs from file"""
        try:
            with open(self.custom_costs_file, 'r') as f:
                custom_costs = json.load(f)
            
            for provider, models in custom_costs.items():
                for model_name, costs in models.items():
                    self.db.update_model_cost(
                        model_name=model_name,
                        provider=provider,
                        input_cost_per_1k=costs['input_cost_per_1k'],
                        output_cost_per_1k=costs['output_cost_per_1k'],
                        context_window=costs.get('context_window', 4096)
                    )
            
            logger.info(f"Loaded custom costs from {self.custom_costs_file}")
        except Exception as e:
            logger.error(f"Failed to load custom costs: {e}")
    
    def track_request(self, session_id: str, model: str,
                     input_tokens: int, output_tokens: int,
                     provider: Optional[str] = None) -> Optional[RequestCost]:
        """Track a single API request"""
        if not self.enabled:
            return None
        
        try:
            # Log to database
            self.db.log_request_cost(
                session_id=session_id,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                provider=provider
            )
            
            # Get the calculated costs
            model_costs = self.db._get_model_costs(model, provider)
            model_cost = ModelCost(
                model_name=model,
                provider=provider or 'unknown',
                input_cost_per_1k=model_costs['input_cost_per_1k'],
                output_cost_per_1k=model_costs['output_cost_per_1k'],
                context_window=model_costs['context_window']
            )
            
            costs = model_cost.calculate_cost(input_tokens, output_tokens)
            
            # Create RequestCost object
            request_cost = RequestCost(
                session_id=session_id,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                input_cost=costs['input_cost'],
                output_cost=costs['output_cost']
            )
            
            # Update session tracking
            self._update_session_costs(request_cost)
            
            # Check for alerts
            self._check_cost_alerts()
            
            return request_cost
            
        except Exception as e:
            logger.error(f"Failed to track request cost: {e}")
            return None
    
    def _update_session_costs(self, request_cost: RequestCost):
        """Update session-level cost tracking"""
        self.session_costs['total'] += request_cost.total_cost
        self.session_costs['request_count'] += 1
        
        # Track by model
        if request_cost.model not in self.session_costs['by_model']:
            self.session_costs['by_model'][request_cost.model] = {
                'total': 0.0,
                'requests': 0
            }
        self.session_costs['by_model'][request_cost.model]['total'] += request_cost.total_cost
        self.session_costs['by_model'][request_cost.model]['requests'] += 1
        
        # Track by conversation
        if request_cost.session_id not in self.session_costs['by_conversation']:
            self.session_costs['by_conversation'][request_cost.session_id] = {
                'total': 0.0,
                'requests': 0
            }
        self.session_costs['by_conversation'][request_cost.session_id]['total'] += request_cost.total_cost
        self.session_costs['by_conversation'][request_cost.session_id]['requests'] += 1
    
    def _check_cost_alerts(self):
        """Check if costs exceed alert thresholds"""
        # Check monthly budget
        budget_status = self.db.check_budget_threshold(self.alert_threshold)
        if budget_status['exceeded']:
            logger.warning(
                f"Monthly cost budget exceeded! "
                f"Current: ${budget_status['current_month_cost']:.2f}, "
                f"Threshold: ${self.alert_threshold:.2f}"
            )
            # TODO: Implement notification system (email, webhook, etc.)
        
        # Check for cost spikes
        if self.session_costs['request_count'] > 0:
            avg_cost = self.session_costs['total'] / self.session_costs['request_count']
            if avg_cost > self.alert_threshold / 100:  # Alert if avg request > 1% of monthly budget
                logger.warning(
                    f"High average request cost detected: ${avg_cost:.4f}"
                )
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get current session cost summary"""
        return {
            'enabled': self.enabled,
            'session_total': self.session_costs['total'],
            'request_count': self.session_costs['request_count'],
            'average_cost': (
                self.session_costs['total'] / self.session_costs['request_count']
                if self.session_costs['request_count'] > 0 else 0
            ),
            'by_model': self.session_costs['by_model'],
            'top_conversations': sorted(
                self.session_costs['by_conversation'].items(),
                key=lambda x: x[1]['total'],
                reverse=True
            )[:5]
        }
    
    def get_monthly_summary(self) -> Dict[str, Any]:
        """Get current month's cost summary"""
        budget_status = self.db.check_budget_threshold(self.alert_threshold)
        forecast = self.db.get_cost_forecast(30)
        
        return {
            'current_month_cost': budget_status['current_month_cost'],
            'budget_threshold': budget_status['budget_threshold'],
            'percentage_used': budget_status['percentage_used'],
            'remaining_budget': budget_status['remaining_budget'],
            'forecast_30_days': forecast['estimated_cost'],
            'daily_average': forecast['avg_daily_cost']
        }
    
    def export_costs(self, format: str = 'json', output_path: Optional[str] = None) -> str:
        """Export cost data in specified format"""
        if format == 'json':
            json_data = self.db.export_costs_json()
            if output_path:
                with open(output_path, 'w') as f:
                    f.write(json_data)
                logger.info(f"Exported costs to {output_path}")
            return json_data
        
        elif format == 'csv':
            if not output_path:
                output_path = f"costs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            self.db.export_costs_csv(output_path)
            return output_path
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def shutdown(self):
        """Cleanup and export on shutdown if configured"""
        if self.export_on_exit and self.session_costs['request_count'] > 0:
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                export_path = f"costs_export_{timestamp}.json"
                self.export_costs('json', export_path)
                logger.info(f"Exported costs on exit to {export_path}")
            except Exception as e:
                logger.error(f"Failed to export costs on exit: {e}")
        
        # Log session summary
        summary = self.get_session_summary()
        logger.info(f"Cost tracking session summary: {json.dumps(summary, indent=2)}")
