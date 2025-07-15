#!/usr/bin/env python3
"""
Binarybrained-like AI Agent System
Enhanced multi-agent system that provides comprehensive, educational coding assistance
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from agents.enhanced_orchestrator import EnhancedOrchestratorAgent
from agents.enhanced_coder import EnhancedCoderAgent
from agents.planner import PlannerAgent
from agents.researcher import ResearcherAgent
from agents.file_picker import FilePickerAgent
from agents.reviewer import ReviewerAgent
from agents.thinker import ThinkerAgent
from agents.base_agent import AgentMessage
from core.config import settings


# Configure logging with UTF-8 encoding for Windows compatibility
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('Binarybrained_agent.log', encoding='utf-8')
    ]
)

# Fix console output encoding for Windows
import sys
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

logger = logging.getLogger(__name__)

class BinarybrainedSystem:
    """Enhanced multi-agent system with Binarybrained-like capabilities"""
    
    def __init__(self):
        self.orchestrator = None
        self.agents = {}
        self.session_history = []
    
    async def initialize(self):
        """Initialize the enhanced system"""
        logger.info("Initializing Binarybrained-like AI Agent System...")
        
        try:
            # Initialize enhanced orchestrator
            self.orchestrator = EnhancedOrchestratorAgent()
            
            # Initialize specialized agents
            self.agents = {
                'enhanced_coder': EnhancedCoderAgent(),
                'planner': PlannerAgent(),
                'researcher': ResearcherAgent(),
                'file_picker': FilePickerAgent(),
                'reviewer': ReviewerAgent(),
                'thinker': ThinkerAgent()
            }
            # Register agents with orchestrator
            for agent in self.agents.values():
                self.orchestrator.register_agent(agent)
            
            logger.info("[SUCCESS] Binarybrained system initialized successfully!")
            logger.info(f"Available agents: {list(self.agents.keys())}")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize system: {e}")
            
            raise
    
    async def process_request(self, user_request: str) -> dict:
        """Process a user request with enhanced capabilities"""
        try:
            logger.info(f"Processing request: {user_request}")
            
            # Create enhanced message
            message = AgentMessage(
                id=f"request_{datetime.now().timestamp()}",
                sender="user",
                recipient="enhanced_orchestrator",
                content={"request": user_request},
                timestamp=datetime.now(),
                message_type="user_request"
            )
            
            # Process with enhanced orchestrator
            response = await self.orchestrator.process(message)
            
            # Add to session history
            self.session_history.append({
                "timestamp": datetime.now().isoformat(),
                "request": user_request,
                "response": response.data if response.success else response.error,
                "success": response.success
            })
            
            return {
                "success": response.success,
                "response": response.data.get("response", "") if response.success else response.error,
                "metadata": response.metadata,
                "context": response.data.get("context", {}) if response.success else {}
            }
            
        except Exception as e:
            logger.error(f"Request processing failed: {e}")
            return {
                "success": False,
                "response": f"I encountered an error: {str(e)}",
                "metadata": {},
                "context": {}
            }
    
    def get_system_status(self) -> dict:
        """Get current system status"""
        return {
            "system": "Binarybrained-like AI Agent",
            "status": "active" if self.orchestrator else "inactive",
            "agents": list(self.agents.keys()),
            "session_requests": len(self.session_history),
            "llm_status": self.orchestrator.llm.get_status() if self.orchestrator else "unavailable"
        }
    
    async def interactive_mode(self):
        """Run in interactive mode for testing"""
        print("\n[AI] Binarybrained-like AI Agent System")
        print("=" * 50)
        print("Type your coding questions or requests.")
        print("Type 'quit', 'exit', or 'bye' to end the session.")
        print("Type 'status' to see system status.")
        print("Type 'history' to see session history.")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n[GOODBYE] Thanks for using the Binarybrained-like AI Agent!")
                    break
                
                if user_input.lower() == 'status':
                    status = self.get_system_status()
                    print(f"\n[STATUS] System Status:")
                    for key, value in status.items():
                        print(f"  {key}: {value}")
                    continue
                
                if user_input.lower() == 'history':
                    print(f"\n[HISTORY] Session History ({len(self.session_history)} requests):")
                
                    for i, entry in enumerate(self.session_history[-5:], 1):  # Show last 5
                        print(f"  {i}. {entry['request'][:50]}... ({'SUCCESS' if entry['success'] else 'ERROR'})")
                    continue
                
                if not user_input:
                    continue
                
                print("\n[PROCESSING] Working on your request...")
                # Process the request
                result = await self.process_request(user_input)
                
                if result["success"]:
                    print(f"\n[Binarybrained] {result['response']}")
                    
                    # Show metadata if available
                    if result.get("metadata"):
                        metadata = result["metadata"]
                        if metadata.get("agents_used"):
                            print(f"\n[AGENTS] Used: {', '.join(metadata['agents_used'])}")
                else:
                    print(f"\n[ERROR] {result['response']}")
                
            except KeyboardInterrupt:
                print("\n\n[GOODBYE] Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n[ERROR] Unexpected error: {e}")

async def main():
    """Main entry point"""
    system = BinarybrainedSystem()
    
    try:
        await system.initialize()
        
        if len(sys.argv) > 1:
            # Command line mode
            request = " ".join(sys.argv[1:])
            result = await system.process_request(request)
            
            if result["success"]:
                print(result["response"])
            else:
                print(f"Error: {result['response']}")
                sys.exit(1)
        else:
            # Interactive mode
            await system.interactive_mode()
    
    except Exception as e:
        logger.error(f"System failed: {e}")
        print(f"[ERROR] System initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
