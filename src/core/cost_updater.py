"""
Cost Updater Module
Automatically fetches and updates model pricing information from LLM provider APIs
"""

import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging
from pathlib import Path

from ..database.cost_tracking import CostTrackingDB
from ..config import Configuration

logger = logging.getLogger(__name__)


class CostUpdater:
    """Automatically updates model costs from provider APIs"""
    
    # Static pricing data (fallback when APIs are unavailable)
    STATIC_COSTS = {
        "openai": {
            "gpt-4-turbo": {
                "input_cost_per_1k": 0.01,
                "output_cost_per_1k": 0.03,
                "context_window": 128000
            },
            "gpt-4": {
                "input_cost_per_1k": 0.03,
                "output_cost_per_1k": 0.06,
                "context_window": 8192
            },
            "gpt-3.5-turbo": {
                "input_cost_per_1k": 0.0005,
                "output_cost_per_1k": 0.0015,
                "context_window": 16385
            },
            "gpt-4o": {
                "input_cost_per_1k": 0.005,
                "output_cost_per_1k": 0.015,
                "context_window": 128000
            },
            "gpt-4o-mini": {
                "input_cost_per_1k": 0.00015,
                "output_cost_per_1k": 0.0006,
                "context_window": 128000
            }
        },
        "anthropic": {
            "claude-3-opus": {
                "input_cost_per_1k": 0.015,
                "output_cost_per_1k": 0.075,
                "context_window": 200000
            },
            "claude-3-sonnet": {
                "input_cost_per_1k": 0.003,
                "output_cost_per_1k": 0.015,
                "context_window": 200000
            },
            "claude-3-haiku": {
                "input_cost_per_1k": 0.00025,
                "output_cost_per_1k": 0.00125,
                "context_window": 200000
            },
            "claude-2.1": {
                "input_cost_per_1k": 0.008,
                "output_cost_per_1k": 0.024,
                "context_window": 200000
            },
            "claude-instant-1.2": {
                "input_cost_per_1k": 0.0008,
                "output_cost_per_1k": 0.0024,
                "context_window": 100000
            }
        },
        "google": {
            "gemini-pro": {
                "input_cost_per_1k": 0.0005,
                "output_cost_per_1k": 0.0015,
                "context_window": 32768
            },
            "gemini-1.5-pro": {
                "input_cost_per_1k": 0.00125,
                "output_cost_per_1k": 0.00375,
                "context_window": 1048576
            },
            "gemini-1.5-flash": {
                "input_cost_per_1k": 0.00035,
                "output_cost_per_1k": 0.00105,
                "context_window": 1048576
            }
        },
        "groq": {
            "llama2-70b-4096": {
                "input_cost_per_1k": 0.00070,
                "output_cost_per_1k": 0.00080,
                "context_window": 4096
            },
            "mixtral-8x7b-32768": {
                "input_cost_per_1k": 0.00027,
                "output_cost_per_1k": 0.00027,
                "context_window": 32768
            },
            "gemma-7b-it": {
                "input_cost_per_1k": 0.00010,
                "output_cost_per_1k": 0.00010,
                "context_window": 8192
            }
        }
    }
    
    def __init__(self, config: Configuration, db: Optional[CostTrackingDB] = None):
        self.config = config
        self.db = db or CostTrackingDB(config.get('DATABASE_PATH', 'data/swarmbot_chats.db'))
        
        # Update intervals
        self.update_interval = timedelta(hours=config.get('COST_UPDATE_INTERVAL_HOURS', 24))
        self.last_update = None
        
        # API endpoints (these would need actual implementation)
        self.api_endpoints = {
            "openai": "https://api.openai.com/v1/models",  # Would need proper implementation
            "anthropic": None,  # Anthropic doesn't have public pricing API
            "google": None,  # Would need implementation
            "groq": None  # Would need implementation
        }
    
    async def update_all_costs(self, force: bool = False) -> Dict[str, Any]:
        """Update costs for all providers"""
        if not force and self.last_update:
            if datetime.now() - self.last_update < self.update_interval:
                logger.info("Skipping cost update - not due yet")
                return {"status": "skipped", "reason": "update_interval_not_reached"}
        
        results = {
            "updated": [],
            "failed": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Try to update from APIs (if implemented)
        for provider in self.STATIC_COSTS.keys():
            try:
                if await self._update_provider_costs(provider):
                    results["updated"].append(provider)
                else:
                    # Fall back to static costs
                    self._update_from_static(provider)
                    results["updated"].append(f"{provider} (static)")
            except Exception as e:
                logger.error(f"Failed to update costs for {provider}: {e}")
                results["failed"].append({"provider": provider, "error": str(e)})
        
        self.last_update = datetime.now()
        
        # Save update history
        self._save_update_history(results)
        
        return results
    
    async def _update_provider_costs(self, provider: str) -> bool:
        """Update costs from provider API"""
        endpoint = self.api_endpoints.get(provider)
        
        if not endpoint:
            # No API endpoint available, use static costs
            return False
        
        try:
            # This is a placeholder - actual implementation would need:
            # 1. Proper authentication
            # 2. API-specific request formatting
            # 3. Response parsing for each provider
            
            # For now, we'll just return False to use static costs
            logger.info(f"API update for {provider} not implemented - using static costs")
            return False
            
            # Example of what real implementation might look like:
            # async with aiohttp.ClientSession() as session:
            #     headers = self._get_auth_headers(provider)
            #     async with session.get(endpoint, headers=headers) as response:
            #         if response.status == 200:
            #             data = await response.json()
            #             self._parse_and_update_costs(provider, data)
            #             return True
            #         else:
            #             logger.error(f"API request failed for {provider}: {response.status}")
            #             return False
            
        except Exception as e:
            logger.error(f"Error fetching costs from {provider} API: {e}")
            return False
    
    def _update_from_static(self, provider: str):
        """Update database with static cost data"""
        static_costs = self.STATIC_COSTS.get(provider, {})
        
        for model_name, costs in static_costs.items():
            try:
                self.db.update_model_cost(
                    model_name=model_name,
                    provider=provider,
                    input_cost_per_1k=costs['input_cost_per_1k'],
                    output_cost_per_1k=costs['output_cost_per_1k'],
                    context_window=costs['context_window']
                )
                logger.debug(f"Updated costs for {provider}:{model_name}")
            except Exception as e:
                logger.error(f"Failed to update {provider}:{model_name}: {e}")
    
    def _save_update_history(self, results: Dict[str, Any]):
        """Save cost update history for auditing"""
        history_file = Path(self.config.get('DATA_DIR', 'data')) / 'cost_update_history.json'
        
        # Load existing history
        history = []
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load update history: {e}")
        
        # Add new entry
        history.append(results)
        
        # Keep only last 100 entries
        history = history[-100:]
        
        # Save updated history
        try:
            history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save update history: {e}")
    
    def get_cost_for_model(self, model: str, provider: Optional[str] = None) -> Optional[Dict[str, float]]:
        """Get current cost for a specific model"""
        # Try to get from database first
        db_costs = self.db._get_model_costs(model, provider)
        if db_costs:
            return db_costs
        
        # Fall back to static costs
        if provider and provider in self.STATIC_COSTS:
            if model in self.STATIC_COSTS[provider]:
                return self.STATIC_COSTS[provider][model]
        
        # Search all providers if provider not specified
        for prov, models in self.STATIC_COSTS.items():
            if model in models:
                return models[model]
        
        # Model not found
        logger.warning(f"No cost data found for model: {model}")
        return None
    
    async def check_for_new_models(self) -> List[str]:
        """Check for new models that don't have cost data"""
        # This would connect to provider APIs to get list of available models
        # and compare with what we have in the database
        
        # Placeholder implementation
        logger.info("Checking for new models not implemented yet")
        return []
    
    def validate_costs(self) -> Dict[str, Any]:
        """Validate that all costs in database are reasonable"""
        validation_results = {
            "valid": [],
            "warnings": [],
            "errors": []
        }
        
        all_costs = self.db.get_all_model_costs()
        
        for cost_entry in all_costs:
            model = cost_entry['model_name']
            provider = cost_entry['provider']
            
            # Check for zero costs
            if cost_entry['input_cost_per_1k'] == 0 or cost_entry['output_cost_per_1k'] == 0:
                validation_results['warnings'].append({
                    'model': model,
                    'provider': provider,
                    'issue': 'Zero cost detected'
                })
            
            # Check for unreasonably high costs
            if cost_entry['input_cost_per_1k'] > 1.0 or cost_entry['output_cost_per_1k'] > 1.0:
                validation_results['warnings'].append({
                    'model': model,
                    'provider': provider,
                    'issue': 'Unusually high cost (>$1 per 1k tokens)'
                })
            
            # Check for outdated data
            last_updated = datetime.fromisoformat(cost_entry['last_updated'].replace('Z', '+00:00'))
            if datetime.now() - last_updated > timedelta(days=30):
                validation_results['warnings'].append({
                    'model': model,
                    'provider': provider,
                    'issue': f'Cost data is {(datetime.now() - last_updated).days} days old'
                })
            
            # If no issues, mark as valid
            if not any(w['model'] == model and w['provider'] == provider 
                      for w in validation_results['warnings']):
                validation_results['valid'].append(f"{provider}:{model}")
        
        return validation_results
    
    def export_cost_catalog(self, output_path: str):
        """Export current cost catalog to file"""
        catalog = {
            'generated_at': datetime.now().isoformat(),
            'providers': {}
        }
        
        # Get all costs from database
        all_costs = self.db.get_all_model_costs()
        
        # Organize by provider
        for cost_entry in all_costs:
            provider = cost_entry['provider']
            if provider not in catalog['providers']:
                catalog['providers'][provider] = {}
            
            catalog['providers'][provider][cost_entry['model_name']] = {
                'input_cost_per_1k': cost_entry['input_cost_per_1k'],
                'output_cost_per_1k': cost_entry['output_cost_per_1k'],
                'context_window': cost_entry['context_window'],
                'last_updated': cost_entry['last_updated']
            }
        
        # Save to file
        with open(output_path, 'w') as f:
            json.dump(catalog, f, indent=2)
        
        logger.info(f"Exported cost catalog to {output_path}")


# Scheduled update function
async def scheduled_cost_update(config: Configuration, db: CostTrackingDB):
    """Run scheduled cost updates"""
    updater = CostUpdater(config, db)
    
    while True:
        try:
            logger.info("Running scheduled cost update")
            results = await updater.update_all_costs()
            logger.info(f"Cost update results: {results}")
            
            # Validate costs after update
            validation = updater.validate_costs()
            if validation['warnings']:
                logger.warning(f"Cost validation warnings: {validation['warnings']}")
            
        except Exception as e:
            logger.error(f"Error in scheduled cost update: {e}")
        
        # Wait for next update interval
        await asyncio.sleep(updater.update_interval.total_seconds())


if __name__ == "__main__":
    # Test the cost updater
    import asyncio
    from ..config import Configuration
    
    config = Configuration()
    updater = CostUpdater(config)
    
    # Run update
    results = asyncio.run(updater.update_all_costs(force=True))
    print(f"Update results: {json.dumps(results, indent=2)}")
    
    # Validate costs
    validation = updater.validate_costs()
    print(f"Validation results: {json.dumps(validation, indent=2)}")
    
    # Export catalog
    updater.export_cost_catalog("cost_catalog.json")
