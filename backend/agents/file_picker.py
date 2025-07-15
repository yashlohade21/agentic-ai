from .base_agent import BaseAgent, AgentMessage, AgentResponse
from tools.file_operations import ListFilesTool, ReadFilesTool
from typing import List, Dict, Any
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FilePickerAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__("file_picker", **kwargs)
    
    def initialize(self, **kwargs):
        self.list_files_tool = ListFilesTool()
        self.read_files_tool = ReadFilesTool()
        self.add_tool(self.list_files_tool)
        self.add_tool(self.read_files_tool)
        
        self.project_root = kwargs.get('project_root', '.')
        self.allowed_extensions = kwargs.get('allowed_extensions', ['.py', '.js', '.ts', '.md', '.txt', '.json', '.yaml', '.yml'])
        self.max_files = kwargs.get('max_files', 20)
    
    def get_system_prompt(self) -> str:
        return """You are a File Picker Agent. Your job is to find relevant files in a codebase based on user queries.

Your capabilities:
- Search for files by name, extension, or content relevance
- Analyze file structure and organization
- Identify key files for specific tasks
- Provide file summaries and recommendations

When finding files, consider:
1. File names that match the query
2. File extensions relevant to the task
3. Directory structure and organization
4. File size and modification dates
5. Likely importance based on naming conventions

Always provide:
1. List of relevant files with paths
2. Brief explanation of why each file is relevant
3. Recommended priority order for examination
4. Any patterns or insights about the codebase structure"""
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        try:
            query = message.content.get('query') or message.content.get('task')
            file_type = message.content.get('file_type', 'any')
            directory = message.content.get('directory', self.project_root)
            
            if not query:
                return AgentResponse(success=False, error="No query provided")
            
            self.logger.info(f"Finding files for query: {query}")
            
            # Find relevant files
            relevant_files = await self.find_relevant_files(query, file_type, directory)
            
            # Analyze and prioritize files
            analysis = await self.analyze_files(relevant_files, query)
            
            return AgentResponse(
                success=True,
                data={
                    "files": relevant_files,
                    "analysis": analysis,
                    "query": query,
                    "total_found": len(relevant_files)
                },
                metadata={"search_directory": directory, "file_type": file_type}
            )
            
        except Exception as e:
            logger.error(f"File picking failed: {e}")
            return AgentResponse(success=False, error=str(e))
    
    async def find_relevant_files(self, query: str, file_type: str, directory: str) -> List[Dict[str, Any]]:
        """Find files relevant to the query"""
        relevant_files = []
        
        # Determine search pattern based on file type
        if file_type == 'python':
            pattern = '*.py'
        elif file_type == 'javascript':
            pattern = '*.js'
        elif file_type == 'typescript':
            pattern = '*.ts'
        elif file_type == 'markdown':
            pattern = '*.md'
        else:
            pattern = '*'
        
        # List files
        list_result = await self.list_files_tool.execute(
            directory=directory,
            pattern=pattern,
            recursive=True
        )
        
        if not list_result.success:
            return []
        
        all_files = list_result.data.get('files', [])
        
        # Filter and score files based on relevance
        for file_path in all_files:
            relevance_score = self.calculate_relevance(file_path, query)
            if relevance_score > 0:
                file_info = {
                    "path": file_path,
                    "name": os.path.basename(file_path),
                    "extension": Path(file_path).suffix,
                    "relevance_score": relevance_score,
                    "size": self.get_file_size(file_path)
                }
                relevant_files.append(file_info)
        
        # Sort by relevance score and limit results
        relevant_files.sort(key=lambda x: x['relevance_score'], reverse=True)
        return relevant_files[:self.max_files]
    
    def calculate_relevance(self, file_path: str, query: str) -> float:
        """Calculate relevance score for a file based on the query"""
        score = 0.0
        filename = os.path.basename(file_path).lower()
        query_lower = query.lower()
        
        # Direct filename match
        if query_lower in filename:
            score += 10.0
        
        # Partial matches in filename
        query_words = query_lower.split()
        for word in query_words:
            if word in filename:
                score += 5.0
        
        # File extension relevance
        extension = Path(file_path).suffix.lower()
        if extension in self.allowed_extensions:
            score += 1.0
        
        # Special file importance (main files, configs, etc.)
        important_names = ['main', 'index', 'app', 'config', 'setup', 'init']
        for important in important_names:
            if important in filename:
                score += 3.0
        
        # Directory structure hints
        path_lower = file_path.lower()
        if any(word in path_lower for word in query_words):
            score += 2.0
        
        return score
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
    
    async def analyze_files(self, files: List[Dict[str, Any]], query: str) -> str:
        """Analyze found files and provide insights"""
        if not files:
            return "No relevant files found for the query."
        
        analysis_prompt = f"""
        Query: {query}
        
        Found files:
        {self._format_files_for_analysis(files)}
        
        Provide a brief analysis including:
        1. Which files are most likely to be relevant and why
        2. Recommended order for examining the files
        3. Any patterns or insights about the codebase structure
        4. Suggestions for what to look for in each file
        
        Be concise but helpful.
        """
        
        try:
            analysis = await self.call_llm(analysis_prompt)
            return analysis
        except Exception as e:
            logger.warning(f"Failed to generate file analysis: {e}")
            return f"Found {len(files)} relevant files. Top matches: {', '.join([f['name'] for f in files[:3]])}"
    
    def _format_files_for_analysis(self, files: List[Dict[str, Any]]) -> str:
        """Format files list for LLM analysis"""
        formatted = []
        for i, file_info in enumerate(files[:10], 1):  # Limit to top 10 for analysis
            formatted.append(f"{i}. {file_info['path']} (score: {file_info['relevance_score']:.1f}, size: {file_info['size']} bytes)")
        return "\n".join(formatted)
