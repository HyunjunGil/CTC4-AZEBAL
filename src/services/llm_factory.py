"""
LLM Factory for AZEBAL.

Creates and manages LLM service instances based on configuration.
"""

import logging
from typing import Dict, Type
from src.core.config import settings
from src.services.llm_interface import LLMInterface, LLMProvider
from src.services.azure_openai_service import AzureOpenAIService
from src.services.openai_service import OpenAIService
from src.services.anthropic_service import AnthropicService

logger = logging.getLogger(__name__)


class LLMFactory:
    """Factory class for creating LLM service instances."""
    
    _providers: Dict[LLMProvider, Type[LLMInterface]] = {
        LLMProvider.AZURE_OPENAI: AzureOpenAIService,
        LLMProvider.OPENAI: OpenAIService,
        LLMProvider.ANTHROPIC: AnthropicService,
    }
    
    _instance: LLMInterface = None
    
    @classmethod
    def get_llm_service(cls) -> LLMInterface:
        """
        Get the configured LLM service instance.
        
        Returns:
            LLMInterface: The configured LLM service
            
        Raises:
            ValueError: If the provider is not supported
            RuntimeError: If no provider is configured
        """
        if cls._instance is None:
            cls._instance = cls._create_llm_service()
        
        return cls._instance
    
    @classmethod
    def _create_llm_service(cls) -> LLMInterface:
        """Create a new LLM service instance based on configuration."""
        provider_name = settings.llm_provider
        
        if not provider_name:
            # Try to auto-detect based on available configurations
            provider_name = cls._auto_detect_provider()
        
        try:
            provider = LLMProvider(provider_name)
        except ValueError:
            raise ValueError(f"Unsupported LLM provider: {provider_name}")
        
        if provider not in cls._providers:
            raise ValueError(f"Provider {provider.value} is not implemented")
        
        service_class = cls._providers[provider]
        service = service_class()
        
        if not service.is_configured():
            logger.warning(f"LLM provider {service.get_provider_name()} is not properly configured")
        
        logger.info(f"Using LLM provider: {service.get_provider_name()}")
        return service
    
    @classmethod
    def _auto_detect_provider(cls) -> str:
        """
        Auto-detect available LLM provider based on configuration.
        
        Returns:
            str: The provider name
            
        Raises:
            RuntimeError: If no provider is configured
        """
        # Check Azure OpenAI first
        if settings.azure_openai_endpoint and settings.azure_openai_api_key:
            return LLMProvider.AZURE_OPENAI.value
        
        # Check OpenAI
        if settings.openai_api_key:
            return LLMProvider.OPENAI.value
        
        # Check Anthropic
        if settings.anthropic_api_key:
            return LLMProvider.ANTHROPIC.value
        
        raise RuntimeError(
            "No LLM provider is configured. Please set one of: "
            "AZURE_OPENAI_ENDPOINT+AZURE_OPENAI_API_KEY, "
            "OPENAI_API_KEY, or ANTHROPIC_API_KEY"
        )
    
    @classmethod
    def reset(cls):
        """Reset the factory instance (useful for testing)."""
        cls._instance = None
    
    @classmethod
    def list_available_providers(cls) -> Dict[str, bool]:
        """
        List all available providers and their configuration status.
        
        Returns:
            Dict[str, bool]: Provider name -> is_configured mapping
        """
        status = {}
        for provider in LLMProvider:
            try:
                service_class = cls._providers[provider]
                service = service_class()
                status[provider.value] = service.is_configured()
            except Exception as e:
                logger.warning(f"Error checking provider {provider.value}: {e}")
                status[provider.value] = False
        
        return status


# Global factory instance
llm_factory = LLMFactory()
