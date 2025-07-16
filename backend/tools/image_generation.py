import asyncio
import logging
import requests
import base64
import os
from typing import Dict, Any, Optional
from .base_tool import BaseTool, ToolResult

logger = logging.getLogger(__name__)

class ImageGenerationTool(BaseTool):
    """Tool for generating images using various AI image generation APIs"""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="image_generation",
            description="Tool for generating images using various AI image generation APIs"
        )
        self.mistral_api_key = os.getenv("MISTRAL_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.available_providers = self._check_available_providers()
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Return the parameters schema for this tool"""
        return {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Text description of the image to generate"
                },
                "style": {
                    "type": "string",
                    "description": "Style of the image (realistic, artistic, cartoon, etc.)",
                    "default": "realistic"
                },
                "size": {
                    "type": "string",
                    "description": "Size of the image (e.g., '1024x1024', '512x512')",
                    "default": "1024x1024"
                },
                "provider": {
                    "type": "string",
                    "description": "Which provider to use ('auto', 'openai', 'mistral', etc.)",
                    "default": "auto"
                },
                "output_path": {
                    "type": "string",
                    "description": "Where to save the generated image"
                }
            },
            "required": ["prompt"]
        }
    
    def _check_available_providers(self) -> list:
        """Check which image generation providers are available"""
        providers = []
        
        # Note: Mistral AI doesn't currently support image generation via their API
        # This is a placeholder for when they add this capability
        if self.mistral_api_key:
            providers.append("mistral")
        
        if self.openai_api_key:
            providers.append("openai")
        
        # Add other providers as needed
        providers.append("placeholder")  # For demonstration
        
        return providers
    
    async def execute(self, 
                     prompt: str, 
                     style: str = "realistic", 
                     size: str = "1024x1024",
                     provider: str = "auto",
                     output_path: str = None,
                     **kwargs) -> ToolResult:
        """
        Generate an image based on the provided prompt
        
        Args:
            prompt: Text description of the image to generate
            style: Style of the image (realistic, artistic, cartoon, etc.)
            size: Size of the image (e.g., "1024x1024", "512x512")
            provider: Which provider to use ("auto", "openai", "mistral", etc.)
            output_path: Where to save the generated image
        """
        try:
            logger.info(f"Generating image with prompt: {prompt[:100]}...")
            
            # Select provider
            selected_provider = self._select_provider(provider)
            
            if selected_provider == "openai":
                result = await self._generate_with_openai(prompt, style, size, output_path)
            elif selected_provider == "mistral":
                result = await self._generate_with_mistral(prompt, style, size, output_path)
            else:
                result = await self._generate_placeholder(prompt, style, size, output_path)
            
            return ToolResult(
                success=True,
                data=result,
                metadata={
                    "provider": selected_provider,
                    "prompt": prompt,
                    "style": style,
                    "size": size
                }
            )
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return ToolResult(
                success=False,
                error=f"Image generation failed: {str(e)}"
            )
    
    def _select_provider(self, provider: str) -> str:
        """Select the best available provider"""
        if provider != "auto" and provider in self.available_providers:
            return provider
        
        # Auto-select based on availability
        if "openai" in self.available_providers:
            return "openai"
        elif "mistral" in self.available_providers:
            return "mistral"
        else:
            return "placeholder"
    
    async def _generate_with_openai(self, prompt: str, style: str, size: str, output_path: str) -> Dict[str, Any]:
        """Generate image using OpenAI DALL-E"""
        if not self.openai_api_key:
            raise Exception("OpenAI API key not available")
        
        # Enhance prompt with style
        enhanced_prompt = f"{prompt}, {style} style"
        
        payload = {
            "model": "dall-e-3",
            "prompt": enhanced_prompt,
            "n": 1,
            "size": size,
            "response_format": "url"
        }
        
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        response = await asyncio.to_thread(
            requests.post,
            "https://api.openai.com/v1/images/generations",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            image_url = result['data'][0]['url']
            
            # Download and save image if output_path provided
            if output_path:
                await self._download_and_save_image(image_url, output_path)
            
            return {
                "image_url": image_url,
                "output_path": output_path,
                "provider": "openai",
                "enhanced_prompt": enhanced_prompt
            }
        else:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
    
    async def _generate_with_mistral(self, prompt: str, style: str, size: str, output_path: str) -> Dict[str, Any]:
        """Generate image using Mistral (placeholder - not currently supported)"""
        # Note: Mistral AI doesn't currently support image generation
        # This is a placeholder for future implementation
        
        logger.warning("Mistral image generation not yet supported, using placeholder")
        return await self._generate_placeholder(prompt, style, size, output_path)
    
    async def _generate_placeholder(self, prompt: str, style: str, size: str, output_path: str) -> Dict[str, Any]:
        """Generate a placeholder response when no real provider is available"""
        
        # Create a simple text-based placeholder
        placeholder_text = f"""
        IMAGE GENERATION PLACEHOLDER
        
        Prompt: {prompt}
        Style: {style}
        Size: {size}
        
        This is a placeholder for image generation.
        To enable actual image generation, configure:
        - OPENAI_API_KEY for DALL-E
        - Or other image generation APIs
        
        The generated image would show: {prompt}
        """
        
        if output_path:
            # Save placeholder text to file
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            with open(output_path.replace('.png', '.txt').replace('.jpg', '.txt'), 'w') as f:
                f.write(placeholder_text)
        
        return {
            "placeholder": True,
            "description": placeholder_text,
            "output_path": output_path.replace('.png', '.txt').replace('.jpg', '.txt') if output_path else None,
            "provider": "placeholder"
        }
    
    async def _download_and_save_image(self, image_url: str, output_path: str):
        """Download image from URL and save to local path"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            
            # Download image
            response = await asyncio.to_thread(
                requests.get,
                image_url,
                timeout=30
            )
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"Image saved to: {output_path}")
            else:
                raise Exception(f"Failed to download image: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            raise
    
    async def generate_diagram(self, 
                              diagram_type: str,
                              description: str,
                              components: list = None,
                              **kwargs) -> ToolResult:
        """
        Generate architectural or technical diagrams
        
        Args:
            diagram_type: Type of diagram (architecture, flowchart, uml, etc.)
            description: Description of what the diagram should show
            components: List of components to include in the diagram
        """
        
        # Create a detailed prompt for diagram generation
        prompt_parts = [f"Create a {diagram_type} diagram showing {description}"]
        
        if components:
            prompt_parts.append(f"Include these components: {', '.join(components)}")
        
        prompt_parts.extend([
            "Use clear labels and professional styling",
            "Make it suitable for technical documentation",
            "Use standard diagram conventions and symbols"
        ])
        
        diagram_prompt = ". ".join(prompt_parts)
        
        return await self.execute(
            prompt=diagram_prompt,
            style="technical diagram",
            **kwargs
        )
    
    async def generate_logo(self, 
                           company_name: str,
                           industry: str,
                           style_preferences: str = "",
                           **kwargs) -> ToolResult:
        """
        Generate a logo for a company or project
        
        Args:
            company_name: Name of the company/project
            industry: Industry or domain
            style_preferences: Style preferences (modern, classic, minimalist, etc.)
        """
        
        logo_prompt = f"Professional logo for {company_name}, a {industry} company"
        
        if style_preferences:
            logo_prompt += f", {style_preferences} style"
        
        logo_prompt += ", clean design, suitable for business use, vector-style"
        
        return await self.execute(
            prompt=logo_prompt,
            style="logo design",
            **kwargs
        )