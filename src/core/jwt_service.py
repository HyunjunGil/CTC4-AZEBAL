"""
JWT Service for AZEBAL

Handles creation and validation of AZEBAL-specific JWT tokens.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

import jwt
from src.core.config import settings
from src.core.auth import UserInfo
from src.core.token_storage import token_storage
from .logging_config import get_logger

logger = get_logger(__name__)


class JWTService:
    """Service for managing AZEBAL JWT tokens."""

    def __init__(self):
        """Initialize JWT service with configuration."""
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.expiration_hours = settings.jwt_expiration_hours

    def create_token(self, user_info: UserInfo, azure_access_token: str, subscription_id: Optional[str] = None) -> str:
        """
        Create an AZEBAL JWT token for the authenticated user.

        Args:
            user_info: User information from Azure authentication
            azure_access_token: Azure access token to store securely
            subscription_id: Optional Azure subscription ID

        Returns:
            str: JWT token string
        """
        try:
            # Store Azure access token securely and get session ID
            session_id = token_storage.store_token(
                user_principal_name=user_info.user_principal_name,
                azure_access_token=azure_access_token,
                expires_in_hours=self.expiration_hours
            )
            
            # Calculate expiration time
            expiration_time = datetime.now(timezone.utc) + timedelta(hours=self.expiration_hours)

            # Create token payload
            payload = {
                "sub": user_info.object_id,  # Subject (user ID)
                "user_principal_name": user_info.user_principal_name,  # Use consistent key name
                "tenant_id": user_info.tenant_id,
                "display_name": user_info.display_name,
                "email": user_info.email,
                "session_id": session_id,  # Reference to stored Azure token
                "iat": datetime.now(timezone.utc),  # Issued at
                "exp": expiration_time,  # Expiration
                "iss": "azebal",  # Issuer
                "aud": "azebal-client",  # Audience
            }

            # Generate JWT token
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

            logger.info(f"Created JWT token for user: {user_info.user_principal_name}")
            return token

        except Exception as e:
            logger.error(f"Error creating JWT token: {e}")
            raise

    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify and decode AZEBAL JWT token (alias for validate_token)."""
        return self.validate_token(token)
    
    def validate_token(self, token: str) -> Optional[Dict]:
        """
        Validate and decode an AZEBAL JWT token.

        Args:
            token: JWT token to validate

        Returns:
            Dict: Decoded token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                audience="azebal-client",
                issuer="azebal",
            )

            logger.info(f"JWT token validated for user: {payload.get('user_principal_name')}")
            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error validating JWT token: {e}")
            return None

    def get_user_info_from_token(self, token: str) -> Optional[UserInfo]:
        """
        Extract user information from a valid JWT token.

        Args:
            token: JWT token containing user information

        Returns:
            UserInfo: User information if token is valid, None otherwise
        """
        payload = self.validate_token(token)
        if not payload:
            return None

        try:
            return UserInfo(
                object_id=payload["sub"],
                user_principal_name=payload["user_principal_name"],
                tenant_id=payload["tenant_id"],
                display_name=payload.get("display_name"),
                email=payload.get("email"),
            )
        except KeyError as e:
            logger.error(f"Missing required field in JWT payload: {e}")
            return None
    
    def get_azure_access_token(self, azebal_token: str) -> Optional[str]:
        """
        Get Azure access token from AZEBAL JWT token.
        
        Args:
            azebal_token: AZEBAL JWT token
            
        Returns:
            str: Azure access token or None if not found/expired
        """
        payload = self.validate_token(azebal_token)
        if not payload:
            return None
        
        session_id = payload.get("session_id")
        if not session_id:
            logger.error("No session_id found in JWT token")
            return None
        
        azure_token = token_storage.get_token(session_id)
        if not azure_token:
            logger.warning(f"Azure token not found or expired for session: {session_id}")
            return None
        
        return azure_token
