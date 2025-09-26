"""
Ask LLM tool for AZEBAL MCP server.

Provides a simple interface to ask questions to various LLM providers.
Compatible with FastMCP framework.
"""

import logging
from src.services.llm_factory import llm_factory

logger = logging.getLogger(__name__)


async def ask_llm_tool(question: str) -> str:
    """
    Ask a question to the LLM and get a response.
    
    This tool provides a simple interface to ask questions to various LLM providers.
    No authentication is required for this tool.
    
    Args:
        question (str): The question to ask the LLM (e.g., 'What is 3 + 3?', 'Who is Albert Einstein?')
            
    Returns:
        str: The LLM's response as plain text
        
    Examples:
        ask_llm_tool("What is 3 + 3?")
        ask_llm_tool("Who is Albert Einstein?")
        ask_llm_tool("Explain the concept of machine learning")
    """
    if not question or not question.strip():
        return "Error: Please provide a question to ask the LLM."
    
    try:
        # Get LLM service from factory
        llm_service = llm_factory.get_llm_service()
        
        # Check if LLM service is configured
        if not llm_service.is_configured():
            available_providers = llm_factory.list_available_providers()
            configured_providers = [p for p, configured in available_providers.items() if configured]
            
            if configured_providers:
                return f"Error: Current LLM provider ({llm_service.get_provider_name()}) is not configured. Available configured providers: {', '.join(configured_providers)}"
            else:
                return "Error: No LLM provider is configured. Please set API keys for one of: Azure OpenAI, OpenAI, or Anthropic."
        
        # Get response from LLM
        response = await llm_service.ask_llm(question)
        logger.info(f"LLM response received from {llm_service.get_provider_name()}")
        return response
        
    except Exception as e:
        logger.error(f"Error in ask_llm_tool: {str(e)}")
        return f"Error: {str(e)}"


