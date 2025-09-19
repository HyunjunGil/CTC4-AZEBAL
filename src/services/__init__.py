"""
AZEBAL Services Module

Contains external service integrations:
- Azure API client for resource queries
- Third-party service connectors
"""

from .azure_client import AzureAPIClient

__all__ = ["AzureAPIClient"]
