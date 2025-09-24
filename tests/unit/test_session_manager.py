"""
Unit tests for session manager.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from src.core.session_manager import (
    DebugSession,
    SessionManager,
    session_manager
)


class TestDebugSession:
    """Test DebugSession functionality."""
    
    def test_debug_session_creation(self):
        """Test creating a debug session."""
        trace_id = "test-trace-123"
        user = "test@example.com"
        error_desc = "Test error"
        context = {"test": "data"}
        
        session = DebugSession(
            trace_id=trace_id,
            user_principal_name=user,
            error_description=error_desc,
            context=context
        )
        
        assert session.trace_id == trace_id
        assert session.user_principal_name == user
        assert session.error_description == error_desc
        assert session.context == context
        assert session.status == "active"
        assert session.progress == 0
        assert session.function_call_count == 0
    
    def test_add_function_result(self):
        """Test adding function results to session."""
        session = DebugSession(
            trace_id="test",
            user_principal_name="user",
            error_description="error",
            context={}
        )
        
        result = {"success": True, "data": "test"}
        session.add_function_result("test_function", result)
        
        assert session.function_call_count == 1
        assert "test_function" in session.function_results
        assert session.function_results["test_function"] == result
        assert len(session.function_calls) == 1
        assert session.function_calls[0]["function"] == "test_function"
        assert session.function_calls[0]["status"] == "success"
    
    def test_add_function_result_with_error(self):
        """Test adding function result with error."""
        session = DebugSession(
            trace_id="test",
            user_principal_name="user", 
            error_description="error",
            context={}
        )
        
        result = {"error": "Function failed", "details": "Some error"}
        session.add_function_result("failing_function", result)
        
        assert session.function_calls[0]["status"] == "failed"
    
    def test_add_finding(self):
        """Test adding findings to session."""
        session = DebugSession(
            trace_id="test",
            user_principal_name="user",
            error_description="error", 
            context={}
        )
        
        session.add_finding("Test finding", "warning", "test_category")
        
        assert len(session.findings) == 1
        assert session.findings[0]["finding"] == "Test finding"
        assert session.findings[0]["severity"] == "warning"
        assert session.findings[0]["category"] == "test_category"
    
    def test_update_progress(self):
        """Test updating session progress."""
        session = DebugSession(
            trace_id="test",
            user_principal_name="user",
            error_description="error",
            context={}
        )
        
        session.update_progress(50)
        assert session.progress == 50
        
        # Test bounds
        session.update_progress(150)  # Should be capped at 100
        assert session.progress == 100
        
        session.update_progress(-10)  # Should be floored at 0
        assert session.progress == 0
    
    def test_mark_as_completed(self):
        """Test marking session as completed."""
        session = DebugSession(
            trace_id="test",
            user_principal_name="user",
            error_description="error",
            context={}
        )
        
        session.mark_as_completed()
        
        assert session.status == "completed"
        assert session.progress == 100
    
    def test_mark_as_failed(self):
        """Test marking session as failed."""
        session = DebugSession(
            trace_id="test",
            user_principal_name="user",
            error_description="error",
            context={}
        )
        
        reason = "Test failure reason"
        session.mark_as_failed(reason)
        
        assert session.status == "failed"
        assert any(reason in log["message"] for log in session.execution_logs)
    
    def test_is_expired(self):
        """Test session expiration check."""
        session = DebugSession(
            trace_id="test",
            user_principal_name="user",
            error_description="error",
            context={}
        )
        
        # Fresh session should not be expired
        assert not session.is_expired(3600)  # 1 hour timeout
        
        # Modify last_activity to simulate old session
        session.last_activity = datetime.now(timezone.utc) - timedelta(hours=2)
        assert session.is_expired(3600)  # Should be expired
    
    def test_get_memory_estimate(self):
        """Test memory estimation."""
        session = DebugSession(
            trace_id="test",
            user_principal_name="user",
            error_description="error",
            context={"large_data": "x" * 1000}
        )
        
        # Add some function results
        session.add_function_result("func1", {"data": "x" * 500})
        session.add_log("Test log message")
        
        memory_mb = session.get_memory_estimate_mb()
        assert memory_mb > 0
        assert isinstance(memory_mb, float)
    
    def test_get_context_for_llm(self):
        """Test getting context formatted for LLM."""
        session = DebugSession(
            trace_id="test-123",
            user_principal_name="user",
            error_description="error",
            context={}
        )
        
        session.add_finding("Test finding 1")
        session.add_finding("Test finding 2")
        session.add_function_result("test_func", {"result": "data"})
        
        context = session.get_context_for_llm()
        
        assert context["trace_id"] == "test-123"
        assert context["status"] == "active"
        assert context["function_calls_made"] == 1
        assert len(context["key_findings"]) == 2
        assert len(context["recent_function_calls"]) == 1


class TestSessionManager:
    """Test SessionManager functionality."""
    
    def test_create_session(self):
        """Test creating a new session."""
        manager = SessionManager(max_sessions=10, session_timeout=300)
        
        session = manager.create_session(
            user_principal_name="test@example.com",
            error_description="Test error",
            context={"test": "data"}
        )
        
        assert session.user_principal_name == "test@example.com"
        assert session.error_description == "Test error"
        assert session.context == {"test": "data"}
        assert session.trace_id in manager.sessions
    
    def test_create_session_with_trace_id(self):
        """Test creating session with specific trace ID."""
        manager = SessionManager()
        trace_id = "custom-trace-123"
        
        session = manager.create_session(
            user_principal_name="test@example.com",
            error_description="Test error",
            context={},
            trace_id=trace_id
        )
        
        assert session.trace_id == trace_id
        assert trace_id in manager.sessions
    
    def test_get_session(self):
        """Test retrieving existing session."""
        manager = SessionManager()
        
        # Create session
        session = manager.create_session(
            user_principal_name="test@example.com",
            error_description="Test error",
            context={}
        )
        trace_id = session.trace_id
        
        # Retrieve session
        retrieved = manager.get_session(trace_id)
        
        assert retrieved is not None
        assert retrieved.trace_id == trace_id
        assert retrieved.user_principal_name == "test@example.com"
    
    def test_get_nonexistent_session(self):
        """Test retrieving non-existent session."""
        manager = SessionManager()
        
        session = manager.get_session("nonexistent-trace-id")
        assert session is None
    
    def test_get_or_create_session_existing(self):
        """Test get_or_create with existing session."""
        manager = SessionManager()
        
        # Create session
        original = manager.create_session(
            user_principal_name="test@example.com",
            error_description="Test error",
            context={}
        )
        trace_id = original.trace_id
        
        # Get or create should return existing
        retrieved = manager.get_or_create_session(
            trace_id=trace_id,
            user_principal_name="different@example.com"  # Should be ignored
        )
        
        assert retrieved.trace_id == trace_id
        assert retrieved.user_principal_name == "test@example.com"  # Original value
    
    def test_get_or_create_session_new(self):
        """Test get_or_create with new session."""
        manager = SessionManager()
        
        session = manager.get_or_create_session(
            trace_id="new-trace-123",
            user_principal_name="test@example.com",
            error_description="Test error",
            context={"test": "data"}
        )
        
        assert session.trace_id == "new-trace-123"
        assert session.user_principal_name == "test@example.com"
        assert "new-trace-123" in manager.sessions
    
    def test_delete_session(self):
        """Test deleting a session."""
        manager = SessionManager()
        
        # Create session
        session = manager.create_session(
            user_principal_name="test@example.com",
            error_description="Test error",
            context={}
        )
        trace_id = session.trace_id
        
        # Verify it exists
        assert trace_id in manager.sessions
        
        # Delete it
        result = manager.delete_session(trace_id)
        assert result is True
        assert trace_id not in manager.sessions
        
        # Try to delete again
        result = manager.delete_session(trace_id)
        assert result is False
    
    def test_list_sessions(self):
        """Test listing sessions."""
        manager = SessionManager()
        
        # Create sessions for different users
        manager.create_session("user1@example.com", "Error 1", {})
        manager.create_session("user2@example.com", "Error 2", {})
        manager.create_session("user1@example.com", "Error 3", {})
        
        # List all sessions
        all_sessions = manager.list_sessions()
        assert len(all_sessions) == 3
        
        # List sessions for specific user
        user1_sessions = manager.list_sessions("user1@example.com")
        assert len(user1_sessions) == 2
        assert all(s["user_principal_name"] == "user1@example.com" for s in user1_sessions)
        
        user2_sessions = manager.list_sessions("user2@example.com")
        assert len(user2_sessions) == 1
    
    def test_cleanup_expired_sessions(self):
        """Test cleanup of expired sessions."""
        manager = SessionManager(session_timeout=60)  # 1 minute timeout
        
        # Create session and make it old
        session = manager.create_session("test@example.com", "Error", {})
        session.last_activity = datetime.now(timezone.utc) - timedelta(minutes=2)  # 2 minutes ago
        
        initial_count = len(manager.sessions)
        assert initial_count == 1
        
        # Trigger cleanup by creating another session
        manager.create_session("test2@example.com", "Error 2", {})
        
        # Expired session should be cleaned up
        assert len(manager.sessions) == 1  # Only the new session remains
    
    def test_cleanup_oldest_sessions(self):
        """Test cleanup when max capacity is reached."""
        manager = SessionManager(max_sessions=2)
        
        # Create sessions up to capacity
        session1 = manager.create_session("user1@example.com", "Error 1", {})
        session2 = manager.create_session("user2@example.com", "Error 2", {})
        
        # Make first session older
        session1.last_activity = datetime.now(timezone.utc) - timedelta(minutes=1)
        
        # Create one more session (should trigger cleanup)
        session3 = manager.create_session("user3@example.com", "Error 3", {})
        
        # Should have only 2 sessions (oldest removed)
        assert len(manager.sessions) == 2
        assert session1.trace_id not in manager.sessions  # Oldest removed
        assert session2.trace_id in manager.sessions
        assert session3.trace_id in manager.sessions
    
    def test_get_session_stats(self):
        """Test getting session statistics."""
        manager = SessionManager(max_sessions=10, session_timeout=300)
        
        # Create some sessions
        manager.create_session("user1@example.com", "Error 1", {})
        session2 = manager.create_session("user2@example.com", "Error 2", {})
        
        # Make one session expired
        session2.last_activity = datetime.now(timezone.utc) - timedelta(minutes=10)
        
        stats = manager.get_session_stats()
        
        assert stats["total_sessions"] == 2
        assert stats["max_sessions"] == 10
        assert stats["session_timeout"] == 300
        assert "capacity_usage" in stats
        assert "estimated_memory_mb" in stats
    
    def test_cleanup_all(self):
        """Test clearing all sessions."""
        manager = SessionManager()
        
        # Create multiple sessions
        manager.create_session("user1@example.com", "Error 1", {})
        manager.create_session("user2@example.com", "Error 2", {})
        
        assert len(manager.sessions) == 2
        
        # Clear all
        manager.cleanup_all()
        
        assert len(manager.sessions) == 0


class TestGlobalSessionManager:
    """Test the global session_manager instance."""
    
    def test_global_session_manager_exists(self):
        """Test that global session manager is available."""
        assert session_manager is not None
        assert isinstance(session_manager, SessionManager)
    
    def test_global_session_manager_functionality(self):
        """Test basic functionality of global session manager."""
        # Clean up any existing sessions
        session_manager.cleanup_all()
        
        # Create a session
        session = session_manager.create_session(
            user_principal_name="test@example.com",
            error_description="Global test error",
            context={}
        )
        
        # Verify it can be retrieved
        retrieved = session_manager.get_session(session.trace_id)
        assert retrieved is not None
        assert retrieved.trace_id == session.trace_id
        
        # Clean up
        session_manager.cleanup_all()


if __name__ == "__main__":
    pytest.main([__file__])
