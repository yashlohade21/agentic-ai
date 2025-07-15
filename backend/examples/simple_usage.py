"""
Simple usage example for the Multi-Agent AI System
"""

import asyncio
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multi_agent_main import MultiAgentSystem

async def simple_example():
    """Simple example of using the multi-agent system"""
    
    # Initialize the system
    system = MultiAgentSystem()
    
    # Example requests
    requests = [
        "Write a Python function to reverse a string",
        "Research Python web frameworks",
        "Find all .py files in the current directory",
        "Create a simple calculator class"
    ]
    
    print("🤖 Multi-Agent System - Simple Usage Example")
    print("=" * 50)
    
    for i, request in enumerate(requests, 1):
        print(f"\n📝 Request {i}: {request}")
        print("-" * 30)
        
        try:
            result = await system.process_request(request)
            
            if result['success']:
                print("✅ Success!")
                print(f"Result: {result['data']['result'][:200]}...")  # Truncate for display
                
                if 'plan' in result['data']:
                    print(f"Plan steps: {len(result['data']['plan'])}")
            else:
                print(f"❌ Error: {result['error']}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print()

async def interactive_example():
    """Interactive example"""
    system = MultiAgentSystem()
    
    print("🤖 Interactive Multi-Agent System")
    print("Type 'quit' to exit")
    print("-" * 30)
    
    while True:
        try:
            user_input = input("\n💬 Your request: ").strip()
            
            if user_input.lower() in ['quit', 'exit']:
                break
            
            if not user_input:
                continue
            
            print("⚙️ Processing...")
            result = await system.process_request(user_input)
            
            if result['success']:
                print(f"✅ {result['data']['result']}")
            else:
                print(f"❌ {result['error']}")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("👋 Goodbye!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        asyncio.run(interactive_example())
    else:
        asyncio.run(simple_example())
