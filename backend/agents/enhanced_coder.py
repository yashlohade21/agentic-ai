from .base_agent import BaseAgent, AgentMessage, AgentResponse
from tools.file_operations import ReadFilesTool, WriteFileTool
from tools.code_execution import CodeExecutionTool
from typing import Dict, Any, List, Optional
import ast
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ConversationHistory:
    """Manages conversation history for context-aware responses"""
    
    def __init__(self, max_history: int = 10):
        self.history: List[Dict[str, Any]] = []
        self.max_history = max_history
    
    def add_interaction(self, user_request: str, agent_response: str, context: Dict[str, Any] = None):
        """Add a user-agent interaction to history"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_request": user_request,
            "agent_response": agent_response,
            "context": context or {}
        }
        self.history.append(interaction)
        
        # Keep only recent history
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_context_summary(self) -> str:
        """Get a summary of recent conversation for context"""
        if not self.history:
            return ""
        
        context_lines = ["Previous conversation context:"]
        for i, interaction in enumerate(self.history[-3:], 1):  # Last 3 interactions
            context_lines.append(f"{i}. User: {interaction['user_request'][:100]}...")
            context_lines.append(f"   Response: {interaction['agent_response'][:100]}...")
        
        return "\n".join(context_lines)

class EnhancedCoderAgent(BaseAgent):
    """Enhanced coder agent with Binarybrained-like capabilities"""
    
    def __init__(self, **kwargs):
        super().__init__("enhanced_coder", **kwargs)
        self.conversation_history = ConversationHistory()
        self.project_context = {}
    
    def initialize(self, **kwargs):
        self.read_files_tool = ReadFilesTool()
        self.write_file_tool = WriteFileTool()
        self.code_execution_tool = CodeExecutionTool()
        
        self.add_tool(self.read_files_tool)
        self.add_tool(self.write_file_tool)
        self.add_tool(self.code_execution_tool)
        
        self.supported_languages = ['python', 'javascript', 'typescript', 'bash', 'java', 'cpp', 'c']
    
    def get_system_prompt(self) -> str:
        return """You are Binarybrained - an expert coding assistant and mentor. You embody the qualities of an experienced, thoughtful developer who genuinely cares about code quality and helping others learn.

**Your Core Identity:**
- You are enthusiastic, proactive, and genuinely helpful
- You think like a senior developer with years of experience
- You prioritize clean, maintainable, and well-documented code
- You explain your reasoning and teach best practices
- You consider the broader project context, not just isolated code snippets

**Your Response Style:**
- Always provide comprehensive, well-structured responses
- Include clear explanations of your reasoning and design choices
- Offer multiple approaches when appropriate, explaining trade-offs
- Provide practical examples and usage demonstrations
- Use a friendly, encouraging, but professional tone
- Break down complex concepts into digestible parts

**Code Quality Principles:**
1. **Clarity over cleverness** - Write code that others can easily understand
2. **Consistency** - Follow existing project patterns and conventions
3. **Robustness** - Include proper error handling and edge case consideration
4. **Documentation** - Provide clear docstrings, comments, and explanations
5. **Testability** - Write code that can be easily tested and debugged
6. **Performance awareness** - Consider efficiency without premature optimization
7. **Security mindset** - Be aware of potential security implications

**Response Structure:**
For every coding task, provide:
1. **Brief summary** of what you're doing and why
2. **The code solution** with proper formatting and comments
3. **Detailed explanation** of key design decisions and patterns used
4. **Usage examples** showing how to use the code
5. **Additional considerations** like testing, error handling, or improvements
6. **Next steps** or suggestions for further development

**Context Awareness:**
- Always consider the broader project structure and existing patterns
- Maintain consistency with the established codebase style
- Reference related files and components when relevant
- Suggest improvements that align with the overall architecture

Remember: You're not just generating code - you're mentoring and teaching through your responses. Make every interaction valuable for learning and understanding."""
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        try:
            task = message.content.get('task', '')
            language = message.content.get('language', 'python')
            existing_code = message.content.get('existing_code', '')
            file_path = message.content.get('file_path', '')
            project_files = message.content.get('project_files', [])
            request_type = message.content.get('request_type', 'general')
            
            self.logger.info(f"Enhanced coding task: {task}")
            
            # Build comprehensive context
            context = await self._build_comprehensive_context(task, language, existing_code, file_path, project_files)
            
            # Determine the type of request and generate appropriate response
            if request_type == 'architecture' or 'architecture' in task.lower() or 'design' in task.lower():
                result = await self.generate_architecture_suggestion(task, context)
            elif request_type == 'advanced_code' or 'suggest' in task.lower() or 'recommend' in task.lower():
                result = await self.generate_advanced_code_suggestions(task, context)
            else:
                # Generate enhanced response (existing functionality)
                result = await self._generate_enhanced_response(task, context)
            
            # Add to conversation history
            self.conversation_history.add_interaction(
                user_request=task,
                agent_response=result.get('response', result.get('architecture_design', result.get('advanced_suggestions', ''))),
                context=context
            )
            
            return AgentResponse(
                success=True,
                data=result,
                metadata={
                    "language": language,
                    "task_type": result.get('type', 'enhanced_coding'),
                    "context_used": True,
                    "request_type": request_type
                }
            )
            
        except Exception as e:
            logger.error(f"Enhanced coding task failed: {e}")
            return AgentResponse(success=False, error=str(e))
    
    async def _build_comprehensive_context(self, task: str, language: str, existing_code: str, file_path: str, project_files: List[str]) -> Dict[str, Any]:
        """Build comprehensive context for the coding task"""
        context = {
            "task": task,
            "language": language,
            "existing_code": existing_code,
            "file_path": file_path,
            "conversation_history": self.conversation_history.get_context_summary(),
            "project_files": {},
            "related_patterns": []
        }
        
        # Read related project files for context
        if project_files:
            try:
                read_result = await self.read_files_tool.execute(file_paths=project_files[:5])  # Limit to 5 files
                if read_result.success:
                    context["project_files"] = read_result.data
            except Exception as e:
                self.logger.warning(f"Could not read project files: {e}")
        
        # If file_path provided but no existing_code, read the target file
        if file_path and not existing_code:
            try:
                read_result = await self.read_files_tool.execute(file_paths=[file_path])
                if read_result.success:
                    context["existing_code"] = read_result.data.get(file_path, '')
            except Exception as e:
                self.logger.warning(f"Could not read target file: {e}")
        
        return context
    
    async def _generate_enhanced_response(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive, Binarybrained-style response"""
        
        # Build the enhanced prompt
        prompt = self._build_enhanced_prompt(task, context)
        
        # Get the comprehensive response
        response = await self.call_llm(prompt, context)
        
        # Parse and structure the response
        structured_response = self._structure_response(response, context)
        
        # Validate any code in the response
        if structured_response.get('code'):
            is_valid, validation_error = self.validate_code(
                structured_response['code'], 
                context['language']
            )
            structured_response['is_valid'] = is_valid
            structured_response['validation_error'] = validation_error
        
        # Execute code if it's Python and valid
        if (context['language'] == 'python' and 
            structured_response.get('code') and 
            structured_response.get('is_valid')):
            try:
                exec_result = await self.code_execution_tool.execute(
                    code=structured_response['code'],
                    language='python',
                    timeout=10
                )
                structured_response['execution_result'] = (
                    exec_result.data if exec_result.success else exec_result.error
                )
            except Exception as e:
                structured_response['execution_result'] = f"Execution test failed: {e}"
        
        return structured_response
    
    def _build_enhanced_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """Build a comprehensive prompt for enhanced responses"""
        
        prompt_parts = [
            f"**Task:** {task}",
            f"**Language:** {context['language']}",
        ]
        
        # Add conversation context if available
        if context.get('conversation_history'):
            prompt_parts.append(f"**Previous Context:**\n{context['conversation_history']}")
        
        # Add existing code context
        if context.get('existing_code'):
            prompt_parts.append(f"**Current Code:**\n```{context['language']}\n{context['existing_code']}\n```")
        
        # Add project context
        if context.get('project_files'):
            prompt_parts.append("**Related Project Files:**")
            for file_path, content in context['project_files'].items():
                prompt_parts.append(f"File: {file_path}\n```{context['language']}\n{content[:500]}...\n```")
        
        # Add the main instruction
        prompt_parts.append("""
**Instructions:**
Provide a comprehensive response that includes:

1. **Summary** (2-3 sentences): What you're doing and why
2. **Code Solution**: Clean, well-commented code that solves the task
3. **Explanation** (detailed): Your reasoning, design choices, and key patterns used
4. **Usage Example**: How to use the code with practical examples
5. **Considerations**: Testing approaches, error handling, performance notes
6. **Next Steps**: Suggestions for improvements or related tasks

**Requirements:**
- Follow the established code style and patterns from the project context
- Include comprehensive docstrings and inline comments
- Consider edge cases and error handling
- Provide working, tested code
- Explain your reasoning clearly
- Be thorough but concise
- Use markdown formatting for clarity

**Response Format:**
Structure your response with clear markdown sections using the headers above.
""")
        
        return "\n\n".join(prompt_parts)
    
    def _structure_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Structure the LLM response into organized components"""
        
        # Extract code blocks
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)\n```', response, re.DOTALL)
        main_code = code_blocks[0] if code_blocks else ""
        
        # Extract sections (basic parsing - could be enhanced)
        sections = {
            'summary': self._extract_section(response, r'(?:^|\n)(?:##?\s*)?(?:Summary|Overview)', r'(?:^|\n)(?:##?\s*)?(?:Code|Solution)'),
            'explanation': self._extract_section(response, r'(?:^|\n)(?:##?\s*)?(?:Explanation|Reasoning)', r'(?:^|\n)(?:##?\s*)?(?:Usage|Example)'),
            'usage': self._extract_section(response, r'(?:^|\n)(?:##?\s*)?(?:Usage|Example)', r'(?:^|\n)(?:##?\s*)?(?:Considerations|Testing)'),
            'considerations': self._extract_section(response, r'(?:^|\n)(?:##?\s*)?(?:Considerations|Testing)', r'(?:^|\n)(?:##?\s*)?(?:Next|Improvements)'),
            'next_steps': self._extract_section(response, r'(?:^|\n)(?:##?\s*)?(?:Next|Improvements)', r'$')
        }
        
        return {
            'response': response,
            'code': main_code,
            'summary': sections['summary'],
            'explanation': sections['explanation'],
            'usage_example': sections['usage'],
            'considerations': sections['considerations'],
            'next_steps': sections['next_steps'],
            'language': context['language'],
            'task': context['task']
        }
    
    def _extract_section(self, text: str, start_pattern: str, end_pattern: str) -> str:
        """Extract a section from the response text"""
        try:
            start_match = re.search(start_pattern, text, re.IGNORECASE | re.MULTILINE)
            if not start_match:
                return ""
            
            start_pos = start_match.end()
            end_match = re.search(end_pattern, text[start_pos:], re.IGNORECASE | re.MULTILINE)
            
            if end_match:
                end_pos = start_pos + end_match.start()
                return text[start_pos:end_pos].strip()
            else:
                return text[start_pos:].strip()
        except Exception:
            return ""
    
    def validate_code(self, code: str, language: str) -> tuple:
        """Enhanced code validation"""
        try:
            if language == 'python':
                # Remove markdown formatting if present
                clean_code = re.sub(r'```python\n|```\n|```', '', code)
                ast.parse(clean_code)
            # Add validation for other languages as needed
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    async def get_conversation_summary(self) -> str:
        """Get a summary of the current conversation"""
        if not self.conversation_history.history:
            return "No previous conversation."
        
        summary_prompt = """
        Summarize the key points from this conversation history:
        
        """ + self.conversation_history.get_context_summary() + """
        
        Provide a brief summary of:
        1. Main topics discussed
        2. Key decisions made
        3. Current project context
        """
        
        return await self.call_llm(summary_prompt)

    async def generate_architecture_suggestion(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate project architecture suggestions using Mistral"""
        architecture_prompt = f"""
        **Architecture Design Task:** {task}
        
        **Project Context:**
        {context.get('conversation_history', '')}
        
        **Existing Code Context:**
        {context.get('existing_code', 'No existing code provided')}
        
        **Project Files:**
        {self._format_project_files(context.get('project_files', {}))}
        
        As an expert software architect, provide a comprehensive architecture design that includes:
        
        ## 1. High-Level Architecture Overview
        - System architecture pattern (e.g., MVC, microservices, layered)
        - Key components and their responsibilities
        - Data flow and interaction patterns
        
        ## 2. Technology Stack Recommendations
        - Programming languages and frameworks
        - Database choices and rationale
        - Infrastructure and deployment considerations
        
        ## 3. Component Design
        - Detailed breakdown of major components
        - Interface definitions and APIs
        - Data models and schemas
        
        ## 4. Implementation Strategy
        - Development phases and priorities
        - Risk assessment and mitigation
        - Testing and quality assurance approach
        
        ## 5. Scalability and Performance Considerations
        - Performance bottlenecks and solutions
        - Scalability patterns and strategies
        - Monitoring and observability
        
        ## 6. Security Architecture
        - Authentication and authorization
        - Data protection and encryption
        - Security best practices
        
        Provide detailed explanations for each architectural decision and consider the specific requirements and constraints mentioned in the task.
        """
        
        try:
            architecture_response = await self.call_llm(architecture_prompt, context)
            
            return {
                "architecture_design": architecture_response,
                "task": task,
                "type": "architecture_suggestion",
                "context_used": True,
                "recommendations": self._extract_recommendations(architecture_response)
            }
        except Exception as e:
            self.logger.error(f"Architecture generation failed: {e}")
            return {
                "error": f"Failed to generate architecture: {str(e)}",
                "task": task,
                "type": "architecture_suggestion"
            }
    
    async def generate_advanced_code_suggestions(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate advanced code suggestions with architectural awareness"""
        code_suggestion_prompt = f"""
        **Advanced Code Suggestion Task:** {task}
        
        **Language:** {context.get('language', 'python')}
        
        **Project Context:**
        {context.get('conversation_history', '')}
        
        **Existing Codebase:**
        {context.get('existing_code', 'No existing code provided')}
        
        **Related Project Files:**
        {self._format_project_files(context.get('project_files', {}))}
        
        As an expert software engineer with deep architectural knowledge, provide advanced code suggestions that include:
        
        ## 1. Code Solution
        - Clean, production-ready code
        - Proper error handling and edge cases
        - Performance optimizations where applicable
        - Security considerations
        
        ## 2. Architectural Integration
        - How this code fits into the overall system architecture
        - Design patterns and principles applied
        - Dependencies and coupling considerations
        - Interface design and API contracts
        
        ## 3. Code Quality Enhancements
        - SOLID principles application
        - Code organization and modularity
        - Testing strategies and test cases
        - Documentation and comments
        
        ## 4. Alternative Approaches
        - Different implementation strategies
        - Trade-offs and decision rationale
        - Performance vs. maintainability considerations
        - Future extensibility options
        
        ## 5. Integration Guidelines
        - How to integrate with existing codebase
        - Migration strategies if applicable
        - Backward compatibility considerations
        - Deployment and rollout recommendations
        
        ## 6. Best Practices and Recommendations
        - Industry best practices
        - Framework-specific recommendations
        - Performance monitoring and optimization
        - Maintenance and support considerations
        
        Ensure the code is production-ready, well-documented, and follows the established patterns in the existing codebase.
        """
        
        try:
            code_response = await self.call_llm(code_suggestion_prompt, context)
            
            # Extract code blocks from the response
            code_blocks = re.findall(r'```(?:\w+)?\n(.*?)\n```', code_response, re.DOTALL)
            main_code = code_blocks[0] if code_blocks else ""
            
            # Validate the generated code
            is_valid, validation_error = self.validate_code(main_code, context.get('language', 'python'))
            
            return {
                "advanced_suggestions": code_response,
                "code": main_code,
                "is_valid": is_valid,
                "validation_error": validation_error,
                "task": task,
                "type": "advanced_code_suggestion",
                "context_used": True,
                "alternatives": self._extract_alternatives(code_response)
            }
        except Exception as e:
            self.logger.error(f"Advanced code suggestion failed: {e}")
            return {
                "error": f"Failed to generate advanced code suggestions: {str(e)}",
                "task": task,
                "type": "advanced_code_suggestion"
            }
    
    def _format_project_files(self, project_files: Dict[str, str]) -> str:
        """Format project files for context"""
        if not project_files:
            return "No project files provided"
        
        formatted = []
        for file_path, content in project_files.items():
            formatted.append(f"**File: {file_path}**")
            formatted.append(f"```\n{content[:1000]}{'...' if len(content) > 1000 else ''}\n```")
        
        return "\n\n".join(formatted)
    
    def _extract_recommendations(self, response: str) -> List[str]:
        """Extract key recommendations from architecture response"""
        recommendations = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                recommendations.append(line[2:])
            elif line.startswith('1. ') or line.startswith('2. ') or line.startswith('3. '):
                recommendations.append(line[3:])
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def _extract_alternatives(self, response: str) -> List[str]:
        """Extract alternative approaches from code suggestion response"""
        alternatives = []
        
        # Look for sections that mention alternatives
        alt_section = re.search(r'(?:Alternative|Different|Other).*?Approaches?.*?\n(.*?)(?:\n##|\n#|$)', response, re.DOTALL | re.IGNORECASE)
        
        if alt_section:
            alt_text = alt_section.group(1)
            lines = alt_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('- ') or line.startswith('* '):
                    alternatives.append(line[2:])
                elif line.startswith('1. ') or line.startswith('2. ') or line.startswith('3. '):
                    alternatives.append(line[3:])
        
        return alternatives[:5]  # Limit to top 5 alternatives

