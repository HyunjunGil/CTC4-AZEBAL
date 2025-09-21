"""
AZEBAL Greeting Tool

A simple test tool that returns a greeting message.
"""

from typing import Any, Dict


def greeting_tool() -> Dict[str, Any]:
    """
    A simple greeting tool that returns 'hello'.

    Returns:
        Dict[str, Any]: A dictionary containing the greeting message
    """
    return {"message": "hello"}
