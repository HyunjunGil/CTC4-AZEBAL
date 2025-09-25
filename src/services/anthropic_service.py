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
    
    async def _call_llm_with_functions(
        self, 
        messages: list, 
        functions: list, 
        **kwargs
    ) -> Dict[str, Any]:
        """
        Call Anthropic Claude API with function calling support.
        
        Note: Anthropic uses "tools" instead of "functions" but we'll adapt the interface.
        
        Args:
            messages: List of conversation messages
            functions: List of function definitions
            **kwargs: Additional parameters (max_tokens, temperature, etc.)
            
        Returns:
            Dict containing the LLM response with potential function calls
            
        Raises:
            Exception: If the API call fails
        """
        # Convert function definitions to Anthropic tools format
        tools = []
        for func in functions:
            tools.append({
                "name": func["name"],
                "description": func["description"],
                "input_schema": func["parameters"]
            })
        
        # Convert messages to Anthropic format
        anthropic_messages = []
        for msg in messages:
            if msg["role"] == "system":
                # Anthropic handles system messages differently
                anthropic_messages.append({
                    "role": "user",
                    "content": f"System: {msg['content']}"
                })
            elif msg["role"] == "function":
                # Anthropic uses tool_result for function responses
                anthropic_messages.append({
                    "role": "user",
                    "content": f"Function {msg['name']} result: {msg['content']}"
                })
            else:
                anthropic_messages.append(msg)
        
        response = self.client.messages.create(
            model=kwargs.get("model", self.model_name),
            max_tokens=kwargs.get("max_tokens", 1000),
            temperature=kwargs.get("temperature", 0.7),
            messages=anthropic_messages,
            tools=tools,
            tool_choice={"type": "auto"}  # Let the model decide when to use tools
        )
        
        # Check if the model wants to use a tool
        if response.content and response.content[0].type == "tool_use":
            tool_use = response.content[0]
            return {
                "function_call": {
                    "name": tool_use.name,
                    "arguments": tool_use.input
                }
            }
        else:
            # Extract text content
            text_content = ""
            for content in response.content:
                if content.type == "text":
                    text_content += content.text
            
            return {
                "content": text_content
            }