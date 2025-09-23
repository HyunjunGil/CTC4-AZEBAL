"""
OpenAI Service for LLM interactions.

Handles OpenAI API communication for chat completions.
"""

import logging
from typing import Optional, Dict, Any
from openai import OpenAI
from src.core.config import settings
from src.services.llm_interface import LLMInterface

logger = logging.getLogger(__name__)


class OpenAIService(LLMInterface):
    """Service for interacting with OpenAI ChatGPT."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not configured")
            self.client = None
            return
            
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model_name = settings.openai_model_name
        
    def is_configured(self) -> bool:
        """Check if OpenAI is properly configured."""
        return self.client is not None
        
    def get_provider_name(self) -> str:
        """Get the name of the LLM provider."""
        return "OpenAI ChatGPT"
    
    def get_default_parameters(self) -> Dict[str, Any]:
        """Get default parameters for OpenAI."""
        return {
            "max_tokens": 1000,
            "temperature": 0.7,
            "model": self.model_name
        }
        
    async def _call_llm_api(self, question: str, **kwargs) -> str:
        """
        Call OpenAI API specifically.
        
        Args:
            question: The question to ask the LLM
            **kwargs: Additional parameters (max_tokens, temperature, etc.)
            
        Returns:
            The LLM's response as a string
            
        Raises:
            Exception: If the API call fails
        """
        response = self.client.chat.completions.create(
            model=kwargs.get("model", self.model_name),
            messages=[
                {
                    "role": "user", 
                    "content": question
                }
            ],
            max_tokens=kwargs.get("max_tokens", 1000),
            temperature=kwargs.get("temperature", 0.7)
        )
        
        return response.choices[0].message.content
