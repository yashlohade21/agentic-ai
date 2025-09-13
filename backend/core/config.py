import os
from typing import List, Optional
from pathlib import Path

class Config:
    """Simple configuration class that loads from environment variables"""
    
    def __init__(self):
        # Load .env file if it exists
        self._load_env_file()
        
        # API Keys (for paid services - optional)
        self.openai_api_key: Optional[str] = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key: Optional[str] = os.getenv('ANTHROPIC_API_KEY')
        self.binarybrained_api_key: Optional[str] = os.getenv('BINARYBRAINED_API_KEY')
        self.mistral_api_key: Optional[str] = os.getenv('MISTRAL_API_KEY')       
        # Free LLM API Keys - only use if real tokens provided
        self.huggingface_api_token: Optional[str] = os.getenv('HUGGINGFACE_API_TOKEN') if os.getenv('HUGGINGFACE_API_TOKEN', '').startswith('hf_') else None
        self.google_api_key: Optional[str] = os.getenv('GOOGLE_API_KEY')
        
        # Local LLM Settings
        self.ollama_base_url: str = os.getenv('OLLAMA_BASE_URL', "http://localhost:11434")
        self.ollama_model: str = os.getenv('OLLAMA_MODEL', "llama3.2")
        
        # Optimized LLM Provider Priority - working providers first, fastest to slowest
        # Mistral is working well, BinaryBrained has rate limits, skip broken providers
        available_providers = []
        
        # Add providers only if they have valid credentials or are always available
        if self.mistral_api_key:
            available_providers.append("mistral")
        if self.binarybrained_api_key:
            available_providers.append("binarybrained")
        if self.huggingface_api_token:
            available_providers.append("huggingface")
        if self.google_api_key:
            available_providers.append("gemini")
        
        # Always add ollama as fallback (local, no API key needed)
        available_providers.append("ollama")
        
        # If no API keys provided, use basic fallback order
        if not available_providers:
            available_providers = ["mistral", "binarybrained", "ollama"]
            
        self.llm_providers: List[str] = available_providers
        
        # System Settings
        self.max_concurrent_agents: int = int(os.getenv('MAX_CONCURRENT_AGENTS', '3'))
        self.default_model: str = os.getenv('DEFAULT_MODEL', "llama-3.3-70b-versatile")  # Updated to supported Groq model
        self.log_level: str = os.getenv('LOG_LEVEL', "INFO")
        # Agent Settings
        self.agent_timeout: int = int(os.getenv('AGENT_TIMEOUT', '300'))
        self.max_retries: int = int(os.getenv('MAX_RETRIES', '3'))
        
        # File Settings
        self.max_file_size_mb: int = int(os.getenv('MAX_FILE_SIZE_MB', '10'))
        self.allowed_file_types: List[str] = ['.py', '.js', '.ts', '.md', '.txt', '.json', '.yaml', '.yml']
        
        # Search Settings
        self.google_cse_id: Optional[str] = os.getenv('GOOGLE_CSE_ID')
        self.serp_api_key: Optional[str] = os.getenv('SERP_API_KEY')
    
    def _load_env_file(self):
        """Load environment variables from .env file if it exists"""
        # Check both project root and backend directory
        env_files = [Path('.env'), Path('backend/.env'), Path(__file__).parent.parent / '.env']
        env_file = None
        for ef in env_files:
            if ef.exists():
                env_file = ef
                break
        if env_file and env_file.exists():
            try:
                print(f"Loading environment from: {env_file}")
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            # Remove quotes if present
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            elif value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]
                            os.environ[key] = value
                            print(f"Loaded {key}={'*' * len(value) if 'KEY' in key or 'TOKEN' in key else value}")
            except Exception as e:
                print(f"Warning: Could not load .env file: {e}")

# Global settings instance
settings = Config()
