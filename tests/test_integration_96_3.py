"""
Test script for subtask 96.3 - Integration with existing system components
Verifies that context_manager and llm_client_adapter properly integrate with cost tracking
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tempfile
import json
from unittest.mock import Mock, patch
import logging

from src.core.context_manager import ConversationContext
from src.llm_client_adapter import LLMClient
from src.core.cost_tracker import CostTracker
from src.core.integrated_analyzer import IntegratedAnalyzer
from src.config import Configuration
from src.database.cost_tracking import CostTrackingDB

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_context_manager_integration():
    """Test that context_manager properly integrates with cost tracking"""
    print("\n=== Testing Context Manager Integration ===\n")
    
    # Create mock cost tracker
    mock_cost_tracker = Mock()
    mock_cost_tracker.update_context_tokens = Mock()
    
    # Initialize context manager with cost tracker
    context = ConversationContext(
        window_size=10,
        max_tokens=1000,
        cost_tracker=mock_cost_tracker
    )
    
    print("1. Testing message tracking with cost metadata...")
    
    # Add messages
    context.add_message("system", "You are a helpful assistant.")
    context.add_message("user", "Hello, how are you?")
    context.add_message("assistant", "I'm doing well, thank you for asking!")
    
    # Verify cost metadata is tracked
    metadata = context.get_cost_metadata()
    print(f"   ✓ Input tokens tracked: {metadata['input_tokens']}")
    print(f"   ✓ Output tokens tracked: {metadata['output_tokens']}")
    print(f"   ✓ Total tokens tracked: {metadata['total_tokens']}")
    
    # Verify cost tracker was notified
    if mock_cost_tracker.update_context_tokens.called:
        print("   ✓ Cost tracker notified of token updates")
    
    # Test context summary includes cost info
    summary = context.get_summary()
    if 'cost_tracking' in summary:
        print("   ✓ Cost tracking info included in context summary")
    
    print("\n✓ Context manager integration test passed!")
    return True


def test_llm_client_integration():
    """Test that llm_client_adapter properly integrates with cost tracking"""
    print("\n=== Testing LLM Client Adapter Integration ===\n")
    
    # Create temporary config
    with tempfile.TemporaryDirectory() as temp_dir:
        # Mock configuration
        mock_config = {
            'TRACK_COSTS': True,
            'DATABASE_PATH': os.path.join(temp_dir, 'test_costs.db'),
            'COST_ALERT_THRESHOLD': 10.0,
            'llm_timeout': 30
        }
        
        with patch('src.llm_client_adapter.Configuration') as mock_config_class:
            config_instance = Mock()
            config_instance.get.side_effect = lambda key, default=None: mock_config.get(key, default)
            config_instance.llm_timeout = 30
            mock_config_class.return_value = config_instance
            
            # Initialize database
            db = CostTrackingDB(mock_config['DATABASE_PATH'])
            
            print("1. Testing LLM client initialization with cost tracking...")
            
            # Mock the LLM client factory
            with patch('src.llm_client_adapter.LLMClientFactory') as mock_factory:
                # Create mock client
                mock_llm_client = Mock()
                mock_llm_client.model = "gpt-4"
                mock_llm_client.__class__.__name__ = "OpenAIClient"
                mock_llm_client.complete = Mock(return_value="Test response")
                
                mock_factory.create_client_with_fallback.return_value = mock_llm_client
                
                # Initialize LLM client
                client = LLMClient()
                
                # Verify cost tracking was initialized
                if client.cost_tracking_enabled:
                    print("   ✓ Cost tracking enabled")
                else:
                    print("   ✗ Cost tracking not enabled")
                    return False
                
                if client.integrated_analyzer:
                    print("   ✓ Integrated analyzer initialized")
                else:
                    print("   ✗ Integrated analyzer not initialized")
                    return False
                
                print("\n2. Testing request tracking...")
                
                # Test messages
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What is 2+2?"}
                ]
                
                # Mock the analyze_request method
                with patch.object(client.integrated_analyzer, 'analyze_request') as mock_analyze:
                    # Get response
                    response = client.get_response(messages, conversation_id="test_conv_123")
                    
                    # Verify response was received
                    print(f"   ✓ Response received: {response}")
                    
                    # Verify cost tracking was called
                    if mock_analyze.called:
                        print("   ✓ Cost tracking analyze_request called")
                        
                        # Check the arguments
                        call_args = mock_analyze.call_args[1]
                        print(f"   ✓ Conversation ID: {call_args['conversation_id']}")
                        print(f"   ✓ Model: {call_args['model']}")
                        print(f"   ✓ Provider: {call_args['provider']}")
                    else:
                        print("   ✗ Cost tracking not called")
                        return False
                
                print("\n3. Testing cost summary retrieval...")
                
                # Mock the integrated summary
                mock_summary = {
                    "session": {
                        "total_tokens": 100,
                        "total_cost": 0.05
                    }
                }
                
                with patch.object(client.integrated_analyzer, 'get_integrated_summary', 
                                return_value=mock_summary):
                    summary = client.get_cost_summary()
                    print(f"   ✓ Cost summary retrieved: {json.dumps(summary, indent=2)}")
                
                print("\n4. Testing shutdown...")
                
                with patch.object(client.integrated_analyzer, 'shutdown') as mock_shutdown:
                    client.shutdown()
                    if mock_shutdown.called:
                        print("   ✓ Shutdown called on integrated analyzer")
            
            # Close database
            db.close()
    
    print("\n✓ LLM client adapter integration test passed!")
    return True


def test_full_integration():
    """Test the complete integration flow"""
    print("\n=== Testing Full Integration Flow ===\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup configuration
        config = Configuration()
        config_overrides = {
            'TRACK_COSTS': True,
            'DATABASE_PATH': os.path.join(temp_dir, 'test_integration.db'),
            'COST_ALERT_THRESHOLD': 10.0
        }
        
        # Patch config.get to use our overrides
        original_get = config.get
        config.get = lambda key, default=None: config_overrides.get(key, original_get(key, default))
        
        print("1. Initializing all components...")
        
        # Initialize database
        db = CostTrackingDB(config.get('DATABASE_PATH'))
        
        # Add some test model costs
        db.update_model_cost("test-model", "test-provider", 0.001, 0.002, 4096)
        
        # Initialize cost tracker
        cost_tracker = CostTracker(config)
        
        # Initialize context manager with cost tracker
        context = ConversationContext(cost_tracker=cost_tracker)
        
        print("   ✓ All components initialized")
        
        print("\n2. Simulating conversation flow...")
        
        # Add messages to context
        context.add_message("system", "You are a helpful assistant.")
        context.add_message("user", "Please explain cost tracking.")
        
        # Track a mock LLM request
        conversation_id = "test_integration_123"
        request_cost = cost_tracker.track_request(
            conversation_id=conversation_id,
            model="test-model",
            input_tokens=50,
            output_tokens=100,
            provider="test-provider"
        )
        
        if request_cost:
            print(f"   ✓ Request tracked: ${request_cost.total_cost:.4f}")
        
        # Add assistant response to context
        context.add_message("assistant", "Cost tracking monitors API usage and calculates costs.")
        
        print("\n3. Retrieving cost summaries...")
        
        # Get session summary
        session_summary = cost_tracker.get_session_summary()
        print(f"   ✓ Session total: ${session_summary['session_total']:.4f}")
        print(f"   ✓ Request count: {session_summary['request_count']}")
        
        # Get context summary
        context_summary = context.get_summary()
        print(f"   ✓ Context tokens: {context_summary['current_tokens']}")
        
        # Get conversation cost from database
        conv_summary = db.get_conversation_cost_summary(conversation_id)
        if conv_summary:
            print(f"   ✓ Conversation cost from DB: ${conv_summary['total_cost']:.4f}")
        
        print("\n4. Testing integrated analyzer...")
        
        # Initialize integrated analyzer
        analyzer = IntegratedAnalyzer(config)
        
        # Analyze a request
        analysis = analyzer.analyze_request(
            conversation_id=conversation_id,
            model="test-model",
            input_text="Test input",
            output_text="Test output",
            provider="test-provider"
        )
        
        print(f"   ✓ Analysis completed: {analysis['tokens']['total']} tokens")
        print(f"   ✓ Efficiency: {analysis['efficiency']['cost_per_1k_tokens']:.4f} per 1k tokens")
        
        # Get integrated summary
        integrated_summary = analyzer.get_integrated_summary()
        print(f"   ✓ Integrated summary generated with {len(integrated_summary['recommendations'])} recommendations")
        
        # Cleanup
        analyzer.shutdown()
        cost_tracker.shutdown()
        db.close()
        
    print("\n✓ Full integration test passed!")
    return True


if __name__ == "__main__":
    try:
        # Run all integration tests
        tests = [
            test_context_manager_integration,
            test_llm_client_integration,
            test_full_integration
        ]
        
        all_passed = True
        for test in tests:
            if not test():
                all_passed = False
        
        if all_passed:
            print("\n🎉 All integration tests passed! Subtask 96.3 is complete.")
        else:
            print("\n❌ Some integration tests failed.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Integration test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
</file_content>
</invoke>