"""
Tests for the greeting tool.
"""

import pytest
from src.tools.greeting import greeting_tool


class TestGreetingTool:
    """Test cases for the greeting tool."""
    
    def test_greeting_tool_returns_hello(self):
        """Test that greeting tool returns 'hello' message."""
        result = greeting_tool()
        
        assert isinstance(result, dict)
        assert "message" in result
        assert result["message"] == "hello"
    
    def test_greeting_tool_structure(self):
        """Test that greeting tool returns correct structure."""
        result = greeting_tool()
        
        assert isinstance(result, dict)
        assert len(result) == 1
        assert list(result.keys()) == ["message"]
