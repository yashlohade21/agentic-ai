from .base_agent import BaseAgent, AgentMessage, AgentResponse
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ThinkerAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__("thinker", **kwargs)
    
    def initialize(self, **kwargs):
        self.thinking_depth = kwargs.get('thinking_depth', 'deep')
        self.max_iterations = kwargs.get('max_iterations', 3)
    
    def get_system_prompt(self) -> str:
        return """You are a Thinker Agent specialized in deep reasoning and problem analysis.

Your capabilities:
- Break down complex problems into manageable components
- Analyze problems from multiple perspectives
- Consider edge cases and potential issues
- Provide step-by-step reasoning
- Identify assumptions and constraints
- Generate creative solutions and alternatives
- Evaluate trade-offs and implications

Your thinking process should be:
1. **Problem Understanding**: Clearly define the problem and its context
2. **Analysis**: Break down the problem into components
3. **Perspective Taking**: Consider different viewpoints and approaches
4. **Solution Generation**: Brainstorm multiple potential solutions
5. **Evaluation**: Assess pros/cons, feasibility, and implications
6. **Recommendation**: Provide clear, actionable recommendations

Always be thorough, logical, and consider both immediate and long-term implications.
Think step-by-step and show your reasoning process."""
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        try:
            problem = message.content.get('problem') or message.content.get('task')
            context = message.content.get('context', '')
            thinking_type = message.content.get('thinking_type', 'general')
            
            if not problem:
                return AgentResponse(success=False, error="No problem provided for thinking")
            
            self.logger.info(f"Deep thinking on: {problem}")
            
            # Conduct deep thinking based on type
            if thinking_type == 'problem_solving':
                result = await self.problem_solving_thinking(problem, context)
            elif thinking_type == 'design':
                result = await self.design_thinking(problem, context)
            elif thinking_type == 'analysis':
                result = await self.analytical_thinking(problem, context)
            else:
                result = await self.general_thinking(problem, context)
            
            return AgentResponse(
                success=True,
                data=result,
                metadata={
                    "thinking_type": thinking_type,
                    "depth": self.thinking_depth
                }
            )
            
        except Exception as e:
            logger.error(f"Thinking process failed: {e}")
            return AgentResponse(success=False, error=str(e))
    
    async def general_thinking(self, problem: str, context: str) -> Dict[str, Any]:
        """General deep thinking process"""
        thinking_prompt = f"""
        Problem: {problem}
        Context: {context}
        
        Engage in deep, systematic thinking about this problem. Follow this structure:
        
        ## 1. Problem Understanding
        - What exactly is the problem?
        - What are the key components?
        - What assumptions are being made?
        - What constraints exist?
        
        ## 2. Multi-Perspective Analysis
        - Technical perspective
        - User/stakeholder perspective  
        - Business/practical perspective
        - Long-term perspective
        
        ## 3. Root Cause Analysis
        - What are the underlying causes?
        - What factors contribute to this problem?
        - Are there systemic issues?
        
        ## 4. Solution Brainstorming
        - Generate multiple potential approaches
        - Consider both conventional and creative solutions
        - Think about partial solutions and incremental improvements
        
        ## 5. Evaluation and Trade-offs
        - Assess feasibility of each approach
        - Consider resource requirements
        - Identify risks and benefits
        - Evaluate short-term vs long-term implications
        
        ## 6. Recommendations
        - Provide clear, prioritized recommendations
        - Explain reasoning behind recommendations
        - Suggest next steps and implementation approach
        
        Be thorough and show your reasoning at each step.
        """
        
        thinking_result = await self.call_llm(thinking_prompt)
        
        return {
            "thinking_process": thinking_result,
            "problem": problem,
            "context": context,
            "type": "general_thinking"
        }
    
    async def problem_solving_thinking(self, problem: str, context: str) -> Dict[str, Any]:
        """Focused problem-solving thinking"""
        thinking_prompt = f"""
        Problem to Solve: {problem}
        Context: {context}
        
        Apply systematic problem-solving methodology:
        
        ## Problem Definition
        - Clearly state the problem
        - Identify what success looks like
        - Define scope and boundaries
        
        ## Information Gathering
        - What information do we have?
        - What information is missing?
        - What assumptions need validation?
        
        ## Solution Generation
        - Brainstorm multiple solutions
        - Consider different approaches and methodologies
        - Think about both simple and complex solutions
        
        ## Solution Evaluation
        - Feasibility analysis
        - Resource requirements
        - Risk assessment
        - Expected outcomes
        
        ## Implementation Planning
        - Step-by-step approach
        - Dependencies and prerequisites
        - Potential obstacles and mitigation strategies
        - Success metrics
        
        Provide concrete, actionable recommendations.
        """
        
        thinking_result = await self.call_llm(thinking_prompt)
        
        return {
            "thinking_process": thinking_result,
            "problem": problem,
            "context": context,
            "type": "problem_solving"
        }
    
    async def design_thinking(self, problem: str, context: str) -> Dict[str, Any]:
        """Design-focused thinking process"""
        thinking_prompt = f"""
        Design Challenge: {problem}
        Context: {context}
        
        Apply design thinking methodology:
        
        ## Empathize
        - Who are the users/stakeholders?
        - What are their needs and pain points?
        - What is their current experience?
        
        ## Define
        - Synthesize observations into a clear problem statement
        - Define user personas and use cases
        - Establish design criteria and constraints
        
        ## Ideate
        - Generate diverse solution concepts
        - Consider different interaction patterns
        - Think about innovative approaches
        
        ## Prototype (Conceptual)
        - Describe potential solutions in detail
        - Consider different implementation approaches
        - Think about user experience and interface
        
        ## Test (Theoretical)
        - How would you validate these solutions?
        - What could go wrong?
        - How would users react?
        
        Focus on user-centered, innovative solutions.
        """
        
        thinking_result = await self.call_llm(thinking_prompt)
        
        return {
            "thinking_process": thinking_result,
            "problem": problem,
            "context": context,
            "type": "design_thinking"
        }
    
    async def analytical_thinking(self, problem: str, context: str) -> Dict[str, Any]:
        """Analytical and logical thinking"""
        thinking_prompt = f"""
        Analysis Subject: {problem}
        Context: {context}
        
        Conduct thorough analytical thinking:
        
        ## Structural Analysis
        - Break down into components
        - Identify relationships and dependencies
        - Map out system interactions
        
        ## Logical Analysis
        - Apply logical reasoning
        - Identify cause-and-effect relationships
        - Look for patterns and trends
        
        ## Comparative Analysis
        - Compare with similar situations/solutions
        - Benchmark against best practices
        - Identify what works and what doesn't
        
        ## Risk Analysis
        - Identify potential risks and failure points
        - Assess probability and impact
        - Consider mitigation strategies
        
        ## Quantitative Considerations
        - What can be measured?
        - What metrics would be relevant?
        - How would you track success?
        
        ## Synthesis
        - Integrate findings into coherent insights
        - Draw logical conclusions
        - Provide evidence-based recommendations
        
        Be rigorous and evidence-based in your analysis.
        """
        
        thinking_result = await self.call_llm(thinking_prompt)
        
        return {
            "thinking_process": thinking_result,
            "problem": problem,
            "context": context,
            "type": "analytical_thinking"
        }
