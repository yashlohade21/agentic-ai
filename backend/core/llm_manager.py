import asyncio
import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import requests
import json
# Removed langchain_ollama import to avoid hanging
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.config = kwargs
        self.available = True
        self.error_count = 0
        self.max_errors = 3
    
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generate response from the LLM"""
        pass
    
    def mark_error(self):
        """Mark an error and disable if too many errors"""
        self.error_count += 1
        if self.error_count >= self.max_errors:
            self.available = False
            logger.warning(f"Provider {self.name} disabled due to too many errors")
    
    def reset_errors(self):
        """Reset error count and re-enable provider"""
        self.error_count = 0
        self.available = True

class OllamaProvider(LLMProvider):
    """Ollama local LLM provider"""
    
    def __init__(self, model_name: str = "llama3.2", base_url: str = "http://localhost:11434", **kwargs):
        super().__init__("ollama", **kwargs)
        self.model_name = model_name
        self.base_url = base_url
        self.llm = None
        self._initialize()
    
    def _initialize(self):
        # Skip Ollama initialization to avoid hanging - will be disabled
        logger.warning("Ollama provider disabled to avoid connection issues")
        self.available = False
    
    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        raise Exception("Ollama provider not available - disabled to avoid connection issues")

class HuggingFaceProvider(LLMProvider):
    """Hugging Face free inference API provider"""
    
    def __init__(self, model_name: str = "gpt2", api_token: str = None, **kwargs):
        super().__init__("huggingface", **kwargs)
        self.model_name = model_name
        self.api_token = api_token
        self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        self.headers = {"Authorization": f"Bearer {api_token}"} if api_token else {}
        self._test_connection()
    
    def _test_connection(self):
        """Skip connection test to avoid hanging"""
        # Skip connection test to avoid hanging during initialization
        pass
    
    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        if not self.available:
            raise Exception("HuggingFace provider not available")
            
        try:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:" if system_prompt else f"User: {prompt}\nAssistant:"
            payload = {
                "inputs": full_prompt,
                "parameters": {
                    "max_new_tokens": 150,
                    "temperature": 0.7,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            response = await asyncio.to_thread(
                requests.post, 
                self.api_url, 
                headers=self.headers, 
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    self.reset_errors()
                    return result[0].get('generated_text', '').strip()
                else:
                    raise Exception("Invalid response format")
            else:
                raise Exception(f"API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.mark_error()
            raise Exception(f"HuggingFace generation failed: {e}")

class GeminiProvider(LLMProvider):
    """Google Gemini free tier provider"""
    
    def __init__(self, api_key: str = None, model_name: str = "gemini-pro", **kwargs):
        super().__init__("gemini", **kwargs)
        self.api_key = api_key
        self.model_name = model_name
        self.llm = None
        if api_key:
            self._initialize()
    
    def _initialize(self):
        try:
            if ChatGoogleGenerativeAI is None:
                raise ImportError("langchain_google_genai not installed")
            self.llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.api_key,
                temperature=0.7
            )
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini: {e}")
            self.available = False
    
    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        if not self.available or not self.llm:
            raise Exception("Gemini provider not available")
        
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = await asyncio.to_thread(self.llm.invoke, full_prompt)
            self.reset_errors()
            return response.content
        except Exception as e:
            self.mark_error()
            raise Exception(f"Gemini generation failed: {e}")

class BinaryBrainedProvider(LLMProvider):
    """BinaryBrained free tier provider - Fixed implementation"""
    
    def __init__(self, api_key: str = None, model_name: str = "llama3-8b-8192", **kwargs):
        super().__init__("binarybrained", **kwargs)
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        } if api_key else {}
        
        if not api_key:
            self.available = False
            logger.warning("BinaryBrained API key not provided")
    
    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        if not self.available or not self.api_key:
            raise Exception("BinaryBrained provider not available or API key missing")
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1024
            }
            
            response = await asyncio.to_thread(
                requests.post,
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    self.reset_errors()
                    return result['choices'][0]['message']['content']
                else:
                    raise Exception(f"Invalid response format: {result}")
            else:
                raise Exception(f"API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.mark_error()
            raise Exception(f"BinaryBrained generation failed: {e}")

class LLMManager:
    """Manages multiple LLM providers with fallback logic"""
    
    def __init__(self, providers: List[LLMProvider]):
        self.providers = providers
        self.current_provider_index = 0
        self.logger = logging.getLogger("llm_manager")
    
    def add_provider(self, provider: LLMProvider):
        """Add a new provider to the list"""
        self.providers.append(provider)
    
    def get_available_providers(self) -> List[LLMProvider]:
        """Get list of currently available providers"""
        return [p for p in self.providers if p.available]
    
    async def generate(self, prompt: str, system_prompt: str = None, max_retries: int = None) -> str:
        """Generate response using available providers with fallback"""
        available_providers = self.get_available_providers()
        
        if not available_providers:
            raise Exception("No LLM providers available")
        
        max_retries = max_retries or len(available_providers)
        last_error = None
        
        for attempt in range(max_retries):
            provider = available_providers[attempt % len(available_providers)]
            
            try:
                self.logger.info(f"Attempting generation with {provider.name}")
                result = await provider.generate(prompt, system_prompt)
                self.logger.info(f"Successfully generated response with {provider.name}")
                return result
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"Provider {provider.name} failed: {e}")
                continue
        
        raise Exception(f"All providers failed. Last error: {last_error}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        return {
            "providers": [
                {
                    "name": p.name,
                    "available": p.available,
                    "error_count": p.error_count
                }
                for p in self.providers
            ],
            "total_providers": len(self.providers),
            "available_providers": len(self.get_available_providers())
        }
