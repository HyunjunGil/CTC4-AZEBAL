"""
Login Tool for AZEBAL

MCP tool for authenticating users with Azure access tokens.
"""

from typing import Dict, Any
import hashlib
import re

from src.core.auth import AzureAuthService
from src.core.jwt_service import JWTService
from src.core.config import settings
from src.core.logging_config import get_logger

logger = get_logger(__name__)


def safe_token_hash(token: str) -> str:
    """토큰을 안전하게 해시화하여 로깅용으로 사용"""
    if not token or len(token) < 10:
        return "***INVALID***"
    
    # 앞 6글자 + 해시 8글자로 식별 가능하면서 안전한 형태
    prefix = token[:6]
    token_hash = hashlib.sha256(token.encode()).hexdigest()[:8]
    return f"{prefix}...{token_hash}"


def sanitize_error_message(message: str) -> str:
    """에러 메시지에서 토큰 같은 민감한 정보 제거"""
    # JWT 패턴 제거 (eyJ로 시작하는 긴 문자열)
    jwt_pattern = r'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'
    message = re.sub(jwt_pattern, '[REDACTED_TOKEN]', message)
    
    # Bearer 토큰 패턴 제거
    bearer_pattern = r'Bearer\s+[A-Za-z0-9_-]+'
    message = re.sub(bearer_pattern, 'Bearer [REDACTED]', message)
    
    return message


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
    # 토큰 해시 생성 (로깅용)
    token_hash = safe_token_hash(azure_access_token)
    
    try:
        logger.info(f"Starting login process for token: {token_hash}")

        # 기본 유효성 검사
        if not azure_access_token or not azure_access_token.strip():
            logger.warning(f"Empty token provided: {token_hash}")
            return {
                "success": False,
                "message": "Azure access token is required",
                "error": "EMPTY_TOKEN",
            }

        # Initialize services
        auth_service = AzureAuthService()
        jwt_service = JWTService()

        # Authenticate user with Azure
        is_authenticated, user_info = auth_service.authenticate_user(azure_access_token)

        if not is_authenticated or not user_info:
            logger.warning(f"Authentication failed for token: {token_hash}")
            return {
                "success": False,
                "message": "Authentication failed. Please check your Azure access token.",
                "error": "INVALID_TOKEN",
            }

        # Create AZEBAL JWT token with Azure access token
        try:
            azebal_token = jwt_service.create_token(user_info, azure_access_token)
            
            logger.info(f"Login successful for user: {user_info.user_principal_name} (token: {token_hash})")

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
            error_msg = sanitize_error_message(str(e))
            logger.error(f"Error creating AZEBAL token for user (token: {token_hash}): {error_msg}")
            return {
                "success": False,
                "message": "Login failed due to internal error",
                "error": "TOKEN_CREATION_FAILED",
            }

    except Exception as e:
        error_msg = sanitize_error_message(str(e))
        logger.error(f"Unexpected error during login for token {token_hash}: {error_msg}")
        return {
            "success": False,
            "message": "Login failed due to unexpected error",
            "error": "UNEXPECTED_ERROR",
        }
