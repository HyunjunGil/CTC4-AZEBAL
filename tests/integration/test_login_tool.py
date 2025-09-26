"""
Integration tests for login tool.
"""

import pytest
from unittest.mock import patch, Mock
import httpx

from src.tools.login import login_tool


class TestLoginTool:
    """Test cases for login tool integration."""
    
    @patch('src.tools.login.AzureAuthService')
    @patch('src.tools.login.JWTService')
    def test_login_success(self, mock_jwt_service_class, mock_auth_service_class):
        """Test successful login flow."""
        # Mock authentication service
        mock_auth_service = Mock()
        mock_auth_service_class.return_value = mock_auth_service
        
        # Mock user info
        mock_user_info = Mock()
        mock_user_info.object_id = "test-object-id"
        mock_user_info.user_principal_name = "test@example.com"
        mock_user_info.tenant_id = "test-tenant-id"
        mock_user_info.display_name = "Test User"
        mock_user_info.email = "test@example.com"
        
        # Mock successful authentication
        mock_auth_service.authenticate_user.return_value = (True, mock_user_info)
        
        # Mock JWT service
        mock_jwt_service = Mock()
        mock_jwt_service_class.return_value = mock_jwt_service
        mock_jwt_service.create_token.return_value = "test-azebal-token"
        
        # Test login
        result = login_tool("test-azure-token")
        
        # Verify result
        assert result["success"] is True
        assert result["message"] == "Login successful"
        assert result["azebal_token"] == "test-azebal-token"
        assert result["user_info"]["object_id"] == "test-object-id"
        assert result["user_info"]["user_principal_name"] == "test@example.com"
        assert result["user_info"]["tenant_id"] == "test-tenant-id"
        assert result["user_info"]["display_name"] == "Test User"
        assert result["user_info"]["email"] == "test@example.com"
        
        # Verify service calls
        mock_auth_service.authenticate_user.assert_called_once_with("test-azure-token")
        mock_jwt_service.create_token.assert_called_once_with(mock_user_info)
    
    @patch('src.tools.login.AzureAuthService')
    def test_login_authentication_fails(self, mock_auth_service_class):
        """Test login with authentication failure."""
        # Mock authentication service
        mock_auth_service = Mock()
        mock_auth_service_class.return_value = mock_auth_service
        
        # Mock authentication failure
        mock_auth_service.authenticate_user.return_value = (False, None)
        
        # Test login
        result = login_tool("invalid-azure-token")
        
        # Verify result
        assert result["success"] is False
        assert result["message"] == "Authentication failed. Please check your Azure access token."
        assert result["error"] == "INVALID_TOKEN"
        assert "azebal_token" not in result
        
        # Verify service calls
        mock_auth_service.authenticate_user.assert_called_once_with("invalid-azure-token")
    
    @patch('src.tools.login.AzureAuthService')
    @patch('src.tools.login.JWTService')
    def test_login_token_creation_fails(self, mock_jwt_service_class, mock_auth_service_class):
        """Test login with JWT token creation failure."""
        # Mock authentication service
        mock_auth_service = Mock()
        mock_auth_service_class.return_value = mock_auth_service
        
        # Mock user info
        mock_user_info = Mock()
        mock_user_info.object_id = "test-object-id"
        mock_user_info.user_principal_name = "test@example.com"
        mock_user_info.tenant_id = "test-tenant-id"
        mock_user_info.display_name = "Test User"
        mock_user_info.email = "test@example.com"
        
        # Mock successful authentication
        mock_auth_service.authenticate_user.return_value = (True, mock_user_info)
        
        # Mock JWT service with creation failure
        mock_jwt_service = Mock()
        mock_jwt_service_class.return_value = mock_jwt_service
        mock_jwt_service.create_token.side_effect = Exception("JWT creation failed")
        
        # Test login
        result = login_tool("test-azure-token")
        
        # Verify result
        assert result["success"] is False
        assert result["message"] == "Login failed due to internal error"
        assert result["error"] == "TOKEN_CREATION_FAILED"
        assert "azebal_token" not in result
        
        # Verify service calls
        mock_auth_service.authenticate_user.assert_called_once_with("test-azure-token")
        mock_jwt_service.create_token.assert_called_once_with(mock_user_info)
    
    @patch('src.tools.login.AzureAuthService')
    def test_login_unexpected_error(self, mock_auth_service_class):
        """Test login with unexpected error."""
        # Mock authentication service with unexpected error
        mock_auth_service_class.side_effect = Exception("Unexpected error")
        
        # Test login
        result = login_tool("test-azure-token")
        
        # Verify result
        assert result["success"] is False
        assert result["message"] == "Login failed due to unexpected error"
        assert result["error"] == "UNEXPECTED_ERROR"
        assert "azebal_token" not in result
    
    def test_login_with_empty_token(self):
        """Test login with empty token."""
        result = login_tool("")
        
        # Should still attempt authentication but likely fail
        assert "success" in result
        assert "message" in result
    
    def test_login_with_none_token(self):
        """Test login with None token."""
        result = login_tool(None)
        
        # Should handle gracefully
        assert "success" in result
        assert "message" in result
