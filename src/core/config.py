"""
Configuration management for AZEBAL.

Handles environment variables and application settings.
"""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Azure Configuration
    azure_subscription_id: Optional[str] = Field(
        default=None, description="Azure subscription ID for resource management operations"
    )

    # Redis Configuration
    redis_host: str = Field(default="localhost", description="Redis host for session storage")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    redis_db: int = Field(default=0, description="Redis database number")

    # JWT Configuration
    jwt_secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT token signing",
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiration_hours: int = Field(default=24, description="JWT token expiration time in hours")

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    secure_logging: bool = Field(default=False, description="Enable secure logging mode")

    # MCP Server Configuration
    mcp_port: int = Field(default=8443, description="MCP server port")
    mcp_http_port: int = Field(default=8000, description="MCP HTTP server port")
    use_https: bool = Field(default=False, description="Use HTTPS for MCP server")

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra environment variables that aren't defined
    )


# Global settings instance
settings = Settings()
