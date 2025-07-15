from .base_tool import BaseTool, ToolResult
import asyncio
import os
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class TerminalTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="run_terminal_command",
            description="Execute terminal/command line commands"
        )
    
    async def execute(self, command: str, cwd: str = None, timeout: int = 60, **kwargs) -> ToolResult:
        try:
            # Set working directory
            work_dir = cwd if cwd else os.getcwd()
            
            # Create subprocess
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=work_dir
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
                        "command": command,
                        "cwd": work_dir
                    },
                    metadata={"execution_time": "completed"}
                )
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return ToolResult(
                    success=False,
                    error=f"Command timed out after {timeout} seconds"
                )
                
        except Exception as e:
            logger.error(f"Terminal command failed: {e}")
            return ToolResult(success=False, error=str(e))
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Terminal command to execute"
                },
                "cwd": {
                    "type": "string",
                    "description": "Working directory for command execution"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Command timeout in seconds",
                    "default": 60
                }
            },
            "required": ["command"]
        }
