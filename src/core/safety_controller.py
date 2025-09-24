"""
Safety Controller for AZEBAL Autonomous AI Operations

Implements multi-layer safety controls to prevent infinite loops and resource exhaustion.
"""

import time
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timezone

from src.core.logging_config import get_logger
from src.core.session_manager import DebugSession

logger = get_logger(__name__)


@dataclass
class SafetyLimits:
    """Safety limits for autonomous operations."""
    
    # Time limits (optimized for Cursor timeout constraints)
    max_total_time: int = 40  # 40 seconds total
    max_function_time: int = 8  # 8 seconds per function
    
    # Resource limits
    max_function_calls: int = 8
    max_api_calls_per_minute: int = 30
    max_memory_usage_mb: float = 50.0
    
    # Behavior limits
    max_depth: int = 5
    max_retry_attempts: int = 2
    
    # Loop detection
    max_repeated_functions: int = 3
    max_identical_errors: int = 2


class SafetyController:
    """Multi-layer safety system for autonomous AI operations."""
    
    def __init__(self, limits: Optional[SafetyLimits] = None):
        """
        Initialize safety controller.
        
        Args:
            limits: Optional custom safety limits
        """
        self.limits = limits or SafetyLimits()
        self.api_call_timestamps: List[float] = []
        
        logger.info(f"SafetyController initialized with limits: {self.limits}")
    
    def start_analysis(self, session: DebugSession) -> None:
        """Initialize safety controls for a session."""
        session.start_time = time.time()
        session.function_call_count = 0
        session.depth = 0
        
        session.add_log("Safety controller initialized", "info")
        logger.info(f"[{session.trace_id}] Safety controls started")
    
    def should_stop(self, session: DebugSession) -> bool:
        """
        Check if analysis should be stopped for safety reasons.
        
        Args:
            session: Debug session to check
            
        Returns:
            bool: True if analysis should stop
        """
        # Time limit check
        if self._is_time_limit_exceeded(session):
            return True
        
        # Function call limit check
        if self._is_function_limit_exceeded(session):
            return True
        
        # Depth limit check
        if self._is_depth_limit_exceeded(session):
            return True
        
        # Loop detection
        if self._detect_infinite_loop(session):
            return True
        
        # Memory usage check
        if self._is_memory_limit_exceeded(session):
            return True
        
        return False
    
    def check_function_safety(
        self, 
        function_name: str, 
        args: Dict[str, Any], 
        session: DebugSession
    ) -> tuple[bool, str]:
        """
        Check if it's safe to execute a function.
        
        Args:
            function_name: Name of function to execute
            args: Function arguments
            session: Debug session
            
        Returns:
            tuple[bool, str]: (is_safe, reason_if_not_safe)
        """
        # Basic safety checks
        if self.should_stop(session):
            return False, "Session safety limits exceeded"
        
        # Rate limiting check
        if self._is_rate_limited():
            return False, "API rate limit exceeded"
        
        # Function-specific safety checks
        if function_name in ["query_azure_logs", "get_azure_resource_status"]:
            resource_id = args.get("resource_id")
            if not self._validate_azure_resource_id(resource_id):
                return False, f"Invalid Azure resource ID: {resource_id}"
        
        # Check for argument injection
        if self._detect_argument_injection(args):
            return False, "Potentially unsafe arguments detected"
        
        # Check function repetition
        if self._is_function_repeated_too_often(function_name, session):
            return False, f"Function {function_name} called too many times"
        
        return True, ""
    
    def record_function_call(
        self, 
        session: DebugSession, 
        function_name: str,
        execution_time: float,
        result: Dict[str, Any]
    ) -> None:
        """
        Record a function call for safety tracking.
        
        Args:
            session: Debug session
            function_name: Name of executed function
            execution_time: Time taken to execute
            result: Function result
        """
        session.function_call_count += 1
        session.depth += 1
        
        # Record API call timestamp for rate limiting
        self.api_call_timestamps.append(time.time())
        
        # Clean old timestamps (keep only last minute)
        cutoff_time = time.time() - 60  # 1 minute ago
        self.api_call_timestamps = [
            ts for ts in self.api_call_timestamps if ts > cutoff_time
        ]
        
        # Log function call
        session.add_log(
            f"Function executed: {function_name} (time: {execution_time:.2f}s)", 
            "info"
        )
        
        # Check for errors in result
        if "error" in result:
            session.add_log(f"Function error: {result.get('error')}", "warning")
        
        logger.debug(f"[{session.trace_id}] Function call recorded: {function_name}")
    
    def _is_time_limit_exceeded(self, session: DebugSession) -> bool:
        """Check if time limit is exceeded."""
        if not session.start_time:
            return False
        
        elapsed_time = time.time() - session.start_time
        if elapsed_time > self.limits.max_total_time:
            session.add_log(f"Time limit exceeded: {elapsed_time:.2f}s > {self.limits.max_total_time}s", "warning")
            logger.warning(f"[{session.trace_id}] Time limit exceeded")
            return True
        
        return False
    
    def _is_function_limit_exceeded(self, session: DebugSession) -> bool:
        """Check if function call limit is exceeded."""
        if session.function_call_count >= self.limits.max_function_calls:
            session.add_log(f"Function call limit exceeded: {session.function_call_count} >= {self.limits.max_function_calls}", "warning")
            logger.warning(f"[{session.trace_id}] Function call limit exceeded")
            return True
        
        return False
    
    def _is_depth_limit_exceeded(self, session: DebugSession) -> bool:
        """Check if analysis depth limit is exceeded."""
        if session.depth >= self.limits.max_depth:
            session.add_log(f"Analysis depth limit exceeded: {session.depth} >= {self.limits.max_depth}", "warning")
            logger.warning(f"[{session.trace_id}] Depth limit exceeded")
            return True
        
        return False
    
    def _is_rate_limited(self) -> bool:
        """Check if API rate limit is exceeded."""
        recent_calls = len(self.api_call_timestamps)
        if recent_calls >= self.limits.max_api_calls_per_minute:
            logger.warning(f"API rate limit exceeded: {recent_calls} calls in last minute")
            return True
        
        return False
    
    def _is_memory_limit_exceeded(self, session: DebugSession) -> bool:
        """Check if memory usage limit is exceeded."""
        estimated_memory = session.get_memory_estimate_mb()
        if estimated_memory > self.limits.max_memory_usage_mb:
            session.add_log(f"Memory limit exceeded: {estimated_memory:.2f}MB > {self.limits.max_memory_usage_mb}MB", "warning")
            logger.warning(f"[{session.trace_id}] Memory limit exceeded")
            return True
        
        return False
    
    def _detect_infinite_loop(self, session: DebugSession) -> bool:
        """Detect potential infinite loops in function calls."""
        if len(session.function_calls) < 3:
            return False
        
        # Check for repeated function patterns
        recent_functions = [fc["function"] for fc in session.function_calls[-5:]]
        function_counts = {}
        
        for func in recent_functions:
            function_counts[func] = function_counts.get(func, 0) + 1
        
        # Check if any function is repeated too many times
        for func, count in function_counts.items():
            if count > self.limits.max_repeated_functions:
                session.add_log(f"Infinite loop detected: {func} called {count} times recently", "warning")
                logger.warning(f"[{session.trace_id}] Infinite loop detected for function: {func}")
                return True
        
        return False
    
    def _is_function_repeated_too_often(self, function_name: str, session: DebugSession) -> bool:
        """Check if a specific function is being called too often."""
        recent_calls = [fc for fc in session.function_calls[-10:] if fc["function"] == function_name]
        
        if len(recent_calls) > self.limits.max_repeated_functions:
            logger.warning(f"[{session.trace_id}] Function {function_name} called too often")
            return True
        
        return False
    
    def _validate_azure_resource_id(self, resource_id: str) -> bool:
        """Validate Azure resource ID format."""
        if not resource_id:
            return False
        
        # Basic Azure resource ID pattern
        pattern = r'^/subscriptions/[^/]+/resourceGroups/[^/]+/providers/[^/]+/.+'
        return bool(re.match(pattern, resource_id))
    
    def _detect_argument_injection(self, args: Dict[str, Any]) -> bool:
        """Detect potentially unsafe arguments."""
        dangerous_patterns = [
            r'<script',
            r'javascript:',
            r'data:',
            r'\$\(',
            r'eval\(',
            r'exec\(',
            r'system\(',
            r'shell_exec\(',
            r'`.*`',  # Command substitution
            r'\|\s*\w+',  # Pipe to commands
            r'&&\s*\w+',  # Command chaining
            r';\s*\w+',  # Command separation
        ]
        
        for key, value in args.items():
            if isinstance(value, str):
                value_lower = value.lower()
                for pattern in dangerous_patterns:
                    if re.search(pattern, value_lower, re.IGNORECASE):
                        logger.warning(f"Potentially unsafe argument detected: {key}")
                        return True
        
        return False
    
    def get_safety_status(self, session: DebugSession) -> Dict[str, Any]:
        """Get current safety status for a session."""
        current_time = time.time()
        elapsed_time = current_time - session.start_time if session.start_time else 0
        
        return {
            "session_id": session.trace_id,
            "safety_status": "active",
            "elapsed_time": elapsed_time,
            "time_limit": self.limits.max_total_time,
            "function_calls": session.function_call_count,
            "function_limit": self.limits.max_function_calls,
            "depth": session.depth,
            "depth_limit": self.limits.max_depth,
            "memory_estimate_mb": session.get_memory_estimate_mb(),
            "memory_limit_mb": self.limits.max_memory_usage_mb,
            "api_calls_last_minute": len(self.api_call_timestamps),
            "api_limit_per_minute": self.limits.max_api_calls_per_minute,
            "should_stop": self.should_stop(session)
        }


class GracefulDegradationHandler:
    """Handle cases where autonomous analysis needs to fall back to simpler methods."""
    
    @staticmethod
    def handle_function_failure(
        function_name: str, 
        error: Exception, 
        session: DebugSession
    ) -> Dict[str, Any]:
        """
        Handle function execution failures gracefully.
        
        Args:
            function_name: Name of failed function
            error: Exception that occurred
            session: Debug session
            
        Returns:
            Dict containing fallback response
        """
        error_msg = str(error)
        session.add_log(f"Function {function_name} failed: {error_msg}", "error")
        
        # Suggest alternative approaches
        alternatives = {
            "get_azure_resource_status": [
                "Check Azure portal for resource health",
                "Use Azure CLI: az resource show --ids {resource_id}",
                "Review Azure Activity Log for recent changes"
            ],
            "query_azure_logs": [
                "Check logs directly in Azure portal",
                "Use Azure CLI: az monitor log-analytics query",
                "Review application-specific logs"
            ],
            "check_network_connectivity": [
                "Use Azure Network Watcher",
                "Check Network Security Group rules",
                "Verify virtual network configuration"
            ],
            "check_resource_permissions": [
                "Check Azure RBAC in portal",
                "Use Azure CLI: az role assignment list",
                "Verify user permissions with administrator"
            ]
        }
        
        alternative_steps = alternatives.get(function_name, [
            "Try manual troubleshooting steps",
            "Check Azure portal for resource status",
            "Contact support if issue persists"
        ])
        
        return {
            "status": "partial_failure",
            "function": function_name,
            "error": error_msg,
            "message": f"Function {function_name} failed, but analysis can continue.",
            "alternative_steps": alternative_steps,
            "session_progress": session.get_context_for_llm(),
            "recommendations": [
                "Continue with available analysis tools",
                "Use manual verification steps provided",
                "Check error logs for detailed information"
            ]
        }
    
    @staticmethod
    def suggest_manual_steps(session: DebugSession) -> List[str]:
        """Suggest manual debugging steps when autonomous analysis is insufficient."""
        base_steps = [
            "Check Azure portal for resource health indicators",
            "Review Azure Monitor alerts and metrics",
            "Verify network security group rules",
            "Check Azure AD permissions and role assignments",
            "Review resource configuration for recent changes"
        ]
        
        # Customize suggestions based on session findings
        customized_steps = []
        
        # Check findings for specific issues
        findings_text = ' '.join([f["finding"].lower() for f in session.findings])
        
        if "network" in findings_text:
            customized_steps.append("Focus on network connectivity and firewall rules")
        
        if "permission" in findings_text or "access" in findings_text:
            customized_steps.append("Review access permissions and authentication settings")
        
        if "deployment" in findings_text:
            customized_steps.append("Check deployment logs and configuration")
        
        if "storage" in findings_text:
            customized_steps.append("Verify storage account access and configuration")
        
        if "app service" in findings_text or "web" in findings_text:
            customized_steps.append("Review App Service configuration and logs")
        
        # Combine customized and base steps
        return customized_steps + base_steps
    
    @staticmethod
    def create_fallback_response(
        failed_operation: str, 
        available_data: Dict[str, Any], 
        session: DebugSession
    ) -> Dict[str, Any]:
        """Create meaningful response when primary analysis fails."""
        manual_steps = GracefulDegradationHandler.suggest_manual_steps(session)
        
        return {
            "status": "partial_success",
            "failed_operation": failed_operation,
            "message": f"Primary analysis for {failed_operation} failed, but partial results are available.",
            "available_data": available_data,
            "manual_steps": manual_steps,
            "session_context": session.get_context_for_llm(),
            "next_actions": [
                "Review available analysis data",
                "Follow manual debugging steps",
                "Use Azure portal for detailed investigation"
            ]
        }


# Global safety controller instance
safety_controller = SafetyController()
