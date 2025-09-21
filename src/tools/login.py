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
    Login tool that authenticates users with Azure access tokens.

    Args:
        azure_access_token: Azure CLI access token for authentication

    Returns:
        Dict containing login result and AZEBAL JWT token if successful
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
