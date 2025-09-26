"""
Azure Authentication Service

Handles Azure access token validation and user information extraction.
"""

from typing import Optional, Tuple
from dataclasses import dataclass

import jwt
import httpx

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class UserInfo:
    """User information extracted from Azure access token."""

    object_id: str
    user_principal_name: str
    tenant_id: str
    display_name: Optional[str] = None
    email: Optional[str] = None


class AzureAuthService:
    """Service for Azure authentication and token validation."""

    def __init__(self):
        """Initialize Azure authentication service."""
        pass

    def validate_access_token(self, access_token: str) -> bool:
        """
        Validate Azure access token by making a test API call.

        Args:
            access_token: Azure access token to validate

        Returns:
            bool: True if token is valid, False otherwise
        """
        try:
            # Test the token by making a simple API call to Azure Management API
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            # Use a lightweight API call to validate the token
            # This calls the Azure Resource Manager API to get subscription info
            url = "https://management.azure.com/subscriptions?api-version=2021-04-01"

            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, headers=headers)

                if response.status_code == 200:
                    logger.info("Azure access token validation successful")
                    return True
                elif response.status_code == 401:
                    logger.warning("Azure access token validation failed: Unauthorized")
                    return False
                else:
                    logger.warning(
                        f"Azure access token validation failed with status: {response.status_code}"
                    )
                    return False

        except httpx.RequestError as e:
            logger.error(f"Network error during token validation: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during token validation: {e}")
            return False

    def extract_user_info(self, access_token: str) -> Optional[UserInfo]:
        """
        Extract user information from Azure access token.

        Args:
            access_token: Azure access token containing user information

        Returns:
            UserInfo: Extracted user information or None if extraction fails
        """
        try:
            # Decode the JWT token without verification (we already validated it)
            # Note: In production, you might want to verify the token signature
            decoded_token = jwt.decode(access_token, options={"verify_signature": False})

            # Extract user information from token claims
            object_id = decoded_token.get("oid")
            user_principal_name = decoded_token.get("upn") or decoded_token.get(
                "preferred_username"
            )
            tenant_id = decoded_token.get("tid")
            display_name = decoded_token.get("name")
            email = decoded_token.get("email") or user_principal_name

            if not object_id or not tenant_id:
                logger.error("Missing required user information in token")
                return None

            user_info = UserInfo(
                object_id=object_id,
                user_principal_name=user_principal_name or "",
                tenant_id=tenant_id,
                display_name=display_name,
                email=email,
            )

            logger.info(f"Successfully extracted user info for: {user_info.user_principal_name}")
            return user_info

        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid JWT token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error extracting user info from token: {e}")
            return None

    def authenticate_user(self, access_token: str) -> Tuple[bool, Optional[UserInfo]]:
        """
        Complete authentication process: validate token and extract user info.

        Args:
            access_token: Azure access token to authenticate

        Returns:
            Tuple[bool, Optional[UserInfo]]: (is_valid, user_info)
        """
        logger.info("Starting Azure user authentication process")

        # Step 1: Validate the access token
        if not self.validate_access_token(access_token):
            logger.warning("Token validation failed")
            return False, None

        # Step 2: Extract user information
        user_info = self.extract_user_info(access_token)
        if not user_info:
            logger.warning("Failed to extract user information from token")
            return False, None

        logger.info(f"Authentication successful for user: {user_info.user_principal_name}")
        return True, user_info
