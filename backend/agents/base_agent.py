from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import asyncio
import logging
from datetime import datetime
# Removed unused langchain imports that were causing import issues
from core.llm_manager import LLMManager, OllamaProvider, HuggingFaceProvider, GeminiProvider, BinaryBrainedProvider, MistralProvider
import os

class AgentMessage(BaseModel):
    id: str
    sender: str
    recipient: str
    content: Dict[str, Any]
    timestamp: datetime
    message_type: str

class AgentResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class BaseAgent(ABC):
    def __init__(self, name: str, model_name: str = None, **kwargs):
        self.name = name
        # Import here to avoid circular import
        from core.config import settings
        self.model_name = model_name or settings.default_model
        self.logger = logging.getLogger(f"agent.{name}")
        self.state = {}
        self.tools = []
        self.llm = self._initialize_llm()
        self.initialize(**kwargs)
    
    def _initialize_llm(self):
        """Initialize the LLM manager with multiple free providers"""
        from core.config import settings
        
        providers = []
        
        # Add providers based on configuration and availability
        for provider_name in settings.llm_providers:
            try:
                if provider_name == "ollama":
                    providers.append(OllamaProvider(
                        model_name=settings.ollama_model,
                        base_url=settings.ollama_base_url
                    ))
                elif provider_name == "binarybrained" and settings.binarybrained_api_key:
                    providers.append(BinaryBrainedProvider(
                        api_key=settings.binarybrained_api_key,
                        model_name="llama3-8b-8192"
                    ))
                elif provider_name == "mistral" and settings.mistral_api_key:
                    providers.append(MistralProvider(
                        api_key=settings.mistral_api_key,
                        model_name="mistral-large-latest"
                    ))
                elif provider_name == "gemini" and settings.google_api_key:
                    providers.append(GeminiProvider(
                        api_key=settings.google_api_key,
                        model_name="gemini-pro"
                    ))
            except Exception as e:
                self.logger.warning(f"Failed to initialize {provider_name} provider: {e}")
        
        if not providers:
            # Fallback to basic Ollama if no providers configured
            self.logger.warning("No providers configured, falling back to basic Ollama")
            providers.append(OllamaProvider())
        
        return LLMManager(providers)
    
    @abstractmethod
    def initialize(self, **kwargs):
        """Initialize agent-specific components"""
        pass
    
    @abstractmethod
    async def process(self, message: AgentMessage) -> AgentResponse:
        """Process incoming message and return response"""
        pass
    
    def get_system_prompt(self) -> str:
        """Return agent-specific system prompt"""
        return f"You are {self.name}, a specialized AI agent."
    
    async def call_llm(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Call the LLM manager with prompt and context"""
        try:
            system_prompt = self.get_system_prompt()
            if context:
                system_prompt += f"\n\nContext: {context}"
            
            response = await self.llm.generate(prompt, system_prompt)
            return response
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise
    
    def add_tool(self, tool):
        """Add a tool to this agent's toolkit"""
        self.tools.append(tool)
    
    async def use_tool(self, tool_name: str, **kwargs) -> Any:
        """Use a specific tool"""
        for tool in self.tools:
            if tool.name == tool_name:
                return await tool.execute(**kwargs)
        raise ValueError(f"Tool {tool_name} not found")
