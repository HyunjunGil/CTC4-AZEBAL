"""
LLM Interface for AZEBAL.

Provides an abstract interface for different LLM providers.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers."""
    AZURE_OPENAI = "azure_openai"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class LLMInterface(ABC):
    """Abstract interface for LLM services."""
    
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the LLM service is properly configured."""
        pass
    
    @abstractmethod
    async def _call_llm_api(self, question: str, **kwargs) -> str:
        """
        Call the specific LLM API. This method must be implemented by each provider.
        
        Args:
            question: The question to ask the LLM
            **kwargs: Additional parameters specific to the LLM provider
            
        Returns:
            The LLM's response as a string
            
        Raises:
            Exception: If the API call fails
        """
        pass
    
    async def ask_llm(self, question: str, **kwargs) -> str:
        """
        Ask a question to the LLM and get a response.
        
        This method implements the common logic for all LLM providers.
        
        Args:
            question: The question to ask the LLM
            **kwargs: Additional parameters specific to the LLM provider
            
        Returns:
            The LLM's response as a string
            
        Raises:
            RuntimeError: If the LLM service is not configured
            Exception: If the API call fails
        """
        if not self.is_configured():
            raise RuntimeError(f"{self.get_provider_name()} is not configured. Please set the required API keys and configuration.")
            
        try:
            logger.info(f"Sending question to {self.get_provider_name()}: {question[:100]}...")
            
            # Merge default parameters with provided kwargs
            params = self.get_default_parameters()
            params.update(kwargs)
            
            # Call the provider-specific API implementation
            response = await self._call_llm_api(question, **params)
            
            logger.info(f"Received response from {self.get_provider_name()}: {response[:100]}...")
            
            return response
            
        except Exception as e:
            logger.error(f"Error calling {self.get_provider_name()}: {str(e)}")
            raise
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of the LLM provider."""
        pass
    
    def get_default_parameters(self) -> Dict[str, Any]:
        """Get default parameters for the LLM."""
        return {
            "max_tokens": 1000,
            "temperature": 0.7
        }
