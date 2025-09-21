"""
Unit tests for Azure authentication service.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import httpx
import jwt

from src.core.auth import AzureAuthService, UserInfo


class TestAzureAuthService:
    """Test cases for AzureAuthService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.auth_service = AzureAuthService()
    
    @patch('httpx.Client')
    def test_validate_access_token_success(self, mock_client_class):
        """Test successful token validation."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        result = self.auth_service.validate_access_token("valid-token")
        
        assert result is True
        mock_client.get.assert_called_once()
    
    @patch('httpx.Client')
    def test_validate_access_token_unauthorized(self, mock_client_class):
        """Test token validation with unauthorized response."""
        # Mock unauthorized response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        result = self.auth_service.validate_access_token("invalid-token")
        
        assert result is False
    
    @patch('httpx.Client')
    def test_validate_access_token_network_error(self, mock_client_class):
        """Test token validation with network error."""
        # Mock network error
        mock_client = Mock()
        mock_client.get.side_effect = httpx.RequestError("Network error")
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        result = self.auth_service.validate_access_token("token")
        
        assert result is False
    
    @patch('jwt.decode')
    def test_extract_user_info_success(self, mock_jwt_decode):
        """Test successful user info extraction."""
        # Mock JWT decode response
        mock_jwt_decode.return_value = {
            "oid": "test-object-id",
            "upn": "test@example.com",
            "tid": "test-tenant-id",
            "name": "Test User",
            "email": "test@example.com"
        }
        
        result = self.auth_service.extract_user_info("valid-token")
        
        assert result is not None
        assert isinstance(result, UserInfo)
        assert result.object_id == "test-object-id"
        assert result.user_principal_name == "test@example.com"
        assert result.tenant_id == "test-tenant-id"
        assert result.display_name == "Test User"
        assert result.email == "test@example.com"
    
    @patch('jwt.decode')
    def test_extract_user_info_missing_required_fields(self, mock_jwt_decode):
        """Test user info extraction with missing required fields."""
        # Mock JWT decode response missing required fields
        mock_jwt_decode.return_value = {
            "upn": "test@example.com",
            # Missing oid and tid
        }
        
        result = self.auth_service.extract_user_info("token")
        
        assert result is None
    
    @patch('jwt.decode')
    def test_extract_user_info_invalid_token(self, mock_jwt_decode):
        """Test user info extraction with invalid token."""
        # Mock JWT decode error
        mock_jwt_decode.side_effect = jwt.InvalidTokenError("Invalid token")
        
        result = self.auth_service.extract_user_info("invalid-token")
        
        assert result is None
    
    @patch('src.core.auth.AzureAuthService.validate_access_token')
    @patch('src.core.auth.AzureAuthService.extract_user_info')
    def test_authenticate_user_success(self, mock_extract, mock_validate):
        """Test successful user authentication."""
        # Mock successful validation and extraction
        mock_validate.return_value = True
        mock_user_info = UserInfo(
            object_id="test-object-id",
            user_principal_name="test@example.com",
            tenant_id="test-tenant-id"
        )
        mock_extract.return_value = mock_user_info
        
        is_valid, user_info = self.auth_service.authenticate_user("valid-token")
        
        assert is_valid is True
        assert user_info == mock_user_info
        mock_validate.assert_called_once_with("valid-token")
        mock_extract.assert_called_once_with("valid-token")
    
    @patch('src.core.auth.AzureAuthService.validate_access_token')
    def test_authenticate_user_validation_fails(self, mock_validate):
        """Test user authentication with validation failure."""
        # Mock validation failure
        mock_validate.return_value = False
        
        is_valid, user_info = self.auth_service.authenticate_user("invalid-token")
        
        assert is_valid is False
        assert user_info is None
        mock_validate.assert_called_once_with("invalid-token")
    
    @patch('src.core.auth.AzureAuthService.validate_access_token')
    @patch('src.core.auth.AzureAuthService.extract_user_info')
    def test_authenticate_user_extraction_fails(self, mock_extract, mock_validate):
        """Test user authentication with extraction failure."""
        # Mock successful validation but failed extraction
        mock_validate.return_value = True
        mock_extract.return_value = None
        
        is_valid, user_info = self.auth_service.authenticate_user("token")
        
        assert is_valid is False
        assert user_info is None
        mock_validate.assert_called_once_with("token")
        mock_extract.assert_called_once_with("token")
