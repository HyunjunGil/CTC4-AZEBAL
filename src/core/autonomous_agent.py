"""
Autonomous AI Agent for AZEBAL - OPTIMIZED VERSION

Improved implementation with pre-loaded static data and minimal LLM calls.
Static error patterns and solution data are included in initial messages.
"""

import json
import asyncio
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from src.core.logging_config import get_logger
from src.core.session_manager import DebugSession
from src.core.safety_controller import safety_controller, GracefulDegradationHandler
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
    """Autonomous AI agent for Azure debugging with optimized function calling."""
    
    def __init__(
        self, 
        azure_client: AzureAPIClient,
        session: DebugSession
    ):
        """
        Initialize autonomous debug agent.
        
        Args:
            azure_client: Azure API client
            session: Debug session
        """
        self.azure_client = azure_client
        self.session = session
        self.llm_service = llm_factory.get_llm_service()
        
        # Available functions for the AI - ONLY live Azure data retrieval
        self.available_functions = {
            "get_azure_resource_status": self._get_azure_resource_status,
            "query_azure_logs": self._query_azure_logs,
            "check_resource_permissions": self._check_resource_permissions,
            "get_resource_group_resources": self._get_resource_group_resources,
            "get_subscriptions": self._get_subscriptions,
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
        
        Implements the 4-state debugging flow: done|request|continue|fail
        
        Args:
            error_context: Error context
            function_definitions: Available function definitions
            
        Returns:
            AnalysisResult: Analysis result with proper status
        """
        # Build initial conversation with pre-loaded static data
        messages = self._build_initial_prompt(error_context)
        
        while not safety_controller.should_stop(self.session):
            try:
                # Call LLM with function definitions
                logger.debug(f"[{self.session.trace_id}] Calling LLM with {len(function_definitions)} functions")
                
                # Call the actual LLM with function calling support
                response = await self.llm_service.ask_llm_with_functions(messages, function_definitions)
                
                if response.get("function_call"):
                    # LLM requests a function call - continue investigation
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
                    safety_controller.record_function_call(
                        self.session,
                        function_result.name,
                        function_result.execution_time,
                        function_result.result
                    )
                    
                else:
                    # LLM has concluded analysis - return DONE status with complete error report
                    logger.info(f"[{self.session.trace_id}] LLM concluded analysis - generating final report")
                    return self._parse_final_response(response.get("content", ""), self.session)
                    
            except Exception as e:
                logger.error(f"[{self.session.trace_id}] Error in analysis loop: {str(e)}")
                self.session.add_log(f"Analysis loop error: {str(e)}", "error")
                
                # Analysis failed due to unexpected error - return FAIL status
                return AnalysisResult(
                    status=AnalysisStatus.FAIL,
                    message=f"Analysis failed due to internal error: {str(e)}",
                    trace_id=self.session.trace_id,
                    progress=0,
                    analysis_results={"error": str(e), "stage": "analysis_loop"}
                )
        
        # Safety controller stopped the analysis - return CONTINUE status
        logger.warning(f"[{self.session.trace_id}] Analysis stopped by safety controller")
        self.session.add_log("Analysis paused due to safety limits", "warning")
        
        return AnalysisResult(
            status=AnalysisStatus.CONTINUE,
            message="Analysis paused due to time/depth limits. Use continue functionality to resume.",
            trace_id=self.session.trace_id,
            progress=self.session.progress,
            session_context=self.session.get_context_for_llm(),
            analysis_results={
                "partial_findings": [f["finding"] for f in self.session.findings],
                "function_calls_made": len(self.session.function_calls),
                "session_duration": time.time() - self.session.created_at.timestamp(),
                "continue_reason": "safety_limits_reached"
            }
        )
    
    
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
        
        # Parse arguments if they're a JSON string
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                logger.warning(f"[{self.session.trace_id}] Failed to parse function arguments: {arguments}")
                arguments = {}
        
        logger.info(f"[{self.session.trace_id}] Executing function: {function_name}")
        self.session.add_log(f"Executing function: {function_name}")
        
        # Safety check
        is_safe, reason = safety_controller.check_function_safety(
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
            }
        ]
        
    def _build_initial_prompt(self, error_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build the initial prompt for autonomous analysis with pre-loaded reference data."""
        error_description = error_context.get('description', 'No description provided')
        
        system_prompt = f"""You are AZEBAL, an expert Azure debugging assistant. Your goal is to analyze the provided error and systematically investigate the root cause using available Azure APIs.

## Communication Context
You are communicating with an intelligent program interface (not a human) that serves as your execution environment. This program:
1. **Provides Information**: Supplies error patterns, solution references, and context data
2. **Executes Functions**: Runs Azure API calls and debugging tools when you request them
3. **Manages User Interaction**: Handles communication with the actual human developer using this system

## Input Handling Rules
Before starting analysis, determine the request type:

1. **Azure Error/Issue (PRIMARY SCOPE)**: Problems with Azure resources, services, configurations, permissions, connectivity
   → Proceed with full debugging analysis

2. **Azure Information Query**: Simple requests for Azure resource information, status checks, or general Azure questions
   → Provide direct answers using available functions without full debugging workflow

3. **Non-Azure Related**: Issues unrelated to Microsoft Azure (AWS, GCP, local development, non-cloud issues)
   → Politely decline: "This request appears to be outside my Azure specialization. I can only assist with Microsoft Azure related issues, errors, and resource management."

Your responses should be:
- **Concise during investigation**: Brief explanations when calling functions (1-2 sentences)
- **Comprehensive at conclusion**: Detailed final analysis with clear recommendations
- **Function-focused**: Request specific Azure data through function calls rather than asking for general information
- **Format compliant**: Either call a function OR provide text response, never both simultaneously

Response Format Rules:
1. If you need Azure data: Call the appropriate function with proper parameters
2. If you have sufficient information: Provide comprehensive text analysis
3. Always include brief reasoning for function calls (1-2 sentences)
4. Never request information that isn't available through the provided functions

Available Functions (Azure resource investigation only):
- get_azure_resource_status: Check status of any Azure resource
- query_azure_logs: Get logs from Azure Monitor
- check_resource_permissions: Verify access permissions
- get_resource_group_resources: List resources in a resource group
- get_subscriptions: Get available subscriptions

Analysis Approach (for errors/debugging):
1. First analyze the error using the provided error pattern reference data
2. Use get_subscriptions to understand the available Azure environment
3. Use get_azure_resource_status to check the health of key resources you identify
4. If logs might contain relevant information, use query_azure_logs
5. Check permissions if the error might be access-related
6. Use the provided common solution patterns as reference for your recommendations
7. Provide comprehensive analysis and actionable recommendations

Information Query Approach (for simple queries):
1. Identify what Azure information is being requested
2. Call appropriate functions to gather the requested data
3. Provide direct, informative response without full debugging analysis

Important Guidelines:
- Be systematic and logical in your investigation
- Always explain your reasoning for each function call
- Use the tools to gather live Azure data, then analyze using the reference patterns
- Keep intermediate responses brief and focused - save detailed analysis for the final response
- When calling functions, provide only concise explanations (1-2 sentences max)
- Your final response should be comprehensive, but intermediate responses should be concise
- When you have enough information, conclude with:
  * Clear analysis of what went wrong
  * Step-by-step debugging process
  * Specific, actionable recommendations
- Don't call functions unnecessarily - only when you need specific Azure resource data

Current Error Context:
Error Description: {error_description}
Session ID: {self.session.trace_id}"""

        # Get error patterns and common solutions for the specific error
        error_patterns = self._get_error_patterns_static(error_description)
        common_solutions = self._get_common_solutions_static_all()
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Please analyze this Azure error: {error_description}"},
            {"role": "assistant", "content": "Initiating systematic error analysis. Processing error context and preparing investigation plan."},
            {"role": "user", "content": f"Error pattern analysis data:\n\n{json.dumps(error_patterns, indent=2)}"},
            {"role": "assistant", "content": "Error patterns processed. Awaiting solution reference data."},
            {"role": "user", "content": f"Common solution patterns data:\n\n{json.dumps(common_solutions, indent=2)}"},
            {"role": "assistant", "content": "Reference data loaded. Beginning Azure environment investigation."}
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
    
    # Azure function implementations (unchanged)
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

    # Static helper methods for error patterns and solutions
    def _get_error_patterns_static(self, error_text: str) -> Dict[str, Any]:
        """Get error pattern reference data (static - no async needed)."""
        patterns = {
            "authentication": {
                "keywords": ["401", "unauthorized", "authentication failed", "login", "token", "credential"],
                "category": "authentication",
                "severity": "high",
                "common_causes": [
                    "Expired access token",
                    "Invalid credentials", 
                    "Missing authentication header",
                    "Service principal misconfiguration"
                ],
                "azure_services": ["Azure Active Directory", "Key Vault", "Storage"],
                "troubleshooting_steps": [
                    "Check token expiration",
                    "Verify service principal configuration",
                    "Check authentication headers"
                ]
            },
            "permission": {
                "keywords": ["403", "forbidden", "access denied", "permission", "rbac", "role"],
                "category": "permission",
                "severity": "high", 
                "common_causes": [
                    "Insufficient RBAC permissions",
                    "Resource-level access restrictions",
                    "Subscription-level permissions",
                    "Resource group permissions"
                ],
                "azure_services": ["Resource Manager", "Storage", "Compute"],
                "troubleshooting_steps": [
                    "Check RBAC role assignments",
                    "Verify resource-level permissions",
                    "Check inherited permissions"
                ]
            },
            "network": {
                "keywords": ["timeout", "connection", "network", "unreachable", "dns", "firewall"],
                "category": "network",
                "severity": "medium",
                "common_causes": [
                    "Network security group blocking access",
                    "Firewall rules",
                    "DNS resolution issues",
                    "Private endpoint configuration"
                ],
                "azure_services": ["Virtual Network", "DNS", "Firewall", "Load Balancer"],
                "troubleshooting_steps": [
                    "Check network security groups",
                    "Verify DNS resolution",
                    "Test network connectivity"
                ]
            },
            "storage": {
                "keywords": ["storage", "blob", "file", "disk", "quota", "space"],
                "category": "storage",
                "severity": "medium",
                "common_causes": [
                    "Storage quota exceeded",
                    "Storage account configuration",
                    "Access key issues",
                    "Container/share permissions"
                ],
                "azure_services": ["Storage Account", "Blob Storage", "File Storage"],
                "troubleshooting_steps": [
                    "Check storage quota",
                    "Verify access keys",
                    "Check container permissions"
                ]
            },
            "compute": {
                "keywords": ["vm", "virtual machine", "compute", "instance", "scale", "cpu", "memory"],
                "category": "compute", 
                "severity": "high",
                "common_causes": [
                    "VM resource constraints",
                    "Scale set configuration",
                    "Image or OS issues",
                    "Extension failures"
                ],
                "azure_services": ["Virtual Machines", "Scale Sets", "Container Instances"],
                "troubleshooting_steps": [
                    "Check VM resource utilization",
                    "Review VM extensions",
                    "Verify VM configuration"
                ]
            }
        }
        
        found_patterns = []
        error_lower = error_text.lower()
        
        for pattern_name, pattern_data in patterns.items():
            if any(keyword in error_lower for keyword in pattern_data["keywords"]):
                found_patterns.append({
                    "pattern_name": pattern_name,
                    **pattern_data
                })
        
        return {
            "success": True,
            "error_text": error_text,
            "matched_patterns": found_patterns,
            "primary_category": found_patterns[0]["category"] if found_patterns else "unknown",
            "total_patterns_found": len(found_patterns),
            "analysis": f"Found {len(found_patterns)} matching error patterns" + 
                      (f", primary category: {found_patterns[0]['category']}" if found_patterns else ", no specific patterns matched")
        }
    
    def _get_common_solutions_static_all(self) -> Dict[str, Any]:
        """Get all common solutions reference data (static - no async needed)."""
        solutions = {
            ("storage", "authentication"): {
                "immediate_actions": [
                    "Verify storage account access keys",
                    "Check SAS token validity and permissions",
                    "Confirm service principal has Storage Blob Data roles"
                ],
                "short_term_fixes": [
                    "Regenerate storage account keys if compromised",
                    "Update application configuration with correct keys",
                    "Configure managed identity for storage access"
                ],
                "long_term_improvements": [
                    "Implement Azure Key Vault for key management", 
                    "Use managed identity instead of access keys",
                    "Set up key rotation automation"
                ],
                "monitoring": [
                    "Enable storage analytics logging",
                    "Set up alerts for authentication failures"
                ]
            },
            ("storage", "permission"): {
                "immediate_actions": [
                    "Check RBAC role assignments on storage account",
                    "Verify container/blob-level permissions", 
                    "Confirm network access rules"
                ],
                "short_term_fixes": [
                    "Assign appropriate Storage Blob roles",
                    "Update storage account network rules",
                    "Configure proper SAS token permissions"
                ],
                "long_term_improvements": [
                    "Implement least-privilege access model",
                    "Use Azure Policy for storage security",
                    "Regular access reviews"
                ],
                "monitoring": [
                    "Enable audit logging for permission changes",
                    "Monitor unauthorized access attempts"
                ]
            },
            ("compute", "authentication"): {
                "immediate_actions": [
                    "Check VM service principal configuration",
                    "Verify managed identity assignment",
                    "Test Azure CLI/PowerShell authentication"
                ],
                "short_term_fixes": [
                    "Re-assign managed identity to VM",
                    "Update service principal credentials",
                    "Configure proper identity roles"
                ],
                "long_term_improvements": [
                    "Standardize managed identity usage",
                    "Implement identity governance",
                    "Automate identity assignment"
                ],
                "monitoring": [
                    "Enable VM identity activity logging",
                    "Monitor authentication failures"
                ]
            },
            ("network", "permission"): {
                "immediate_actions": [
                    "Check Network Security Group rules",
                    "Verify subnet route table configuration",
                    "Confirm firewall rules and policies"
                ],
                "short_term_fixes": [
                    "Update NSG rules to allow required traffic",
                    "Configure proper routing tables",
                    "Adjust firewall policies"
                ],
                "long_term_improvements": [
                    "Implement network segmentation strategy",
                    "Use Azure Policy for network governance",
                    "Standardize network security patterns"
                ],
                "monitoring": [
                    "Enable Network Watcher flow logs",
                    "Monitor network security rule changes"
                ]
            }
        }
        
        return {
            "success": True,
            "total_solution_patterns": len(solutions),
            "available_combinations": list(solutions.keys()),
            "solutions": {f"{combo[0]}-{combo[1]}": data for combo, data in solutions.items()},
            "usage_note": "Use the service_type and issue_type to find relevant solutions. Format: 'service_type-issue_type'"
        }