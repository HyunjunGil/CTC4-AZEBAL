"""
Azure OpenAI Service for LLM interactions.

Handles Azure OpenAI API communication for chat completions.
"""

import logging
from typing import Optional, Dict, Any
from openai import AzureOpenAI
from src.core.config import settings
from src.services.llm_interface import LLMInterface

logger = logging.getLogger(__name__)


class AzureOpenAIService(LLMInterface):
    """Service for interacting with Azure OpenAI."""
    
    def __init__(self):
        """Initialize Azure OpenAI client."""
        if not settings.azure_openai_endpoint or not settings.azure_openai_api_key:
            logger.warning("Azure OpenAI credentials not configured")
            self.client = None
            return
            
        self.client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version
        )
        self.deployment_name = settings.azure_openai_deployment_name
        
    def is_configured(self) -> bool:
        """Check if Azure OpenAI is properly configured."""
        return self.client is not None
        
    def get_provider_name(self) -> str:
        """Get the name of the LLM provider."""
        return "Azure OpenAI"
    
    def get_default_parameters(self) -> Dict[str, Any]:
        """Get default parameters for Azure OpenAI."""
        return {
            "max_tokens": 1000,
            "temperature": 0.7,
            "model": self.deployment_name
        }
    
    async def _call_llm_api(self, question: str, **kwargs) -> str:
        """
        Call Azure OpenAI API specifically.
        
        Args:
            question: The question to ask the LLM
            **kwargs: Additional parameters (max_tokens, temperature, etc.)
            
        Returns:
            The LLM's response as a string
            
        Raises:
            Exception: If the API call fails
        """
        response = self.client.chat.completions.create(
            model=kwargs.get("model", self.deployment_name),
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


