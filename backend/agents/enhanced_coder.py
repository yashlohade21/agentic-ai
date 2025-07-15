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
    """Enhanced coder agent with Codebuff-like capabilities"""
    
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
        return """You are Codebuff - an expert coding assistant and mentor. You embody the qualities of an experienced, thoughtful developer who genuinely cares about code quality and helping others learn.

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
            
            self.logger.info(f"Enhanced coding task: {task}")
            
            # Build comprehensive context
            context = await self._build_comprehensive_context(task, language, existing_code, file_path, project_files)
            
            # Generate enhanced response
            result = await self._generate_enhanced_response(task, context)
            
            # Add to conversation history
            self.conversation_history.add_interaction(
                user_request=task,
                agent_response=result.get('response', ''),
                context=context
            )
            
            return AgentResponse(
                success=True,
                data=result,
                metadata={
                    "language": language,
                    "task_type": "enhanced_coding",
                    "context_used": True
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
        """Generate a comprehensive, Codebuff-style response"""
        
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
