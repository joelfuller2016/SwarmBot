"""
API Key Validation System for SwarmBot
Validates all configured API keys to ensure they are working correctly
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class APIKeyValidator:
    """Validates API keys for various LLM and service providers"""
    
    def __init__(self, config):
        """Initialize the validator with configuration"""
        self.config = config
        self.validation_results = {}
        self.validation_timestamp = None
        
    async def validate_all_keys(self) -> Dict[str, Any]:
        """Validate all configured API keys"""
        logger.info("Starting API key validation...")
        self.validation_timestamp = datetime.utcnow()
        
        # Validate LLM providers
        llm_results = await self._validate_llm_providers()
        
        # Validate service providers
        service_results = await self._validate_service_providers()
        
        # Combine results
        self.validation_results = {
            'timestamp': self.validation_timestamp.isoformat(),
            'llm_providers': llm_results,
            'service_providers': service_results,
            'summary': self._generate_summary(llm_results, service_results)
        }
        
        return self.validation_results
    
    async def _validate_llm_providers(self) -> Dict[str, Any]:
        """Validate LLM provider API keys"""
        results = {}
        
        # OpenAI validation
        if self.config.api_keys.get('openai'):
            results['openai'] = await self._validate_openai(self.config.api_keys['openai'])
        
        # Anthropic validation
        if self.config.api_keys.get('anthropic'):
            results['anthropic'] = await self._validate_anthropic(self.config.api_keys['anthropic'])
        
        # Groq validation
        if self.config.api_keys.get('groq'):
            results['groq'] = await self._validate_groq(self.config.api_keys['groq'])
        
        # Azure validation
        if self.config.api_keys.get('azure'):
            results['azure'] = await self._validate_azure(self.config.api_keys['azure'])
        
        return results
    
    async def _validate_service_providers(self) -> Dict[str, Any]:
        """Validate service provider API keys"""
        results = {}
        
        # GitHub validation
        if self.config.server_api_keys.get('GITHUB_PERSONAL_ACCESS_TOKEN'):
            results['github'] = await self._validate_github(
                self.config.server_api_keys['GITHUB_PERSONAL_ACCESS_TOKEN']
            )
        
        # Brave Search validation
        if self.config.server_api_keys.get('BRAVE_API_KEY'):
            results['brave'] = await self._validate_brave(
                self.config.server_api_keys['BRAVE_API_KEY']
            )
        
        # ElevenLabs validation
        if self.config.server_api_keys.get('ELEVENLABS_API_KEY'):
            results['elevenlabs'] = await self._validate_elevenlabs(
                self.config.server_api_keys['ELEVENLABS_API_KEY']
            )
        
        return results
    
    async def _validate_openai(self, api_key: str) -> Dict[str, Any]:
        """Validate OpenAI API key"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
                
                # Use models endpoint for validation (minimal cost)
                async with session.get(
                    'https://api.openai.com/v1/models',
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'valid': True,
                            'status': 'active',
                            'models_available': len(data.get('data', [])),
                            'message': 'API key is valid'
                        }
                    elif response.status == 401:
                        return {
                            'valid': False,
                            'status': 'invalid',
                            'message': 'Invalid API key'
                        }
                    else:
                        return {
                            'valid': False,
                            'status': 'error',
                            'message': f'Unexpected status: {response.status}'
                        }
        except Exception as e:
            logger.error(f"Error validating OpenAI key: {e}")
            return {
                'valid': False,
                'status': 'error',
                'message': str(e)
            }
    
    async def _validate_anthropic(self, api_key: str) -> Dict[str, Any]:
        """Validate Anthropic API key"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'x-api-key': api_key,
                    'anthropic-version': '2023-06-01',
                    'Content-Type': 'application/json'
                }
                
                # Use a minimal completion request
                data = {
                    'model': 'claude-3-opus-20240229',
                    'messages': [{'role': 'user', 'content': 'Hi'}],
                    'max_tokens': 1
                }
                
                async with session.post(
                    'https://api.anthropic.com/v1/messages',
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        return {
                            'valid': True,
                            'status': 'active',
                            'message': 'API key is valid'
                        }
                    elif response.status == 401:
                        return {
                            'valid': False,
                            'status': 'invalid',
                            'message': 'Invalid API key'
                        }
                    else:
                        return {
                            'valid': False,
                            'status': 'error',
                            'message': f'Unexpected status: {response.status}'
                        }
        except Exception as e:
            logger.error(f"Error validating Anthropic key: {e}")
            return {
                'valid': False,
                'status': 'error',
                'message': str(e)
            }
    
    async def _validate_groq(self, api_key: str) -> Dict[str, Any]:
        """Validate Groq API key"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
                
                # Use models endpoint
                async with session.get(
                    'https://api.groq.com/openai/v1/models',
                    headers=headers
                ) as response:
                    if response.status == 200:
                        return {
                            'valid': True,
                            'status': 'active',
                            'message': 'API key is valid'
                        }
                    elif response.status == 401:
                        return {
                            'valid': False,
                            'status': 'invalid',
                            'message': 'Invalid API key'
                        }
                    else:
                        return {
                            'valid': False,
                            'status': 'error',
                            'message': f'Unexpected status: {response.status}'
                        }
        except Exception as e:
            logger.error(f"Error validating Groq key: {e}")
            return {
                'valid': False,
                'status': 'error',
                'message': str(e)
            }
    
    async def _validate_azure(self, api_key: str) -> Dict[str, Any]:
        """Validate Azure OpenAI API key"""
        # Azure validation requires endpoint URL as well
        azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        if not azure_endpoint:
            return {
                'valid': False,
                'status': 'missing_config',
                'message': 'Azure endpoint not configured'
            }
        
        try:
            # Azure OpenAI validation logic here
            return {
                'valid': False,
                'status': 'not_implemented',
                'message': 'Azure validation not yet implemented'
            }
        except Exception as e:
            logger.error(f"Error validating Azure key: {e}")
            return {
                'valid': False,
                'status': 'error',
                'message': str(e)
            }
    
    async def _validate_github(self, api_key: str) -> Dict[str, Any]:
        """Validate GitHub Personal Access Token"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {api_key}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                
                async with session.get(
                    'https://api.github.com/user',
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'valid': True,
                            'status': 'active',
                            'username': data.get('login'),
                            'message': 'Token is valid'
                        }
                    elif response.status == 401:
                        return {
                            'valid': False,
                            'status': 'invalid',
                            'message': 'Invalid token'
                        }
                    else:
                        return {
                            'valid': False,
                            'status': 'error',
                            'message': f'Unexpected status: {response.status}'
                        }
        except Exception as e:
            logger.error(f"Error validating GitHub token: {e}")
            return {
                'valid': False,
                'status': 'error',
                'message': str(e)
            }
    
    async def _validate_brave(self, api_key: str) -> Dict[str, Any]:
        """Validate Brave Search API key"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'X-Subscription-Token': api_key,
                    'Accept': 'application/json'
                }
                
                # Simple search query for validation
                params = {'q': 'test', 'count': 1}
                
                async with session.get(
                    'https://api.search.brave.com/res/v1/web/search',
                    headers=headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        return {
                            'valid': True,
                            'status': 'active',
                            'message': 'API key is valid'
                        }
                    elif response.status == 401:
                        return {
                            'valid': False,
                            'status': 'invalid',
                            'message': 'Invalid API key'
                        }
                    else:
                        return {
                            'valid': False,
                            'status': 'error',
                            'message': f'Unexpected status: {response.status}'
                        }
        except Exception as e:
            logger.error(f"Error validating Brave key: {e}")
            return {
                'valid': False,
                'status': 'error',
                'message': str(e)
            }
    
    async def _validate_elevenlabs(self, api_key: str) -> Dict[str, Any]:
        """Validate ElevenLabs API key"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'xi-api-key': api_key,
                    'Accept': 'application/json'
                }
                
                async with session.get(
                    'https://api.elevenlabs.io/v1/user',
                    headers=headers
                ) as response:
                    if response.status == 200:
                        return {
                            'valid': True,
                            'status': 'active',
                            'message': 'API key is valid'
                        }
                    elif response.status == 401:
                        return {
                            'valid': False,
                            'status': 'invalid',
                            'message': 'Invalid API key'
                        }
                    else:
                        return {
                            'valid': False,
                            'status': 'error',
                            'message': f'Unexpected status: {response.status}'
                        }
        except Exception as e:
            logger.error(f"Error validating ElevenLabs key: {e}")
            return {
                'valid': False,
                'status': 'error',
                'message': str(e)
            }
    
    def _generate_summary(self, llm_results: Dict, service_results: Dict) -> Dict[str, Any]:
        """Generate a summary of validation results"""
        all_results = {**llm_results, **service_results}
        
        total = len(all_results)
        valid = sum(1 for r in all_results.values() if r.get('valid', False))
        invalid = sum(1 for r in all_results.values() if not r.get('valid', False))
        
        return {
            'total_keys': total,
            'valid_keys': valid,
            'invalid_keys': invalid,
            'success_rate': (valid / total * 100) if total > 0 else 0,
            'all_valid': valid == total
        }
    
    def get_validation_report(self) -> str:
        """Generate a human-readable validation report"""
        if not self.validation_results:
            return "No validation results available. Run validate_all_keys() first."
        
        report = ["API Key Validation Report", "=" * 50]
        report.append(f"Timestamp: {self.validation_results['timestamp']}")
        report.append("")
        
        # LLM Providers
        report.append("LLM Providers:")
        for provider, result in self.validation_results['llm_providers'].items():
            status = "✓" if result['valid'] else "✗"
            report.append(f"  {status} {provider}: {result['message']}")
        
        report.append("")
        report.append("Service Providers:")
        for service, result in self.validation_results['service_providers'].items():
            status = "✓" if result['valid'] else "✗"
            report.append(f"  {status} {service}: {result['message']}")
        
        report.append("")
        summary = self.validation_results['summary']
        report.append(f"Summary: {summary['valid_keys']}/{summary['total_keys']} keys valid ({summary['success_rate']:.1f}%)")
        
        return "\n".join(report)


# Integration with SwarmBot
async def validate_api_keys(config) -> bool:
    """Validate all API keys and return True if all required keys are valid"""
    validator = APIKeyValidator(config)
    results = await validator.validate_all_keys()
    
    print(validator.get_validation_report())
    
    # Check if the selected LLM provider has a valid key
    llm_results = results['llm_providers']
    selected_provider = config.llm_provider
    
    if selected_provider in llm_results:
        if not llm_results[selected_provider]['valid']:
            logger.error(f"Selected LLM provider '{selected_provider}' has invalid API key")
            return False
    else:
        logger.warning(f"Selected LLM provider '{selected_provider}' has no API key configured")
        return False
    
    # Log warnings for invalid service keys but don't fail
    for service, result in results['service_providers'].items():
        if not result['valid']:
            logger.warning(f"Service '{service}' has invalid API key: {result['message']}")
    
    return True


if __name__ == "__main__":
    # Test the validator
    from src.config import Configuration
    
    async def test_validation():
        config = Configuration()
        validator = APIKeyValidator(config)
        results = await validator.validate_all_keys()
        print(validator.get_validation_report())
    
    asyncio.run(test_validation())
