# 12. Coding Standards

## 12.1. Code Style and Formatting

### Python Code Style
- **Formatter**: `Black` with default settings (88 character line length)
- **Linter**: `Flake8` with configuration in `setup.cfg` or `pyproject.toml`
- **Import Sorting**: `isort` with Black-compatible profile
- **Type Checking**: `mypy` with strict mode enabled
- **Naming Convention**: Follow PEP 8 strictly

### Code Formatting Rules
```bash
# Auto-format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/
mypy src/
```

## 12.2. Type Hints and Documentation

### Type Hints (MANDATORY)
- **100% type hinting required** for all function parameters, return values, and class attributes
- Use `typing` module for complex types
- Use `typing.Optional` for nullable values
- Use `typing.Union` or `|` syntax for union types (Python 3.10+)
- Use `typing.Protocol` for structural subtyping

```python
from typing import Dict, List, Optional, Union, Protocol
from pydantic import BaseModel

class UserData(BaseModel):
    id: int
    name: str
    email: Optional[str] = None

def process_users(users: List[UserData]) -> Dict[str, int]:
    """Process user data and return statistics."""
    return {"total": len(users), "with_email": sum(1 for u in users if u.email)}
```

### Docstring Standards
- Use Google-style docstrings for all public functions, classes, and modules
- Include type information, parameter descriptions, return values, and exceptions
- Include usage examples for complex functions

```python
def authenticate_user(token: str, required_scopes: List[str]) -> Optional[UserData]:
    """
    Authenticate user using JWT token and validate required scopes.
    
    Args:
        token: JWT token string
        required_scopes: List of required OAuth scopes
        
    Returns:
        UserData if authentication successful, None otherwise
        
    Raises:
        AuthenticationError: If token is invalid or expired
        ScopeError: If user lacks required scopes
        
    Example:
        >>> user = authenticate_user("jwt_token", ["read:users"])
        >>> if user:
        ...     print(f"Welcome {user.name}")
    """
```

## 12.3. Project Structure Standards

### File Organization
- Follow the established source tree structure in `9-source-tree.md`
- Place related functionality in appropriate modules
- Keep modules focused and single-purpose
- Use `__init__.py` files to control public API

### Import Organization
```python
# Standard library imports
import os
import sys
from typing import Dict, List

# Third-party imports
import structlog
from fastapi import FastAPI
from pydantic import BaseModel

# Local imports
from src.core.config import settings
from src.services.azure_client import AzureClient
```

## 12.4. Error Handling and Logging

### Structured Logging
- Use `structlog` for all logging
- Include correlation IDs for request tracing
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Never log sensitive information (passwords, tokens, PII)

```python
import structlog

logger = structlog.get_logger(__name__)

def process_request(request_id: str, data: Dict[str, Any]) -> None:
    logger.info("Processing request", request_id=request_id, data_keys=list(data.keys()))
    
    try:
        result = validate_data(data)
        logger.info("Request processed successfully", request_id=request_id)
    except ValidationError as e:
        logger.error("Validation failed", request_id=request_id, error=str(e))
        raise
```

### Exception Handling
- Create custom exception classes for domain-specific errors
- Use specific exception types rather than generic `Exception`
- Always include context in exception messages
- Use `raise ... from e` for exception chaining

```python
class AzureServiceError(Exception):
    """Base exception for Azure service operations."""
    pass

class AuthenticationError(AzureServiceError):
    """Raised when authentication fails."""
    pass

def authenticate_with_azure(credentials: str) -> str:
    try:
        return azure_client.authenticate(credentials)
    except AzureClientError as e:
        raise AuthenticationError(f"Failed to authenticate with Azure: {e}") from e
```

## 12.5. Testing Standards

### Test Organization
- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- End-to-end tests in `tests/e2e/`
- Use descriptive test names that explain the scenario
- One test per assertion when possible

### Test Structure
```python
import pytest
from unittest.mock import Mock, patch
from src.services.azure_client import AzureClient

class TestAzureClient:
    """Test suite for AzureClient."""
    
    @pytest.fixture
    def azure_client(self):
        """Create AzureClient instance for testing."""
        return AzureClient(api_key="test_key")
    
    def test_authenticate_success(self, azure_client):
        """Test successful authentication."""
        # Arrange
        credentials = "valid_credentials"
        expected_token = "access_token"
        
        with patch.object(azure_client, '_make_request') as mock_request:
            mock_request.return_value = {"access_token": expected_token}
            
            # Act
            result = azure_client.authenticate(credentials)
            
            # Assert
            assert result == expected_token
            mock_request.assert_called_once_with("auth", {"credentials": credentials})
    
    def test_authenticate_invalid_credentials(self, azure_client):
        """Test authentication with invalid credentials."""
        # Arrange
        credentials = "invalid_credentials"
        
        with patch.object(azure_client, '_make_request') as mock_request:
            mock_request.side_effect = AuthenticationError("Invalid credentials")
            
            # Act & Assert
            with pytest.raises(AuthenticationError, match="Invalid credentials"):
                azure_client.authenticate(credentials)
```

### Test Coverage
- Maintain minimum 80% code coverage
- Test all public methods and functions
- Test error conditions and edge cases
- Use `pytest-cov` for coverage reporting

## 12.6. Configuration and Environment

### Configuration Management
- Use `pydantic-settings` for configuration validation
- Store sensitive data in environment variables
- Provide sensible defaults for development
- Validate configuration at startup

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings."""
    
    # Azure Configuration
    azure_tenant_id: str
    azure_client_id: str
    azure_client_secret: str
    
    # Database Configuration
    database_url: str = "sqlite:///./azebal.db"
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "json"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

## 12.7. Security Standards

### Input Validation
- Validate all external inputs using Pydantic models
- Sanitize user inputs before processing
- Use parameterized queries for database operations
- Implement rate limiting for API endpoints

### Secret Management
- Never commit secrets to version control
- Use Azure Key Vault for production secrets
- Rotate secrets regularly
- Use environment variables for local development

## 12.8. Performance Standards

### Code Performance
- Use async/await for I/O operations
- Implement proper connection pooling
- Cache frequently accessed data
- Profile code for performance bottlenecks

### Memory Management
- Use context managers for resource management
- Implement proper cleanup in destructors
- Monitor memory usage in production
- Use generators for large datasets

## 12.9. Code Review Checklist

Before submitting code for review, ensure:

- [ ] All functions have type hints and docstrings
- [ ] Code follows PEP 8 and Black formatting
- [ ] All tests pass with 80%+ coverage
- [ ] No hardcoded secrets or sensitive data
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate and structured
- [ ] Configuration is externalized
- [ ] Dependencies are properly managed
- [ ] Code is properly documented
- [ ] Performance considerations are addressed

## 12.10. Development Tools

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
```

### IDE Configuration
- Configure your IDE to use Black for formatting
- Enable type checking with mypy
- Use flake8 for linting
- Set up auto-formatting on save
