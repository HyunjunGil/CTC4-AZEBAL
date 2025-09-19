"""
AZEBAL Tools Module

This module contains MCP tool definitions and schemas for the AZEBAL server.
Implements the 'login' and 'debug_error' tools as specified in the PRD.
"""

from .definitions import login_tool, debug_error_tool
from .schemas import LoginRequest, LoginResponse, DebugErrorRequest, DebugErrorResponse

__all__ = [
    "login_tool",
    "debug_error_tool", 
    "LoginRequest",
    "LoginResponse",
    "DebugErrorRequest", 
    "DebugErrorResponse"
]
