"""
Token Storage Service for AZEBAL

Secure storage for Azure access tokens using in-memory cache (MVP) or Redis.
"""

import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Any
from dataclasses import dataclass
import json
import base64
import hashlib
from threading import Lock

from src.core.logging_config import get_logger
from src.core.config import settings

logger = get_logger(__name__)


@dataclass
class TokenInfo:
    """Token information stored securely."""
    
    session_id: str
    user_principal_name: str
    azure_access_token: str
    expires_at: datetime
    created_at: datetime
    subscription_id: Optional[str] = None
    
    def is_expired(self) -> bool:
        """Check if the token is expired."""
        return datetime.now(timezone.utc) > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "session_id": self.session_id,
            "user_principal_name": self.user_principal_name,
            "azure_access_token": self.azure_access_token,
            "expires_at": self.expires_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "subscription_id": self.subscription_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TokenInfo":
        """Create from dictionary."""
        return cls(
            session_id=data["session_id"],
            user_principal_name=data["user_principal_name"],
            azure_access_token=data["azure_access_token"],
            expires_at=datetime.fromisoformat(data["expires_at"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            subscription_id=data.get("subscription_id")
        )


class TokenEncryption:
    """Simple token encryption for secure storage."""
    
    @staticmethod
    def _get_key() -> str:
        """Get encryption key from settings."""
        # Use JWT secret as base for encryption key
        return hashlib.sha256(settings.jwt_secret_key.encode()).hexdigest()[:32]
    
    @classmethod
    def encrypt_token(cls, token: str) -> str:
        """
        Encrypt Azure access token.
        
        Note: This is a simple encryption for MVP.
        In production, use proper encryption libraries like cryptography.
        """
        try:
            key = cls._get_key()
            # Simple XOR encryption for MVP
            encrypted = []
            for i, char in enumerate(token):
                key_char = key[i % len(key)]
                encrypted.append(chr(ord(char) ^ ord(key_char)))
            
            encrypted_str = ''.join(encrypted)
            # Base64 encode to make it safe for storage
            return base64.b64encode(encrypted_str.encode()).decode()
        except Exception as e:
            logger.error(f"Error encrypting token: {str(e)}")
            return token  # Fallback to unencrypted for MVP
    
    @classmethod
    def decrypt_token(cls, encrypted_token: str) -> str:
        """Decrypt Azure access token."""
        try:
            key = cls._get_key()
            # Decode from base64
            encrypted_str = base64.b64decode(encrypted_token.encode()).decode()
            
            # Simple XOR decryption
            decrypted = []
            for i, char in enumerate(encrypted_str):
                key_char = key[i % len(key)]
                decrypted.append(chr(ord(char) ^ ord(key_char)))
            
            return ''.join(decrypted)
        except Exception as e:
            logger.error(f"Error decrypting token: {str(e)}")
            return encrypted_token  # Fallback to original for MVP


class InMemoryTokenStorage:
    """
    In-memory token storage for MVP.
    
    Note: Tokens will be lost on server restart.
    For production, use Redis-based storage.
    """
    
    def __init__(self):
        self._tokens: Dict[str, TokenInfo] = {}
        self._lock = Lock()
        self._cleanup_interval = 300  # 5 minutes
        self._last_cleanup = time.time()
        
        logger.info("InMemoryTokenStorage initialized")
    
    def store_token(
        self, 
        user_principal_name: str, 
        azure_access_token: str,
        subscription_id: Optional[str] = None,
        expires_in_hours: int = 1
    ) -> str:
        """
        Store Azure access token securely.
        
        Args:
            user_principal_name: User identifier
            azure_access_token: Azure access token to store
            subscription_id: Optional Azure subscription ID
            expires_in_hours: Token expiration in hours
            
        Returns:
            str: Session ID for token retrieval
        """
        session_id = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)
        
        # Encrypt the token
        encrypted_token = TokenEncryption.encrypt_token(azure_access_token)
        
        token_info = TokenInfo(
            session_id=session_id,
            user_principal_name=user_principal_name,
            azure_access_token=encrypted_token,
            expires_at=expires_at,
            created_at=datetime.now(timezone.utc),
            subscription_id=subscription_id
        )
        
        with self._lock:
            self._tokens[session_id] = token_info
            self._cleanup_expired_tokens()
        
        logger.info(f"Stored token for user: {user_principal_name}, session: {session_id}")
        return session_id
    
    def get_token(self, session_id: str) -> Optional[str]:
        """
        Retrieve Azure access token by session ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            str: Decrypted Azure access token or None if not found/expired
        """
        with self._lock:
            token_info = self._tokens.get(session_id)
            
            if not token_info:
                logger.warning(f"Token not found for session: {session_id}")
                return None
            
            if token_info.is_expired():
                logger.warning(f"Token expired for session: {session_id}")
                del self._tokens[session_id]
                return None
            
            # Decrypt and return token
            decrypted_token = TokenEncryption.decrypt_token(token_info.azure_access_token)
            logger.debug(f"Retrieved token for session: {session_id}")
            return decrypted_token
    
    def get_token_info(self, session_id: str) -> Optional[TokenInfo]:
        """Get full token information."""
        with self._lock:
            token_info = self._tokens.get(session_id)
            
            if not token_info:
                return None
            
            if token_info.is_expired():
                del self._tokens[session_id]
                return None
            
            # Return copy with decrypted token
            token_copy = TokenInfo(
                session_id=token_info.session_id,
                user_principal_name=token_info.user_principal_name,
                azure_access_token=TokenEncryption.decrypt_token(token_info.azure_access_token),
                expires_at=token_info.expires_at,
                created_at=token_info.created_at,
                subscription_id=token_info.subscription_id
            )
            
            return token_copy
    
    def delete_token(self, session_id: str) -> bool:
        """Delete stored token."""
        with self._lock:
            if session_id in self._tokens:
                del self._tokens[session_id]
                logger.info(f"Deleted token for session: {session_id}")
                return True
            else:
                logger.warning(f"Cannot delete token - session not found: {session_id}")
                return False
    
    def _cleanup_expired_tokens(self) -> None:
        """Clean up expired tokens."""
        current_time = time.time()
        
        # Only cleanup every 5 minutes
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        self._last_cleanup = current_time
        
        expired_sessions = [
            session_id for session_id, token_info in self._tokens.items()
            if token_info.is_expired()
        ]
        
        for session_id in expired_sessions:
            del self._tokens[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired tokens")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        with self._lock:
            total_tokens = len(self._tokens)
            expired_count = sum(1 for token in self._tokens.values() if token.is_expired())
            
            return {
                "total_tokens": total_tokens,
                "active_tokens": total_tokens - expired_count,
                "expired_tokens": expired_count,
                "storage_type": "in_memory"
            }
    
    def clear_all(self) -> None:
        """Clear all tokens (for testing)."""
        with self._lock:
            token_count = len(self._tokens)
            self._tokens.clear()
            logger.info(f"Cleared all {token_count} tokens")


# Global token storage instance (MVP: in-memory)
token_storage = InMemoryTokenStorage()
