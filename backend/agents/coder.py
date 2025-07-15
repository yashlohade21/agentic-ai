from .base_agent import BaseAgent, AgentMessage, AgentResponse
from tools.file_operations import ReadFilesTool, WriteFileTool
from tools.code_execution import CodeExecutionTool
from typing import Dict, Any
import ast
import re
import logging

logger = logging.getLogger(__name__)

class CoderAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__("coder", **kwargs)
    
    def initialize(self, **kwargs):
        self.read_files_tool = ReadFilesTool()
        self.write_file_tool = WriteFileTool()
        self.code_execution_tool = CodeExecutionTool()
        
        self.add_tool(self.read_files_tool)
        self.add_tool(self.write_file_tool)
        self.add_tool(self.code_execution_tool)
        
        self.supported_languages = ['python', 'javascript', 'typescript', 'bash']
    
    def get_system_prompt(self) -> str:
        return """You are a Coder Agent. You write, modify, and review code with high quality and attention to detail.

Your capabilities:
- Write new functions, classes, and modules
- Modify existing code while preserving functionality
- Fix bugs and errors
- Optimize code performance
- Add comprehensive documentation and comments
- Follow language-specific best practices
- Test code functionality

Always follow these principles:
1. Write clean, readable, and maintainable code
2. Follow language best practices and conventions
3. Add appropriate error handling and validation
4. Include comprehensive docstrings and comments
5. Consider edge cases and potential issues
6. Test code when possible
7. Preserve existing functionality when modifying code

When modifying existing code:
- Read and understand the current implementation
- Make minimal necessary changes
- Maintain existing code style and patterns
- Add comments explaining significant changes"""
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        try:
            task = message.content.get('task', '')
            language = message.content.get('language', 'python')
            existing_code = message.content.get('existing_code', '')
            file_path = message.content.get('file_path', '')
            
            self.logger.info(f"Coding task: {task}")
            
            # Determine the type of coding task
            if 'write' in task.lower() or 'create' in task.lower():
                result = await self.write_new_code(task, language, file_path)
            elif 'modify' in task.lower() or 'update' in task.lower() or 'fix' in task.lower():
                result = await self.modify_existing_code(task, existing_code, language, file_path)
            elif 'review' in task.lower() or 'analyze' in task.lower():
                result = await self.review_code(task, existing_code, language)
            else:
                result = await self.general_coding_task(task, language, existing_code, file_path)
            
            return AgentResponse(
                success=True,
                data=result,
                metadata={"language": language, "task_type": "coding"}
            )
            
        except Exception as e:
            logger.error(f"Coding task failed: {e}")
            return AgentResponse(success=False, error=str(e))
    
    async def write_new_code(self, task: str, language: str, file_path: str = '') -> Dict[str, Any]:
        """Write new code from scratch"""
        prompt = f"""
        Task: {task}
        Language: {language}
        File path: {file_path}
        
        Write clean, well-documented code that accomplishes this task.
        Include:
        1. Proper imports and dependencies
        2. Clear function/class definitions
        3. Comprehensive docstrings
        4. Error handling where appropriate
        5. Example usage if applicable
        
        Follow {language} best practices and conventions.
        """
        
        code = await self.call_llm(prompt)
        
        # Validate code syntax
        is_valid, validation_error = self.validate_code(code, language)
        
        result = {
            "code": code,
            "language": language,
            "is_valid": is_valid,
            "validation_error": validation_error,
            "task": task
        }
        
        # Write to file if path provided and code is valid
        if file_path and is_valid:
            write_result = await self.write_file_tool.execute(
                file_path=file_path,
                content=code
            )
            result["file_written"] = write_result.success
            result["file_path"] = file_path
        
        return result
    
    async def modify_existing_code(self, task: str, existing_code: str, language: str, file_path: str = '') -> Dict[str, Any]:
        """Modify existing code"""
        # If file_path provided but no existing_code, read the file
        if file_path and not existing_code:
            read_result = await self.read_files_tool.execute(file_paths=[file_path])
            if read_result.success:
                existing_code = read_result.data.get(file_path, '')
        
        prompt = f"""
        Task: {task}
        Language: {language}
        
        Existing code:
        ```{language}
        {existing_code}
        ```
        
        Modify the code to accomplish the task while:
        1. Preserving existing functionality that should remain
        2. Following the existing code style and patterns
        3. Adding proper documentation for changes
        4. Maintaining or improving error handling
        5. Ensuring backward compatibility where possible
        
        Provide the complete modified code.
        """
        
        modified_code = await self.call_llm(prompt)
        
        # Validate modified code
        is_valid, validation_error = self.validate_code(modified_code, language)
        
        result = {
            "original_code": existing_code,
            "modified_code": modified_code,
            "language": language,
            "is_valid": is_valid,
            "validation_error": validation_error,
            "task": task
        }
        
        # Write modified code to file if valid
        if file_path and is_valid:
            write_result = await self.write_file_tool.execute(
                file_path=file_path,
                content=modified_code
            )
            result["file_written"] = write_result.success
            result["file_path"] = file_path
        
        return result
    
    async def review_code(self, task: str, code: str, language: str) -> Dict[str, Any]:
        """Review and analyze code"""
        prompt = f"""
        Task: {task}
        Language: {language}
        
        Code to review:
        ```{language}
        {code}
        ```
        
        Provide a comprehensive code review including:
        1. Code quality assessment
        2. Potential bugs or issues
        3. Performance considerations
        4. Best practice recommendations
        5. Security concerns (if any)
        6. Suggestions for improvement
        7. Overall rating and summary
        
        Be constructive and specific in your feedback.
        """
        
        review = await self.call_llm(prompt)
        
        # Also validate syntax
        is_valid, validation_error = self.validate_code(code, language)
        
        return {
            "code": code,
            "review": review,
            "language": language,
            "is_valid": is_valid,
            "validation_error": validation_error,
            "task": task
        }
    
    async def general_coding_task(self, task: str, language: str, existing_code: str = '', file_path: str = '') -> Dict[str, Any]:
        """Handle general coding tasks"""
        context = ""
        if existing_code:
            context = f"\nExisting code context:\n```{language}\n{existing_code}\n```"
        
        prompt = f"""
        Task: {task}
        Language: {language}
        {context}
        
        Complete this coding task with high quality code that:
        1. Solves the problem effectively
        2. Follows best practices
        3. Includes proper documentation
        4. Handles errors appropriately
        5. Is maintainable and readable
        
        If modifying existing code, preserve important functionality.
        """
        
        code = await self.call_llm(prompt)
        
        # Validate code
        is_valid, validation_error = self.validate_code(code, language)
        
        result = {
            "code": code,
            "language": language,
            "is_valid": is_valid,
            "validation_error": validation_error,
            "task": task
        }
        
        # Test code execution if it's Python and is valid
        if language == 'python' and is_valid:
            try:
                exec_result = await self.code_execution_tool.execute(
                    code=code,
                    language='python',
                    timeout=10
                )
                result["execution_result"] = exec_result.data if exec_result.success else exec_result.error
            except Exception as e:
                result["execution_result"] = f"Execution test failed: {e}"
        
        return result
    
    def validate_code(self, code: str, language: str) -> tuple:
        """Validate code syntax"""
        try:
            if language == 'python':
                ast.parse(code)
            # Add validation for other languages as needed
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    

