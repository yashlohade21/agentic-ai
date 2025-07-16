from .base_agent import BaseAgent, AgentMessage, AgentResponse
from tools.image_generation import ImageGenerationTool
from typing import Dict, Any
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class ImageGenerationAgent(BaseAgent):
    """Specialized agent for image generation and visual content creation"""
    
    def __init__(self, **kwargs):
        super().__init__("image_generation", **kwargs)
    
    def initialize(self, **kwargs):
        self.image_tool = ImageGenerationTool()
        self.add_tool(self.image_tool)
        
        self.supported_types = [
            'logo', 'diagram', 'illustration', 'concept_art', 
            'technical_diagram', 'flowchart', 'architecture_diagram'
        ]
        
        self.output_directory = kwargs.get('output_directory', './generated_images')
        os.makedirs(self.output_directory, exist_ok=True)
    
    def get_system_prompt(self) -> str:
        return """You are an Image Generation Agent specialized in creating visual content using AI image generation tools.

**Your Capabilities:**
- Generate images from text descriptions
- Create logos and branding materials
- Design technical diagrams and flowcharts
- Produce architectural visualizations
- Create concept art and illustrations
- Generate visual aids for presentations

**Your Approach:**
1. **Understand Requirements**: Analyze the user's request to understand the type of image needed
2. **Optimize Prompts**: Create detailed, specific prompts that will produce high-quality results
3. **Select Appropriate Style**: Choose the right visual style for the intended use case
4. **Generate and Refine**: Create images and suggest improvements or variations
5. **Provide Context**: Explain design choices and suggest how to use the generated images

**Quality Standards:**
- Create detailed, specific prompts for better results
- Consider the intended use case and audience
- Suggest appropriate styles and formats
- Provide multiple options when possible
- Explain design decisions and rationale

**Response Format:**
Always provide:
1. Generated image(s) with clear descriptions
2. Explanation of design choices
3. Suggestions for usage and variations
4. Technical details (size, format, style)
5. Recommendations for improvements or alternatives"""
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        try:
            request = message.content.get('request', '')
            image_type = message.content.get('type', 'general')
            prompt = message.content.get('prompt', request)
            style = message.content.get('style', 'realistic')
            size = message.content.get('size', '1024x1024')
            
            self.logger.info(f"Image generation request: {request}")
            
            # Analyze the request to determine the best approach
            analysis = await self._analyze_image_request(request, image_type)
            
            # Generate the image based on the analysis
            result = await self._generate_image_with_analysis(prompt, analysis, style, size)
            
            return AgentResponse(
                success=True,
                data=result,
                metadata={
                    "image_type": image_type,
                    "style": style,
                    "size": size,
                    "analysis": analysis
                }
            )
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return AgentResponse(success=False, error=str(e))
    
    async def _analyze_image_request(self, request: str, image_type: str) -> Dict[str, Any]:
        """Analyze the image request to optimize generation"""
        
        analysis_prompt = f"""
        Analyze this image generation request:
        
        Request: "{request}"
        Type: {image_type}
        
        Provide analysis in the following format:
        
        **Image Type**: (logo, diagram, illustration, etc.)
        **Primary Purpose**: (branding, documentation, presentation, etc.)
        **Target Audience**: (technical, business, general public, etc.)
        **Recommended Style**: (professional, artistic, technical, etc.)
        **Key Elements**: (list main visual elements needed)
        **Color Scheme**: (suggested colors or palette)
        **Composition**: (layout and arrangement suggestions)
        **Technical Requirements**: (size, format, resolution needs)
        
        Be specific and actionable in your recommendations.
        """
        
        try:
            analysis_response = await self.call_llm(analysis_prompt)
            
            # Parse the analysis (simplified parsing)
            analysis = {
                "raw_analysis": analysis_response,
                "image_type": self._extract_field(analysis_response, "Image Type"),
                "purpose": self._extract_field(analysis_response, "Primary Purpose"),
                "audience": self._extract_field(analysis_response, "Target Audience"),
                "style": self._extract_field(analysis_response, "Recommended Style"),
                "elements": self._extract_field(analysis_response, "Key Elements"),
                "colors": self._extract_field(analysis_response, "Color Scheme"),
                "composition": self._extract_field(analysis_response, "Composition"),
                "requirements": self._extract_field(analysis_response, "Technical Requirements")
            }
            
            return analysis
            
        except Exception as e:
            logger.warning(f"Analysis failed, using defaults: {e}")
            return {
                "image_type": image_type,
                "purpose": "general",
                "style": "professional",
                "raw_analysis": f"Analysis failed: {str(e)}"
            }
    
    def _extract_field(self, text: str, field_name: str) -> str:
        """Extract a specific field from the analysis text"""
        import re
        
        pattern = rf"\*\*{field_name}\*\*:?\s*([^\n*]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        return "Not specified"
    
    async def _generate_image_with_analysis(self, prompt: str, analysis: Dict[str, Any], style: str, size: str) -> Dict[str, Any]:
        """Generate image using the analysis to optimize the prompt"""
        
        # Enhance the prompt based on analysis
        enhanced_prompt = await self._enhance_prompt(prompt, analysis)
        
        # Determine output path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_image_{timestamp}.png"
        output_path = os.path.join(self.output_directory, filename)
        
        # Generate the image
        if analysis.get("image_type") == "diagram" or "diagram" in prompt.lower():
            result = await self.image_tool.generate_diagram(
                diagram_type=analysis.get("image_type", "flowchart"),
                description=enhanced_prompt,
                output_path=output_path,
                size=size
            )
        elif analysis.get("image_type") == "logo" or "logo" in prompt.lower():
            # Extract company name and industry from prompt
            company_name = self._extract_company_name(prompt)
            industry = analysis.get("purpose", "technology")
            
            result = await self.image_tool.generate_logo(
                company_name=company_name,
                industry=industry,
                style_preferences=analysis.get("style", style),
                output_path=output_path,
                size=size
            )
        else:
            # General image generation
            result = await self.image_tool.execute(
                prompt=enhanced_prompt,
                style=analysis.get("style", style),
                size=size,
                output_path=output_path
            )
        
        # Combine results with analysis
        combined_result = {
            "generation_result": result.data if result.success else {"error": result.error},
            "analysis": analysis,
            "enhanced_prompt": enhanced_prompt,
            "original_prompt": prompt,
            "output_path": output_path,
            "recommendations": await self._generate_recommendations(analysis, result)
        }
        
        return combined_result
    
    async def _enhance_prompt(self, original_prompt: str, analysis: Dict[str, Any]) -> str:
        """Enhance the original prompt based on analysis"""
        
        enhancement_prompt = f"""
        Enhance this image generation prompt based on the analysis:
        
        Original Prompt: "{original_prompt}"
        
        Analysis:
        - Image Type: {analysis.get('image_type', 'general')}
        - Purpose: {analysis.get('purpose', 'general')}
        - Style: {analysis.get('style', 'professional')}
        - Key Elements: {analysis.get('elements', 'not specified')}
        - Color Scheme: {analysis.get('colors', 'not specified')}
        - Composition: {analysis.get('composition', 'not specified')}
        
        Create an enhanced prompt that:
        1. Incorporates the recommended style and elements
        2. Specifies appropriate colors and composition
        3. Includes technical quality indicators
        4. Maintains the original intent while improving specificity
        
        Return only the enhanced prompt, no additional text.
        """
        
        try:
            enhanced = await self.call_llm(enhancement_prompt)
            return enhanced.strip()
        except Exception as e:
            logger.warning(f"Prompt enhancement failed: {e}")
            return original_prompt
    
    def _extract_company_name(self, prompt: str) -> str:
        """Extract company name from prompt for logo generation"""
        # Simple extraction - could be enhanced with NLP
        words = prompt.split()
        
        # Look for common patterns
        for i, word in enumerate(words):
            if word.lower() in ['for', 'company', 'brand', 'startup']:
                if i > 0:
                    return words[i-1]
                elif i < len(words) - 1:
                    return words[i+1]
        
        # Fallback: use first capitalized word
        for word in words:
            if word[0].isupper() and len(word) > 2:
                return word
        
        return "Company"
    
    async def _generate_recommendations(self, analysis: Dict[str, Any], generation_result) -> Dict[str, Any]:
        """Generate recommendations for using and improving the generated image"""
        
        recommendations_prompt = f"""
        Based on this image generation analysis and result, provide recommendations:
        
        Analysis: {analysis.get('raw_analysis', 'No analysis available')}
        Generation Success: {generation_result.success if generation_result else False}
        
        Provide recommendations for:
        1. **Usage**: How to best use this image
        2. **Variations**: Suggested variations or alternatives
        3. **Improvements**: How to improve the image or prompt
        4. **Technical**: Format, size, or quality considerations
        5. **Integration**: How to integrate with other materials
        
        Be practical and specific in your recommendations.
        """
        
        try:
            recommendations = await self.call_llm(recommendations_prompt)
            return {
                "text": recommendations,
                "usage_suggestions": self._extract_usage_suggestions(recommendations),
                "variations": self._extract_variations(recommendations)
            }
        except Exception as e:
            return {
                "text": f"Could not generate recommendations: {str(e)}",
                "usage_suggestions": [],
                "variations": []
            }
    
    def _extract_usage_suggestions(self, recommendations: str) -> list:
        """Extract usage suggestions from recommendations"""
        suggestions = []
        lines = recommendations.split('\n')
        
        in_usage_section = False
        for line in lines:
            line = line.strip()
            if 'usage' in line.lower() and ('**' in line or '#' in line):
                in_usage_section = True
                continue
            elif ('**' in line or '#' in line) and in_usage_section:
                in_usage_section = False
            elif in_usage_section and (line.startswith('- ') or line.startswith('* ')):
                suggestions.append(line[2:])
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def _extract_variations(self, recommendations: str) -> list:
        """Extract variation suggestions from recommendations"""
        variations = []
        lines = recommendations.split('\n')
        
        in_variations_section = False
        for line in lines:
            line = line.strip()
            if 'variation' in line.lower() and ('**' in line or '#' in line):
                in_variations_section = True
                continue
            elif ('**' in line or '#' in line) and in_variations_section:
                in_variations_section = False
            elif in_variations_section and (line.startswith('- ') or line.startswith('* ')):
                variations.append(line[2:])
        
        return variations[:5]  # Limit to 5 variations

