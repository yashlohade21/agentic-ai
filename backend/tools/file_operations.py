from .base_tool import BaseTool, ToolResult
from pathlib import Path
import aiofiles
import os
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ReadFilesTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="read_files",
            description="Read contents of multiple files"
        )
    
    async def execute(self, file_paths: List[str], **kwargs) -> ToolResult:
        try:
            results = {}
            for file_path in file_paths:
                path = Path(file_path)
                if path.exists() and path.is_file():
                    try:
                        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                            content = await f.read()
                            results[file_path] = content
                    except UnicodeDecodeError:
                        # Try with different encoding for binary files
                        results[file_path] = f"Binary file: {file_path}"
                else:
                    results[file_path] = f"File not found: {file_path}"
            
            return ToolResult(success=True, data=results)
        except Exception as e:
            logger.error(f"Error reading files: {e}")
            return ToolResult(success=False, error=str(e))
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of file paths to read"
                }
            },
            "required": ["file_paths"]
        }

class WriteFileTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="write_file",
            description="Write content to a file"
        )
    
    async def execute(self, file_path: str, content: str, **kwargs) -> ToolResult:
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            return ToolResult(
                success=True,
                data={"file_path": file_path, "bytes_written": len(content.encode('utf-8'))}
            )
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            return ToolResult(success=False, error=str(e))
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path where to write the file"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file"
                }
            },
            "required": ["file_path", "content"]
        }

class ListFilesTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="list_files",
            description="List files in a directory with optional filtering"
        )
    
    async def execute(self, directory: str = ".", pattern: str = "*", recursive: bool = False, **kwargs) -> ToolResult:
        try:
            path = Path(directory)
            if not path.exists():
                return ToolResult(success=False, error=f"Directory not found: {directory}")
            
            files = []
            if recursive:
                for file_path in path.rglob(pattern):
                    if file_path.is_file():
                        files.append(str(file_path))
            else:
                for file_path in path.glob(pattern):
                    if file_path.is_file():
                        files.append(str(file_path))
            
            return ToolResult(
                success=True,
                data={"files": files, "count": len(files)},
                metadata={"directory": directory, "pattern": pattern, "recursive": recursive}
            )
        except Exception as e:
            logger.error(f"Error listing files in {directory}: {e}")
            return ToolResult(success=False, error=str(e))
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory to list files from",
                    "default": "."
                },
                "pattern": {
                    "type": "string", 
                    "description": "File pattern to match",
                    "default": "*"
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Whether to search recursively",
                    "default": False
                }
            }
        }
