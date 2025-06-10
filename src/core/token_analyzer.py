"""
Token Analyzer Module
Provides token counting and analysis functionality for LLM interactions
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
import tiktoken
from collections import defaultdict

logger = logging.getLogger(__name__)


class TokenAnalyzer:
    """Analyzes token usage across different models and contexts"""
    
    def __init__(self, config):
        self.config = config
        self.token_usage_log = []
        self.encoders = {}
        
        # Token limits for different models
        self.model_limits = {
            "gpt-4": 8192,
            "gpt-4-turbo": 128000,
            "gpt-3.5-turbo": 16385,
            "claude-3-opus": 200000,
            "claude-3-sonnet": 200000,
            "claude-3-haiku": 200000,
            "claude-2.1": 200000,
            "gemini-pro": 32768,
            "gemini-1.5-pro": 1048576
        }
        
        # Initialize token counters
        self.session_tokens = defaultdict(int)
        self.model_tokens = defaultdict(lambda: defaultdict(int))
    
    def count_tokens(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """Count tokens in text for a specific model"""
        try:
            # Get or create encoder for the model
            encoder = self._get_encoder(model)
            if encoder:
                return len(encoder.encode(text))
            else:
                # Fallback: estimate based on character count
                # Rough estimate: 1 token ≈ 4 characters
                return len(text) // 4
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            return len(text) // 4
    
    def _get_encoder(self, model: str):
        """Get the appropriate encoder for a model"""
        if model not in self.encoders:
            try:
                # Map model names to tiktoken encoding names
                encoding_map = {
                    "gpt-4": "cl100k_base",
                    "gpt-4-turbo": "cl100k_base",
                    "gpt-3.5-turbo": "cl100k_base",
                    "gpt-4o": "o200k_base",
                    "gpt-4o-mini": "o200k_base"
                }
                
                # Get encoding name
                encoding_name = encoding_map.get(model, "cl100k_base")
                
                # Try to get the encoder
                self.encoders[model] = tiktoken.get_encoding(encoding_name)
            except Exception as e:
                logger.warning(f"Could not load encoder for {model}: {e}")
                self.encoders[model] = None
        
        return self.encoders[model]
    
    def log_token_usage(self, timestamp: datetime, server_name: str, 
                       component: str, tokens: int, details: Optional[Dict] = None):
        """Log token usage for analysis"""
        entry = {
            "timestamp": timestamp.isoformat(),
            "server_name": server_name,
            "component": component,
            "tokens": tokens,
            "details": details or {}
        }
        
        self.token_usage_log.append(entry)
        
        # Update counters
        self.session_tokens["total"] += tokens
        self.session_tokens[server_name] += tokens
        
        if details:
            if "input_tokens" in details:
                self.model_tokens[server_name]["input"] += details["input_tokens"]
            if "output_tokens" in details:
                self.model_tokens[server_name]["output"] += details["output_tokens"]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get token usage summary"""
        summary = {
            "total_tokens": self.session_tokens["total"],
            "by_server": {},
            "by_component": defaultdict(int),
            "timeline": []
        }
        
        # Aggregate by server
        for server, tokens in self.session_tokens.items():
            if server != "total":
                summary["by_server"][server] = {
                    "total": tokens,
                    "input": self.model_tokens[server]["input"],
                    "output": self.model_tokens[server]["output"]
                }
        
        # Aggregate by component
        for entry in self.token_usage_log:
            summary["by_component"][entry["component"]] += entry["tokens"]
        
        # Create timeline (last 20 entries)
        summary["timeline"] = self.token_usage_log[-20:]
        
        return summary
    
    def check_token_limits(self, model: str, tokens: int) -> Dict[str, Any]:
        """Check if token count is within model limits"""
        limit = self.model_limits.get(model, 4096)
        
        return {
            "model": model,
            "tokens": tokens,
            "limit": limit,
            "percentage": (tokens / limit) * 100,
            "within_limit": tokens <= limit,
            "remaining": max(0, limit - tokens)
        }
    
    def get_token_distribution(self) -> Dict[str, Any]:
        """Get distribution of tokens across different categories"""
        distribution = {
            "by_type": {
                "input": 0,
                "output": 0
            },
            "by_model": {},
            "efficiency_metrics": {}
        }
        
        # Calculate distributions
        for model, tokens in self.model_tokens.items():
            distribution["by_type"]["input"] += tokens["input"]
            distribution["by_type"]["output"] += tokens["output"]
            
            distribution["by_model"][model] = {
                "input": tokens["input"],
                "output": tokens["output"],
                "total": tokens["input"] + tokens["output"],
                "ratio": tokens["output"] / tokens["input"] if tokens["input"] > 0 else 0
            }
        
        # Calculate efficiency metrics
        total_input = distribution["by_type"]["input"]
        total_output = distribution["by_type"]["output"]
        total_tokens = total_input + total_output
        
        if total_tokens > 0:
            distribution["efficiency_metrics"] = {
                "output_ratio": total_output / total_tokens,
                "input_ratio": total_input / total_tokens,
                "avg_response_amplification": total_output / total_input if total_input > 0 else 0
            }
        
        return distribution
    
    def export_token_log(self, output_path: str):
        """Export token usage log to file"""
        with open(output_path, 'w') as f:
            json.dump({
                "exported_at": datetime.now().isoformat(),
                "summary": self.get_summary(),
                "distribution": self.get_token_distribution(),
                "detailed_log": self.token_usage_log
            }, f, indent=2)
        
        logger.info(f"Exported token log to {output_path}")
