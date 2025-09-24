"""
Unit tests for safety controller.
"""

import pytest
import time
from unittest.mock import Mock, patch
from datetime import datetime, timedelta, timezone

from src.core.safety_controller import (
    SafetyController,
    SafetyLimits,
    GracefulDegradationHandler
)
from src.core.session_manager import DebugSession


class TestSafetyLimits:
    """Test SafetyLimits dataclass."""
    
    def test_default_limits(self):
        """Test default safety limits."""
        limits = SafetyLimits()
        
        assert limits.max_total_time == 40
        assert limits.max_function_time == 8
        assert limits.max_function_calls == 8
        assert limits.max_api_calls_per_minute == 30
        assert limits.max_memory_usage_mb == 50.0
        assert limits.max_depth == 5
        assert limits.max_retry_attempts == 2
        assert limits.max_repeated_functions == 3
        assert limits.max_identical_errors == 2
    
    def test_custom_limits(self):
        """Test custom safety limits."""
        limits = SafetyLimits(
            max_total_time=60,
            max_function_calls=10,
            max_depth=8
        )
        
        assert limits.max_total_time == 60
        assert limits.max_function_calls == 10
        assert limits.max_depth == 8
        # Other values should remain default
        assert limits.max_function_time == 8


class TestSafetyController:
    """Test SafetyController functionality."""
    
    def test_initialization(self):
        """Test safety controller initialization."""
        controller = SafetyController()
        
        assert controller.limits is not None
        assert isinstance(controller.limits, SafetyLimits)
        assert controller.api_call_timestamps == []
    
    def test_initialization_with_custom_limits(self):
        """Test safety controller with custom limits."""
        custom_limits = SafetyLimits(max_total_time=60)
        controller = SafetyController(custom_limits)
        
        assert controller.limits.max_total_time == 60
    
    def test_start_analysis(self):
        """Test starting analysis with safety controls."""
        controller = SafetyController()
        session = Mock(spec=DebugSession)
        session.add_log = Mock()
        session.trace_id = "test-trace-123"  # Add required attribute
        
        controller.start_analysis(session)
        
        assert hasattr(session, 'start_time')
        assert session.function_call_count == 0
        assert session.depth == 0
        session.add_log.assert_called_with("Safety controller initialized", "info")
    
    def test_should_stop_fresh_session(self):
        """Test should_stop with fresh session."""
        controller = SafetyController()
        session = self._create_test_session()
        controller.start_analysis(session)
        
        assert not controller.should_stop(session)
    
    def test_should_stop_time_limit_exceeded(self):
        """Test should_stop when time limit is exceeded."""
        controller = SafetyController()
        session = self._create_test_session()
        
        # Simulate old start time
        session.start_time = time.time() - 50  # 50 seconds ago
        
        assert controller.should_stop(session)
    
    def test_should_stop_function_limit_exceeded(self):
        """Test should_stop when function call limit is exceeded."""
        controller = SafetyController()
        session = self._create_test_session()
        controller.start_analysis(session)
        
        # Exceed function call limit
        session.function_call_count = 10  # Over the default limit of 8
        
        assert controller.should_stop(session)
    
    def test_should_stop_depth_limit_exceeded(self):
        """Test should_stop when depth limit is exceeded."""
        controller = SafetyController()
        session = self._create_test_session()
        controller.start_analysis(session)
        
        # Exceed depth limit
        session.depth = 6  # Over the default limit of 5
        
        assert controller.should_stop(session)
    
    def test_check_function_safety_valid(self):
        """Test function safety check with valid inputs."""
        controller = SafetyController()
        session = self._create_test_session()
        controller.start_analysis(session)
        
        is_safe, reason = controller.check_function_safety(
            "get_subscriptions",
            {},
            session
        )
        
        assert is_safe is True
        assert reason == ""
    
    def test_check_function_safety_session_limits_exceeded(self):
        """Test function safety check when session limits are exceeded."""
        controller = SafetyController()
        session = self._create_test_session()
        controller.start_analysis(session)
        
        # Exceed time limit
        session.start_time = time.time() - 50
        
        is_safe, reason = controller.check_function_safety(
            "test_function",
            {},
            session
        )
        
        assert is_safe is False
        assert "Session safety limits exceeded" in reason
    
    def test_check_function_safety_invalid_resource_id(self):
        """Test function safety check with invalid Azure resource ID."""
        controller = SafetyController()
        session = self._create_test_session()
        controller.start_analysis(session)
        
        is_safe, reason = controller.check_function_safety(
            "get_azure_resource_status",
            {"resource_id": "invalid-resource-id"},
            session
        )
        
        assert is_safe is False
        assert "Invalid Azure resource ID" in reason
    
    def test_check_function_safety_argument_injection(self):
        """Test function safety check with potentially unsafe arguments."""
        controller = SafetyController()
        session = self._create_test_session()
        controller.start_analysis(session)
        
        is_safe, reason = controller.check_function_safety(
            "test_function",
            {"query": "<script>alert('xss')</script>"},
            session
        )
        
        assert is_safe is False
        assert "Potentially unsafe arguments detected" in reason
    
    def test_check_function_safety_repeated_function(self):
        """Test function safety check with repeated function calls."""
        controller = SafetyController()
        session = self._create_test_session()
        controller.start_analysis(session)
        
        # Add repeated function calls - add enough to trigger the infinite loop detection first
        for i in range(5):  # More than max_repeated_functions (3) to trigger infinite loop detection
            session.function_calls.append({
                "function": "test_function", 
                "timestamp": datetime.now(timezone.utc)
            })
        
        # The should_stop method will be called first and detect infinite loop
        # So we expect "Session safety limits exceeded" rather than the specific function message
        is_safe, reason = controller.check_function_safety(
            "test_function",
            {},
            session
        )
        
        assert is_safe is False
        assert "Session safety limits exceeded" in reason
    
    def test_record_function_call(self):
        """Test recording function calls."""
        controller = SafetyController()
        session = self._create_test_session()
        session.add_log = Mock()
        
        result = {"success": True, "data": "test"}
        controller.record_function_call(session, "test_function", 1.5, result)
        
        assert session.function_call_count == 1
        assert session.depth == 1
        assert len(controller.api_call_timestamps) == 1
        session.add_log.assert_called()
    
    def test_record_function_call_with_error(self):
        """Test recording function call with error result."""
        controller = SafetyController()
        session = self._create_test_session()
        session.add_log = Mock()
        
        result = {"error": "Function failed", "details": "Some error"}
        controller.record_function_call(session, "failing_function", 0.5, result)
        
        # Should log both the function execution and the error
        assert session.add_log.call_count >= 2
    
    def test_rate_limiting(self):
        """Test API rate limiting."""
        controller = SafetyController()
        session = self._create_test_session()
        
        # Add many recent API calls
        current_time = time.time()
        controller.api_call_timestamps = [current_time - i for i in range(35)]  # 35 calls
        
        is_safe, reason = controller.check_function_safety(
            "test_function",
            {},
            session
        )
        
        assert is_safe is False
        assert "API rate limit exceeded" in reason
    
    def test_validate_azure_resource_id_valid(self):
        """Test Azure resource ID validation with valid ID."""
        controller = SafetyController()
        
        valid_id = "/subscriptions/12345/resourceGroups/test-rg/providers/Microsoft.Web/sites/test-app"
        assert controller._validate_azure_resource_id(valid_id) is True
    
    def test_validate_azure_resource_id_invalid(self):
        """Test Azure resource ID validation with invalid ID."""
        controller = SafetyController()
        
        invalid_ids = [
            "",
            "not-a-resource-id",
            "/subscriptions/12345",  # Too short
            "subscriptions/12345/resourceGroups/test"  # Missing leading slash
        ]
        
        for invalid_id in invalid_ids:
            assert controller._validate_azure_resource_id(invalid_id) is False
    
    def test_detect_infinite_loop(self):
        """Test infinite loop detection."""
        controller = SafetyController()
        session = self._create_test_session()
        
        # Add repeated function calls
        for i in range(5):
            session.function_calls.append({
                "function": "repeated_function",
                "timestamp": datetime.now(timezone.utc)
            })
        
        assert controller._detect_infinite_loop(session) is True
    
    def test_get_safety_status(self):
        """Test getting safety status."""
        controller = SafetyController()
        session = self._create_test_session()
        controller.start_analysis(session)
        
        status = controller.get_safety_status(session)
        
        assert status["session_id"] == session.trace_id
        assert status["safety_status"] == "active"
        assert "elapsed_time" in status
        assert "function_calls" in status
        assert "memory_estimate_mb" in status
        assert "should_stop" in status
    
    def _create_test_session(self) -> Mock:
        """Create a mock debug session for testing."""
        session = Mock(spec=DebugSession)
        session.trace_id = "test-trace-123"
        session.function_call_count = 0
        session.depth = 0
        session.function_calls = []
        session.findings = []
        session.add_log = Mock()
        session.get_memory_estimate_mb = Mock(return_value=1.0)
        session.start_time = time.time()  # Add start_time for time calculations
        return session


class TestGracefulDegradationHandler:
    """Test GracefulDegradationHandler functionality."""
    
    def test_handle_function_failure(self):
        """Test handling function failures."""
        session = Mock(spec=DebugSession)
        session.add_log = Mock()
        session.get_context_for_llm = Mock(return_value={"test": "context"})
        
        error = Exception("Test error message")
        result = GracefulDegradationHandler.handle_function_failure(
            "test_function",
            error,
            session
        )
        
        assert result["status"] == "partial_failure"
        assert result["function"] == "test_function"
        assert "Test error message" in result["error"]
        assert "alternative_steps" in result
        assert "recommendations" in result
        session.add_log.assert_called_with("Function test_function failed: Test error message", "error")
    
    def test_handle_function_failure_known_function(self):
        """Test handling failure for known function with specific alternatives."""
        session = Mock(spec=DebugSession)
        session.add_log = Mock()
        session.get_context_for_llm = Mock(return_value={})
        
        error = Exception("Azure API failed")
        result = GracefulDegradationHandler.handle_function_failure(
            "get_azure_resource_status",
            error,
            session
        )
        
        assert "Check Azure portal" in str(result["alternative_steps"])
        assert "az resource show" in str(result["alternative_steps"])
    
    def test_suggest_manual_steps_basic(self):
        """Test suggesting manual steps with basic session."""
        session = Mock(spec=DebugSession)
        session.findings = []
        
        steps = GracefulDegradationHandler.suggest_manual_steps(session)
        
        assert len(steps) > 0
        assert any("Azure portal" in step for step in steps)
        assert any("Azure Monitor" in step for step in steps)
    
    def test_suggest_manual_steps_with_network_findings(self):
        """Test suggesting manual steps with network-related findings."""
        session = Mock(spec=DebugSession)
        session.findings = [
            {"finding": "Network connectivity issue detected", "severity": "warning"}
        ]
        
        steps = GracefulDegradationHandler.suggest_manual_steps(session)
        
        # Should include network-specific suggestion at the beginning
        assert any("network connectivity" in step.lower() for step in steps)
    
    def test_suggest_manual_steps_with_permission_findings(self):
        """Test suggesting manual steps with permission-related findings."""
        session = Mock(spec=DebugSession)
        session.findings = [
            {"finding": "Permission denied for resource access", "severity": "error"}
        ]
        
        steps = GracefulDegradationHandler.suggest_manual_steps(session)
        
        # Should include permission-specific suggestion
        assert any("permission" in step.lower() for step in steps)
    
    def test_suggest_manual_steps_multiple_findings(self):
        """Test suggesting manual steps with multiple types of findings."""
        session = Mock(spec=DebugSession)
        session.findings = [
            {"finding": "Network timeout occurred", "severity": "warning"},
            {"finding": "Deployment configuration issue", "severity": "info"},
            {"finding": "Storage account access problem", "severity": "error"}
        ]
        
        steps = GracefulDegradationHandler.suggest_manual_steps(session)
        
        # Should include suggestions for multiple issue types
        assert any("network" in step.lower() for step in steps)
        assert any("deployment" in step.lower() for step in steps)
        assert any("storage" in step.lower() for step in steps)
    
    def test_create_fallback_response(self):
        """Test creating fallback response."""
        session = Mock(spec=DebugSession)
        session.get_context_for_llm = Mock(return_value={"session": "context"})
        
        available_data = {"partial": "results"}
        
        with patch.object(GracefulDegradationHandler, 'suggest_manual_steps') as mock_suggest:
            mock_suggest.return_value = ["Step 1", "Step 2"]
            
            result = GracefulDegradationHandler.create_fallback_response(
                "test_operation",
                available_data,
                session
            )
        
        assert result["status"] == "partial_success"
        assert result["failed_operation"] == "test_operation"
        assert result["available_data"] == available_data
        assert result["manual_steps"] == ["Step 1", "Step 2"]
        assert "next_actions" in result
        mock_suggest.assert_called_once_with(session)


if __name__ == "__main__":
    pytest.main([__file__])
