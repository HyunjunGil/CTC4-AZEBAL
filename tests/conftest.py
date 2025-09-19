"""
Global pytest configuration and fixtures for AZEBAL tests.

This module provides common fixtures and test configuration used across
all test modules in the AZEBAL test suite.
"""

import asyncio
import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, Mock

import pytest
from redis import Redis

# Set test environment variables before importing application modules
os.environ["ENVIRONMENT"] = "test"
os.environ["TESTING"] = "true"
os.environ["MOCK_AZURE_APIS"] = "true"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_redis() -> Mock:
    """Mock Redis client for testing."""
    redis_mock = Mock(spec=Redis)
    redis_mock.hget.return_value = None
    redis_mock.hset.return_value = True
    redis_mock.delete.return_value = 1
    redis_mock.exists.return_value = False
    return redis_mock


@pytest.fixture
def mock_azure_client() -> Mock:
    """Mock Azure API client for testing."""
    from src.services.azure_client import AzureAPIClient
    
    azure_mock = Mock(spec=AzureAPIClient)
    azure_mock.get_subscriptions.return_value = []
    azure_mock.get_resource_groups.return_value = []
    azure_mock.get_virtual_machines.return_value = []
    return azure_mock


@pytest.fixture
def mock_openai_client() -> AsyncMock:
    """Mock OpenAI/Azure OpenAI client for testing."""
    openai_mock = AsyncMock()
    openai_mock.chat.completions.create.return_value.choices = [
        Mock(message=Mock(content="Mock LLM response"))
    ]
    return openai_mock


@pytest.fixture
def sample_user_session() -> dict:
    """Sample user session data for testing."""
    return {
        "user_principal_name": "test.user@kt.com",
        "ms_access_token": "encrypted_ms_token_data",
        "ms_refresh_token": "encrypted_refresh_token_data",
        "expires_at": "2025-09-19T12:00:00Z",
        "created_at": "2025-09-19T10:00:00Z"
    }


@pytest.fixture
def sample_debug_request() -> dict:
    """Sample debug error request for testing."""
    return {
        "access_token": "valid_azebal_token",
        "error_summary": "Azure Container Registry authentication failed",
        "extra_source_code": """
        # Kubernetes deployment configuration
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: sample-app
        spec:
          template:
            spec:
              containers:
              - name: app
                image: myacr.azurecr.io/sample-app:latest
        """
    }


@pytest.fixture
def sample_azure_resources() -> dict:
    """Sample Azure resource data for testing."""
    return {
        "subscriptions": [
            {
                "id": "/subscriptions/12345678-1234-1234-1234-123456789012",
                "displayName": "KT Development Subscription"
            }
        ],
        "resource_groups": [
            {
                "name": "rg-azebal-dev",
                "location": "koreacentral"
            }
        ],
        "container_registries": [
            {
                "name": "myacr",
                "loginServer": "myacr.azurecr.io",
                "adminUserEnabled": False
            }
        ]
    }


# Test categories and markers
pytestmark = pytest.mark.asyncio
