"""
Login Tool for AZEBAL

MCP tool for authenticating users with Azure access tokens.
"""

from typing import Dict, Any

from src.core.auth import AzureAuthService
from src.core.jwt_service import JWTService
from src.core.config import settings
from src.core.logging_config import get_logger

logger = get_logger(__name__)


def login_tool(azure_access_token: str) -> Dict[str, Any]:
    """
    Authenticate user with AZEBAL using Azure CLI access token.
    
    This function validates the provided Azure access token through the Azure Management API,
    extracts user information, and creates a secure AZEBAL JWT token for session management.

    PREREQUISITES:
    - User must have Azure CLI installed and authenticated
    - User must have access to at least one Azure subscription
    - Azure access token must be valid and not expired

    AZURE CLI SETUP STEPS:
    1. Install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
    2. Login: 'az login'
    3. Set subscription: 'az account set --subscription "Your-Subscription-Name"'
    4. Get token: 'az account get-access-token --query accessToken --output tsv'

    Args:
        azure_access_token (str): Azure CLI access token obtained from 'az account get-access-token'.
                                 Must be a valid JWT token with proper Azure permissions.

    Returns:
        Dict[str, Any]: Authentication result containing:
            - success (bool): Whether authentication was successful
            - message (str): Human-readable status message
            - azebal_token (str, optional): AZEBAL JWT token for session management
            - user_info (dict, optional): Extracted user information from Azure token
            - error (str, optional): Error code if authentication failed

    Raises:
        No exceptions are raised - all errors are returned in the response dict

    Example:
        >>> result = login_tool("eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIs...")
        >>> if result["success"]:
        ...     print(f"Welcome {result['user_info']['user_principal_name']}")
        ...     azebal_token = result["azebal_token"]
        ... else:
        ...     print(f"Login failed: {result['message']}")
    """
    try:
        logger.info("Starting login process with Azure access token")

        # Initialize services
        auth_service = AzureAuthService(subscription_id=settings.azure_subscription_id)
        jwt_service = JWTService()

        # Authenticate user with Azure
        is_authenticated, user_info = auth_service.authenticate_user(azure_access_token)

        if not is_authenticated or not user_info:
            logger.warning("Authentication failed")
            return {
                "success": False,
                "message": "Authentication failed. Please check your Azure access token.",
                "error": "INVALID_TOKEN",
            }

        # Create AZEBAL JWT token
        try:
            azebal_token = jwt_service.create_token(user_info)
            logger.info(f"Login successful for user: {user_info.user_principal_name}")

            return {
                "success": True,
                "message": "Login successful",
                "azebal_token": azebal_token,
                "user_info": {
                    "object_id": user_info.object_id,
                    "user_principal_name": user_info.user_principal_name,
                    "tenant_id": user_info.tenant_id,
                    "display_name": user_info.display_name,
                    "email": user_info.email,
                },
            }

        except Exception as e:
            logger.error(f"Error creating AZEBAL token: {e}")
            return {
                "success": False,
                "message": "Login failed due to internal error",
                "error": "TOKEN_CREATION_FAILED",
            }

    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        return {
            "success": False,
            "message": "Login failed due to unexpected error",
            "error": "UNEXPECTED_ERROR",
        }
