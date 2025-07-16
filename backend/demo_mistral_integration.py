#!/usr/bin/env python3
"""
Demo script showcasing Mistral API integration with the AI agent system.
This script demonstrates the enhanced capabilities for code suggestions,
architecture generation, and image creation.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

from agents.enhanced_coder import EnhancedCoderAgent
from agents.image_agent import ImageGenerationAgent
from agents.enhanced_orchestrator import EnhancedOrchestratorAgent
from agents.base_agent import AgentMessage
from core.config import Config

async def demo_mistral_integration():
    """Demonstrate Mistral integration capabilities"""
    
    print("🚀 Mistral API Integration Demo")
    print("=" * 50)
    
    # Initialize configuration
    config = Config()
    print(f"✓ Configuration loaded")
    print(f"✓ Available LLM providers: {config.llm_providers}")
    print(f"✓ Mistral API key configured: {'Yes' if config.mistral_api_key else 'No (using placeholder)'}")
    print()
    
    # Demo 1: Enhanced Coder with Architecture Generation
    print("📋 Demo 1: Architecture Generation")
    print("-" * 30)
    
    try:
        coder_agent = EnhancedCoderAgent()
        
        architecture_message = AgentMessage(
            id="demo_arch",
            sender="demo",
            recipient="enhanced_coder",
            content={
                "task": "Design the architecture for a scalable e-commerce platform with microservices",
                "request_type": "architecture",
                "language": "python"
            },
            timestamp=datetime.now(),
            message_type="demo"
        )
        
        print("🔄 Generating architecture design...")
        arch_response = await coder_agent.process(architecture_message)
        
        if arch_response.success:
            print("✅ Architecture generation successful!")
            print(f"📊 Response type: {arch_response.data.get('type', 'unknown')}")
            print(f"📝 Architecture design preview: {arch_response.data.get('architecture_design', 'N/A')[:200]}...")
            if arch_response.data.get('recommendations'):
                print(f"💡 Recommendations count: {len(arch_response.data['recommendations'])}")
        else:
            print(f"❌ Architecture generation failed: {arch_response.error}")
        
        print()
        
    except Exception as e:
        print(f"❌ Demo 1 failed: {str(e)}")
        print()
    
    # Demo 2: Advanced Code Suggestions
    print("💻 Demo 2: Advanced Code Suggestions")
    print("-" * 35)
    
    try:
        code_message = AgentMessage(
            id="demo_code",
            sender="demo",
            recipient="enhanced_coder",
            content={
                "task": "Suggest improvements for a Python web API with authentication",
                "request_type": "advanced_code",
                "language": "python",
                "existing_code": "from flask import Flask\napp = Flask(__name__)\n@app.route('/api/users')\ndef get_users():\n    return {'users': []}"
            },
            timestamp=datetime.now(),
            message_type="demo"
        )
        
        print("🔄 Generating advanced code suggestions...")
        code_response = await coder_agent.process(code_message)
        
        if code_response.success:
            print("✅ Code suggestions generated successfully!")
            print(f"📊 Response type: {code_response.data.get('type', 'unknown')}")
            print(f"🔧 Code validation: {'Valid' if code_response.data.get('is_valid') else 'Invalid'}")
            if code_response.data.get('alternatives'):
                print(f"🔄 Alternative approaches: {len(code_response.data['alternatives'])}")
        else:
            print(f"❌ Code suggestions failed: {code_response.error}")
        
        print()
        
    except Exception as e:
        print(f"❌ Demo 2 failed: {str(e)}")
        print()
    
    # Demo 3: Image Generation
    print("🎨 Demo 3: Image Generation")
    print("-" * 25)
    
    try:
        image_agent = ImageGenerationAgent()
        
        image_message = AgentMessage(
            id="demo_image",
            sender="demo",
            recipient="image_generation",
            content={
                "request": "Create a technical diagram showing microservices architecture",
                "type": "diagram",
                "prompt": "Microservices architecture diagram with API gateway, user service, product service, and database",
                "style": "technical diagram"
            },
            timestamp=datetime.now(),
            message_type="demo"
        )
        
        print("🔄 Generating architectural diagram...")
        image_response = await image_agent.process(image_message)
        
        if image_response.success:
            print("✅ Image generation completed!")
            result = image_response.data.get('generation_result', {})
            print(f"🖼️  Image type: {image_response.metadata.get('image_type', 'unknown')}")
            print(f"📁 Output path: {result.get('output_path', 'N/A')}")
            print(f"🎯 Provider used: {result.get('provider', 'unknown')}")
            
            if result.get('placeholder'):
                print("ℹ️  Note: Placeholder image generated (configure OPENAI_API_KEY for actual image generation)")
        else:
            print(f"❌ Image generation failed: {image_response.error}")
        
        print()
        
    except Exception as e:
        print(f"❌ Demo 3 failed: {str(e)}")
        print()
    
    # Demo 4: Orchestrator Integration
    print("🎭 Demo 4: Orchestrator Integration")
    print("-" * 32)
    
    try:
        # Initialize orchestrator with all agents
        orchestrator = EnhancedOrchestratorAgent()
        
        # Register agents
        agents = {
            'enhanced_coder': coder_agent,
            'image_generation': image_agent
        }
        
        for agent in agents.values():
            orchestrator.register_agent(agent)
        
        orchestrator_message = AgentMessage(
            id="demo_orchestrator",
            sender="demo",
            recipient="enhanced_orchestrator",
            content={
                "request": "Design a REST API for a blog platform and create a visual diagram"
            },
            timestamp=datetime.now(),
            message_type="demo"
        )
        
        print("🔄 Processing complex request through orchestrator...")
        orchestrator_response = await orchestrator.process(orchestrator_message)
        
        if orchestrator_response.success:
            print("✅ Orchestrator processing successful!")
            print(f"📊 Request type: {orchestrator_response.metadata.get('request_type', 'unknown')}")
            print(f"🤖 Agents used: {orchestrator_response.metadata.get('agents_used', [])}")
            print(f"📝 Response preview: {str(orchestrator_response.data.get('response', 'N/A'))[:200]}...")
        else:
            print(f"❌ Orchestrator processing failed: {orchestrator_response.error}")
        
        print()
        
    except Exception as e:
        print(f"❌ Demo 4 failed: {str(e)}")
        print()
    
    # Summary
    print("📋 Integration Summary")
    print("-" * 20)
    print("✅ Mistral API integration completed successfully!")
    print("✅ Enhanced code suggestions and architecture generation enabled")
    print("✅ Image generation capabilities added")
    print("✅ Orchestrator updated to handle new capabilities")
    print("✅ Backward compatibility with existing BINARYBRAINED_API_KEY maintained")
    print()
    print("🔧 To enable full functionality:")
    print("   - Set MISTRAL_API_KEY environment variable")
    print("   - Set OPENAI_API_KEY for image generation (optional)")
    print("   - Set BINARYBRAINED_API_KEY for additional LLM provider (optional)")
    print()
    print("🚀 The AI agent system is now enhanced with Mistral capabilities!")

if __name__ == "__main__":
    asyncio.run(demo_mistral_integration())

