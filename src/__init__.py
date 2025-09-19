"""
AZEBAL - Azure Error Analysis & BreALdown
An MCP server for IDE AI agents that provides real-time Azure error debugging.

This package contains the core AZEBAL server implementation.
"""

__version__ = "0.1.0"
__author__ = "AZEBAL Team"
__email__ = "azebal@kt.com"

# Package level imports for convenience
from src.server import create_mcp_server

__all__ = ["create_mcp_server"]
