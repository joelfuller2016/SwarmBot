"""
Budget alerting and monitoring system for cost tracking
Provides real-time alerts when costs exceed thresholds
"""

import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from decimal import Decimal
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

from ..database.cost_tracking import CostTrackingDB
from ..config import Configuration

logger = logging.getLogger(__name__)


class AlertLevel:
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning" 
    CRITICAL = "critical"


class BudgetAlert:
    """Represents a budget alert"""
    
    def __init__(self, alert_type: str, level: str, message: str,
                 current_value: float, threshold: float,
                 metadata: Optional[Dict] = None):
        self.alert_id = f"{alert_type}_{datetime.now().timestamp()}"
        self.alert_type = alert_type
        self.level = level
        self.message = message
        self.current_value = current_value
        self.threshold = threshold
        self.timestamp = datetime.now()
        self.metadata = metadata or {}
        self.acknowledged = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary"""
        return {
            'alert_id': self.alert_id,
            'alert_type': self.alert_type,
            'level': self.level,
            'message': self.message,
            'current_value': self.current_value,
            'threshold': self.threshold,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata,
            'acknowledged': self.acknowledged
        }


class BudgetMonitor:
    """Monitors costs and triggers alerts based on configured thresholds"""
    
    def __init__(self, config: Configuration, cost_db: CostTrackingDB):
        self.config = config
        self.cost_db = cost_db
        self.active_alerts: Dict[str, BudgetAlert] = {}
        self.alert_callbacks: List[Callable[[BudgetAlert], None]] = []
        
        # Load alert configuration
        self.thresholds = self._load_thresholds()
        self.check_interval = timedelta(minutes=5)  # Check every 5 minutes
        self.last_check = None
        
    def _load_thresholds(self) -> Dict[str, Any]:
        """Load alert thresholds from configuration"""
        return {
            'monthly_budget': float(self.config.config.get('COST_ALERT_THRESHOLD', 10.0)),
            'daily_limit': float(self.config.config.get('DAILY_COST_LIMIT', 1.0)),
            'session_limit': float(self.config.config.get('SESSION_COST_LIMIT', 0.5)),
            'model_limits': self._load_model_limits(),
            'warning_percentage': float(self.config.config.get('BUDGET_WARNING_PERCENT', 80)),
            'critical_percentage': float(self.config.config.get('BUDGET_CRITICAL_PERCENT', 95))
        }
    
    def _load_model_limits(self) -> Dict[str, float]:
        """Load per-model cost limits"""
        limits_file = self.config.config.get('MODEL_LIMITS_FILE')
        if limits_file and os.path.exists(limits_file):
            try:
                with open(limits_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load model limits: {e}")
        
        # Default limits
        return {
            'gpt-4': 2.0,
            'gpt-3.5-turbo': 0.5,
            'claude-3-opus': 3.0,
            'claude-3-sonnet': 1.0
        }
    
    def register_alert_callback(self, callback: Callable[[BudgetAlert], None]):
        """Register a callback for when alerts are triggered"""
        self.alert_callbacks.append(callback)
    
    def check_budgets(self) -> List[BudgetAlert]:
        """Check all budget thresholds and generate alerts"""
        if self.last_check and datetime.now() - self.last_check < self.check_interval:
            return []  # Too soon since last check
        
        self.last_check = datetime.now()
        new_alerts = []
        
        # Check monthly budget
        monthly_alert = self._check_monthly_budget()
        if monthly_alert:
            new_alerts.append(monthly_alert)
        
        # Check daily limit
        daily_alert = self._check_daily_limit()
        if daily_alert:
            new_alerts.append(daily_alert)
        
        # Check model-specific limits
        model_alerts = self._check_model_limits()
        new_alerts.extend(model_alerts)
        
        # Check for unusual spending patterns
        anomaly_alerts = self._check_spending_anomalies()
        new_alerts.extend(anomaly_alerts)
        
        # Process new alerts
        for alert in new_alerts:
            if alert.alert_id not in self.active_alerts:
                self.active_alerts[alert.alert_id] = alert
                self._trigger_alert(alert)
        
        return new_alerts
    
    def _check_monthly_budget(self) -> Optional[BudgetAlert]:
        """Check if monthly budget is exceeded or near limit"""
        budget_status = self.cost_db.check_budget_threshold(self.thresholds['monthly_budget'])
        
        current_cost = budget_status['current_month_cost']
        threshold = budget_status['budget_threshold']
        percentage = budget_status['percentage_used']
        
        if budget_status['exceeded']:
            return BudgetAlert(
                alert_type="monthly_budget_exceeded",
                level=AlertLevel.CRITICAL,
                message=f"Monthly budget exceeded! Current: ${current_cost:.2f}, Budget: ${threshold:.2f}",
                current_value=current_cost,
                threshold=threshold,
                metadata={'percentage': percentage}
            )
        elif percentage >= self.thresholds['critical_percentage']:
            return BudgetAlert(
                alert_type="monthly_budget_critical",
                level=AlertLevel.CRITICAL,
                message=f"Monthly budget at {percentage:.1f}%! Current: ${current_cost:.2f}, Budget: ${threshold:.2f}",
                current_value=current_cost,
                threshold=threshold,
                metadata={'percentage': percentage}
            )
        elif percentage >= self.thresholds['warning_percentage']:
            # Check if we already have this warning
            alert_id = f"monthly_budget_warning_{datetime.now().strftime('%Y-%m')}"
            if alert_id not in self.active_alerts:
                return BudgetAlert(
                    alert_type="monthly_budget_warning",
                    level=AlertLevel.WARNING,
                    message=f"Monthly budget at {percentage:.1f}%. Current: ${current_cost:.2f}, Budget: ${threshold:.2f}",
                    current_value=current_cost,
                    threshold=threshold,
                    metadata={'percentage': percentage}
                )
        
        return None
    
    def _check_daily_limit(self) -> Optional[BudgetAlert]:
        """Check if daily spending limit is exceeded"""
        daily_costs = self.cost_db.get_daily_costs(1)
        if not daily_costs:
            return None
        
        today_cost = daily_costs[0].get('total_cost', 0)
        daily_limit = self.thresholds['daily_limit']
        
        if today_cost > daily_limit:
            return BudgetAlert(
                alert_type="daily_limit_exceeded",
                level=AlertLevel.WARNING,
                message=f"Daily spending limit exceeded! Today: ${today_cost:.2f}, Limit: ${daily_limit:.2f}",
                current_value=today_cost,
                threshold=daily_limit
            )
        
        return None
    
    def _check_model_limits(self) -> List[BudgetAlert]:
        """Check per-model spending limits"""
        alerts = []
        model_stats = self.cost_db.get_model_usage_stats()
        
        for stat in model_stats:
            model = stat['model']
            total_cost = stat['total_cost']
            
            if model in self.thresholds['model_limits']:
                limit = self.thresholds['model_limits'][model]
                if total_cost > limit:
                    alerts.append(BudgetAlert(
                        alert_type=f"model_limit_exceeded_{model}",
                        level=AlertLevel.WARNING,
                        message=f"Model {model} cost limit exceeded! Total: ${total_cost:.2f}, Limit: ${limit:.2f}",
                        current_value=total_cost,
                        threshold=limit,
                        metadata={'model': model, 'request_count': stat['total_requests']}
                    ))
        
        return alerts
    
    def _check_spending_anomalies(self) -> List[BudgetAlert]:
        """Detect unusual spending patterns"""
        alerts = []
        
        # Get last 7 days of costs
        daily_costs = self.cost_db.get_daily_costs(7)
        if len(daily_costs) < 7:
            return alerts  # Not enough data
        
        # Calculate average and detect spikes
        costs = [d['total_cost'] for d in daily_costs]
        avg_cost = sum(costs) / len(costs)
        today_cost = costs[0] if costs else 0
        
        # Alert if today's cost is 3x the average
        if today_cost > avg_cost * 3 and today_cost > 0.1:  # Ignore tiny amounts
            alerts.append(BudgetAlert(
                alert_type="spending_spike",
                level=AlertLevel.WARNING,
                message=f"Unusual spending spike detected! Today: ${today_cost:.2f}, 7-day avg: ${avg_cost:.2f}",
                current_value=today_cost,
                threshold=avg_cost * 3,
                metadata={'average': avg_cost, 'spike_ratio': today_cost / avg_cost if avg_cost > 0 else 0}
            ))
        
        return alerts
    
    def _trigger_alert(self, alert: BudgetAlert):
        """Trigger alert callbacks and notifications"""
        logger.warning(f"Budget alert triggered: {alert.message}")
        
        # Call registered callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
        
        # Send email notification if configured
        if self.config.config.get('ENABLE_EMAIL_ALERTS', False):
            self._send_email_alert(alert)
        
        # Log to database
        self._log_alert_to_db(alert)
    
    def _send_email_alert(self, alert: BudgetAlert):
        """Send email notification for alert"""
        try:
            smtp_config = {
                'host': self.config.config.get('SMTP_HOST', 'smtp.gmail.com'),
                'port': int(self.config.config.get('SMTP_PORT', 587)),
                'username': self.config.config.get('SMTP_USERNAME'),
                'password': self.config.config.get('SMTP_PASSWORD'),
                'from_email': self.config.config.get('ALERT_FROM_EMAIL'),
                'to_emails': self.config.config.get('ALERT_TO_EMAILS', '').split(',')
            }
            
            if not all([smtp_config['username'], smtp_config['password'], smtp_config['to_emails']]):
                logger.warning("Email alerts enabled but SMTP not fully configured")
                return
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = smtp_config['from_email'] or smtp_config['username']
            msg['To'] = ', '.join(smtp_config['to_emails'])
            msg['Subject'] = f"SwarmBot Cost Alert: {alert.alert_type}"
            
            # Email body
            body = f"""
SwarmBot Cost Alert

Type: {alert.alert_type}
Level: {alert.level}
Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

{alert.message}

Current Value: ${alert.current_value:.2f}
Threshold: ${alert.threshold:.2f}

Additional Details:
{json.dumps(alert.metadata, indent=2)}

--
This is an automated alert from SwarmBot Cost Tracking System
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(smtp_config['host'], smtp_config['port']) as server:
                server.starttls()
                server.login(smtp_config['username'], smtp_config['password'])
                server.send_message(msg)
                
            logger.info(f"Email alert sent for {alert.alert_type}")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def _log_alert_to_db(self, alert: BudgetAlert):
        """Log alert to database for historical tracking"""
        try:
            cursor = self.cost_db.conn.cursor()
            cursor.execute("""
                INSERT INTO budget_alerts
                (alert_id, alert_type, level, message, current_value, 
                 threshold, timestamp, metadata, acknowledged)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.alert_id,
                alert.alert_type,
                alert.level,
                alert.message,
                alert.current_value,
                alert.threshold,
                alert.timestamp,
                json.dumps(alert.metadata),
                alert.acknowledged
            ))
            self.cost_db.conn.commit()
        except Exception as e:
            logger.error(f"Failed to log alert to database: {e}")
    
    def acknowledge_alert(self, alert_id: str):
        """Mark an alert as acknowledged"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged = True
            
            # Update database
            try:
                cursor = self.cost_db.conn.cursor()
                cursor.execute("""
                    UPDATE budget_alerts
                    SET acknowledged = 1
                    WHERE alert_id = ?
                """, (alert_id,))
                self.cost_db.conn.commit()
            except Exception as e:
                logger.error(f"Failed to acknowledge alert in database: {e}")
    
    def get_active_alerts(self) -> List[BudgetAlert]:
        """Get all active, unacknowledged alerts"""
        return [alert for alert in self.active_alerts.values() 
                if not alert.acknowledged]
    
    def get_alert_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical alerts from database"""
        try:
            cursor = self.cost_db.conn.cursor()
            cursor.execute("""
                SELECT * FROM budget_alerts
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
                ORDER BY timestamp DESC
            """, (days,))
            
            columns = [desc[0] for desc in cursor.description]
            alerts = []
            for row in cursor.fetchall():
                alert_dict = dict(zip(columns, row))
                if 'metadata' in alert_dict and alert_dict['metadata']:
                    alert_dict['metadata'] = json.loads(alert_dict['metadata'])
                alerts.append(alert_dict)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get alert history: {e}")
            return []


class BudgetConfiguration:
    """Manages budget configuration and rules"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "budget_config.json"
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict[str, Any]:
        """Load budget rules from configuration file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load budget rules: {e}")
        
        # Default rules
        return {
            'monthly_budgets': {
                'default': 10.0,
                'by_month': {}  # Can specify different budgets for different months
            },
            'model_preferences': {
                'cost_optimization': True,
                'preferred_models': ['gpt-3.5-turbo', 'claude-3-haiku'],
                'fallback_on_budget_exceed': True
            },
            'alert_rules': {
                'email_enabled': False,
                'webhook_enabled': False,
                'webhook_url': '',
                'alert_cooldown_minutes': 60
            },
            'spending_policies': {
                'max_cost_per_request': 0.10,
                'max_requests_per_hour': 100,
                'require_approval_above': 1.0
            }
        }
    
    def save_rules(self):
        """Save budget rules to configuration file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.rules, f, indent=2)
            logger.info("Budget rules saved successfully")
        except Exception as e:
            logger.error(f"Failed to save budget rules: {e}")
    
    def update_monthly_budget(self, amount: float, month: Optional[str] = None):
        """Update monthly budget amount"""
        if month:
            self.rules['monthly_budgets']['by_month'][month] = amount
        else:
            self.rules['monthly_budgets']['default'] = amount
        self.save_rules()
    
    def get_monthly_budget(self, month: Optional[str] = None) -> float:
        """Get monthly budget for specific month or default"""
        if month and month in self.rules['monthly_budgets']['by_month']:
            return self.rules['monthly_budgets']['by_month'][month]
        return self.rules['monthly_budgets']['default']
