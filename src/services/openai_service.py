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
    
    async def _call_llm_with_functions(
        self, 
        messages: list, 
        functions: list, 
        **kwargs
    ) -> Dict[str, Any]:
        """
        Call OpenAI API with function calling support.
        
        Args:
            messages: List of conversation messages
            functions: List of function definitions
            **kwargs: Additional parameters (max_tokens, temperature, etc.)
            
        Returns:
            Dict containing the LLM response with potential function calls
            
        Raises:
            Exception: If the API call fails
        """
        # Prepare function definitions for OpenAI
        function_definitions = []
        for func in functions:
            function_definitions.append({
                "name": func["name"],
                "description": func["description"],
                "parameters": func["parameters"]
            })
        
        response = self.client.chat.completions.create(
            model=kwargs.get("model", self.model_name),
            messages=messages,
            functions=function_definitions,
            function_call="auto",  # Let the model decide when to call functions
            max_tokens=kwargs.get("max_tokens", 1000),
            temperature=kwargs.get("temperature", 0.7)
        )
        
        message = response.choices[0].message
        
        # Check if the model wants to call a function
        if message.function_call:
            return {
                "function_call": {
                    "name": message.function_call.name,
                    "arguments": message.function_call.arguments
                }
            }
        else:
            return {
                "content": message.content
            }