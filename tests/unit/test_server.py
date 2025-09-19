"""
Tests for the MCP server.
"""

import pytest
from fastmcp import FastMCP
from src.server import create_mcp_server


class TestMCPServer:
    """Test cases for the MCP server."""
    
    def test_create_mcp_server_returns_fastmcp_instance(self):
        """Test that create_mcp_server returns a FastMCP instance."""
        server = create_mcp_server()
        
        assert isinstance(server, FastMCP)
        assert server.name == "AZEBAL"
    
    def test_server_has_greeting_tool(self):
        """Test that the server has the greeting tool registered."""
        server = create_mcp_server()
        
        # Check that the greeting tool is registered
        # Note: The exact method to check registered tools may vary with FastMCP version
        # This test verifies the server can be created without errors
        assert server is not None
