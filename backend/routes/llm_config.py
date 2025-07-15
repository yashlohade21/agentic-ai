import os
import sys
import logging
from typing import Optional
from flask import Blueprint

# Add the original backend to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

try:
    from core.llm_manager import LLMManager, BinaryBrainedProvider, GeminiProvider, HuggingFaceProvider
    from core.config import settings
except ImportError as e:
    print(f'Warning: Could not import LLM components: {e}')
    LLMManager = None
    BinaryBrainedProvider = None
    GeminiProvider = None
    HuggingFaceProvider = None
    settings = None

logger = logging.getLogger(__name__)

class LLMConfig:
    """LLM Configuration for the Flask app"""
    
    def __init__(self):
        self.llm_manager = None
        self.initialized = False
    
    def initialize(self) -> bool:
        """Initialize the LLM manager with available providers"""
        if self.initialized:
            return True
        
        if not LLMManager:
            logger.error("LLM components not available")
            return False
        
        try:
            providers = []
            
            # Try to initialize BinaryBrained provider (Groq API)
            groq_api_key = os.getenv('GROQ_API_KEY') or os.getenv('BINARYBRAINED_API_KEY')
            if groq_api_key:
                try:
                    provider = BinaryBrainedProvider(
                        api_key=groq_api_key,
                        model_name="llama3-8b-8192"
                    )
                    providers.append(provider)
                    logger.info("BinaryBrained provider initialized")
                except Exception as e:
                    logger.warning(f"Failed to initialize BinaryBrained provider: {e}")
            
            # Try to initialize Gemini provider
            google_api_key = os.getenv('GOOGLE_API_KEY')
            if google_api_key:
                try:
                    provider = GeminiProvider(
                        api_key=google_api_key,
                        model_name="gemini-pro"
                    )
                    providers.append(provider)
                    logger.info("Gemini provider initialized")
                except Exception as e:
                    logger.warning(f"Failed to initialize Gemini provider: {e}")
            
            # Try to initialize HuggingFace provider
            hf_token = os.getenv('HUGGINGFACE_API_TOKEN')
            if hf_token:
                try:
                    provider = HuggingFaceProvider(
                        api_token=hf_token,
                        model_name="microsoft/DialoGPT-medium"
                    )
                    providers.append(provider)
                    logger.info("HuggingFace provider initialized")
                except Exception as e:
                    logger.warning(f"Failed to initialize HuggingFace provider: {e}")
            
            if not providers:
                # Create a fallback mock provider for testing
                logger.warning("No API keys found, creating mock provider for testing")
                providers.append(MockProvider())
            
            self.llm_manager = LLMManager(providers)
            self.initialized = True
            logger.info(f"LLM Manager initialized with {len(providers)} providers")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM manager: {e}")
            return False
    
    def get_manager(self) -> Optional[LLMManager]:
        """Get the LLM manager instance"""
        if not self.initialized:
            self.initialize()
        return self.llm_manager

class MockProvider:
    """Mock provider for testing when no API keys are available"""
    
    def __init__(self):
        self.name = "mock"
        self.available = True
        self.error_count = 0
        self.max_errors = 3
    
    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generate a mock response"""
        return f"This is a mock response to: {prompt[:50]}... (Mock AI is working! Please configure API keys for real AI responses.)"
    
    def mark_error(self):
        self.error_count += 1
    
    def reset_errors(self):
        self.error_count = 0

# Global LLM configuration instance
llm_config = LLMConfig()