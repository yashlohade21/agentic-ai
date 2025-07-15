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
        
        # Free LLM API Keys
        self.huggingface_api_token: Optional[str] = os.getenv('HUGGINGFACE_API_TOKEN')
        self.google_api_key: Optional[str] = os.getenv('GOOGLE_API_KEY')
        
        # Local LLM Settings
        self.ollama_base_url: str = os.getenv('OLLAMA_BASE_URL', "http://localhost:11434")
        self.ollama_model: str = os.getenv('OLLAMA_MODEL', "llama3.2")
        
        # LLM Provider Priority (first available will be used) - BinaryBrained prioritized
        
        self.llm_providers: List[str] = ["binarybrained", "ollama", "huggingface", "gemini"]
        
        # System Settings
        self.max_concurrent_agents: int = int(os.getenv('MAX_CONCURRENT_AGENTS', '3'))
        self.default_model: str = os.getenv('DEFAULT_MODEL', "llama3-8b-8192")  # Default to BinaryBrained model
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
        env_file = Path('.env')
        if env_file.exists():
            try:
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
            except Exception as e:
                print(f"Warning: Could not load .env file: {e}")

# Global settings instance
settings = Config()
