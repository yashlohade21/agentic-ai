from .base_tool import BaseTool, ToolResult
import asyncio
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class CodeExecutionTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="execute_code",
            description="Execute code in a safe environment"
        )
        self.supported_languages = {
            'python': {'extension': '.py', 'command': ['python']},
            'javascript': {'extension': '.js', 'command': ['node']},
            'bash': {'extension': '.sh', 'command': ['bash']},
            'powershell': {'extension': '.ps1', 'command': ['powershell', '-File']}
        }
    
    async def execute(self, code: str, language: str = 'python', timeout: int = 30, **kwargs) -> ToolResult:
        try:
            if language not in self.supported_languages:
                return ToolResult(
                    success=False, 
                    error=f"Unsupported language: {language}. Supported: {list(self.supported_languages.keys())}"
                )
            
            lang_config = self.supported_languages[language]
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(
                mode='w', 
                suffix=lang_config['extension'], 
                delete=False
            ) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            try:
                # Execute code
                command = lang_config['command'] + [temp_file_path]
                
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=os.getcwd()
                )
                
                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(), 
                        timeout=timeout
                    )
                    
                    return ToolResult(
                        success=True,
                        data={
                            "stdout": stdout.decode('utf-8'),
                            "stderr": stderr.decode('utf-8'),
                            "return_code": process.returncode,
                            "language": language
                        },
                        metadata={"execution_time": "completed"}
                    )
                    
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
                    return ToolResult(
                        success=False,
                        error=f"Code execution timed out after {timeout} seconds"
                    )
                    
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass
                    
        except Exception as e:
            logger.error(f"Code execution failed: {e}")
            return ToolResult(success=False, error=str(e))
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Code to execute"
                },
                "language": {
                    "type": "string",
                    "description": "Programming language",
                    "enum": list(self.supported_languages.keys()),
                    "default": "python"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Execution timeout in seconds",
                    "default": 30
                }
            },
            "required": ["code"]
        }
