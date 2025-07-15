#!/usr/bin/env python3
"""
Test script to verify BinaryBrained API integration works properly
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.config import settings
from core.llm_manager import BinaryBrainedProvider, LLMManager

async def test_binarybrained_provider():
    """Test BinaryBrained provider directly"""
    print("Testing BinaryBrained Provider...")
    
    # Check if API key is available
    if not settings.binarybrained_api_key:
        print("ERROR: BINARYBRAINED_API_KEY not found in environment variables")
        print("Please set your BINARYBRAINED_API_KEY in the .env file or environment")
        return False
    
    print(f"SUCCESS: Found BinaryBrained API key: {settings.binarybrained_api_key[:10]}...")
    
    # Test BinaryBrained provider
    try:
        provider = BinaryBrainedProvider(api_key=settings.binarybrained_api_key)
        
        if not provider.available:
            print("ERROR: BinaryBrained provider not available")
            return False
        
        print("SUCCESS: BinaryBrained provider initialized successfully")
        
        # Test generation
        response = await provider.generate(
            "Say hello and confirm you are working!",
            "You are a helpful AI assistant."
        )
        
        print(f"SUCCESS: BinaryBrained response: {response}")
        return True
        
    except Exception as e:
        print(f"ERROR: BinaryBrained provider test failed: {e}")
        return False

async def test_llm_manager():
    """Test LLM Manager with BinaryBrained priority"""
    print("\nTesting LLM Manager...")
    
    try:
        from agents.base_agent import BaseAgent
        
        # Create a simple test agent
        class TestAgent(BaseAgent):
            def initialize(self, **kwargs):
                pass
            
            async def process(self, message):
                pass
        
        agent = TestAgent("test_agent")
        
        # Test LLM call
        response = await agent.call_llm("What is 2+2? Answer briefly.")
        print(f"SUCCESS: LLM Manager response: {response}")
        
        # Check provider status
        status = agent.llm.get_status()
        print(f"SUCCESS: Provider status: {status}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: LLM Manager test failed: {e}")
        return False

async def test_multi_agent_system():
    """Test the full multi-agent system"""
    print("\nTesting Multi-Agent System...")
    
    try:
        from multi_agent_main import MultiAgentSystem
        
        system = MultiAgentSystem()
        
        # Test simple request
        result = await system.process_request("Say hello and tell me you're working!")
        
        if result['success']:
            print(f"SUCCESS: Multi-Agent System response: {result['data']['result']}")
            return True
        else:
            print(f"ERROR: Multi-Agent System failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"ERROR: Multi-Agent System test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("Starting BinaryBrained API Integration Tests")
    print("=" * 50)
    
    # Test 1: BinaryBrained Provider
    test1_passed = await test_binarybrained_provider()
    
    # Test 2: LLM Manager
    test2_passed = await test_llm_manager() if test1_passed else False
    
    # Test 3: Multi-Agent System
    test3_passed = await test_multi_agent_system() if test2_passed else False
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"  BinaryBrained Provider: {'PASS' if test1_passed else 'FAIL'}")
    print(f"  LLM Manager: {'PASS' if test2_passed else 'FAIL'}")
    print(f"  Multi-Agent System: {'PASS' if test3_passed else 'FAIL'}")
    
    if all([test1_passed, test2_passed, test3_passed]):
        print("\nAll tests passed! Your AI Agent system is ready to use with BinaryBrained!")
        print("\nTo use the system:")
        print("1. Make sure your BINARYBRAINED_API_KEY is set in the .env file")
        print("2. Run: python multi_agent_main.py")
        print("3. Start asking questions!")
    else:
        print("\nSome tests failed. Please check the errors above.")
        
        if not test1_passed:
            print("\nQuick fix suggestions:")
            print("1. Ensure BINARYBRAINED_API_KEY is set in your .env file")
            print("2. Verify your BinaryBrained API key is valid")
            print("3. Check your internet connection")

if __name__ == "__main__":
    asyncio.run(main())