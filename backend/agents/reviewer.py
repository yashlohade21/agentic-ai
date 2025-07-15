from .base_agent import BaseAgent, AgentMessage, AgentResponse
from tools.file_operations import ReadFilesTool
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ReviewerAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__("reviewer", **kwargs)
    
    def initialize(self, **kwargs):
        self.read_files_tool = ReadFilesTool()
        self.add_tool(self.read_files_tool)
        
        self.review_criteria = kwargs.get('review_criteria', [
            'code_quality',
            'functionality',
            'security',
            'performance',
            'maintainability',
            'documentation'
        ])
    
    def get_system_prompt(self) -> str:
        return """You are a Reviewer Agent. You provide thorough, constructive reviews of code, documents, and other work products.

Your review criteria include:
1. Code Quality: Clean, readable, well-structured code
2. Functionality: Does it work as intended? Are there bugs?
3. Security: Are there security vulnerabilities or concerns?
4. Performance: Is the code efficient? Any performance issues?
5. Maintainability: Is the code easy to maintain and extend?
6. Documentation: Is it well-documented with clear comments?
7. Best Practices: Does it follow language/framework conventions?
8. Testing: Are there adequate tests? Is the code testable?

Provide reviews that are:
- Constructive and helpful
- Specific with examples
- Balanced (highlight both strengths and areas for improvement)
- Actionable with clear recommendations
- Professional and respectful

Always include:
1. Overall assessment and rating
2. Specific issues found with line references when possible
3. Recommendations for improvement
4. Positive aspects worth highlighting
5. Priority level for each issue (Critical, High, Medium, Low)"""
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        try:
            content_to_review = message.content.get('content', '')
            file_path = message.content.get('file_path', '')
            review_type = message.content.get('review_type', 'code')
            focus_areas = message.content.get('focus_areas', self.review_criteria)
            
            # If file_path provided, read the file
            if file_path and not content_to_review:
                read_result = await self.read_files_tool.execute(file_paths=[file_path])
                if read_result.success:
                    content_to_review = read_result.data.get(file_path, '')
                else:
                    return AgentResponse(success=False, error=f"Could not read file: {file_path}")
            
            if not content_to_review:
                return AgentResponse(success=False, error="No content provided for review")
            
            self.logger.info(f"Reviewing {review_type}: {file_path or 'content'}")
            
            # Perform the review
            review_result = await self.conduct_review(
                content_to_review, 
                review_type, 
                focus_areas, 
                file_path
            )
            
            return AgentResponse(
                success=True,
                data=review_result,
                metadata={
                    "review_type": review_type,
                    "file_path": file_path,
                    "focus_areas": focus_areas
                }
            )
            
        except Exception as e:
            logger.error(f"Review failed: {e}")
            return AgentResponse(success=False, error=str(e))
    
    async def conduct_review(self, content: str, review_type: str, focus_areas: List[str], file_path: str = '') -> Dict[str, Any]:
        """Conduct a comprehensive review"""
        
        # Determine language/type from file extension or content
        language = self._detect_language(content, file_path)
        
        review_prompt = f"""
        Review Type: {review_type}
        Language/Type: {language}
        File Path: {file_path}
        Focus Areas: {', '.join(focus_areas)}
        
        Content to Review:
        ```{language}
        {content}
        ```
        
        Provide a comprehensive review covering the specified focus areas:
        {self._format_focus_areas(focus_areas)}
        
        Structure your review as follows:
        
        ## Overall Assessment
        - Overall rating (1-10)
        - Summary of strengths and weaknesses
        - General recommendations
        
        ## Detailed Findings
        For each issue found:
        - **Priority**: Critical/High/Medium/Low
        - **Category**: Which focus area it relates to
        - **Issue**: Description of the problem
        - **Location**: Line numbers or specific sections if applicable
        - **Recommendation**: How to fix or improve
        
        ## Positive Aspects
        - What was done well
        - Good practices observed
        - Strengths to maintain
        
        ## Action Items
        - Prioritized list of improvements
        - Quick wins vs. longer-term improvements
        - Suggestions for next steps
        
        Be specific, constructive, and actionable in your feedback.
        """
        
        review_text = await self.call_llm(review_prompt)
        
        # Parse and structure the review
        structured_review = self._structure_review(review_text)
        
        return {
            "review_text": review_text,
            "structured_review": structured_review,
            "content": content,
            "language": language,
            "file_path": file_path,
            "focus_areas": focus_areas
        }
    
    def _detect_language(self, content: str, file_path: str) -> str:
        """Detect the language/type of content"""
        if file_path:
            extension = file_path.split('.')[-1].lower()
            extension_map = {
                'py': 'python',
                'js': 'javascript',
                'ts': 'typescript',
                'java': 'java',
                'cpp': 'cpp',
                'c': 'c',
                'cs': 'csharp',
                'php': 'php',
                'rb': 'ruby',
                'go': 'go',
                'rs': 'rust',
                'md': 'markdown',
                'html': 'html',
                'css': 'css',
                'json': 'json',
                'yaml': 'yaml',
                'yml': 'yaml',
                'xml': 'xml'
            }
            return extension_map.get(extension, 'text')
        
        # Try to detect from content
        if 'def ' in content and 'import ' in content:
            return 'python'
        elif 'function ' in content and ('var ' in content or 'let ' in content or 'const ' in content):
            return 'javascript'
        elif '<?php' in content:
            return 'php'
        elif '#include' in content and 'int main' in content:
            return 'c'
        
        return 'text'
    
    def _format_focus_areas(self, focus_areas: List[str]) -> str:
        """Format focus areas for the prompt"""
        area_descriptions = {
            'code_quality': 'Code structure, readability, naming conventions, organization',
            'functionality': 'Correctness, logic errors, edge cases, expected behavior',
            'security': 'Vulnerabilities, input validation, authentication, authorization',
            'performance': 'Efficiency, optimization opportunities, resource usage',
            'maintainability': 'Modularity, extensibility, code reuse, complexity',
            'documentation': 'Comments, docstrings, README, inline documentation',
            'testing': 'Test coverage, testability, test quality',
            'best_practices': 'Language conventions, framework patterns, industry standards'
        }
        
        formatted = []
        for area in focus_areas:
            description = area_descriptions.get(area, area)
            formatted.append(f"- **{area.title()}**: {description}")
        
        return '\n'.join(formatted)
    
    def _structure_review(self, review_text: str) -> Dict[str, Any]:
        """Extract structured data from review text"""
        # This is a simplified parser - in practice, you might want more sophisticated parsing
        structured = {
            "overall_rating": None,
            "summary": "",
            "issues": [],
            "positive_aspects": [],
            "action_items": []
        }
        
        # Try to extract overall rating
        import re
        rating_match = re.search(r'rating.*?(\d+(?:\.\d+)?)', review_text.lower())
        if rating_match:
            try:
                structured["overall_rating"] = float(rating_match.group(1))
            except ValueError:
                pass
        
        # Extract sections (simplified)
        sections = review_text.split('##')
        for section in sections:
            section = section.strip()
            if section.lower().startswith('overall assessment'):
                structured["summary"] = section
            elif section.lower().startswith('positive aspects'):
                structured["positive_aspects"] = [line.strip() for line in section.split('\n')[1:] if line.strip()]
            elif section.lower().startswith('action items'):
                structured["action_items"] = [line.strip() for line in section.split('\n')[1:] if line.strip()]
        
        return structured
