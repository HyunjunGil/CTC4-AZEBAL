"""
Session Manager for AZEBAL Debug Sessions

Manages in-memory debugging sessions with trace IDs for autonomous analysis.
"""

import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from threading import Lock

from src.core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class DebugSession:
    """Debug session data structure for autonomous analysis."""
    
    trace_id: str
    user_principal_name: str
    error_description: str
    context: Dict[str, Any]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Analysis state
    status: str = "active"  # active, paused, completed, failed
    progress: int = 0
    depth: int = 0
    
    # Function call history
    function_calls: List[Dict[str, Any]] = field(default_factory=list)
    function_results: Dict[str, Any] = field(default_factory=dict)
    
    # Analysis findings
    identified_resources: List[str] = field(default_factory=list)
    findings: List[Dict[str, Any]] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    
    # Safety tracking
    start_time: Optional[float] = None
    function_call_count: int = 0
    execution_logs: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_function_result(self, function_name: str, result: Dict[str, Any]) -> None:
        """Add function execution result to session memory."""
        self.function_results[function_name] = result
        self.function_calls.append({
            "function": function_name,
            "timestamp": datetime.now(timezone.utc),
            "result_summary": str(result)[:200],  # Truncate for memory efficiency
            "status": "success" if "error" not in result else "failed"
        })
        self.function_call_count += 1
        self.last_activity = datetime.now(timezone.utc)
        
        logger.debug(f"[{self.trace_id}] Added function result: {function_name}")
    
    def add_finding(self, finding: str, severity: str = "info", category: str = "general") -> None:
        """Add a finding to the analysis."""
        self.findings.append({
            "finding": finding,
            "severity": severity,
            "category": category,
            "timestamp": datetime.now(timezone.utc)
        })
        
        logger.info(f"[{self.trace_id}] New finding ({severity}): {finding}")
    
    def add_log(self, message: str, level: str = "info") -> None:
        """Add a log entry to the session."""
        self.execution_logs.append({
            "message": message,
            "level": level,
            "timestamp": datetime.now(timezone.utc)
        })
        
        if level == "error":
            logger.error(f"[{self.trace_id}] {message}")
        elif level == "warning":
            logger.warning(f"[{self.trace_id}] {message}")
        else:
            logger.info(f"[{self.trace_id}] {message}")
    
    def get_context_for_llm(self) -> Dict[str, Any]:
        """Get session context formatted for LLM consumption."""
        return {
            "trace_id": self.trace_id,
            "status": self.status,
            "progress": self.progress,
            "depth": self.depth,
            "function_calls_made": len(self.function_calls),
            "identified_resources": self.identified_resources,
            "key_findings": [f["finding"] for f in self.findings[-5:]],  # Last 5 findings
            "recent_function_calls": [
                {
                    "function": fc["function"],
                    "status": fc["status"],
                    "timestamp": fc["timestamp"].isoformat()
                }
                for fc in self.function_calls[-3:]  # Last 3 function calls
            ],
            "execution_time": (datetime.now(timezone.utc) - self.created_at).total_seconds() if self.created_at else 0,
            "next_steps": self.next_steps
        }
    
    def update_progress(self, progress: int) -> None:
        """Update session progress."""
        self.progress = max(0, min(100, progress))
        self.last_activity = datetime.now(timezone.utc)
        
        logger.info(f"[{self.trace_id}] Progress updated: {self.progress}%")
    
    def mark_as_completed(self) -> None:
        """Mark session as completed."""
        self.status = "completed"
        self.progress = 100
        self.last_activity = datetime.now(timezone.utc)
        
        logger.info(f"[{self.trace_id}] Session marked as completed")
    
    def mark_as_failed(self, reason: str) -> None:
        """Mark session as failed."""
        self.status = "failed"
        self.add_log(f"Session failed: {reason}", "error")
        self.last_activity = datetime.now(timezone.utc)
        
        logger.error(f"[{self.trace_id}] Session marked as failed: {reason}")
    
    def is_expired(self, timeout_seconds: int) -> bool:
        """Check if session is expired based on last activity."""
        if not self.last_activity:
            return True
        
        expiry_time = self.last_activity + timedelta(seconds=timeout_seconds)
        return datetime.now(timezone.utc) > expiry_time
    
    def get_memory_estimate_mb(self) -> float:
        """Estimate memory usage of this session in MB."""
        base_size = 0.1  # Base session overhead
        
        # Function results size
        function_data_size = len(str(self.function_results)) / (1024 * 1024)
        
        # Execution logs size
        logs_size = len(str(self.execution_logs)) / (1024 * 1024)
        
        # Context size
        context_size = len(str(self.context)) / (1024 * 1024)
        
        return base_size + function_data_size + logs_size + context_size


class SessionManager:
    """Manages debugging sessions in memory."""
    
    def __init__(self, max_sessions: int = 100, session_timeout: int = 3600):
        """
        Initialize session manager.
        
        Args:
            max_sessions: Maximum number of sessions to keep in memory
            session_timeout: Session timeout in seconds (default: 1 hour)
        """
        self.sessions: Dict[str, DebugSession] = {}
        self.max_sessions = max_sessions
        self.session_timeout = session_timeout
        self._lock = Lock()  # Thread safety for concurrent access
        
        logger.info(f"SessionManager initialized: max_sessions={max_sessions}, timeout={session_timeout}s")
    
    def create_session(
        self,
        user_principal_name: str,
        error_description: str,
        context: Dict[str, Any],
        trace_id: Optional[str] = None
    ) -> DebugSession:
        """
        Create a new debugging session.
        
        Args:
            user_principal_name: User identifier
            error_description: Error to debug
            context: Additional context for debugging
            trace_id: Optional trace ID (will generate if not provided)
        
        Returns:
            DebugSession: Created session
        """
        if not trace_id:
            trace_id = str(uuid.uuid4())
        
        with self._lock:
            # Clean up before creating new session
            self._cleanup_expired_sessions()
            
            # Check capacity and cleanup if needed
            if len(self.sessions) >= self.max_sessions:
                self._cleanup_oldest_sessions()
            
            session = DebugSession(
                trace_id=trace_id,
                user_principal_name=user_principal_name,
                error_description=error_description,
                context=context
            )
            
            self.sessions[trace_id] = session
            
            logger.info(f"Created new session: {trace_id} for user: {user_principal_name}")
            return session
    
    def get_session(self, trace_id: str) -> Optional[DebugSession]:
        """
        Get existing session by trace ID.
        
        Args:
            trace_id: Session trace ID
        
        Returns:
            DebugSession: Session if found, None otherwise
        """
        with self._lock:
            session = self.sessions.get(trace_id)
            if session:
                session.last_activity = datetime.now(timezone.utc)
                logger.debug(f"Retrieved session: {trace_id}")
            else:
                logger.warning(f"Session not found: {trace_id}")
            
            return session
    
    def delete_session(self, trace_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            trace_id: Session trace ID
        
        Returns:
            bool: True if deleted, False if not found
        """
        with self._lock:
            if trace_id in self.sessions:
                del self.sessions[trace_id]
                logger.info(f"Deleted session: {trace_id}")
                return True
            else:
                logger.warning(f"Cannot delete session - not found: {trace_id}")
                return False
    
    def list_sessions(self, user_principal_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List sessions, optionally filtered by user.
        
        Args:
            user_principal_name: Optional user filter
        
        Returns:
            List[Dict]: Session summaries
        """
        with self._lock:
            sessions = []
            for session in self.sessions.values():
                if user_principal_name and session.user_principal_name != user_principal_name:
                    continue
                
                sessions.append({
                    "trace_id": session.trace_id,
                    "user_principal_name": session.user_principal_name,
                    "status": session.status,
                    "progress": session.progress,
                    "created_at": session.created_at.isoformat(),
                    "last_activity": session.last_activity.isoformat(),
                    "function_calls": len(session.function_calls),
                    "findings": len(session.findings)
                })
            
            return sessions
    
    def _cleanup_expired_sessions(self) -> None:
        """Remove expired sessions to prevent memory leaks."""
        current_time = datetime.now(timezone.utc)
        expired_sessions = [
            trace_id for trace_id, session in self.sessions.items()
            if session.is_expired(self.session_timeout)
        ]
        
        for trace_id in expired_sessions:
            del self.sessions[trace_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def _cleanup_oldest_sessions(self) -> None:
        """Remove oldest sessions when max capacity is reached."""
        if len(self.sessions) < self.max_sessions:
            return
        
        # Sort sessions by last activity (oldest first)
        sorted_sessions = sorted(
            self.sessions.items(),
            key=lambda x: x[1].last_activity
        )
        
        # Remove oldest sessions until we're under the limit
        sessions_to_remove = len(self.sessions) - self.max_sessions + 1
        
        for trace_id, _ in sorted_sessions[:sessions_to_remove]:
            del self.sessions[trace_id]
        
        logger.info(f"Cleaned up {sessions_to_remove} oldest sessions to maintain capacity limit")
    
    def get_session_count(self) -> int:
        """Get current number of active sessions."""
        return len(self.sessions)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics for monitoring."""
        with self._lock:
            current_time = datetime.now(timezone.utc)
            active_count = 0
            expired_count = 0
            total_memory_mb = 0
            
            for session in self.sessions.values():
                total_memory_mb += session.get_memory_estimate_mb()
                
                if session.is_expired(self.session_timeout):
                    expired_count += 1
                else:
                    active_count += 1
            
            return {
                "total_sessions": len(self.sessions),
                "active_sessions": active_count,
                "expired_sessions": expired_count,
                "max_sessions": self.max_sessions,
                "capacity_usage": f"{len(self.sessions)}/{self.max_sessions}",
                "estimated_memory_mb": round(total_memory_mb, 2),
                "session_timeout": self.session_timeout
            }
    
    def cleanup_all(self) -> None:
        """Clear all sessions (useful for testing)."""
        with self._lock:
            session_count = len(self.sessions)
            self.sessions.clear()
            logger.info(f"Cleared all {session_count} sessions")


# Global session manager instance
session_manager = SessionManager()
