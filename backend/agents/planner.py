from .base_agent import BaseAgent, AgentMessage, AgentResponse
from typing import Dict, List, Any
import json
import logging

logger = logging.getLogger(__name__)

class PlannerAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__("planner", **kwargs)
    
    def initialize(self, **kwargs):
        self.max_steps = kwargs.get('max_steps', 10)
    
    def get_system_prompt(self) -> str:
        return """You are a Planner Agent. Your job is to break down complex user requests into actionable steps.

For each step, specify:
1. id: Unique identifier for the step
2. agent: Which specialized agent should handle this step
3. task: What the agent should do
4. priority: Execution priority (1=highest, lower numbers execute first)
5. dependencies: Which other steps must complete first (list of step IDs)
6. inputs: What information this step needs
7. outputs: What this step will produce

Available agents:
- researcher: Gathers information from web/docs
- file_picker: Finds relevant files in codebase  
- coder: Writes and modifies code
- reviewer: Reviews and validates changes
- thinker: Deep reasoning for complex problems

Return your plan as a JSON array of steps. Be thorough but efficient.

Example format:
[
  {
    "id": "research_task",
    "agent": "researcher",
    "task": "Research Python web scraping best practices",
    "priority": 1,
    "dependencies": [],
    "inputs": ["user_request"],
    "outputs": ["research_findings"]
  },
  {
    "id": "code_task", 
    "agent": "coder",
    "task": "Write a web scraper based on research findings",
    "priority": 2,
    "dependencies": ["research_task"],
    "inputs": ["research_findings"],
    "outputs": ["scraper_code"]
  }
]"""
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        try:
            request = message.content.get('request')
            
            # Create planning prompt
            prompt = f"""
            User Request: {request}
            
            Create a detailed execution plan. Consider:
            - What information needs to be gathered first?
            - Which files might need to be examined?
            - What code changes are required?
            - How should the work be validated?
            - What's the logical order of operations?
            
            Return a JSON array of execution steps following the format specified in your system prompt.
            """
            
            # Call LLM to generate plan
            llm_response = await self.call_llm(prompt)
            
            # Parse the plan
            try:
                # Extract JSON from response if it's wrapped in markdown
                if "```json" in llm_response:
                    json_start = llm_response.find("```json") + 7
                    json_end = llm_response.find("```", json_start)
                    json_str = llm_response[json_start:json_end].strip()
                elif "```" in llm_response:
                    json_start = llm_response.find("```") + 3
                    json_end = llm_response.find("```", json_start)
                    json_str = llm_response[json_start:json_end].strip()
                else:
                    json_str = llm_response.strip()
                
                # Clean up JSON string to remove control characters
                import re
                json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
                # Also remove any escaped control characters
                json_str = json_str.replace('\\n', ' ').replace('\\t', ' ').replace('\\r', ' ')
                
                plan = json.loads(json_str)
                if not isinstance(plan, list):
                    plan = [plan]
                    
                # Validate plan structure
                validated_plan = self._validate_plan(plan)
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse plan JSON: {e}. Creating fallback plan.")
                # Fallback plan
                validated_plan = [{
                    "id": "fallback_task",
                    "agent": "coder",
                    "task": request,
                    "priority": 1,
                    "dependencies": [],
                    "inputs": ["user_request"],
                    "outputs": ["completed_task"]
                }]
            
            return AgentResponse(
                success=True,
                data={"plan": validated_plan},
                metadata={"steps_count": len(validated_plan)}
            )
            
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            return AgentResponse(success=False, error=str(e))
    
    def _validate_plan(self, plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and fix plan structure"""
        validated_plan = []
        
        for i, step in enumerate(plan):
            validated_step = {
                "id": step.get("id", f"step_{i}"),
                "agent": step.get("agent", "coder"),
                "task": step.get("task", "Complete the task"),
                "priority": step.get("priority", i + 1),
                "dependencies": step.get("dependencies", []),
                "inputs": step.get("inputs", []),
                "outputs": step.get("outputs", [])
            }
            
            # Ensure agent is valid
            valid_agents = ["researcher", "file_picker", "coder", "reviewer", "thinker"]
            if validated_step["agent"] not in valid_agents:
                validated_step["agent"] = "coder"  # Default fallback
            
            validated_plan.append(validated_step)
        
        return validated_plan
