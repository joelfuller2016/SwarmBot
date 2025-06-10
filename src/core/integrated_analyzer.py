"""
Integrated Token and Cost Analyzer
Combines token analysis with real-time cost tracking for comprehensive usage monitoring
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import logging
from collections import defaultdict

from .cost_tracker import CostTracker, RequestCost
from .token_analyzer import TokenAnalyzer
from ..config import Configuration

logger = logging.getLogger(__name__)


class IntegratedAnalyzer:
    """Integrates token analysis with cost tracking for comprehensive monitoring"""
    
    def __init__(self, config: Configuration):
        self.config = config
        self.token_analyzer = TokenAnalyzer(config)
        self.cost_tracker = CostTracker(config)
        
        # Integrated metrics
        self.session_metrics = {
            'total_tokens': 0,
            'total_cost': 0.0,
            'requests': [],
            'by_model': defaultdict(lambda: {
                'tokens': {'input': 0, 'output': 0},
                'cost': 0.0,
                'requests': 0
            }),
            'token_efficiency': [],  # Cost per token over time
            'cost_breakdown': {
                'input_cost': 0.0,
                'output_cost': 0.0
            }
        }
    
    def analyze_request(self, conversation_id: str, model: str,
                       input_text: str, output_text: str,
                       provider: Optional[str] = None) -> Dict[str, Any]:
        """Analyze a request for both tokens and cost"""
        # Count tokens
        input_tokens = self.token_analyzer.count_tokens(input_text, model)
        output_tokens = self.token_analyzer.count_tokens(output_text, model)
        
        # Track cost
        request_cost = self.cost_tracker.track_request(
            conversation_id=conversation_id,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            provider=provider
        )
        
        # Update integrated metrics
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'conversation_id': conversation_id,
            'model': model,
            'provider': provider,
            'tokens': {
                'input': input_tokens,
                'output': output_tokens,
                'total': input_tokens + output_tokens
            },
            'cost': request_cost.to_dict() if request_cost else None,
            'efficiency': {
                'cost_per_1k_tokens': (
                    (request_cost.total_cost / (input_tokens + output_tokens)) * 1000
                    if request_cost and (input_tokens + output_tokens) > 0 else 0
                ),
                'tokens_per_dollar': (
                    (input_tokens + output_tokens) / request_cost.total_cost
                    if request_cost and request_cost.total_cost > 0 else 0
                )
            }
        }
        
        # Update session metrics
        self._update_session_metrics(analysis)
        
        # Log token usage with cost context
        self.token_analyzer.log_token_usage(
            timestamp=datetime.now(),
            server_name=f"{provider}:{model}" if provider else model,
            component="request",
            tokens=input_tokens + output_tokens,
            details={
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'cost': request_cost.total_cost if request_cost else 0
            }
        )
        
        return analysis
    
    def _update_session_metrics(self, analysis: Dict[str, Any]):
        """Update session-level integrated metrics"""
        tokens = analysis['tokens']
        cost = analysis['cost']
        
        # Update totals
        self.session_metrics['total_tokens'] += tokens['total']
        if cost:
            self.session_metrics['total_cost'] += cost['total_cost']
            self.session_metrics['cost_breakdown']['input_cost'] += cost['input_cost']
            self.session_metrics['cost_breakdown']['output_cost'] += cost['output_cost']
        
        # Store request
        self.session_metrics['requests'].append(analysis)
        
        # Update by-model metrics
        model = analysis['model']
        self.session_metrics['by_model'][model]['tokens']['input'] += tokens['input']
        self.session_metrics['by_model'][model]['tokens']['output'] += tokens['output']
        if cost:
            self.session_metrics['by_model'][model]['cost'] += cost['total_cost']
        self.session_metrics['by_model'][model]['requests'] += 1
        
        # Track efficiency over time
        if cost and tokens['total'] > 0:
            self.session_metrics['token_efficiency'].append({
                'timestamp': analysis['timestamp'],
                'cost_per_1k_tokens': analysis['efficiency']['cost_per_1k_tokens']
            })
    
    def get_integrated_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary combining token and cost analysis"""
        # Get individual summaries
        token_summary = self.token_analyzer.get_summary()
        cost_summary = self.cost_tracker.get_session_summary()
        monthly_summary = self.cost_tracker.get_monthly_summary()
        
        # Calculate integrated metrics
        avg_cost_per_token = (
            self.session_metrics['total_cost'] / self.session_metrics['total_tokens']
            if self.session_metrics['total_tokens'] > 0 else 0
        )
        
        # Model comparison
        model_comparison = []
        for model, metrics in self.session_metrics['by_model'].items():
            if metrics['requests'] > 0:
                model_comparison.append({
                    'model': model,
                    'total_tokens': metrics['tokens']['input'] + metrics['tokens']['output'],
                    'total_cost': metrics['cost'],
                    'requests': metrics['requests'],
                    'avg_tokens_per_request': (
                        (metrics['tokens']['input'] + metrics['tokens']['output']) / 
                        metrics['requests']
                    ),
                    'avg_cost_per_request': metrics['cost'] / metrics['requests'],
                    'cost_efficiency': (
                        metrics['cost'] / (metrics['tokens']['input'] + metrics['tokens']['output']) * 1000
                        if (metrics['tokens']['input'] + metrics['tokens']['output']) > 0 else 0
                    )
                })
        
        # Sort by cost efficiency
        model_comparison.sort(key=lambda x: x['cost_efficiency'])
        
        return {
            'session': {
                'total_tokens': self.session_metrics['total_tokens'],
                'total_cost': self.session_metrics['total_cost'],
                'request_count': len(self.session_metrics['requests']),
                'avg_cost_per_token': avg_cost_per_token,
                'avg_cost_per_1k_tokens': avg_cost_per_token * 1000,
                'cost_breakdown': self.session_metrics['cost_breakdown']
            },
            'models': model_comparison,
            'token_analysis': token_summary,
            'cost_tracking': cost_summary,
            'monthly': monthly_summary,
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate cost optimization recommendations"""
        recommendations = []
        
        # Check model efficiency
        if self.session_metrics['by_model']:
            # Find most and least efficient models
            models = [
                (model, metrics['cost'] / (metrics['tokens']['input'] + metrics['tokens']['output']) * 1000)
                for model, metrics in self.session_metrics['by_model'].items()
                if (metrics['tokens']['input'] + metrics['tokens']['output']) > 0
            ]
            
            if len(models) > 1:
                models.sort(key=lambda x: x[1])
                most_efficient = models[0]
                least_efficient = models[-1]
                
                if least_efficient[1] > most_efficient[1] * 2:
                    recommendations.append(
                        f"Consider using {most_efficient[0]} instead of {least_efficient[0]} "
                        f"to reduce costs by {((least_efficient[1] - most_efficient[1]) / least_efficient[1] * 100):.1f}%"
                    )
        
        # Check token usage patterns
        if self.session_metrics['requests']:
            avg_output_ratio = sum(
                r['tokens']['output'] / r['tokens']['total'] 
                for r in self.session_metrics['requests']
                if r['tokens']['total'] > 0
            ) / len(self.session_metrics['requests'])
            
            if avg_output_ratio > 0.7:
                recommendations.append(
                    "High output token ratio detected. Consider using more concise prompts "
                    "or requesting shorter responses to reduce costs."
                )
        
        # Check budget usage
        monthly = self.cost_tracker.get_monthly_summary()
        if monthly['percentage_used'] > 80:
            recommendations.append(
                f"Monthly budget usage at {monthly['percentage_used']:.1f}%. "
                f"Consider implementing rate limiting or switching to cheaper models."
            )
        
        # Check for inefficient patterns
        if self.session_metrics['token_efficiency']:
            recent_efficiency = [
                e['cost_per_1k_tokens'] 
                for e in self.session_metrics['token_efficiency'][-10:]
            ]
            if len(recent_efficiency) >= 2:
                if recent_efficiency[-1] > recent_efficiency[0] * 1.5:
                    recommendations.append(
                        "Cost efficiency is decreasing. Review recent usage patterns "
                        "and consider optimizing prompts or model selection."
                    )
        
        return recommendations
    
    def analyze_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Analyze a specific conversation's token usage and costs"""
        # Get conversation costs from database
        conv_summary = self.cost_tracker.db.get_conversation_cost_summary(conversation_id)
        
        # Get requests for this conversation
        conv_requests = [
            r for r in self.session_metrics['requests']
            if r['conversation_id'] == conversation_id
        ]
        
        if not conv_requests and not conv_summary:
            return {'error': 'Conversation not found'}
        
        # Calculate metrics
        total_tokens = sum(r['tokens']['total'] for r in conv_requests)
        total_cost = sum(r['cost']['total_cost'] for r in conv_requests if r['cost'])
        
        return {
            'conversation_id': conversation_id,
            'request_count': len(conv_requests),
            'total_tokens': total_tokens,
            'total_cost': total_cost,
            'database_summary': conv_summary,
            'token_breakdown': {
                'input': sum(r['tokens']['input'] for r in conv_requests),
                'output': sum(r['tokens']['output'] for r in conv_requests)
            },
            'cost_breakdown': {
                'input': sum(r['cost']['input_cost'] for r in conv_requests if r['cost']),
                'output': sum(r['cost']['output_cost'] for r in conv_requests if r['cost'])
            },
            'models_used': list(set(r['model'] for r in conv_requests)),
            'efficiency': {
                'avg_cost_per_request': total_cost / len(conv_requests) if conv_requests else 0,
                'avg_tokens_per_request': total_tokens / len(conv_requests) if conv_requests else 0,
                'cost_per_1k_tokens': (total_cost / total_tokens * 1000) if total_tokens > 0 else 0
            }
        }
    
    def export_integrated_report(self, format: str = 'json', 
                               output_path: Optional[str] = None) -> str:
        """Export comprehensive integrated report"""
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'summary': self.get_integrated_summary(),
            'detailed_requests': self.session_metrics['requests'][-100:],  # Last 100 requests
            'token_usage_log': self.token_analyzer.token_usage_log[-100:],  # Last 100 entries
            'model_costs': self.cost_tracker.db.get_all_model_costs(),
            'slow_queries': self.cost_tracker.db.get_slow_queries()
        }
        
        if format == 'json':
            json_str = json.dumps(report_data, indent=2, default=str)
            if output_path:
                with open(output_path, 'w') as f:
                    f.write(json_str)
                logger.info(f"Exported integrated report to {output_path}")
            return json_str
        
        # Add support for other formats (PDF, HTML) in the future
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def shutdown(self):
        """Cleanup and finalize both analyzers"""
        # Generate final report
        final_summary = self.get_integrated_summary()
        logger.info(f"Integrated analyzer final summary: {json.dumps(final_summary, indent=2)}")
        
        # Shutdown individual components
        self.cost_tracker.shutdown()
        # Token analyzer doesn't have a shutdown method, but we could add one if needed
