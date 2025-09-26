"""
Logging configuration for AZEBAL.

Provides consistent logging format across all modules.
"""

import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO", log_format: Optional[str] = None, use_stderr: bool = True) -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Custom log format string
        use_stderr: If True, log to stderr instead of stdout (important for MCP stdio)
    """
    if log_format is None:
        log_format = (
            "%(asctime)s [%(levelname)-8s] %(message)s "
            "(%(name)s:%(lineno)d)"
        )
    
    # Use stderr for logging to avoid interfering with MCP stdio communication
    stream = sys.stderr if use_stderr else sys.stdout
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(stream)
        ],
        force=True  # Override any existing configuration
    )
    
    # Set specific loggers to appropriate levels
    logging.getLogger("azure").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Ensure our loggers use the configured level
    azebal_loggers = [
        "src.core.auth",
        "src.core.jwt_service", 
        "src.tools.login",
        "src.server"
    ]
    
    for logger_name in azebal_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, level.upper()))


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with consistent configuration.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def disable_logging() -> None:
    """
    Disable all logging to ensure clean MCP stdio communication.
    Use this when running in stdio mode to avoid interfering with JSON-RPC.
    """
    logging.disable(logging.CRITICAL)


def enable_logging(level: str = "INFO") -> None:
    """
    Re-enable logging after it was disabled.
    
    Args:
        level: Logging level to enable
    """
    logging.disable(logging.NOTSET)
    setup_logging(level=level, use_stderr=True)
