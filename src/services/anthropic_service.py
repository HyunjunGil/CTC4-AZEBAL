"""
Anthropic Service for LLM interactions.

Handles Anthropic Claude API communication.
"""

import logging
from typing import Optional, Dict, Any
import anthropic
from src.core.config import settings
from src.services.llm_interface import LLMInterface

logger = logging.getLogger(__name__)


class AnthropicService(LLMInterface):
    """Service for interacting with Anthropic Claude."""
    
    def __init__(self):
        """Initialize Anthropic client."""
        if not settings.anthropic_api_key:
            logger.warning("Anthropic API key not configured")
            self.client = None
            return
            
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model_name = settings.anthropic_model_name
        
    def is_configured(self) -> bool:
        """Check if Anthropic is properly configured."""
        return self.client is not None
        
    def get_provider_name(self) -> str:
        """Get the name of the LLM provider."""
        return "Anthropic Claude"
    
    def get_default_parameters(self) -> Dict[str, Any]:
        """Get default parameters for Anthropic."""
        return {
            "max_tokens": 1000,
            "temperature": 0.7,
            "model": self.model_name
        }
        
    async def _call_llm_api(self, question: str, **kwargs) -> str:
        """
        Call Anthropic Claude API specifically.
        
        Args:
            question: The question to ask the LLM
            **kwargs: Additional parameters (max_tokens, temperature, etc.)
            
        Returns:
            The LLM's response as a string
            
        Raises:
            Exception: If the API call fails
        """
        response = self.client.messages.create(
            model=kwargs.get("model", self.model_name),
            max_tokens=kwargs.get("max_tokens", 1000),
            temperature=kwargs.get("temperature", 0.7),
            messages=[
                {
                    "role": "user",
                    "content": question
                }
            ]
        )
        
        return response.content[0].text
