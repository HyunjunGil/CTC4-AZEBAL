"""
AZEBAL MCP Server

Basic MCP server implementation using FastMCP library.
Supports both stdio and SSE transport methods.
"""

from fastmcp import FastMCP
from src.tools.greeting import greeting_tool
from src.tools.login import login_tool
from src.core.logging_config import setup_logging, disable_logging


def create_mcp_server(disable_logs: bool = False) -> FastMCP:
    """
    Creates and configures the AZEBAL MCP server.

    Args:
        disable_logs: If True, disable logging to prevent stdio interference
        
    Returns:
        FastMCP: Configured MCP server instance
    """
    # Initialize or disable logging based on mode
    if disable_logs:
        disable_logging()
    else:
        setup_logging(level="INFO", use_stderr=True)
    
    # Create FastMCP server instance
    mcp = FastMCP("AZEBAL")

    # Register the greeting tool
    @mcp.tool()
    def greeting() -> str:
        """A simple greeting tool that returns 'hello'"""
        result = greeting_tool()
        return result["message"]

    # Register the login tool
    @mcp.tool()
    def login(azure_access_token: str) -> dict:
        """
        Login to AZEBAL using Azure CLI access token.

        Args:
            azure_access_token: Azure CLI access token obtained from 'az account get-access-token'

        Returns:
            dict: Login result with AZEBAL JWT token if successful
        """
        return login_tool(azure_access_token)

    return mcp


def main():
    """Main entry point for the MCP server."""
    server = create_mcp_server()
    server.run()


if __name__ == "__main__":
    main()
