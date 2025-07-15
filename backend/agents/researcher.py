from .base_agent import BaseAgent, AgentMessage, AgentResponse
from tools.web_search import WebSearchTool
from typing import List, Dict
import asyncio
import logging

logger = logging.getLogger(__name__)

class ResearcherAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__("researcher", **kwargs)
    
    def initialize(self, **kwargs):
        self.web_search = WebSearchTool()
        self.add_tool(self.web_search)
        self.max_results = kwargs.get('max_results', 5)
    
    def get_system_prompt(self) -> str:
        return """You are a Research Agent. You gather information from web searches and documentation to help answer questions and provide context for tasks.

Your capabilities:
- Web search for current information
- Documentation lookup
- Summarizing research findings
- Identifying relevant resources
- Providing technical context

Always provide:
1. Summary of findings
2. Key insights
3. Relevant links/sources
4. Confidence level in the information
5. Actionable recommendations

Be thorough but concise. Focus on practical, actionable information."""
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        try:
            query = message.content.get('query') or message.content.get('task')
            if not query:
                return AgentResponse(success=False, error="No query provided")
            
            self.logger.info(f"Researching: {query}")
            
            # Perform web search
            search_result = await self.web_search.execute(query=query, max_results=self.max_results)
            
            if not search_result.success:
                return AgentResponse(success=False, error=f"Search failed: {search_result.error}")
            
            search_results = search_result.data.get('results', [])
            
            # Summarize findings using LLM
            summary_prompt = f"""
            Research Query: {query}
            
            Search Results:
            {self.format_search_results(search_results)}
            
            Provide a comprehensive research summary including:
            1. Key findings and insights
            2. Important technical details
            3. Best practices or recommendations
            4. Relevant tools, libraries, or resources mentioned
            5. Confidence assessment of the information
            6. Actionable next steps
            
            Be concise but thorough. Focus on practical information that would help someone working on this topic.
            """
            
            summary = await self.call_llm(summary_prompt)
            
            return AgentResponse(
                success=True,
                data={
                    "summary": summary,
                    "raw_results": search_results,
                    "query": query,
                    "sources": [result.get('url', '') for result in search_results]
                },
                metadata={"results_count": len(search_results)}
            )
            
        except Exception as e:
            logger.error(f"Research failed for query '{query}': {e}")
            return AgentResponse(success=False, error=str(e))
    
    def format_search_results(self, results: List[Dict]) -> str:
        """Format search results for LLM processing"""
        if not results:
            return "No search results found."
        
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(f"{i}. {result.get('title', 'No title')}")
            formatted.append(f"   URL: {result.get('url', 'No URL')}")
            formatted.append(f"   Snippet: {result.get('snippet', 'No snippet')}")
            formatted.append("")
        return "\n".join(formatted)
