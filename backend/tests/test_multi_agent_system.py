import pytest
import asyncio
from datetime import datetime

# Import agents for testing
from agents.orchestrator import OrchestratorAgent
from agents.planner import PlannerAgent
from agents.researcher import ResearcherAgent
from agents.file_picker import FilePickerAgent
from agents.coder import CoderAgent
from agents.reviewer import ReviewerAgent
from agents.thinker import ThinkerAgent
from agents.base_agent import AgentMessage

# Import tools
from tools.file_operations import ReadFilesTool, WriteFileTool, ListFilesTool
from tools.web_search import WebSearchTool
from tools.code_execution import CodeExecutionTool

@pytest.fixture
def orchestrator():
    return OrchestratorAgent()

@pytest.fixture
def planner():
    return PlannerAgent()

@pytest.fixture
def researcher():
    return ResearcherAgent()

@pytest.fixture
def file_picker():
    return FilePickerAgent()

@pytest.fixture
def coder():
    return CoderAgent()

@pytest.fixture
def reviewer():
    return ReviewerAgent()

@pytest.fixture
def thinker():
    return ThinkerAgent()

class TestAgentInitialization:
    """Test agent initialization and basic functionality"""
    
    def test_orchestrator_initialization(self, orchestrator):
        assert orchestrator.name == "orchestrator"
        assert orchestrator.agents == {}
        assert orchestrator.max_concurrent_agents == 3
    
    def test_planner_initialization(self, planner):
        assert planner.name == "planner"
        assert planner.max_steps == 10
    
    def test_researcher_initialization(self, researcher):
        assert researcher.name == "researcher"
        assert researcher.max_results == 5
        assert len(researcher.tools) > 0
    
    def test_file_picker_initialization(self, file_picker):
        assert file_picker.name == "file_picker"
        assert file_picker.max_files == 20
        assert len(file_picker.tools) > 0
    
    def test_coder_initialization(self, coder):
        assert coder.name == "coder"
        assert 'python' in coder.supported_languages
        assert len(coder.tools) > 0
    
    def test_reviewer_initialization(self, reviewer):
        assert reviewer.name == "reviewer"
        assert 'code_quality' in reviewer.review_criteria
    
    def test_thinker_initialization(self, thinker):
        assert thinker.name == "thinker"
        assert thinker.thinking_depth == 'deep'

class TestAgentRegistration:
    """Test agent registration with orchestrator"""
    
    def test_single_agent_registration(self, orchestrator, planner):
        orchestrator.register_agent(planner)
        assert "planner" in orchestrator.agents
        assert orchestrator.agents["planner"] == planner
    
    def test_multiple_agent_registration(self, orchestrator, planner, researcher, coder):
        agents = [planner, researcher, coder]
        for agent in agents:
            orchestrator.register_agent(agent)
        
        assert len(orchestrator.agents) == 3
        assert "planner" in orchestrator.agents
        assert "researcher" in orchestrator.agents
        assert "coder" in orchestrator.agents

class TestTools:
    """Test tool functionality"""
    
    @pytest.mark.asyncio
    async def test_list_files_tool(self):
        tool = ListFilesTool()
        result = await tool.execute(directory=".", pattern="*.py")
        assert result.success
        assert "files" in result.data
        assert isinstance(result.data["files"], list)
    
    @pytest.mark.asyncio
    async def test_write_and_read_files_tool(self):
        write_tool = WriteFileTool()
        read_tool = ReadFilesTool()
        
        test_content = "# Test file\nprint('Hello, World!')"
        test_file = "test_temp_file.py"
        
        # Write file
        write_result = await write_tool.execute(
            file_path=test_file,
            content=test_content
        )
        assert write_result.success
        
        # Read file
        read_result = await read_tool.execute(file_paths=[test_file])
        assert read_result.success
        assert test_file in read_result.data
        assert read_result.data[test_file] == test_content
        
        # Cleanup
        import os
        if os.path.exists(test_file):
            os.remove(test_file)
    
    @pytest.mark.asyncio
    async def test_web_search_tool(self):
        tool = WebSearchTool()
        result = await tool.execute(query="Python programming", max_results=3)
        assert result.success
        assert "results" in result.data
        assert len(result.data["results"]) <= 3
    
    @pytest.mark.asyncio
    async def test_code_execution_tool(self):
        tool = CodeExecutionTool()
        simple_code = "print('Hello from test')\nresult = 2 + 2\nprint(f'Result: {result}')"
        
        result = await tool.execute(code=simple_code, language="python")
        assert result.success
        assert "stdout" in result.data
        assert "Hello from test" in result.data["stdout"]

class TestAgentProcessing:
    """Test individual agent processing"""
    
    @pytest.mark.asyncio
    async def test_planner_creates_plan(self, planner):
        message = AgentMessage(
            id="test_plan",
            sender="test",
            recipient="planner",
            content={"request": "Create a simple Python calculator"},
            timestamp=datetime.now(),
            message_type="plan_request"
        )
        
        response = await planner.process(message)
        assert response.success
        assert "plan" in response.data
        assert isinstance(response.data["plan"], list)
        assert len(response.data["plan"]) > 0
    
    @pytest.mark.asyncio
    async def test_researcher_search(self, researcher):
        message = AgentMessage(
            id="test_research",
            sender="test",
            recipient="researcher",
            content={"query": "Python best practices"},
            timestamp=datetime.now(),
            message_type="research_request"
        )
        
        response = await researcher.process(message)
        assert response.success
        assert "summary" in response.data
        assert "raw_results" in response.data
    
    @pytest.mark.asyncio
    async def test_file_picker_find_files(self, file_picker):
        message = AgentMessage(
            id="test_file_pick",
            sender="test",
            recipient="file_picker",
            content={"query": "python files", "file_type": "python"},
            timestamp=datetime.now(),
            message_type="file_request"
        )
        
        response = await file_picker.process(message)
        assert response.success
        assert "files" in response.data
        assert "analysis" in response.data
    
    @pytest.mark.asyncio
    async def test_coder_write_code(self, coder):
        message = AgentMessage(
            id="test_code",
            sender="test",
            recipient="coder",
            content={
                "task": "Write a simple function to add two numbers",
                "language": "python"
            },
            timestamp=datetime.now(),
            message_type="code_request"
        )
        
        response = await coder.process(message)
        assert response.success
        assert "code" in response.data
        assert "is_valid" in response.data
    
    @pytest.mark.asyncio
    async def test_reviewer_review_code(self, reviewer):
        test_code = """
def add_numbers(a, b):
    return a + b

def main():
    result = add_numbers(5, 3)
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
"""
        
        message = AgentMessage(
            id="test_review",
            sender="test",
            recipient="reviewer",
            content={
                "content": test_code,
                "review_type": "code"
            },
            timestamp=datetime.now(),
            message_type="review_request"
        )
        
        response = await reviewer.process(message)
        assert response.success
        assert "review_text" in response.data
        assert "structured_review" in response.data
    
    @pytest.mark.asyncio
    async def test_thinker_deep_thinking(self, thinker):
        message = AgentMessage(
            id="test_think",
            sender="test",
            recipient="thinker",
            content={
                "problem": "How to optimize a slow database query",
                "thinking_type": "problem_solving"
            },
            timestamp=datetime.now(),
            message_type="thinking_request"
        )
        
        response = await thinker.process(message)
        assert response.success
        assert "thinking_process" in response.data
        assert "type" in response.data

class TestIntegration:
    """Integration tests for the complete system"""
    
    @pytest.mark.asyncio
    async def test_simple_workflow(self):
        """Test a simple end-to-end workflow"""
        orchestrator = OrchestratorAgent()
        planner = PlannerAgent()
        coder = CoderAgent()
        
        # Register agents
        orchestrator.register_agent(planner)
        orchestrator.register_agent(coder)
        
        # Create user request
        user_request = AgentMessage(
            id="integration_test",
            sender="user",
            recipient="orchestrator",
            content={"request": "Write a Python function to calculate factorial"},
            timestamp=datetime.now(),
            message_type="user_request"
        )
        
        # Process request
        result = await orchestrator.process(user_request)
        
        # Verify result
        assert result.success
        assert "result" in result.data
        assert "plan" in result.data
    
    @pytest.mark.asyncio
    async def test_complex_workflow(self):
        """Test a more complex workflow with multiple agents"""
        orchestrator = OrchestratorAgent()
        
        # Register multiple agents
        agents = [
            PlannerAgent(),
            ResearcherAgent(),
            FilePickerAgent(),
            CoderAgent(),
            ReviewerAgent()
        ]
        
        for agent in agents:
            orchestrator.register_agent(agent)
        
        # Create complex request
        user_request = AgentMessage(
            id="complex_test",
            sender="user",
            recipient="orchestrator",
            content={
                "request": "Research Python web scraping, find relevant files in the project, and create a simple web scraper"
            },
            timestamp=datetime.now(),
            message_type="user_request"
        )
        
        # Process request
        result = await orchestrator.process(user_request)
        
        # Verify result
        assert result.success
        assert "result" in result.data
        assert "plan" in result.data
        assert len(result.data["plan"]) > 1  # Should have multiple steps

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.mark.asyncio
    async def test_invalid_message_handling(self, planner):
        """Test handling of invalid messages"""
        message = AgentMessage(
            id="invalid_test",
            sender="test",
            recipient="planner",
            content={},  # Empty content
            timestamp=datetime.now(),
            message_type="invalid"
        )
        
        response = await planner.process(message)
        # Should handle gracefully, either with fallback or error
        assert isinstance(response.success, bool)
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test timeout handling in orchestrator"""
        orchestrator = OrchestratorAgent(timeout_seconds=1)  # Very short timeout
        
        # This test would need a mock agent that takes longer than 1 second
        # For now, just verify the timeout setting
        assert orchestrator.timeout_seconds == 1
    
    @pytest.mark.asyncio
    async def test_missing_agent_handling(self, orchestrator):
        """Test handling when required agent is not registered"""
        # Don't register any agents
        
        user_request = AgentMessage(
            id="missing_agent_test",
            sender="user",
            recipient="orchestrator",
            content={"request": "Test request"},
            timestamp=datetime.now(),
            message_type="user_request"
        )
        
        result = await orchestrator.process(user_request)
        # Should handle gracefully with fallback
        assert isinstance(result.success, bool)

# Performance tests
class TestPerformance:
    """Performance and load tests"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        orchestrator = OrchestratorAgent(max_concurrent_agents=2)
        planner = PlannerAgent()
        orchestrator.register_agent(planner)
        
        # Create multiple concurrent requests
        requests = []
        for i in range(3):
            message = AgentMessage(
                id=f"concurrent_test_{i}",
                sender="user",
                recipient="orchestrator",
                content={"request": f"Task {i}"},
                timestamp=datetime.now(),
                message_type="user_request"
            )
            requests.append(orchestrator.process(message))
        
        # Execute concurrently
        results = await asyncio.gather(*requests, return_exceptions=True)
        
        # Verify all completed (successfully or with controlled errors)
        assert len(results) == 3
        for result in results:
            assert not isinstance(result, Exception) or "timeout" in str(result).lower()

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
