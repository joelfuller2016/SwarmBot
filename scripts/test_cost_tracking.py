#!/usr/bin/env python3
"""
Test script for cost tracking integration
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm_client_adapter import LLMClient
from src.config import Configuration
from src.database.cost_tracking import CostTrackingDB

def test_cost_tracking():
    """Test the cost tracking integration"""
    print("🧪 Testing Cost Tracking Integration...")
    
    # Initialize configuration
    config = Configuration()
    
    # Initialize LLM client (will use fallback if no API key)
    try:
        client = LLMClient()
        print(f"✅ LLM Client initialized with provider: {client.provider_name}")
        print(f"   Cost tracking enabled: {client.cost_tracking_enabled}")
        
        if not client.cost_tracking_enabled:
            print("⚠️  Cost tracking is disabled. Enable it by setting TRACK_COSTS=true")
            return
        
        # Test conversation
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello! Can you tell me what 2 + 2 equals?"}
        ]
        
        print("\n📨 Sending test request to LLM...")
        response = client.get_response(test_messages, conversation_id="test_conversation_001")
        print(f"✅ Response received: {response[:100]}...")
        
        # Get cost summary
        cost_summary = client.get_cost_summary()
        print(f"\n💰 Cost Summary:")
        if 'session' in cost_summary:
            session = cost_summary['session']
            print(f"   Total tokens: {session.get('total_tokens', 0)}")
            print(f"   Total cost: ${session.get('total_cost', 0):.6f}")
            print(f"   Requests: {session.get('request_count', 0)}")
        
        # Check database directly
        db_path = config.get('DATABASE_PATH', 'data/swarmbot_chats.db')
        db = CostTrackingDB(db_path)
        
        # Get conversation costs
        conv_summary = db.get_conversation_cost_summary("test_conversation_001")
        if conv_summary:
            print(f"\n📊 Database Verification:")
            print(f"   Conversation total cost: ${conv_summary['total_cost']:.6f}")
            print(f"   Request count: {conv_summary['request_count']}")
        
        # Get model usage stats
        model_stats = db.get_model_usage_stats()
        if model_stats:
            print(f"\n📈 Model Usage Statistics:")
            for stat in model_stats[:3]:  # Show top 3
                print(f"   {stat['model']}: {stat['total_requests']} requests, ${stat['total_cost']:.6f} total")
        
        # Clean up
        client.shutdown()
        db.close()
        
        print("\n✅ Cost tracking integration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(test_cost_tracking())
