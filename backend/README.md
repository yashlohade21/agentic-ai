# Multi-Agent AI System

A sophisticated multi-agent AI system that coordinates specialized agents to handle complex tasks through intelligent orchestration.

## 🌟 Features

- **Modular Architecture**: Specialized agents for different tasks
- **Intelligent Orchestration**: Automatic task planning and delegation
- **Multiple LLM Support**: Works with Claude, GPT, Llama, and more
- **Rich Tool Integration**: File operations, web search, code execution
- **Async Processing**: High-performance concurrent execution
- **Comprehensive Testing**: Full test suite with pytest
- **Easy Configuration**: Environment-based configuration

## 🏗️ Architecture

```
User Request → Orchestrator → [Specialized Agents] → Results → User
                    ↓
              Shared State/Memory
                    ↓
              Tools & External APIs
```

### Specialized Agents

- **🎯 Orchestrator**: Main controller that manages workflow
- **📋 Planner**: Breaks down complex tasks into steps
- **🔍 Researcher**: Gathers information from web/docs
- **📁 File Picker**: Finds relevant files in codebase
- **💻 Coder**: Writes and modifies code
- **👀 Reviewer**: Reviews and validates changes
- **🧠 Thinker**: Deep reasoning for complex problems

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd multi-agent-system

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 2. Basic Usage

```bash
# Interactive mode
python multi_agent_main.py

# Single request
python multi_agent_main.py --request "Write a Python function to sort a list"

# Batch processing
python multi_agent_main.py --batch examples/example_requests.txt
```

### 3. Python API

```python
import asyncio
from multi_agent_main import MultiAgentSystem

async def main():
    system = MultiAgentSystem()
    result = await system.process_request("Create a web scraper")
    print(result['data']['result'])

asyncio.run(main())
```

## 📁 Project Structure

```
multi-agent-system/
├── agents/                 # Specialized AI agents
│   ├── __init__.py
│   ├── base_agent.py      # Base agent class
│   ├── orchestrator.py    # Main orchestrator
│   ├── planner.py         # Task planning
│   ├── researcher.py      # Web research
│   ├── file_picker.py     # File discovery
│   ├── coder.py           # Code generation
│   ├── reviewer.py        # Code/content review
│   └── thinker.py         # Deep reasoning
├── tools/                  # Agent tools and utilities
│   ├── __init__.py
│   ├── base_tool.py       # Base tool class
│   ├── file_operations.py # File I/O tools
│   ├── web_search.py      # Web search tool
│   ├── code_execution.py  # Code execution
│   └── terminal.py        # Terminal commands
├── core/                   # Core system components
│   ├── __init__.py
│   ├── state_manager.py   # State management
│   └── config.py          # Configuration
├── tests/                  # Test suite
│   ├── __init__.py
│   └── test_multi_agent_system.py
├── examples/               # Usage examples
│   ├── simple_usage.py
│   └── example_requests.txt
├── multi_agent_main.py     # Main application
├── requirements.txt        # Dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with your API keys:

```env
# Required: At least one LLM API key
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key

# Optional: Web search
GOOGLE_API_KEY=your_google_key
GOOGLE_CSE_ID=your_cse_id

# System settings
MAX_CONCURRENT_AGENTS=3
DEFAULT_MODEL=claude-3-5-sonnet-20241022
LOG_LEVEL=INFO
```

### Supported Models

- **Anthropic Claude**: claude-3-5-sonnet-20241022, claude-3-haiku-20240307
- **OpenAI GPT**: gpt-4, gpt-4-turbo, gpt-3.5-turbo
- **Groq**: llama3-70b-8192, llama3-8b-8192
- **Local Ollama**: llama3.1:8b, llama3.1:70b

## 🛠️ Usage Examples

### Interactive Mode

```bash
python multi_agent_main.py
```

```
🤖 Multi-Agent AI System
==================================================
🔵 You: Write a Python function to calculate prime numbers

⚙️ Processing...

✅ Result:
Here's a Python function to calculate prime numbers:

```python
def is_prime(n):
    """Check if a number is prime."""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def generate_primes(limit):
    """Generate prime numbers up to a limit."""
    primes = []
    for num in range(2, limit + 1):
        if is_prime(num):
            primes.append(num)
    return primes
```

📋 Execution Plan:
  1. [planner] Create execution plan for prime number function (Priority: 1)
  2. [coder] Write Python function for prime number calculation (Priority: 2)
  3. [reviewer] Review the generated code for quality (Priority: 3)
```

### Programmatic Usage

```python
import asyncio
from multi_agent_main import MultiAgentSystem

async def example():
    system = MultiAgentSystem()
    
    # Research task
    result = await system.process_request(
        "Research the latest Python web frameworks and their pros/cons"
    )
    
    if result['success']:
        print("Research Results:")
        print(result['data']['result'])
    
    # Coding task
    result = await system.process_request(
        "Create a REST API endpoint for user authentication"
    )
    
    if result['success']:
        print("Generated Code:")
        print(result['data']['result'])

asyncio.run(example())
```

### Batch Processing

Create a file with requests:

```txt
# requests.txt
Write a function to merge two sorted arrays
Research machine learning model deployment strategies
Find all configuration files in this project
Create a data validation class
```

Run batch processing:

```bash
python multi_agent_main.py --batch requests.txt
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_multi_agent_system.py::TestAgentInitialization -v
pytest tests/test_multi_agent_system.py::TestIntegration -v

# Run with coverage
pip install pytest-cov
pytest tests/ --cov=agents --cov=tools --cov=core
```

## 🔧 Advanced Usage

### Custom Agents

Create your own specialized agent:

```python
from agents.base_agent import BaseAgent, AgentMessage, AgentResponse

class CustomAgent(BaseAgent):
    def initialize(self, **kwargs):
        # Initialize your agent
        pass
    
    def get_system_prompt(self) -> str:
        return "You are a custom specialized agent..."
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        # Process the message
        result = await self.call_llm("Your prompt here")
        
        return AgentResponse(
            success=True,
            data={"result": result}
        )

# Register with orchestrator
system = MultiAgentSystem()
system.orchestrator.register_agent(CustomAgent())
```

### Custom Tools

Create custom tools for your agents:

```python
from tools.base_tool import BaseTool, ToolResult

class CustomTool(BaseTool):
    def __init__(self):
        super().__init__("custom_tool", "Description of what it does")
    
    async def execute(self, **kwargs) -> ToolResult:
        # Your tool logic here
        return ToolResult(success=True, data={"result": "Tool output"})
    
    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "Parameter description"}
            },
            "required": ["param1"]
        }

# Add to agent
agent.add_tool(CustomTool())
```

## 📊 Monitoring and Logging

The system includes comprehensive logging:

```python
import logging

# Configure logging level
logging.basicConfig(level=logging.INFO)

# Logs are written to:
# - Console output
# - multi_agent_system.log file
```

Monitor agent performance:

```bash
# View real-time logs
tail -f multi_agent_system.log

# Filter by agent
grep "agent.coder" multi_agent_system.log
```

## 🚀 Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "multi_agent_main.py"]
```

### Production Considerations

1. **API Rate Limits**: Configure appropriate delays and retries
2. **Resource Management**: Monitor memory and CPU usage
3. **Error Handling**: Implement comprehensive error recovery
4. **Security**: Validate all inputs and sanitize outputs
5. **Scaling**: Use async processing and connection pooling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure you're in the project directory
cd multi-agent-system
python -c "import agents; print('Success')"
```

**API Key Issues**
```bash
# Check environment variables
python -c "import os; print('ANTHROPIC_API_KEY' in os.environ)"
```

**Module Not Found**
```bash
# Install dependencies
pip install -r requirements.txt
```

**Performance Issues**
- Reduce `MAX_CONCURRENT_AGENTS` in .env
- Use smaller/faster models
- Implement caching for repeated requests

### Getting Help

1. Check the logs in `multi_agent_system.log`
2. Run tests to verify system integrity
3. Review configuration in `.env`
4. Check API key validity and quotas

## 🔮 Future Enhancements

- [ ] Web UI interface
- [ ] Plugin system for custom agents
- [ ] Distributed processing support
- [ ] Advanced workflow visualization
- [ ] Integration with more LLM providers
- [ ] Real-time collaboration features
- [ ] Advanced state persistence
- [ ] Performance analytics dashboard

---

**Built with ❤️ for the AI community**
