from typing import Dict, List, Any
from .base_agent import BaseAgent, AgentMessage, AgentResponse
from core.state_manager import StateManager
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class OrchestratorAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__("orchestrator", **kwargs)
        self.agents = {}
        self.state_manager = StateManager()
        self.workflow_steps = []
    
    def initialize(self, **kwargs):
        self.max_concurrent_agents = kwargs.get('max_concurrent_agents', 3)
        self.timeout_seconds = kwargs.get('timeout_seconds', 300)
    
    def get_system_prompt(self) -> str:
        return """You are the Orchestrator Agent, the main controller of a multi-agent AI system.

Your responsibilities:
- Coordinate workflow between specialized agents
- Break down complex user requests into manageable tasks
- Delegate tasks to appropriate agents
- Consolidate results from multiple agents
- Ensure efficient execution and error handling

Available agents and their capabilities:
- planner: Creates detailed execution plans
- researcher: Gathers information from web searches
- file_picker: Finds relevant files in codebase
- coder: Writes and modifies code
- reviewer: Reviews and validates changes
- thinker: Deep reasoning for complex problems

Always prioritize efficiency and clear communication."""
    
    def register_agent(self, agent: BaseAgent):
        """Register a specialized agent"""
        self.agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name}")
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        """Main orchestration logic"""
        try:
            user_request = message.content.get('request')
            self.logger.info(f"Processing request: {user_request}")
            
            # Step 1: Create execution plan
            plan = await self.create_plan(user_request)
            
            # Step 2: Execute plan
            results = await self.execute_plan(plan)
            
            # Step 3: Consolidate results
            final_result = await self.consolidate_results(results, user_request)
            
            return AgentResponse(
                success=True,
                data={"result": final_result, "plan": plan, "detailed_results": results},
                metadata={"execution_time": "calculated_time"}
            )
            
        except Exception as e:
            self.logger.error(f"Orchestration failed: {str(e)}")
            return AgentResponse(success=False, error=str(e))
    
    async def create_plan(self, request: str) -> List[Dict[str, Any]]:
        """Create execution plan using planner agent"""
        if 'planner' not in self.agents:
            # Fallback: create simple plan
            return [{"id": "fallback_task", "agent": "coder", "task": request, "priority": 1}]
        
        planner_message = AgentMessage(
            id="plan_request",
            sender="orchestrator",
            recipient="planner",
            content={"request": request},
            timestamp=datetime.now(),
            message_type="plan_request"
        )
        
        response = await self.agents['planner'].process(planner_message)
        if response.success:
            return response.data.get('plan', [])
        else:
            # Fallback plan
            return [{"id": "fallback_task", "agent": "coder", "task": request, "priority": 1}]
    
    async def execute_plan(self, plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute the plan by delegating to appropriate agents"""
        results = {}
        
        # Group tasks by priority for parallel execution
        priority_groups = {}
        for step in plan:
            priority = step.get('priority', 1)
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(step)
        
        # Execute by priority (lower numbers first)
        for priority in sorted(priority_groups.keys()):
            tasks = priority_groups[priority]
            
            # Execute tasks in this priority group concurrently
            concurrent_tasks = []
            for task in tasks:
                agent_name = task.get('agent')
                if agent_name in self.agents:
                    task_coroutine = self.execute_task(agent_name, task)
                    concurrent_tasks.append(task_coroutine)
            
            # Wait for all tasks in this priority to complete
            if concurrent_tasks:
                task_results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
                
                # Process results
                for i, result in enumerate(task_results):
                    task_id = tasks[i].get('id', f'task_{i}')
                    if isinstance(result, Exception):
                        results[task_id] = {"error": str(result)}
                    else:
                        results[task_id] = result
        
        return results
    
    async def execute_task(self, agent_name: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task with the specified agent"""
        agent = self.agents[agent_name]
        
        message = AgentMessage(
            id=task.get('id', 'task'),
            sender="orchestrator",
            recipient=agent_name,
            content=task,
            timestamp=datetime.now(),
            message_type="task_execution"
        )
        
        try:
            response = await asyncio.wait_for(
                agent.process(message),
                timeout=self.timeout_seconds
            )
            return response.data if response.success else {"error": response.error}
        except asyncio.TimeoutError:
            return {"error": f"Task timed out after {self.timeout_seconds} seconds"}
    
    async def consolidate_results(self, results: Dict[str, Any], original_request: str) -> str:
        """Consolidate results from multiple agents"""
        successful_results = []
        errors = []
        
        for task_id, result in results.items():
            if "error" in result:
                errors.append(f"{task_id}: {result['error']}")
            else:
                successful_results.append(result)
        
        # Use LLM to create a coherent response
        consolidation_prompt = f"""
        Original user request: {original_request}
        
        Task results:
        {self._format_results(results)}
        
        Please provide a coherent, helpful response to the user based on these results.
        If there were errors, acknowledge them but focus on what was accomplished.
        """
        
        try:
            consolidated_response = await self.call_llm(consolidation_prompt)
            return consolidated_response
        except Exception as e:
            # Fallback consolidation
            if errors:
                error_summary = "\n".join(errors)
                return f"Completed with some errors:\n{error_summary}\n\nSuccessful results: {len(successful_results)} tasks completed."
            else:
                return "All tasks completed successfully."
    
    def _format_results(self, results: Dict[str, Any]) -> str:
        """Format results for LLM consolidation"""
        formatted = []
        for task_id, result in results.items():
            formatted.append(f"Task {task_id}:")
            if "error" in result:
                formatted.append(f"  Error: {result['error']}")
            else:
                formatted.append(f"  Result: {str(result)[:500]}...")  # Truncate long results
        return "\n".join(formatted)
