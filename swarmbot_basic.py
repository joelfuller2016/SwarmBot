#!/usr/bin/env python3
"""
SwarmBot - Basic MCP Chatbot
A simplified version to get started with basic functionality
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Any

import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class SimpleLLMClient:
    """Simple LLM client for basic chat functionality"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")
    
    def get_response(self, messages: List[Dict[str, str]]) -> str:
        """Get a response from Groq LLM"""
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "messages": messages,
            "model": "llama-3.2-90b-vision-preview",
            "temperature": 0.7,
            "max_tokens": 2048,
            "stream": False
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"Error getting LLM response: {e}")
            return f"Error: {str(e)}"

class BasicSwarmBot:
    """Basic chatbot without MCP complexity"""
    
    def __init__(self):
        self.llm_client = SimpleLLMClient()
        self.messages = []
        self.system_prompt = """You are SwarmBot, an AI assistant that will eventually evolve into a sophisticated multi-agent orchestrator. 
For now, you're starting as a helpful chatbot. You're friendly, informative, and eager to assist users with their questions.
Remember: You have the potential to grow and develop new capabilities over time."""
        
        # Initialize with system message
        self.messages.append({
            "role": "system",
            "content": self.system_prompt
        })
    
    def chat(self, user_input: str) -> str:
        """Process user input and return response"""
        # Add user message
        self.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Get LLM response
        response = self.llm_client.get_response(self.messages)
        
        # Add assistant response to history
        self.messages.append({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    def reset(self):
        """Reset conversation history"""
        self.messages = [{
            "role": "system",
            "content": self.system_prompt
        }]


def main():
    """Main entry point for basic SwarmBot"""
    print("🤖 SwarmBot Basic - Starting up...")
    print("=" * 60)
    
    try:
        bot = BasicSwarmBot()
        print("✅ SwarmBot initialized successfully!")
        print("Type 'quit' or 'exit' to end the conversation")
        print("Type 'reset' to start a new conversation")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    print("\n👋 Goodbye! SwarmBot signing off...")
                    break
                
                if user_input.lower() == 'reset':
                    bot.reset()
                    print("🔄 Conversation reset!")
                    continue
                
                if not user_input:
                    continue
                
                print("\n🤖 SwarmBot: ", end="", flush=True)
                response = bot.chat(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted! SwarmBot signing off...")
                break
            except Exception as e:
                logger.error(f"Error in chat loop: {e}")
                print(f"\n❌ Error: {e}")
    
    except Exception as e:
        logger.error(f"Failed to initialize SwarmBot: {e}")
        print(f"❌ Failed to start SwarmBot: {e}")
        print("Please check your .env file and ensure GROQ_API_KEY is set correctly")


if __name__ == "__main__":
    main()