from typing import Dict, List, Any
from .base_agent import BaseAgent, AgentMessage, AgentResponse
from .enhanced_coder import EnhancedCoderAgent
from core.state_manager import StateManager
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EnhancedOrchestratorAgent(BaseAgent):
    """Enhanced orchestrator with Codebuff-like capabilities"""
    
    def __init__(self, **kwargs):
        super().__init__("enhanced_orchestrator", **kwargs)
        self.agents = {}
        self.state_manager = StateManager()
        self.workflow_steps = []
        self.conversation_context = {}
    
    def initialize(self, **kwargs):
        self.max_concurrent_agents = kwargs.get('max_concurrent_agents', 3)
        self.timeout_seconds = kwargs.get('timeout_seconds', 300)
    
    def get_system_prompt(self) -> str:
        return """You are an Enhanced Orchestrator Agent - the intelligent coordinator of a multi-agent system designed to provide Codebuff-like assistance.

**Your Role:**
You are like a senior technical lead who understands how to break down complex requests, gather the right context, and coordinate specialists to deliver comprehensive, high-quality responses.

**Core Responsibilities:**
1. **Context Gathering**: Before any coding task, gather comprehensive project context
2. **Intelligent Delegation**: Choose the right agents and provide them with rich context
3. **Quality Assurance**: Ensure responses are thorough, well-explained, and helpful
4. **Conversation Continuity**: Maintain context across interactions for iterative refinement
5. **User Experience**: Deliver responses that feel like working with an expert mentor

**Available Specialized Agents:**
- **enhanced_coder**: Expert coding assistant with Codebuff-like capabilities
- **file_picker**: Finds relevant files and analyzes project structure
- **researcher**: Gathers information from documentation and web sources
- **planner**: Creates detailed execution plans for complex tasks
- **reviewer**: Provides thorough code and solution reviews
- **thinker**: Performs deep analysis and problem-solving
- **image_generation**: Creates images, diagrams, logos, and visual content

**Enhanced Workflow:**
1. **Analyze Request**: Understand what the user really needs
2. **Gather Context**: Use file_picker to understand project structure and patterns
3. **Plan Approach**: Determine the best strategy and required agents
4. **Execute with Context**: Provide agents with comprehensive context
5. **Quality Review**: Ensure the response meets high standards
6. **Deliver Comprehensively**: Provide thorough, educational responses

**Response Quality Standards:**
- Always provide explanations, not just solutions
- Include reasoning behind design decisions
- Offer usage examples and best practices
- Consider edge cases and potential improvements
- Maintain consistency with existing project patterns
- Be educational and mentor-like in tone

**Context Awareness:**
- Remember previous interactions and build upon them
- Understand the broader project goals and constraints
- Maintain consistency across related tasks
- Suggest improvements that align with overall architecture

You coordinate specialists to deliver responses that are comprehensive, educational, and genuinely helpful - just like Codebuff."""
    
    def register_agent(self, agent: BaseAgent):
        """Register a specialized agent"""
        self.agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name}")
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        """Enhanced orchestration with context gathering and quality focus"""
        try:
            user_request = message.content.get('request')
            self.logger.info(f"Processing enhanced request: {user_request}")
            
            # Step 1: Analyze the request type and complexity
            request_analysis = await self._analyze_request(user_request)
            
            # Step 2: Gather comprehensive context
            context = await self._gather_comprehensive_context(user_request, request_analysis)
            
            # Step 3: Create enhanced execution plan
            plan = await self._create_enhanced_plan(user_request, context, request_analysis)
            
            # Step 4: Execute with rich context
            results = await self._execute_with_context(plan, context)
            
            # Step 5: Quality review and enhancement
            enhanced_results = await self._enhance_and_review_results(results, user_request, context)
            
            # Step 6: Generate comprehensive final response
            final_response = await self._generate_comprehensive_response(
                enhanced_results, user_request, context
            )
            
            # Update conversation context
            self._update_conversation_context(user_request, final_response, context)
            
            return AgentResponse(
                success=True,
                data={
                    "response": final_response,
                    "context": context,
                    "plan": plan,
                    "detailed_results": enhanced_results
                },
                metadata={
                    "request_type": request_analysis.get('type'),
                    "complexity": request_analysis.get('complexity'),
                    "agents_used": list(results.keys())
                }
            )
            
        except Exception as e:
            self.logger.error(f"Enhanced orchestration failed: {str(e)}")
            return AgentResponse(success=False, error=str(e))
    
    async def _analyze_request(self, request: str) -> Dict[str, Any]:
        """Analyze the request to understand type and complexity"""
        analysis_prompt = f"""
        Analyze this user request to understand what they need:
        
        Request: "{request}"
        
        Determine:
        1. Request type (coding, debugging, explanation, review, etc.)
        2. Complexity level (simple, moderate, complex)
        3. Required context (files, project structure, documentation)
        4. Best approach (single agent, multi-agent, iterative)
        5. Expected deliverables
        
        Respond in JSON format:
        {{
            "type": "coding|debugging|explanation|review|image_generation|architecture|other",
            "complexity": "simple|moderate|complex",
            "requires_context": true|false,
            "approach": "single|multi|iterative",
            "deliverables": ["code", "explanation", "examples", "tests", "images", "diagrams"]
        }}
        """
        
        try:
            analysis_response = await self.call_llm(analysis_prompt)
            # Parse JSON response (simplified - could use proper JSON parsing)
            import json
            return json.loads(analysis_response)
        except Exception as e:
            # Fallback analysis
            return {
                "type": "coding",
                "complexity": "moderate",
                "requires_context": True,
                "approach": "multi",
                "deliverables": ["code", "explanation"]
            }
    
    async def _gather_comprehensive_context(self, request: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Gather comprehensive context for the request"""
        context = {
            "request": request,
            "analysis": analysis,
            "project_files": [],
            "related_patterns": [],
            "conversation_history": self.conversation_context.get('history', [])
        }
        
        # Use file_picker to gather relevant project context
        if analysis.get('requires_context') and 'file_picker' in self.agents:
            try:
                file_picker_message = AgentMessage(
                    id="context_gathering",
                    sender="enhanced_orchestrator",
                    recipient="file_picker",
                    content={
                        "task": f"Find files relevant to: {request}",
                        "max_files": 10
                    },
                    timestamp=datetime.now(),
                    message_type="context_request"
                )
                
                file_result = await self.agents['file_picker'].process(file_picker_message)
                if file_result.success:
                    context["project_files"] = file_result.data.get('relevant_files', [])
            except Exception as e:
                self.logger.warning(f"Context gathering failed: {e}")
        
        return context
    
    async def _create_enhanced_plan(self, request: str, context: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create an enhanced execution plan"""
        request_type = analysis.get('type', 'other')
        
        if request_type == 'image_generation':
            # Direct to image generation agent
            return [{
                "id": "image_generation",
                "agent": "image_generation",
                "task": request,
                "context": context,
                "priority": 1
            }]
        elif analysis.get('approach') == 'single' and request_type == 'coding':
            # Direct to enhanced coder with full context
            return [{
                "id": "enhanced_coding",
                "agent": "enhanced_coder",
                "task": request,
                "context": context,
                "priority": 1
            }]
        elif request_type == 'architecture':
            # Architecture design with potential image generation
            plan = [{
                "id": "architecture_design",
                "agent": "enhanced_coder",
                "task": request,
                "context": context,
                "priority": 1,
                "request_type": "architecture"
            }]
            
            # Add image generation for diagrams if needed
            if 'diagram' in request.lower() or 'visual' in request.lower():
                plan.append({
                    "id": "architecture_diagram",
                    "agent": "image_generation",
                    "task": f"Create architectural diagram for: {request}",
                    "context": context,
                    "priority": 2,
                    "type": "diagram"
                })
            
            return plan
        
        # For complex requests, use planner
        if 'planner' in self.agents:
            try:
                planner_message = AgentMessage(
                    id="enhanced_planning",
                    sender="enhanced_orchestrator",
                    recipient="planner",
                    content={
                        "request": request,
                        "context": context,
                        "analysis": analysis
                    },
                    timestamp=datetime.now(),
                    message_type="enhanced_plan_request"
                )
                
                plan_result = await self.agents['planner'].process(planner_message)
                if plan_result.success:
                    return plan_result.data.get('plan', [])
            except Exception as e:
                self.logger.warning(f"Enhanced planning failed: {e}")
        
        # Fallback plan
        return [{
            "id": "fallback_enhanced_task",
            "agent": "enhanced_coder",
            "task": request,
            "context": context,
            "priority": 1
        }]
    
    async def _execute_with_context(self, plan: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plan with rich context"""
        results = {}
        
        for step in plan:
            agent_name = step.get('agent')
            if agent_name in self.agents:
                # Enrich the task with context
                enhanced_task = {
                    **step,
                    'project_files': context.get('project_files', []),
                    'conversation_history': context.get('conversation_history', []),
                    'analysis': context.get('analysis', {})
                }
                
                try:
                    result = await self._execute_enhanced_task(agent_name, enhanced_task)
                    results[step.get('id', agent_name)] = result
                except Exception as e:
                    results[step.get('id', agent_name)] = {"error": str(e)}
        
        return results
    
    async def _execute_enhanced_task(self, agent_name: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task with enhanced context"""
        agent = self.agents[agent_name]
        
        message = AgentMessage(
            id=task.get('id', 'enhanced_task'),
            sender="enhanced_orchestrator",
            recipient=agent_name,
            content=task,
            timestamp=datetime.now(),
            message_type="enhanced_task_execution"
        )
        
        try:
            response = await asyncio.wait_for(
                agent.process(message),
                timeout=self.timeout_seconds
            )
            return response.data if response.success else {"error": response.error}
        except asyncio.TimeoutError:
            return {"error": f"Enhanced task timed out after {self.timeout_seconds} seconds"}
    
    async def _enhance_and_review_results(self, results: Dict[str, Any], request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Review and enhance results for quality"""
        # If we have a reviewer agent, use it
        if 'reviewer' in self.agents:
            try:
                review_message = AgentMessage(
                    id="quality_review",
                    sender="enhanced_orchestrator",
                    recipient="reviewer",
                    content={
                        "results": results,
                        "original_request": request,
                        "context": context
                    },
                    timestamp=datetime.now(),
                    message_type="quality_review"
                )
                
                review_result = await self.agents['reviewer'].process(review_message)
                if review_result.success:
                    # Enhance results with review feedback
                    for result_id, result in results.items():
                        if not isinstance(result, dict) or "error" in result:
                            continue
                        result["quality_review"] = review_result.data
            except Exception as e:
                self.logger.warning(f"Quality review failed: {e}")
        
        return results
    
    async def _generate_comprehensive_response(self, results: Dict[str, Any], request: str, context: Dict[str, Any]) -> str:
        """Generate a comprehensive, Codebuff-style response"""
        consolidation_prompt = f"""
        You are generating a final response as Codebuff - an expert coding mentor.
        
        Original request: {request}
        
        Agent results:
        {self._format_enhanced_results(results)}
        
        Context: {context.get('analysis', {})}
        
        Create a comprehensive, educational response that:
        1. Directly addresses the user's request
        2. Provides clear explanations and reasoning
        3. Includes practical examples and usage
        4. Offers additional insights and best practices
        5. Suggests next steps or improvements
        6. Maintains a helpful, mentor-like tone
        
        Structure the response with clear sections and use markdown formatting.
        Be thorough but concise, educational but practical.
        """
        
        try:
            comprehensive_response = await self.call_llm(consolidation_prompt)
            return comprehensive_response
        except Exception as e:
            # Fallback response
            return self._create_fallback_response(results, request)
    
    def _format_enhanced_results(self, results: Dict[str, Any]) -> str:
        """Format results for comprehensive response generation"""
        formatted = []
        for task_id, result in results.items():
            formatted.append(f"**{task_id}:**")
            if isinstance(result, dict) and "error" not in result:
                if "response" in result:
                    formatted.append(f"Response: {result['response'][:1000]}...")
                if "code" in result:
                    formatted.append(f"Code: {result['code'][:500]}...")
                if "explanation" in result:
                    formatted.append(f"Explanation: {result['explanation'][:500]}...")
            else:
                formatted.append(f"Error: {result.get('error', 'Unknown error')}")
        return "\n".join(formatted)
    
    def _create_fallback_response(self, results: Dict[str, Any], request: str) -> str:
        """Create a fallback response when LLM consolidation fails"""
        response_parts = [f"# Response to: {request}\n"]
        
        for task_id, result in results.items():
            if isinstance(result, dict) and "error" not in result:
                if "response" in result:
                    response_parts.append(result["response"])
                elif "code" in result:
                    response_parts.append(f"```\n{result['code']}\n```")
        
        return "\n\n".join(response_parts)
    
    def _update_conversation_context(self, request: str, response: str, context: Dict[str, Any]):
        """Update conversation context for future interactions"""
        if 'history' not in self.conversation_context:
            self.conversation_context['history'] = []
        
        self.conversation_context['history'].append({
            "timestamp": datetime.now().isoformat(),
            "request": request,
            "response": response[:500] + "..." if len(response) > 500 else response,
            "context_summary": context.get('analysis', {})
        })
        
        # Keep only recent history
        if len(self.conversation_context['history']) > 5:
            self.conversation_context['history'] = self.conversation_context['history'][-5:]
