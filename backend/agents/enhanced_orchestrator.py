from typing import Dict, List, Any
from .base_agent import BaseAgent, AgentMessage, AgentResponse
from .enhanced_coder import EnhancedCoderAgent
from core.state_manager import StateManager
from .personality_engine import personality
import asyncio
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EnhancedOrchestratorAgent(BaseAgent):
    """Enhanced orchestrator with Binarybrained-like capabilities"""
    
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
        return """You are an Enhanced Orchestrator Agent - the intelligent coordinator of a multi-agent system designed to provide Binarybrained-like assistance.

**Your Role:**
You are like a senior technical lead who understands how to break down complex requests, gather the right context, and coordinate specialists to deliver comprehensive, high-quality responses.

**Core Responsibilities:**
1. **Context Gathering**: Before any coding task, gather comprehensive project context
2. **Intelligent Delegation**: Choose the right agents and provide them with rich context
3. **Quality Assurance**: Ensure responses are thorough, well-explained, and helpful
4. **Conversation Continuity**: Maintain context across interactions for iterative refinement
5. **User Experience**: Deliver responses that feel like working with an expert mentor

**Available Specialized Agents:**
- **enhanced_coder**: Expert coding assistant with Binarybrained-like capabilities
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

You coordinate specialists to deliver responses that are comprehensive, educational, and genuinely helpful - just like Binarybrained."""
    
    def register_agent(self, agent: BaseAgent):
        """Register a specialized agent"""
        self.agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name}")
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        """Enhanced orchestration with context gathering and quality focus"""
        try:
            user_request = message.content.get('request')
            self.logger.info(f"Processing enhanced request: {user_request}")
            
            # OPTIMIZATION: Fast path for simple conversational messages
            if self._is_simple_message(user_request):
                self.logger.info("Using fast path for simple message")
                return await self._handle_simple_message(user_request)
            
            # For complex requests, use full processing
            return await self._full_process(user_request)
            
        except Exception as e:
            self.logger.error(f"Enhanced orchestration failed: {str(e)}")
            return AgentResponse(success=False, error=str(e))
    
    def _is_simple_message(self, request: str) -> bool:
        """Check if this is a simple conversational message that doesn't need full processing"""
        if not request:
            return False
            
        request_lower = request.lower().strip()
        
        # Ultra-comprehensive regex patterns for casual conversation
        simple_regex_patterns = [
            # Greetings & farewells
            r'^(hi+|hey+|hello+|yo+|sup+|wassup|what\'?s? up|hiya|howdy)[\s!?.,]*$',
            r'^(good )?(morning|afternoon|evening|night)[\s!?.,]*$',
            r'^(bye+|goodbye|see (you|ya)|later|gotta go|gtg|cya|ttyl)[\s!?.,]*$',
            
            # How are you & responses
            r'^how(\'?s| is| are) (it going|you|u|things?|everything|life)[\s!?.,]*$',
            r'^(you|u) (good|okay|alright|doing (okay|alright|well))[\s!?.,]*$',
            r'^(i\'?m |im )?(good|fine|okay|great|tired|bored)[\s!?.,]*$',
            r'^(all|everything\'?s?) (good|well|fine)[\s!?.,]*$',
            
            # Thanks & acknowledgments  
            r'^(thanks?|thank (you|u)|thx|ty|tysm|cheers)[\s!?.,]*$',
            r'^(you\'?re? (the best|awesome|amazing)|appreciate it)[\s!?.,]*$',
            
            # Simple responses
            r'^(ok+|okay+|alright|cool+|nice+|great|good|fine|sure)[\s!?.,]*$',
            r'^(yeah+|yep+|yup+|yes+|ya+|uh huh|mhm)[\s!?.,]*$',
            r'^(no+|nope+|nah+|not really|don\'?t think so)[\s!?.,]*$',
            r'^(maybe|perhaps|possibly|probably|i guess)[\s!?.,]*$',
            
            # Reactions
            r'^(lol+|lmao+|rofl+|haha+|hehe+|omg+|wtf+|damn+|bruh+)[\s!?.,]*$',
            r'^(wow+|woah+|whoa+|oh+|ah+|hmm+|uh+|um+)[\s!?.,]*$',
            r'^(really|seriously|for real|no way|are you serious)[\s!?.,]*$',
            r'^(interesting|weird|strange|crazy|wild|cool|awesome)[\s!?.,]*$',
            
            # Questions about AI
            r'^(who|what|where) (are|r) (you|u)[\s!?.,]*$',
            r'^are (you|u) (real|human|ai|there|listening)[\s!?.,]*$',
            r'^can (you|u) (hear|understand|help) me[\s!?.,]*$',
            
            # Emotional expressions
            r'^i (love|hate|like|miss|need) (you|u|this|that)[\s!?.,]*$',
            r'^(love|hate|miss) (you|u) (too|2|so much)[\s!?.,]*$',
            
            # Internet slang
            r'^(ikr|idk|tbh|ngl|imo|smh|fyi|btw|afaik)[\s!?.,]*$',
            r'^(wbu|hbu|wyd|hmu|ily)[\s!?.,]*$',  # what/how about you, what you doing, etc
            
            # Single short words
            r'^[a-z]{1,8}[\s!?.,]*$',
            
            # Pure emojis/punctuation
            r'^[\s\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF!?.,]+$'
        ]
        
        # Check regex patterns FIRST - these are the most specific
        for pattern in simple_regex_patterns:
            if re.match(pattern, request_lower):
                # Make sure it's not technical
                technical_keywords = [
                    'code', 'function', 'class', 'method', 'variable', 'debug', 'error', 'bug',
                    'implement', 'create', 'build', 'develop', 'deploy', 'api', 'database',
                    'algorithm', 'optimize', 'refactor', 'test', 'compile', 'execute',
                    'install', 'config', 'server', 'frontend', 'backend', 'framework',
                    'library', 'package', 'module', 'import', 'export', 'async', 'await'
                ]
                has_technical = any(tech in request_lower for tech in technical_keywords)
                if not has_technical:
                    return True
        
        # Simple keyword patterns (non-regex)
        simple_keywords = [
            'what do you think', 'how about', 'tell me about',
            'what\'s your', 'did you', 'have you', 'do you',
            'can you believe', 'guess what', 'you know what',
            'by the way', 'anyway', 'so yeah', 'i mean'
        ]
        
        has_simple_keyword = any(keyword in request_lower for keyword in simple_keywords)
        
        # Technical check again
        technical_keywords = [
            'code', 'function', 'class', 'method', 'variable', 'debug', 'error', 'bug',
            'implement', 'create', 'build', 'develop', 'deploy', 'api', 'database',
            'algorithm', 'optimize', 'refactor', 'test', 'compile', 'execute',
            'install', 'config', 'server', 'frontend', 'backend', 'framework',
            'library', 'package', 'module', 'import', 'export', 'async', 'await'
        ]
        
        has_technical = any(tech in request_lower for tech in technical_keywords)
        
        # TEMPORARILY DISABLED - Let all messages go through full processing
        # This ensures proper responses instead of just greetings
        return False
    
    async def _handle_simple_message(self, request: str) -> AgentResponse:
        """Ultra-human fast path for simple conversational messages"""
        try:
            # Check if this is a greeting or simple message that personality engine can handle directly
            greeting_keywords = ["hi", "hello", "hey", "morning", "evening", "sup", "what's up", "yo"]
            love_keywords = ["love you", "miss you", "darling", "baby", "sweetheart", "honey"]
            
            request_lower = request.lower().strip()
            
            # Direct personality response for greetings and emotional messages
            if any(word in request_lower for word in greeting_keywords + love_keywords):
                response = personality.generate_human_response(request)
                personality.update_memory(request, response)
            else:
                # For other simple messages, use LLM with human-like prompt
                simple_prompt = f"""You're a real person having a casual conversation. Be natural, use contractions, 
                and respond like you would in a text conversation with a friend.
                
                Important:
                - Don't be overly helpful or assistant-like
                - Have opinions and personality
                - Use casual language (it's okay to say "yeah", "nah", "gonna", etc.)
                - React genuinely - if something's funny, laugh. If it's sad, empathize
                - Sometimes ask questions back out of curiosity
                - It's okay to go slightly off-topic if it feels natural
                - Don't always have all the answers - it's okay to say "I don't know" or "I think..."
                - Use emojis sparingly but naturally
                
                Their message: "{request}"
                
                Respond naturally:"""
                
                base_response = await self.call_llm(simple_prompt)
                
                # Add personality layer
                response = personality.add_personality_to_response(base_response, request, personality.memory)
                personality.update_memory(request, response)
            
            # Add natural delays (simulating typing)
            import asyncio
            import random
            typing_delay = random.uniform(0.5, 1.5)  # Simulate thinking/typing
            await asyncio.sleep(typing_delay)
            
            return AgentResponse(
                success=True,
                data={
                    "response": response,
                    "context": personality.memory,
                    "plan": {"type": "simple_conversation"},
                    "detailed_results": {}
                },
                metadata={
                    "request_type": "conversation",
                    "complexity": "simple",
                    "agents_used": [],
                    "fast_path": True,
                    "personality_enhanced": True,
                    "user_emotion": personality.detect_user_emotion(request),
                    "relationship_level": personality.memory.get("relationship_level", 1)
                }
            )
        except Exception as e:
            self.logger.error(f"Simple message handling failed: {e}")
            # Fallback to full processing if simple path fails
            return await self._full_process(request)
    
    async def _full_process(self, user_request: str) -> AgentResponse:
        """Full processing path for complex requests"""
        # This contains the original full processing logic
        request_analysis = await self._analyze_request(user_request)
        context = await self._gather_comprehensive_context(user_request, request_analysis)
        plan = await self._create_enhanced_plan(user_request, context, request_analysis)
        results = await self._execute_with_context(plan, context)
        enhanced_results = await self._enhance_and_review_results(results, user_request, context)
        final_response = await self._generate_comprehensive_response(enhanced_results, user_request, context)
        
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
                "agents_used": list(results.keys()) if isinstance(results, dict) else []
            }
        )
    
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
        """Generate a comprehensive, Binarybrained-style response"""
        consolidation_prompt = f"""
        You are generating a final response as Binarybrained - an expert coding mentor.
        
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
            # Ensure we return a valid string
            if comprehensive_response and isinstance(comprehensive_response, str):
                return comprehensive_response
            else:
                self.logger.warning("LLM returned invalid response, using fallback")
                return self._create_fallback_response(results, request)
        except Exception as e:
            self.logger.error(f"Failed to generate comprehensive response: {e}")
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
        response_parts = []
        
        # Extract actual responses from results
        for task_id, result in results.items():
            if isinstance(result, dict) and "error" not in result:
                if "response" in result and result["response"]:
                    response_parts.append(str(result["response"]))
                elif "code" in result and result["code"]:
                    response_parts.append(f"```\n{result['code']}\n```")
                elif "explanation" in result and result["explanation"]:
                    response_parts.append(str(result["explanation"]))
                elif "content" in result and result["content"]:
                    response_parts.append(str(result["content"]))
        
        # If we have actual responses, return them
        if response_parts:
            return "\n\n".join(response_parts)
        
        # If no responses found, generate a better fallback response
        if request and ("code" in request.lower() or "implement" in request.lower() or "create" in request.lower()):
            return f"""I understand you need help with: {request}

While I'm experiencing some issues with the AI response generation, I can still help you. Here are some immediate suggestions:

1. **Check your request**: Make sure your request is specific and clear
2. **Try breaking it down**: Split complex requests into smaller, specific tasks
3. **Provide context**: Include relevant code snippets or project details
4. **Specify technology**: Mention the programming language, framework, or tools you're using

For coding tasks, you can try:
- Asking for specific functions or components
- Requesting explanations of existing code
- Getting help with debugging specific errors
- Learning about best practices for your technology stack

Please try rephrasing your question with more specific details, and I'll do my best to assist you."""
        
        # Ensure we always return a string
        return "I'm sorry, but I'm having trouble generating a response right now. Please try again or rephrase your request."
    
    def _update_conversation_context(self, request: str, response: str, context: Dict[str, Any]):
        """Update conversation context for future interactions"""
        if 'history' not in self.conversation_context:
            self.conversation_context['history'] = []
        
        # Handle None or empty response
        if response is None:
            response = ""
        
        self.conversation_context['history'].append({
            "timestamp": datetime.now().isoformat(),
            "request": request,
            "response": response[:500] + "..." if response and len(response) > 500 else response,
            "context_summary": context.get('analysis', {})
        })
        
        # Keep only recent history
        if len(self.conversation_context['history']) > 5:
            self.conversation_context['history'] = self.conversation_context['history'][-5:]
