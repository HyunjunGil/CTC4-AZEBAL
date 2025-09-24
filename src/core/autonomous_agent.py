"""
Autonomous AI Agent for AZEBAL

Implements autonomous AI debugging agent with function calling capabilities.
"""

import json
import asyncio
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from src.core.logging_config import get_logger
from src.core.session_manager import DebugSession
from src.core.safety_controller import SafetyController, GracefulDegradationHandler
from src.services.llm_factory import llm_factory
from src.services.azure_api_client import AzureAPIClient

logger = get_logger(__name__)


class AnalysisStatus(Enum):
    """Analysis status values."""
    DONE = "done"
    REQUEST = "request"
    CONTINUE = "continue"
    FAIL = "fail"


@dataclass
class FunctionCall:
    """Represents a function call request from the LLM."""
    name: str
    arguments: Dict[str, Any]


@dataclass
class FunctionResult:
    """Represents the result of a function call."""
    name: str
    result: Dict[str, Any]
    execution_time: float
    success: bool


@dataclass
class AnalysisResult:
    """Final analysis result."""
    status: AnalysisStatus
    message: str
    trace_id: str
    progress: int = 0
    analysis_results: Optional[Dict[str, Any]] = None
    debugging_process: Optional[List[str]] = None
    actions_to_take: Optional[List[str]] = None
    session_context: Optional[Dict[str, Any]] = None


class AutonomousDebugAgent:
    """Autonomous AI agent for Azure debugging with function calling."""
    
    def __init__(
        self, 
        azure_client: AzureAPIClient,
        safety_controller: SafetyController,
        session: DebugSession
    ):
        """
        Initialize autonomous debug agent.
        
        Args:
            azure_client: Azure API client
            safety_controller: Safety controller for limits
            session: Debug session
        """
        self.azure_client = azure_client
        self.safety_controller = safety_controller
        self.session = session
        self.llm_service = llm_factory.get_llm_service()
        
        # Available functions for the AI
        self.available_functions = {
            "get_azure_resource_status": self._get_azure_resource_status,
            "query_azure_logs": self._query_azure_logs,
            "check_resource_permissions": self._check_resource_permissions,
            "get_resource_group_resources": self._get_resource_group_resources,
            "get_subscriptions": self._get_subscriptions,
            "analyze_error_pattern": self._analyze_error_pattern,
            "suggest_solution": self._suggest_solution,
        }
        
        logger.info(f"[{session.trace_id}] AutonomousDebugAgent initialized with {len(self.available_functions)} functions")
    
    async def analyze_error(self, error_context: Dict[str, Any]) -> AnalysisResult:
        """
        Main entry point for autonomous error analysis.
        
        Args:
            error_context: Context containing error description and related data
            
        Returns:
            AnalysisResult: Complete analysis result
        """
        logger.info(f"[{self.session.trace_id}] Starting autonomous error analysis")
        self.session.add_log("Starting autonomous error analysis")
        
        try:
            # Prepare function definitions for LLM
            function_definitions = self._prepare_function_definitions()
            
            # Start autonomous analysis loop
            result = await self._autonomous_analysis_loop(error_context, function_definitions)
            
            logger.info(f"[{self.session.trace_id}] Autonomous analysis completed with status: {result.status.value}")
            return result
            
        except Exception as e:
            logger.error(f"[{self.session.trace_id}] Autonomous analysis failed: {str(e)}")
            self.session.add_log(f"Analysis failed: {str(e)}", "error")
            
            return AnalysisResult(
                status=AnalysisStatus.FAIL,
                message=f"Analysis failed due to internal error: {str(e)}",
                trace_id=self.session.trace_id
            )
    
    async def _autonomous_analysis_loop(
        self, 
        error_context: Dict[str, Any], 
        function_definitions: List[Dict[str, Any]]
    ) -> AnalysisResult:
        """
        Autonomous analysis loop with function calling.
        
        Args:
            error_context: Error context
            function_definitions: Available function definitions
            
        Returns:
            AnalysisResult: Analysis result
        """
        # Build initial conversation
        messages = self._build_initial_prompt(error_context)
        
        while not self.safety_controller.should_stop(self.session):
            try:
                # Call LLM with function definitions
                logger.debug(f"[{self.session.trace_id}] Calling LLM with {len(function_definitions)} functions")
                
                # For now, simulate LLM response since we need to implement function calling in LLM services
                # This is a placeholder that demonstrates the structure
                # TODO : Replace with actual LLM call
                response = await self._call_llm_with_functions(messages, function_definitions)
                
                if response.get("function_call"):
                    # Execute the requested function
                    function_result = await self._execute_function(response["function_call"])
                    
                    # Add function result to conversation
                    messages.append({
                        "role": "function",
                        "name": response["function_call"]["name"],
                        "content": json.dumps(function_result.result)
                    })
                    
                    # Update session with new information
                    self.session.add_function_result(function_result.name, function_result.result)
                    
                    # Record function call for safety
                    self.safety_controller.record_function_call(
                        self.session,
                        function_result.name,
                        function_result.execution_time,
                        function_result.result
                    )
                    
                else:
                    # LLM has concluded analysis
                    return self._parse_final_response(response.get("content", ""), self.session)
                    
            except Exception as e:
                logger.error(f"[{self.session.trace_id}] Error in analysis loop: {str(e)}")
                self.session.add_log(f"Analysis loop error: {str(e)}", "error")
                
                # Try graceful degradation
                fallback = GracefulDegradationHandler.create_fallback_response(
                    "autonomous_analysis", 
                    {"error": str(e)}, 
                    self.session
                )
                
                return AnalysisResult(
                    status=AnalysisStatus.CONTINUE,
                    message=fallback["message"],
                    trace_id=self.session.trace_id,
                    progress=50,
                    analysis_results=fallback
                )
        
        # Safety controller stopped the analysis
        logger.warning(f"[{self.session.trace_id}] Analysis stopped by safety controller")
        self.session.add_log("Analysis paused due to safety limits", "warning")
        
        return AnalysisResult(
            status=AnalysisStatus.CONTINUE,
            message="Analysis paused due to time/depth limits. Use continue functionality to resume.",
            trace_id=self.session.trace_id,
            progress=self.session.progress,
            session_context=self.session.get_context_for_llm()
        )
    
    async def _call_llm_with_functions(
        self, 
        messages: List[Dict[str, Any]], 
        function_definitions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Call LLM with function calling capability.
        
        Note: This is a placeholder implementation. The actual implementation
        would require extending the LLM services to support function calling.
        """
        logger.debug(f"[{self.session.trace_id}] Simulating LLM call with function definitions")
        
        # For MVP, we'll simulate intelligent function selection based on error context
        error_description = self.session.error_description.lower()
        
        # Simple heuristic to decide which function to call
        if "storage" in error_description and not any(fc["function"] == "get_azure_resource_status" for fc in self.session.function_calls):
            return {
                "function_call": {
                    "name": "get_subscriptions",
                    "arguments": {}
                }
            }
        elif "app service" in error_description or "web" in error_description:
            if not any(fc["function"] == "get_subscriptions" for fc in self.session.function_calls):
                return {
                    "function_call": {
                        "name": "get_subscriptions", 
                        "arguments": {}
                    }
                }
            else:
                return {
                    "function_call": {
                        "name": "analyze_error_pattern",
                        "arguments": {"error_text": error_description}
                    }
                }
        elif len(self.session.function_calls) == 0:
            # First call - get subscriptions
            return {
                "function_call": {
                    "name": "get_subscriptions",
                    "arguments": {}
                }
            }
        elif len(self.session.function_calls) == 1:
            # Second call - analyze error pattern
            return {
                "function_call": {
                    "name": "analyze_error_pattern", 
                    "arguments": {"error_text": error_description}
                }
            }
        else:
            # Conclude analysis
            return {
                "content": "Based on my analysis, I have identified the issue and can provide recommendations."
            }
    
    async def _execute_function(self, function_call: Dict[str, Any]) -> FunctionResult:
        """
        Execute a function call safely.
        
        Args:
            function_call: Function call details
            
        Returns:
            FunctionResult: Function execution result
        """
        function_name = function_call.get("name")
        arguments = function_call.get("arguments", {})
        
        logger.info(f"[{self.session.trace_id}] Executing function: {function_name}")
        self.session.add_log(f"Executing function: {function_name}")
        
        # Safety check
        is_safe, reason = self.safety_controller.check_function_safety(
            function_name, arguments, self.session
        )
        
        if not is_safe:
            logger.warning(f"[{self.session.trace_id}] Function call blocked: {reason}")
            return FunctionResult(
                name=function_name,
                result={"error": f"Function call blocked: {reason}"},
                execution_time=0.0,
                success=False
            )
        
        # Execute function
        start_time = time.time()
        try:
            function = self.available_functions.get(function_name)
            if not function:
                raise ValueError(f"Unknown function: {function_name}")
            
            result = await function(**arguments)
            execution_time = time.time() - start_time
            
            logger.info(f"[{self.session.trace_id}] Function {function_name} completed in {execution_time:.2f}s")
            
            return FunctionResult(
                name=function_name,
                result=result,
                execution_time=execution_time,
                success=True
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"[{self.session.trace_id}] Function {function_name} failed: {str(e)}")
            
            # Handle function failure gracefully
            fallback = GracefulDegradationHandler.handle_function_failure(
                function_name, e, self.session
            )
            
            return FunctionResult(
                name=function_name,
                result=fallback,
                execution_time=execution_time,
                success=False
            )
    
    def _prepare_function_definitions(self) -> List[Dict[str, Any]]:
        """Prepare function definitions for LLM."""
        return [
            {
                "name": "get_azure_resource_status",
                "description": "Get the current status and configuration of any Azure resource",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "resource_id": {
                            "type": "string",
                            "description": "Full Azure resource ID"
                        }
                    },
                    "required": ["resource_id"]
                }
            },
            {
                "name": "query_azure_logs",
                "description": "Query Azure Monitor logs for a specific resource",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "resource_id": {"type": "string"},
                        "time_range": {"type": "string", "description": "Time range like '1h', '24h'"},
                        "query": {"type": "string", "description": "Optional KQL query"}
                    },
                    "required": ["resource_id"]
                }
            },
            {
                "name": "check_resource_permissions",
                "description": "Check user permissions on a specific Azure resource",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "resource_id": {"type": "string"}
                    },
                    "required": ["resource_id"]
                }
            },
            {
                "name": "get_resource_group_resources",
                "description": "Get all resources in a resource group",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "resource_group": {"type": "string"}
                    },
                    "required": ["resource_group"]
                }
            },
            {
                "name": "get_subscriptions",
                "description": "Get list of available Azure subscriptions",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "analyze_error_pattern",
                "description": "Analyze error text to identify patterns and potential causes",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "error_text": {"type": "string"}
                    },
                    "required": ["error_text"]
                }
            },
            {
                "name": "suggest_solution",
                "description": "Generate solution recommendations based on analysis",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "problem_summary": {"type": "string"},
                        "findings": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["problem_summary"]
                }
            }
        ]
    
    def _build_initial_prompt(self, error_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build the initial prompt for autonomous analysis."""
        system_prompt = f"""You are AZEBAL, an expert Azure debugging assistant. Your goal is to analyze the provided error and systematically investigate the root cause using available Azure APIs.

Available Functions:
- get_azure_resource_status: Check status of any Azure resource
- query_azure_logs: Get logs from Azure Monitor
- check_resource_permissions: Verify access permissions
- get_resource_group_resources: List resources in a resource group
- get_subscriptions: Get available subscriptions
- analyze_error_pattern: Analyze error patterns
- suggest_solution: Generate solution recommendations

Analysis Approach:
1. Start by understanding the error context and identifying potentially related Azure resources
2. Use get_subscriptions to understand the available Azure environment
3. Use get_azure_resource_status to check the health of key resources
4. If logs might contain relevant information, use query_azure_logs
5. Check permissions if the error might be access-related
6. Use analyze_error_pattern to understand the error
7. Finally, use suggest_solution to provide actionable recommendations

Important Guidelines:
- Be systematic and logical in your investigation
- Always explain your reasoning for each function call
- If you find the root cause, provide clear remediation steps
- If you need more information, use the available functions
- Conclude with clear, actionable recommendations

Current Error Context:
Error Description: {error_context.get('description', 'No description provided')}
Session ID: {self.session.trace_id}

Begin your systematic analysis now."""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Please analyze this Azure error: {error_context.get('description', '')}"}
        ]
    
    def _parse_final_response(self, content: str, session: DebugSession) -> AnalysisResult:
        """Parse the final LLM response into structured result."""
        logger.info(f"[{session.trace_id}] Parsing final analysis response")
        
        # Update session status
        session.mark_as_completed()
        
        # Generate debugging process from session logs
        debugging_process = [log["message"] for log in session.execution_logs[-10:]]
        
        # Generate actions from session findings
        actions_to_take = [
            "Review the analysis findings below",
            "Follow the recommended remediation steps",
            "Monitor the system after applying fixes",
            "Contact support if issues persist"
        ]
        
        # Add specific actions based on findings
        if session.findings:
            for finding in session.findings[-5:]:  # Last 5 findings
                if "permission" in finding["finding"].lower():
                    actions_to_take.append("Check and update Azure RBAC permissions")
                elif "network" in finding["finding"].lower():
                    actions_to_take.append("Review network configuration and security groups")
                elif "configuration" in finding["finding"].lower():
                    actions_to_take.append("Verify resource configuration settings")
        
        analysis_results = {
            "error_category": "Azure Service Issue",
            "confidence_level": "high" if len(session.findings) > 2 else "medium",
            "identified_resources": session.identified_resources,
            "key_findings": [f["finding"] for f in session.findings],
            "function_calls_made": len(session.function_calls),
            "session_duration": (session.last_activity - session.created_at).total_seconds()
        }
        
        return AnalysisResult(
            status=AnalysisStatus.DONE,
            message=content or "Analysis completed successfully. See detailed results below.",
            trace_id=session.trace_id,
            progress=100,
            analysis_results=analysis_results,
            debugging_process=debugging_process,
            actions_to_take=actions_to_take,
            session_context=session.get_context_for_llm()
        )
    
    # Function implementations
    async def _get_azure_resource_status(self, resource_id: str) -> Dict[str, Any]:
        """Get Azure resource status."""
        logger.info(f"[{self.session.trace_id}] Getting status for resource: {resource_id}")
        result = await self.azure_client.get_resource_status(resource_id)
        
        if result.get("success"):
            self.session.add_finding(f"Retrieved status for resource: {resource_id}", "info", "resource_status")
        else:
            self.session.add_finding(f"Failed to get status for resource: {resource_id}", "warning", "resource_status")
        
        return result
    
    async def _query_azure_logs(self, resource_id: str, time_range: str = "1h", query: Optional[str] = None) -> Dict[str, Any]:
        """Query Azure logs."""
        logger.info(f"[{self.session.trace_id}] Querying logs for resource: {resource_id}")
        result = await self.azure_client.query_resource_logs(resource_id, time_range, query)
        
        self.session.add_finding(f"Queried logs for resource: {resource_id}", "info", "logs")
        return result
    
    async def _check_resource_permissions(self, resource_id: str) -> Dict[str, Any]:
        """Check resource permissions."""
        logger.info(f"[{self.session.trace_id}] Checking permissions for resource: {resource_id}")
        result = await self.azure_client.check_resource_permissions(resource_id)
        
        if result.get("success"):
            self.session.add_finding(f"User has access to resource: {resource_id}", "info", "permissions")
        else:
            self.session.add_finding(f"Permission issue with resource: {resource_id}", "warning", "permissions")
        
        return result
    
    async def _get_resource_group_resources(self, resource_group: str) -> Dict[str, Any]:
        """Get resource group resources."""
        logger.info(f"[{self.session.trace_id}] Getting resources for RG: {resource_group}")
        result = await self.azure_client.get_resource_group_resources(resource_group)
        
        if result.get("success"):
            count = result.get("count", 0)
            self.session.add_finding(f"Found {count} resources in resource group: {resource_group}", "info", "resource_discovery")
        
        return result
    
    async def _get_subscriptions(self) -> Dict[str, Any]:
        """Get Azure subscriptions."""
        logger.info(f"[{self.session.trace_id}] Getting Azure subscriptions")
        result = await self.azure_client.get_subscriptions()
        
        if result.get("success"):
            count = result.get("count", 0)
            self.session.add_finding(f"Found {count} Azure subscriptions", "info", "environment")
        
        return result
    
    async def _analyze_error_pattern(self, error_text: str) -> Dict[str, Any]:
        """Analyze error pattern."""
        logger.info(f"[{self.session.trace_id}] Analyzing error pattern")
        
        # Simple pattern analysis
        patterns = {
            "authentication": ["401", "unauthorized", "authentication failed", "login"],
            "permission": ["403", "forbidden", "access denied", "permission"],
            "network": ["timeout", "connection", "network", "unreachable"],
            "storage": ["storage", "blob", "file", "disk"],
            "compute": ["vm", "virtual machine", "compute", "instance"]
        }
        
        found_patterns = []
        error_lower = error_text.lower()
        
        for category, keywords in patterns.items():
            if any(keyword in error_lower for keyword in keywords):
                found_patterns.append(category)
        
        result = {
            "success": True,
            "error_text": error_text,
            "identified_patterns": found_patterns,
            "recommendations": []
        }
        
        # Add specific recommendations based on patterns
        if "authentication" in found_patterns:
            result["recommendations"].append("Check authentication credentials and token expiration")
        if "permission" in found_patterns:
            result["recommendations"].append("Verify user has required permissions (RBAC)")
        if "network" in found_patterns:
            result["recommendations"].append("Check network configuration and security groups")
        
        self.session.add_finding(f"Identified error patterns: {', '.join(found_patterns)}", "info", "pattern_analysis")
        
        return result
    
    async def _suggest_solution(self, problem_summary: str, findings: Optional[List[str]] = None) -> Dict[str, Any]:
        """Suggest solution based on analysis."""
        logger.info(f"[{self.session.trace_id}] Generating solution suggestions")
        
        findings = findings or [f["finding"] for f in self.session.findings]
        
        suggestions = [
            "Review the identified issues in the analysis",
            "Follow Azure best practices for the affected services",
            "Monitor the system after implementing fixes",
            "Test the solution in a development environment first"
        ]
        
        # Add specific suggestions based on findings
        findings_text = ' '.join(findings).lower()
        
        if "permission" in findings_text:
            suggestions.insert(0, "Update Azure RBAC role assignments for the user")
        if "network" in findings_text:
            suggestions.insert(0, "Review and update network security group rules")
        if "storage" in findings_text:
            suggestions.insert(0, "Check storage account access keys and configuration")
        
        result = {
            "success": True,
            "problem_summary": problem_summary,
            "analyzed_findings": findings,
            "recommended_actions": suggestions,
            "priority": "high" if len(findings) > 3 else "medium"
        }
        
        self.session.add_finding("Generated solution recommendations", "info", "solution")
        
        return result
