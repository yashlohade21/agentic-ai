import asyncio
import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.config = kwargs
        self.available = True
        self.error_count = 0
        self.max_errors = 3
        self.last_error_time = None
        self.cooldown_period = 300  # 5 minutes cooldown after errors
    
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generate response from the LLM"""
        pass
    
    def mark_error(self):
        """Mark an error and disable if too many errors"""
        self.error_count += 1
        self.last_error_time = time.time()
        if self.error_count >= self.max_errors:
            self.available = False
            logger.warning(f"Provider {self.name} disabled due to too many errors")
    
    def reset_errors(self):
        """Reset error count and re-enable provider"""
        self.error_count = 0
        self.available = True
        self.last_error_time = None
    
    def can_retry(self) -> bool:
        """Check if provider can be retried after cooldown"""
        if self.available:
            return True
        if self.last_error_time and (time.time() - self.last_error_time) > self.cooldown_period:
            self.reset_errors()
            return True
        return False

class BinaryBrainedProvider(LLMProvider):
    """BinaryBrained/Groq provider with improved error handling"""
    
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
                "max_tokens": 2048,
                "stream": False
            }
            
            # Use ThreadPoolExecutor for better timeout handling
            with ThreadPoolExecutor() as executor:
                future = executor.submit(self._make_request, payload)
                try:
                    response = await asyncio.wait_for(
                        asyncio.wrap_future(future), 
                        timeout=30.0
                    )
                except asyncio.TimeoutError:
                    raise Exception("Request timeout after 30 seconds")
            
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
    
    def _make_request(self, payload):
        """Make the actual HTTP request"""
        return requests.post(
            self.api_url,
            headers=self.headers,
            json=payload,
            timeout=25  # Slightly less than asyncio timeout
        )

class HuggingFaceProvider(LLMProvider):
    """Hugging Face provider with improved error handling"""
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium", api_token: str = None, **kwargs):
        super().__init__("huggingface", **kwargs)
        self.model_name = model_name
        self.api_token = api_token
        self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        self.headers = {"Authorization": f"Bearer {api_token}"} if api_token else {}
    
    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        if not self.available:
            raise Exception("HuggingFace provider not available")
            
        try:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:" if system_prompt else f"User: {prompt}\nAssistant:"
            payload = {
                "inputs": full_prompt,
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.7,
                    "do_sample": True,
                    "return_full_text": False,
                    "pad_token_id": 50256
                },
                "options": {
                    "wait_for_model": True
                }
            }
            
            with ThreadPoolExecutor() as executor:
                future = executor.submit(self._make_request, payload)
                try:
                    response = await asyncio.wait_for(
                        asyncio.wrap_future(future), 
                        timeout=30.0
                    )
                except asyncio.TimeoutError:
                    raise Exception("Request timeout after 30 seconds")
            
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
    
    def _make_request(self, payload):
        """Make the actual HTTP request"""
        return requests.post(
            self.api_url,
            headers=self.headers,
            json=payload,
            timeout=25
        )

class OpenAIProvider(LLMProvider):
    """OpenAI provider for fallback"""
    
    def __init__(self, api_key: str = None, model_name: str = "gpt-3.5-turbo", **kwargs):
        super().__init__("openai", **kwargs)
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        } if api_key else {}
        
        if not api_key:
            self.available = False
            logger.warning("OpenAI API key not provided")
    
    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        if not self.available or not self.api_key:
            raise Exception("OpenAI provider not available or API key missing")
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1500
            }
            
            with ThreadPoolExecutor() as executor:
                future = executor.submit(self._make_request, payload)
                try:
                    response = await asyncio.wait_for(
                        asyncio.wrap_future(future), 
                        timeout=30.0
                    )
                except asyncio.TimeoutError:
                    raise Exception("Request timeout after 30 seconds")
            
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
            raise Exception(f"OpenAI generation failed: {e}")
    
    def _make_request(self, payload):
        """Make the actual HTTP request"""
        return requests.post(
            self.api_url,
            headers=self.headers,
            json=payload,
            timeout=25
        )

class LocalLLMProvider(LLMProvider):
    """Local LLM provider for offline fallback"""
    
    def __init__(self, **kwargs):
        super().__init__("local", **kwargs)
        # This is always available as a last resort
        self.available = True
    
    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generate a simple response using local processing"""
        try:
            # Simple rule-based responses for common queries
            prompt_lower = prompt.lower()
            
            if any(word in prompt_lower for word in ['hello', 'hi', 'hey']):
                return "Hello! I'm currently running in offline mode. My responses are limited, but I'm here to help with basic queries."
            
            elif any(word in prompt_lower for word in ['code', 'python', 'function']):
                return "I'd love to help with coding, but I'm currently in offline mode with limited capabilities. Please check your internet connection or API keys."
            
            elif any(word in prompt_lower for word in ['error', 'problem', 'issue']):
                return "I understand you're experiencing an issue. In offline mode, I recommend checking your network connection and API configuration."
            
            else:
                return f"I received your message: '{prompt[:100]}...' but I'm currently in offline mode with limited capabilities. Please check your internet connection or API keys for full functionality."
                
        except Exception as e:
            raise Exception(f"Local generation failed: {e}")

class LLMManager:
    """Enhanced LLM manager with better error handling and fallbacks"""
    
    def __init__(self, providers: List[LLMProvider]):
        self.providers = providers
        self.logger = logging.getLogger("llm_manager")
        self.request_count = 0
        self.success_count = 0
    
    def add_provider(self, provider: LLMProvider):
        """Add a new provider to the list"""
        self.providers.append(provider)
    
    def get_available_providers(self) -> List[LLMProvider]:
        """Get list of currently available providers"""
        available = []
        for provider in self.providers:
            if provider.can_retry():
                available.append(provider)
        return available
    
    async def generate(self, prompt: str, system_prompt: str = None, max_retries: int = None) -> str:
        """Generate response using available providers with intelligent fallback"""
        self.request_count += 1
        available_providers = self.get_available_providers()
        
        if not available_providers:
            # Add local provider as last resort
            local_provider = LocalLLMProvider()
            available_providers = [local_provider]
        
        max_retries = max_retries or len(available_providers)
        last_error = None
        
        for attempt in range(max_retries):
            provider = available_providers[attempt % len(available_providers)]
            
            try:
                self.logger.info(f"Attempting generation with {provider.name} (attempt {attempt + 1})")
                result = await provider.generate(prompt, system_prompt)
                self.logger.info(f"Successfully generated response with {provider.name}")
                self.success_count += 1
                return result
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"Provider {provider.name} failed: {e}")
                
                # If this was the last attempt, try local provider
                if attempt == max_retries - 1 and provider.name != "local":
                    try:
                        local_provider = LocalLLMProvider()
                        self.logger.info("Falling back to local provider")
                        result = await local_provider.generate(prompt, system_prompt)
                        return result
                    except Exception as local_error:
                        self.logger.error(f"Local provider also failed: {local_error}")
                
                continue
        
        raise Exception(f"All providers failed. Last error: {last_error}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all providers"""
        return {
            "providers": [
                {
                    "name": p.name,
                    "available": p.available,
                    "can_retry": p.can_retry(),
                    "error_count": p.error_count,
                    "last_error_time": p.last_error_time
                }
                for p in self.providers
            ],
            "total_providers": len(self.providers),
            "available_providers": len(self.get_available_providers()),
            "request_count": self.request_count,
            "success_count": self.success_count,
            "success_rate": (self.success_count / self.request_count * 100) if self.request_count > 0 else 0
        }

def create_llm_manager(config) -> LLMManager:
    """Factory function to create LLM manager with configured providers"""
    providers = []
    
    # Add BinaryBrained/Groq provider (highest priority)
    if config.binarybrained_api_key:
        providers.append(BinaryBrainedProvider(
            api_key=config.binarybrained_api_key,
            model_name="llama3-8b-8192"
        ))
    
    # Add OpenAI provider
    if config.openai_api_key:
        providers.append(OpenAIProvider(
            api_key=config.openai_api_key,
            model_name="gpt-3.5-turbo"
        ))
    
    # Add HuggingFace provider
    if config.huggingface_api_token:
        providers.append(HuggingFaceProvider(
            api_token=config.huggingface_api_token,
            model_name="microsoft/DialoGPT-medium"
        ))
    
    # Always add local provider as fallback
    providers.append(LocalLLMProvider())
    
    return LLMManager(providers)

