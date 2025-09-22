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
        self.max_errors = 2  # Reduced from 3 to 2 for faster failure
        self.last_error_time = None
        self.cooldown_period = 180  # Reduced from 5 minutes to 3 minutes
        self.consecutive_failures = 0
        self.rate_limited = False
        self.rate_limit_reset_time = None
    
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generate response from the LLM"""
        pass
    
    def mark_error(self, error_type="general"):
        """Mark an error and disable if too many errors"""
        self.error_count += 1
        self.consecutive_failures += 1
        self.last_error_time = time.time()
        
        # Handle specific error types
        if error_type == "rate_limit":
            self.rate_limited = True
            self.rate_limit_reset_time = time.time() + 60  # 1 minute rate limit cooldown
            logger.warning(f"Provider {self.name} is rate limited")
        elif error_type == "auth":
            # Auth errors are likely permanent - disable immediately
            self.available = False
            self.error_count = self.max_errors
            logger.error(f"Provider {self.name} disabled due to authentication error")
        
        if self.error_count >= self.max_errors:
            self.available = False
            logger.warning(f"Provider {self.name} disabled due to {self.error_count} errors")
    
    def reset_errors(self):
        """Reset error count and re-enable provider"""
        self.error_count = 0
        self.consecutive_failures = 0
        self.available = True
        self.last_error_time = None
        self.rate_limited = False
        self.rate_limit_reset_time = None
    
    def can_retry(self) -> bool:
        """Check if provider can be retried after cooldown"""
        current_time = time.time()
        
        # Check rate limiting first
        if self.rate_limited and self.rate_limit_reset_time:
            if current_time < self.rate_limit_reset_time:
                return False
            else:
                self.rate_limited = False
                self.rate_limit_reset_time = None
        
        if self.available:
            return True
            
        # Check general cooldown
        if self.last_error_time and (current_time - self.last_error_time) > self.cooldown_period:
            self.reset_errors()
            return True
            
        return False

class BinaryBrainedProvider(LLMProvider):
    """BinaryBrained/Groq provider with improved error handling"""

    def __init__(self, api_key: str = None, model_name: str = "llama-3.3-70b-versatile", **kwargs):
        super().__init__("binarybrained", **kwargs)
        self.api_key = api_key
        # Use llama-3.3-70b-versatile as the default model (currently available on Groq)
        self.model_name = model_name
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        } if api_key else {}

        if not api_key:
            self.available = False
            logger.warning("BinaryBrained API key not provided")
        else:
            logger.info(f"BinaryBrained provider initialized with model: {self.model_name}")
    
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
                    content = result['choices'][0]['message']['content']
                    logger.info(f"BinaryBrained successfully generated response (length: {len(content)})")
                    return content
                else:
                    raise Exception(f"Invalid response format: {result}")
            elif response.status_code == 401:
                self.mark_error("auth")
                raise Exception(f"Authentication failed - check your BINARYBRAINED_API_KEY")
            elif response.status_code == 429:
                self.mark_error("rate_limit")
                raise Exception(f"Rate limit exceeded - please try again later")
            else:
                error_detail = response.text[:500] if response.text else "No error details"
                raise Exception(f"API error: {response.status_code} - {error_detail}")

        except Exception as e:
            if "Authentication failed" not in str(e):
                self.mark_error()
            logger.error(f"BinaryBrained generation failed: {e}")
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

class MistralProvider(LLMProvider):
    """Mistral AI provider"""

    def __init__(self, api_key: str = None, model_name: str = "mistral-small-latest", **kwargs):
        super().__init__("mistral", **kwargs)
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = "https://api.mistral.ai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        } if api_key else {}

        if not api_key:
            self.available = False
            logger.warning("Mistral API key not provided")
        else:
            logger.info(f"Mistral provider initialized with model: {self.model_name}")

    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        if not self.available or not self.api_key:
            raise Exception("Mistral provider not available or API key missing")

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2048
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
                    content = result['choices'][0]['message']['content']
                    logger.info(f"Mistral successfully generated response (length: {len(content)})")
                    return content
                else:
                    raise Exception(f"Invalid response format: {result}")
            elif response.status_code == 401:
                self.mark_error("auth")
                raise Exception(f"Authentication failed - check your MISTRAL_API_KEY")
            elif response.status_code == 429:
                self.mark_error("rate_limit")
                raise Exception(f"Rate limit exceeded - please try again later")
            else:
                error_detail = response.text[:500] if response.text else "No error details"
                raise Exception(f"API error: {response.status_code} - {error_detail}")

        except Exception as e:
            if "Authentication failed" not in str(e):
                self.mark_error()
            logger.error(f"Mistral generation failed: {e}")
            raise Exception(f"Mistral generation failed: {e}")

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
                error_str = str(e).lower()
                
                # Detect specific error types for better handling
                if "401" in error_str or "invalid credentials" in error_str or "unauthorized" in error_str:
                    provider.mark_error("auth")
                    self.logger.warning(f"Provider {provider.name} failed with auth error: {e}")
                elif "rate limit" in error_str or "429" in error_str or "rate limited" in error_str:
                    provider.mark_error("rate_limit") 
                    self.logger.warning(f"Provider {provider.name} is rate limited")
                else:
                    provider.mark_error("general")
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

    def generate_response_sync(self, prompt: str, system_prompt: str = None) -> str:
        """Synchronous wrapper for generate_response_async"""
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.generate_response_async(prompt, system_prompt))
        except RuntimeError:
            # If no event loop is running, create a new one
            return asyncio.run(self.generate_response_async(prompt, system_prompt))

    def analyze_image_with_groq_sync(self, image_data: str, prompt: str = "Describe what you see in this image.") -> str:
        """Analyze image using Groq vision capabilities (synchronous)"""
        try:
            # Find BinaryBrained/Groq provider
            groq_provider = None
            for provider in self.providers:
                if provider.name == "binarybrained" and provider.available:
                    groq_provider = provider
                    break

            if not groq_provider:
                return "Groq/BinaryBrained provider not available for image analysis."

            # Use llava vision model for image analysis
            payload = {
                "model": "llama-3.2-11b-vision-preview",  # Groq's vision model
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1024,
                "temperature": 0.7
            }

            response = requests.post(
                groq_provider.api_url,
                headers=groq_provider.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"Groq vision API error: {response.status_code} - {response.text}")
                return f"Error analyzing image: {response.status_code}"

        except Exception as e:
            logger.error(f"Error in image analysis: {e}")
            return f"Image analysis failed: {str(e)}"

def create_llm_manager(config) -> LLMManager:
    """Factory function to create LLM manager with configured providers"""
    providers = []

    # Add Mistral provider (fast and reliable)
    if config.mistral_api_key:
        providers.append(MistralProvider(
            api_key=config.mistral_api_key,
            model_name="mistral-small-latest"
        ))
        logger.info(f"Added Mistral provider with API key: {config.mistral_api_key[:10]}...")

    # Add BinaryBrained/Groq provider (high quality)
    if config.binarybrained_api_key:
        providers.append(BinaryBrainedProvider(
            api_key=config.binarybrained_api_key,
            model_name="llama-3.3-70b-versatile"  # Updated to current Groq model
        ))
        logger.info(f"Added BinaryBrained provider with API key: {config.binarybrained_api_key[:10]}...")

    # Add OpenAI provider
    if config.openai_api_key:
        providers.append(OpenAIProvider(
            api_key=config.openai_api_key,
            model_name="gpt-3.5-turbo"
        ))
        logger.info(f"Added OpenAI provider")

    # Add HuggingFace provider
    if config.huggingface_api_token:
        providers.append(HuggingFaceProvider(
            api_token=config.huggingface_api_token,
            model_name="microsoft/DialoGPT-medium"
        ))
        logger.info(f"Added HuggingFace provider")

    # Only add local provider if no other providers are available
    if not providers:
        logger.warning("No API providers available, using local fallback only")
        providers.append(LocalLLMProvider())

    logger.info(f"LLM Manager created with {len(providers)} providers: {[p.name for p in providers]}")
    return LLMManager(providers)

