from .base_tool import BaseTool, ToolResult
import aiohttp
import asyncio
from typing import List, Dict, Any
import logging
from core.config import settings

logger = logging.getLogger(__name__)

class WebSearchTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web for information"
        )
    
    async def execute(self, query: str, max_results: int = 5, **kwargs) -> ToolResult:
        try:
            # Try different search methods based on available API keys
            if settings.google_api_key and settings.google_cse_id:
                results = await self._google_search(query, max_results)
            else:
                # Fallback to a simple mock search for demo purposes
                results = await self._mock_search(query, max_results)
            
            return ToolResult(
                success=True,
                data={"results": results, "query": query},
                metadata={"results_count": len(results)}
            )
        except Exception as e:
            logger.error(f"Web search failed for query '{query}': {e}")
            return ToolResult(success=False, error=str(e))
    
    async def _google_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using Google Custom Search API"""
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": settings.google_api_key,
            "cx": settings.google_cse_id,
            "q": query,
            "num": min(max_results, 10)
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    for item in data.get("items", []):
                        results.append({
                            "title": item.get("title", ""),
                            "url": item.get("link", ""),
                            "snippet": item.get("snippet", "")
                        })
                    return results
                else:
                    raise Exception(f"Google search API returned status {response.status}")
    
    async def _mock_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Mock search results for demo purposes"""
        await asyncio.sleep(0.5)  # Simulate API delay
        
        mock_results = [
            {
                "title": f"Search result for '{query}' - Example 1",
                "url": f"https://example.com/search/{query.replace(' ', '-')}-1",
                "snippet": f"This is a mock search result for the query '{query}'. It contains relevant information about the topic."
            },
            {
                "title": f"Search result for '{query}' - Example 2", 
                "url": f"https://example.com/search/{query.replace(' ', '-')}-2",
                "snippet": f"Another mock result for '{query}' with additional context and information."
            },
            {
                "title": f"Documentation for '{query}'",
                "url": f"https://docs.example.com/{query.replace(' ', '-')}",
                "snippet": f"Official documentation and guides related to '{query}' with detailed explanations."
            }
        ]
        
        return mock_results[:max_results]
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 5
                }
            },
            "required": ["query"]
        }
