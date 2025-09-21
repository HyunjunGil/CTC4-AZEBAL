"""
Unit tests for JWT service.
"""

import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta, timezone
import jwt

from src.core.jwt_service import JWTService
from src.core.auth import UserInfo


class TestJWTService:
    """Test cases for JWTService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.jwt_service = JWTService()
        self.test_user_info = UserInfo(
            object_id="test-object-id",
            user_principal_name="test@example.com",
            tenant_id="test-tenant-id",
            display_name="Test User",
            email="test@example.com"
        )
    
    def test_create_token_success(self):
        """Test successful token creation."""
        token = self.jwt_service.create_token(self.test_user_info)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify token contents
        decoded = jwt.decode(
            token,
            self.jwt_service.secret_key,
            algorithms=[self.jwt_service.algorithm],
            audience="azebal-client",
            issuer="azebal"
        )
        
        assert decoded["sub"] == self.test_user_info.object_id
        assert decoded["upn"] == self.test_user_info.user_principal_name
        assert decoded["tenant_id"] == self.test_user_info.tenant_id
        assert decoded["display_name"] == self.test_user_info.display_name
        assert decoded["email"] == self.test_user_info.email
        assert decoded["iss"] == "azebal"
        assert decoded["aud"] == "azebal-client"
    
    def test_create_token_with_minimal_user_info(self):
        """Test token creation with minimal user info."""
        minimal_user_info = UserInfo(
            object_id="test-object-id",
            user_principal_name="test@example.com",
            tenant_id="test-tenant-id"
        )
        
        token = self.jwt_service.create_token(minimal_user_info)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify token contents
        decoded = jwt.decode(
            token,
            self.jwt_service.secret_key,
            algorithms=[self.jwt_service.algorithm],
            audience="azebal-client",
            issuer="azebal"
        )
        
        assert decoded["sub"] == minimal_user_info.object_id
        assert decoded["upn"] == minimal_user_info.user_principal_name
        assert decoded["tenant_id"] == minimal_user_info.tenant_id
        assert decoded.get("display_name") is None
        assert decoded.get("email") is None
    
    def test_validate_token_success(self):
        """Test successful token validation."""
        # Create a valid token
        token = self.jwt_service.create_token(self.test_user_info)
        
        # Validate the token
        payload = self.jwt_service.validate_token(token)
        
        assert payload is not None
        assert payload["sub"] == self.test_user_info.object_id
        assert payload["upn"] == self.test_user_info.user_principal_name
        assert payload["tenant_id"] == self.test_user_info.tenant_id
    
    def test_validate_token_invalid_signature(self):
        """Test token validation with invalid signature."""
        # Create a token with wrong secret
        wrong_secret = "wrong-secret"
        token = jwt.encode(
            {
                "sub": "test-object-id",
                "upn": "test@example.com",
                "tenant_id": "test-tenant-id",
                "iat": datetime.now(timezone.utc),
                "exp": datetime.now(timezone.utc) + timedelta(hours=24),
                "iss": "azebal",
                "aud": "azebal-client"
            },
            wrong_secret,
            algorithm="HS256"
        )
        
        payload = self.jwt_service.validate_token(token)
        
        assert payload is None
    
    def test_validate_token_expired(self):
        """Test token validation with expired token."""
        # Create an expired token
        expired_time = datetime.now(timezone.utc) - timedelta(hours=1)
        token = jwt.encode(
            {
                "sub": "test-object-id",
                "upn": "test@example.com",
                "tenant_id": "test-tenant-id",
                "iat": expired_time,
                "exp": expired_time,
                "iss": "azebal",
                "aud": "azebal-client"
            },
            self.jwt_service.secret_key,
            algorithm="HS256"
        )
        
        payload = self.jwt_service.validate_token(token)
        
        assert payload is None
    
    def test_validate_token_wrong_audience(self):
        """Test token validation with wrong audience."""
        # Create a token with wrong audience
        token = jwt.encode(
            {
                "sub": "test-object-id",
                "upn": "test@example.com",
                "tenant_id": "test-tenant-id",
                "iat": datetime.now(timezone.utc),
                "exp": datetime.now(timezone.utc) + timedelta(hours=24),
                "iss": "azebal",
                "aud": "wrong-audience"
            },
            self.jwt_service.secret_key,
            algorithm="HS256"
        )
        
        payload = self.jwt_service.validate_token(token)
        
        assert payload is None
    
    def test_validate_token_wrong_issuer(self):
        """Test token validation with wrong issuer."""
        # Create a token with wrong issuer
        token = jwt.encode(
            {
                "sub": "test-object-id",
                "upn": "test@example.com",
                "tenant_id": "test-tenant-id",
                "iat": datetime.now(timezone.utc),
                "exp": datetime.now(timezone.utc) + timedelta(hours=24),
                "iss": "wrong-issuer",
                "aud": "azebal-client"
            },
            self.jwt_service.secret_key,
            algorithm="HS256"
        )
        
        payload = self.jwt_service.validate_token(token)
        
        assert payload is None
    
    def test_get_user_info_from_token_success(self):
        """Test successful user info extraction from token."""
        # Create a valid token
        token = self.jwt_service.create_token(self.test_user_info)
        
        # Extract user info
        user_info = self.jwt_service.get_user_info_from_token(token)
        
        assert user_info is not None
        assert isinstance(user_info, UserInfo)
        assert user_info.object_id == self.test_user_info.object_id
        assert user_info.user_principal_name == self.test_user_info.user_principal_name
        assert user_info.tenant_id == self.test_user_info.tenant_id
        assert user_info.display_name == self.test_user_info.display_name
        assert user_info.email == self.test_user_info.email
    
    def test_get_user_info_from_token_invalid(self):
        """Test user info extraction from invalid token."""
        # Use an invalid token
        invalid_token = "invalid.token.here"
        
        user_info = self.jwt_service.get_user_info_from_token(invalid_token)
        
        assert user_info is None
    
    def test_get_user_info_from_token_missing_fields(self):
        """Test user info extraction from token with missing required fields."""
        # Create a token with missing required fields
        token = jwt.encode(
            {
                "sub": "test-object-id",
                # Missing upn and tenant_id
                "iat": datetime.now(timezone.utc),
                "exp": datetime.now(timezone.utc) + timedelta(hours=24),
                "iss": "azebal",
                "aud": "azebal-client"
            },
            self.jwt_service.secret_key,
            algorithm="HS256"
        )
        
        user_info = self.jwt_service.get_user_info_from_token(token)
        
        assert user_info is None
