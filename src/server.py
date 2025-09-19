"""
AZEBAL MCP Server

Basic MCP server implementation using FastMCP library.
Supports both stdio and SSE transport methods.
"""

from fastmcp import FastMCP
from src.tools.greeting import greeting_tool


def create_mcp_server() -> FastMCP:
    """
    Creates and configures the AZEBAL MCP server.
    
    Returns:
        FastMCP: Configured MCP server instance
    """
    # Create FastMCP server instance
    mcp = FastMCP("AZEBAL")
    
    # Register the greeting tool
    @mcp.tool()
    def greeting() -> str:
        """A simple greeting tool that returns 'hello'"""
        result = greeting_tool()
        return result["message"]
    
    return mcp


def main():
    """Main entry point for the MCP server."""
    server = create_mcp_server()
    server.run()


if __name__ == "__main__":
    main()
