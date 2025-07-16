import unittest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.llm_manager import MistralProvider, LLMManager
from core.config import Config
from agents.enhanced_coder import EnhancedCoderAgent
from agents.image_agent import ImageGenerationAgent
from agents.base_agent import AgentMessage
from tools.image_generation import ImageGenerationTool
from datetime import datetime

class TestMistralProvider(unittest.TestCase):
    """Test cases for MistralProvider"""
    
    def setUp(self):
        self.api_key = "test_api_key"
        self.provider = MistralProvider(api_key=self.api_key)
    
    def test_provider_initialization(self):
        """Test MistralProvider initialization"""
        self.assertEqual(self.provider.name, "mistral")
        self.assertEqual(self.provider.api_key, self.api_key)
        self.assertEqual(self.provider.model_name, "mistral-large-latest")
        self.assertTrue(self.provider.available)
    
    def test_provider_initialization_without_api_key(self):
        """Test MistralProvider initialization without API key"""
        provider = MistralProvider()
        self.assertFalse(provider.available)
    
    @patch('requests.post')
    async def test_generate_success(self, mock_post):
        """Test successful generation with MistralProvider"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Generated response'}}]
        }
        mock_post.return_value = mock_response
        
        result = await self.provider.generate("Test prompt", "System prompt")
        
        self.assertEqual(result, "Generated response")
        self.assertEqual(self.provider.error_count, 0)
    
    @patch('requests.post')
    async def test_generate_api_error(self, mock_post):
        """Test API error handling"""
        # Mock API error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        with self.assertRaises(Exception) as context:
            await self.provider.generate("Test prompt")
        
        self.assertIn("Mistral generation failed", str(context.exception))
        self.assertEqual(self.provider.error_count, 1)

class TestLLMManagerWithMistral(unittest.TestCase):
    """Test LLMManager with Mistral integration"""
    
    def setUp(self):
        self.mistral_provider = MistralProvider(api_key="test_key")
        self.llm_manager = LLMManager([self.mistral_provider])
    
    def test_mistral_provider_added(self):
        """Test that Mistral provider is properly added to LLMManager"""
        providers = self.llm_manager.get_available_providers()
        self.assertEqual(len(providers), 1)
        self.assertEqual(providers[0].name, "mistral")
    
    @patch.object(MistralProvider, 'generate')
    async def test_llm_manager_uses_mistral(self, mock_generate):
        """Test that LLMManager uses Mistral provider"""
        mock_generate.return_value = "Mistral response"
        
        result = await self.llm_manager.generate("Test prompt")
        
        self.assertEqual(result, "Mistral response")
        mock_generate.assert_called_once_with("Test prompt", None)

class TestEnhancedCoderWithMistral(unittest.TestCase):
    """Test EnhancedCoderAgent with Mistral integration"""
    
    def setUp(self):
        self.agent = EnhancedCoderAgent()
    
    @patch.object(EnhancedCoderAgent, 'call_llm')
    async def test_architecture_suggestion(self, mock_call_llm):
        """Test architecture suggestion functionality"""
        mock_call_llm.return_value = "Architecture design response"
        
        context = {
            'language': 'python',
            'conversation_history': '',
            'existing_code': '',
            'project_files': {}
        }
        
        result = await self.agent.generate_architecture_suggestion("Design a web application", context)
        
        self.assertEqual(result['type'], 'architecture_suggestion')
        self.assertEqual(result['architecture_design'], 'Architecture design response')
        self.assertTrue(result['context_used'])
    
    @patch.object(EnhancedCoderAgent, 'call_llm')
    async def test_advanced_code_suggestions(self, mock_call_llm):
        """Test advanced code suggestions functionality"""
        mock_call_llm.return_value = "```python\nprint('Hello World')\n```\nAdvanced code suggestions"
        
        context = {
            'language': 'python',
            'conversation_history': '',
            'existing_code': '',
            'project_files': {}
        }
        
        result = await self.agent.generate_advanced_code_suggestions("Suggest improvements", context)
        
        self.assertEqual(result['type'], 'advanced_code_suggestion')
        self.assertIn('advanced_suggestions', result)
        self.assertTrue(result['context_used'])
    
    async def test_process_with_architecture_request(self):
        """Test processing architecture requests"""
        message = AgentMessage(
            id="test",
            sender="test",
            recipient="enhanced_coder",
            content={
                "task": "Design the architecture for a microservices system",
                "request_type": "architecture"
            },
            timestamp=datetime.now(),
            message_type="test"
        )
        
        with patch.object(self.agent, 'generate_architecture_suggestion') as mock_arch:
            mock_arch.return_value = {"type": "architecture_suggestion", "architecture_design": "Test design"}
            
            response = await self.agent.process(message)
            
            self.assertTrue(response.success)
            mock_arch.assert_called_once()

class TestImageGenerationTool(unittest.TestCase):
    """Test ImageGenerationTool"""
    
    def setUp(self):
        self.tool = ImageGenerationTool()
    
    def test_tool_initialization(self):
        """Test ImageGenerationTool initialization"""
        self.assertEqual(self.tool.name, "image_generation")
        self.assertIsInstance(self.tool.available_providers, list)
    
    def test_provider_selection(self):
        """Test provider selection logic"""
        # Test auto selection
        provider = self.tool._select_provider("auto")
        self.assertIn(provider, ["openai", "mistral", "placeholder"])
        
        # Test specific provider selection
        if "openai" in self.tool.available_providers:
            provider = self.tool._select_provider("openai")
            self.assertEqual(provider, "openai")
    
    async def test_placeholder_generation(self):
        """Test placeholder image generation"""
        result = await self.tool._generate_placeholder(
            "Test prompt", "realistic", "1024x1024", "/tmp/test.png"
        )
        
        self.assertTrue(result['placeholder'])
        self.assertIn('description', result)
        self.assertEqual(result['provider'], 'placeholder')

class TestImageGenerationAgent(unittest.TestCase):
    """Test ImageGenerationAgent"""
    
    def setUp(self):
        self.agent = ImageGenerationAgent()
    
    def test_agent_initialization(self):
        """Test ImageGenerationAgent initialization"""
        self.assertEqual(self.agent.name, "image_generation")
        self.assertIsNotNone(self.agent.image_tool)
        self.assertIn('logo', self.agent.supported_types)
        self.assertIn('diagram', self.agent.supported_types)
    
    @patch.object(ImageGenerationAgent, 'call_llm')
    async def test_analyze_image_request(self, mock_call_llm):
        """Test image request analysis"""
        mock_call_llm.return_value = """
        **Image Type**: logo
        **Primary Purpose**: branding
        **Target Audience**: business
        **Recommended Style**: professional
        """
        
        analysis = await self.agent._analyze_image_request("Create a logo for my company", "logo")
        
        self.assertEqual(analysis['image_type'], 'logo')
        self.assertEqual(analysis['purpose'], 'branding')
        self.assertEqual(analysis['audience'], 'business')
    
    def test_extract_company_name(self):
        """Test company name extraction"""
        # Test various prompt formats
        self.assertEqual(self.agent._extract_company_name("Create a logo for TechCorp"), "TechCorp")
        self.assertEqual(self.agent._extract_company_name("Logo for my startup InnovateLab"), "InnovateLab")
        self.assertEqual(self.agent._extract_company_name("Design company branding"), "company")

class TestConfigWithMistral(unittest.TestCase):
    """Test configuration with Mistral API key"""
    
    def test_mistral_api_key_in_config(self):
        """Test that Mistral API key is properly configured"""
        config = Config()
        
        # Test that mistral_api_key attribute exists
        self.assertTrue(hasattr(config, 'mistral_api_key'))
        
        # Test that mistral is in llm_providers list
        self.assertIn('mistral', config.llm_providers)
        
        # Test provider priority (mistral should be second after binarybrained)
        self.assertEqual(config.llm_providers[1], 'mistral')

class TestIntegrationCompatibility(unittest.TestCase):
    """Test compatibility with existing BINARYBRAINED functionality"""
    
    @patch.dict(os.environ, {'BINARYBRAINED_API_KEY': 'test_binary_key', 'MISTRAL_API_KEY': 'test_mistral_key'})
    def test_both_providers_available(self):
        """Test that both BinaryBrained and Mistral providers can coexist"""
        from core.config import Config
        from agents.base_agent import BaseAgent
        
        # Create a test agent to check provider initialization
        class TestAgent(BaseAgent):
            def initialize(self, **kwargs):
                pass
            
            async def process(self, message):
                pass
        
        agent = TestAgent("test_agent")
        
        # Check that both providers are available
        available_providers = agent.llm.get_available_providers()
        provider_names = [p.name for p in available_providers]
        
        # Should have both binarybrained and mistral (if keys are set)
        self.assertIn('binarybrained', provider_names)
        self.assertIn('mistral', provider_names)

def run_async_test(coro):
    """Helper function to run async tests"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

if __name__ == '__main__':
    # Run async tests
    async_test_cases = [
        TestMistralProvider,
        TestLLMManagerWithMistral,
        TestEnhancedCoderWithMistral,
        TestImageGenerationTool,
        TestImageGenerationAgent
    ]
    
    for test_case in async_test_cases:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
        for test in suite:
            if hasattr(test, '_testMethodName') and 'async' in test._testMethodName:
                # Convert async test to sync
                original_method = getattr(test, test._testMethodName)
                if asyncio.iscoroutinefunction(original_method):
                    setattr(test, test._testMethodName, lambda self, method=original_method: run_async_test(method(self)))
    
    unittest.main()

