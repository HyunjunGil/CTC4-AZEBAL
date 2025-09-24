"""
Debug Error Tool for AZEBAL

MCP tool for autonomous Azure error debugging and analysis.
"""

import uuid
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from src.core.auth import UserInfo
from src.core.jwt_service import JWTService
from src.core.config import settings
from src.core.logging_config import get_logger
from src.core.session_manager import session_manager, DebugSession
from src.core.safety_controller import safety_controller, GracefulDegradationHandler
from src.core.autonomous_agent import AutonomousDebugAgent
from src.services.azure_api_client import AzureAPIClient

logger = get_logger(__name__)


@dataclass
class SourceFile:
    """Source file information for debugging context."""
    path: str
    content: str
    relevance: str  # "primary", "secondary", "config"
    size_bytes: int


@dataclass
class EnvironmentInfo:
    """Environment information for debugging context."""
    azure_subscription: Optional[str] = None
    resource_group: Optional[str] = None
    technologies: Optional[List[str]] = None


@dataclass
class DebugContext:
    """Complete debugging context."""
    source_files: List[SourceFile]
    environment_info: EnvironmentInfo


class InputValidator:
    """Input validation for debug_error requests."""
    
    MAX_ERROR_DESCRIPTION_SIZE = 50 * 1024  # 50KB
    MAX_SOURCE_FILES_TOTAL_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_SOURCE_FILES_COUNT = 50
    
    @classmethod
    def validate_error_description(cls, error_description: str) -> tuple[bool, str]:
        """Validate error description."""
        if not error_description:
            return False, "Error description is required"
        
        if len(error_description.encode('utf-8')) > cls.MAX_ERROR_DESCRIPTION_SIZE:
            return False, f"Error description exceeds maximum size of {cls.MAX_ERROR_DESCRIPTION_SIZE} bytes"
        
        return True, ""
    
    @classmethod
    def validate_source_files(cls, source_files: List[Dict[str, Any]]) -> tuple[bool, str]:
        """Validate source files."""
        if not source_files:
            return True, ""  # Source files are optional
        
        if len(source_files) > cls.MAX_SOURCE_FILES_COUNT:
            return False, f"Too many source files. Maximum {cls.MAX_SOURCE_FILES_COUNT} allowed"
        
        total_size = 0
        for i, file_data in enumerate(source_files):
            # Validate required fields
            if not isinstance(file_data, dict):
                return False, f"Source file {i} must be an object"
            
            path = file_data.get('path')
            content = file_data.get('content')
            
            if not path:
                return False, f"Source file {i} missing 'path' field"
            
            if not isinstance(content, str):
                return False, f"Source file {i} 'content' must be a string"
            
            # Check file size
            file_size = len(content.encode('utf-8'))
            total_size += file_size
            
            if total_size > cls.MAX_SOURCE_FILES_TOTAL_SIZE:
                return False, f"Total source files size exceeds {cls.MAX_SOURCE_FILES_TOTAL_SIZE} bytes"
        
        return True, ""
    
    @classmethod
    def validate_azebal_token(cls, azebal_token: str) -> tuple[bool, str]:
        """Validate AZEBAL token."""
        if not azebal_token:
            return False, "AZEBAL token is required"
        
        if not azebal_token.strip():
            return False, "AZEBAL token cannot be empty"
        
        return True, ""


class SensitiveDataFilter:
    """Filter sensitive information from data."""
    
    SENSITIVE_PATTERNS = [
        'password', 'secret', 'key', 'token', 'connectionstring',
        'apikey', 'accesskey', 'secretkey', 'clientsecret', 'credential'
    ]
    
    @classmethod
    def filter_sensitive_data(cls, data: Any) -> Any:
        """Recursively filter sensitive data from any data structure."""
        if isinstance(data, dict):
            filtered = {}
            for key, value in data.items():
                if any(pattern in key.lower() for pattern in cls.SENSITIVE_PATTERNS):
                    filtered[key] = "***MASKED***"
                else:
                    filtered[key] = cls.filter_sensitive_data(value)
            return filtered
        elif isinstance(data, list):
            return [cls.filter_sensitive_data(item) for item in data]
        elif isinstance(data, str):
            # Check if the string looks like a token or credential
            if len(data) > 50 and any(pattern in data.lower() for pattern in cls.SENSITIVE_PATTERNS):
                return "***MASKED***"
            return data
        else:
            return data


async def debug_error_tool(
    azebal_token: str,
    error_description: str,
    context: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Autonomous Azure error debugging and analysis tool.
    
    This function receives error information, autonomously performs debugging analysis
    using Azure APIs and AI reasoning, and returns comprehensive debugging results.
    
    Args:
        azebal_token (str): AZEBAL JWT token for user authentication
        error_description (str): Description of the error to debug (max 50KB)
        context (dict, optional): Additional context including:
            - source_files: List of source files with path, content, relevance, size_bytes
            - environment_info: Environment details like azure_subscription, resource_group, technologies
        session_id (str, optional): Existing session ID to continue analysis. If provided, 
            continues existing session instead of creating a new one.
    
    Returns:
        Dict[str, Any]: Debugging result containing:
            - status (str): "done", "request", "continue", or "fail"
            - trace_id (str): Unique identifier for this debugging session
            - message (str): Human-readable analysis results and recommendations
            - progress (int, optional): Progress percentage (0-100)
            - analysis_results (dict, optional): Structured analysis findings
            - debugging_process (list, optional): Step-by-step debugging process
            - actions_to_take (list, optional): Actionable recommendations
    
    Example:
        >>> result = debug_error_tool(
        ...     azebal_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIs...",
        ...     error_description="Azure App Service deployment failed with 500 error",
        ...     context={
        ...         "source_files": [
        ...             {
        ...                 "path": "main.py",
        ...                 "content": "import os\\nfrom flask import Flask...",
        ...                 "relevance": "primary",
        ...                 "size_bytes": 1024
        ...             }
        ...         ],
        ...         "environment_info": {
        ...             "azure_subscription": "my-subscription",
        ...             "resource_group": "my-rg",
        ...             "technologies": ["python", "flask", "app-service"]
        ...         }
        ...     }
        ... )
        >>> print(f"Status: {result['status']}, Message: {result['message']}")
    """
    # Handle session ID for new or continuing sessions
    if session_id:
        trace_id = session_id
        logger.info(f"Continuing debug_error analysis - session_id: {trace_id}")
    else:
        trace_id = str(uuid.uuid4())
        logger.info(f"Starting new debug_error analysis - trace_id: {trace_id}")
    
    start_time = time.time()
    
    try:
        # Step 1: Input Validation
        logger.info(f"[{trace_id}] Validating input parameters")
        
        # Validate AZEBAL token
        is_valid, error_msg = InputValidator.validate_azebal_token(azebal_token)
        if not is_valid:
            logger.warning(f"[{trace_id}] Token validation failed: {error_msg}")
            return {
                "status": "fail",
                "trace_id": trace_id,
                "message": f"Authentication failed: {error_msg}",
                "error": "INVALID_TOKEN"
            }
        
        # Validate error description
        is_valid, error_msg = InputValidator.validate_error_description(error_description)
        if not is_valid:
            logger.warning(f"[{trace_id}] Error description validation failed: {error_msg}")
            return {
                "status": "fail",
                "trace_id": trace_id,
                "message": f"Invalid input: {error_msg}",
                "error": "INVALID_INPUT"
            }
        
        # Validate context if provided
        if context:
            source_files = context.get('source_files', [])
            is_valid, error_msg = InputValidator.validate_source_files(source_files)
            if not is_valid:
                logger.warning(f"[{trace_id}] Source files validation failed: {error_msg}")
                return {
                    "status": "fail",
                    "trace_id": trace_id,
                    "message": f"Invalid source files: {error_msg}",
                    "error": "INVALID_SOURCE_FILES"
                }
        
        # Step 2: Authenticate user and extract Azure token
        logger.info(f"[{trace_id}] Authenticating user with AZEBAL token")
        jwt_service = JWTService()
        
        try:
            payload = jwt_service.verify_token(azebal_token)
            user_principal_name = payload.get('user_principal_name', 'unknown')
            
            # Get Azure access token from secure storage
            azure_access_token = jwt_service.get_azure_access_token(azebal_token)
            
            if not azure_access_token:
                logger.error(f"[{trace_id}] No Azure access token found for user: {user_principal_name}")
                return {
                    "status": "fail",
                    "trace_id": trace_id,
                    "message": "Azure access token not found or expired. Please login again.",
                    "error": "MISSING_AZURE_TOKEN"
                }
            
            logger.info(f"[{trace_id}] Authentication successful for user: {user_principal_name}")
        except Exception as e:
            logger.error(f"[{trace_id}] AZEBAL token validation failed: {str(e)}")
            return {
                "status": "fail",
                "trace_id": trace_id,
                "message": "Invalid AZEBAL token. Please login again.",
                "error": "TOKEN_EXPIRED"
            }
        
        # Step 3: Filter sensitive information
        logger.info(f"[{trace_id}] Filtering sensitive information from context")
        filtered_context = SensitiveDataFilter.filter_sensitive_data(context) if context else {}
        
        # Step 4: Create or get debugging session
        if session_id:
            logger.info(f"[{trace_id}] Retrieving existing debugging session")
            session = session_manager.get_session(trace_id)
            if not session:
                logger.error(f"[{trace_id}] Session not found for provided session_id")
                return {
                    "status": "fail",
                    "trace_id": trace_id,
                    "message": "Session not found. Please start a new debugging session.",
                    "error": "SESSION_NOT_FOUND"
                }
        else:
            logger.info(f"[{trace_id}] Creating new debugging session")
            session = session_manager.create_session(
                user_principal_name=user_principal_name,
                error_description=error_description,
                context=filtered_context,
                trace_id=trace_id
            )
        
        # Step 5: Extract subscription ID from context
        subscription_id = None
        if filtered_context and 'environment_info' in filtered_context:
            subscription_id = filtered_context['environment_info'].get('azure_subscription')
        
        if not subscription_id:
            logger.warning(f"[{trace_id}] No subscription ID provided in context")
        
        # Step 6: Log analysis plan
        analysis_plan = _create_analysis_plan(error_description, filtered_context)
        logger.info(f"[{trace_id}] Analysis plan created: {analysis_plan}")
        session.add_log(f"Analysis plan created with {len(analysis_plan.get('analysis_steps', []))} steps")
        
        # Step 7: Initialize Azure API Client
        logger.info(f"[{trace_id}] Initializing Azure API client with subscription: {subscription_id or 'None'}")
        azure_client = AzureAPIClient(azure_access_token, subscription_id)
        session.add_log("Azure API client initialized")
        
        # Step 8: Initialize safety controls
        logger.info(f"[{trace_id}] Initializing safety controls")
        safety_controller.start_analysis(session)
        
        # Step 9: Initialize autonomous analysis engine
        logger.info(f"[{trace_id}] Initializing autonomous analysis engine...")
        session.add_log("Initializing autonomous analysis engine")
        
        try:
            # Create autonomous debug agent
            debug_agent = AutonomousDebugAgent(
                azure_client=azure_client,
                session=session
            )
            
            # Start autonomous analysis
            logger.info(f"[{trace_id}] Starting autonomous error analysis")
            analysis_result = await debug_agent.analyze_error({
                "description": error_description,
                "context": filtered_context
            })
            
            # Convert analysis result to response format
            result = {
                "status": analysis_result.status.value,
                "trace_id": analysis_result.trace_id,
                "message": analysis_result.message,
                "progress": analysis_result.progress,
                "analysis_results": analysis_result.analysis_results,
                "debugging_process": analysis_result.debugging_process,
                "actions_to_take": analysis_result.actions_to_take
            }
            
        except Exception as e:
            logger.error(f"[{trace_id}] Autonomous analysis failed: {str(e)}")
            session.add_log(f"Autonomous analysis failed: {str(e)}", "error")
            
            # Fallback to placeholder analysis
            result = _placeholder_analysis(session, analysis_plan, azure_client)
        
        # Step 6: Log completion
        execution_time = time.time() - start_time
        logger.info(f"[{trace_id}] Analysis completed in {execution_time:.2f} seconds")
        
        return result
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"[{trace_id}] Unexpected error during analysis: {str(e)}")
        return {
            "status": "fail",
            "trace_id": trace_id,
            "message": "An unexpected error occurred during analysis. Please try again.",
            "error": "INTERNAL_ERROR",
            "execution_time": execution_time
        }


def _create_analysis_plan(error_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Create an analysis plan based on error description and context."""
    plan = {
        "identified_technologies": [],
        "potential_azure_resources": [],
        "analysis_steps": []
    }
    
    # Analyze error description for keywords
    error_lower = error_description.lower()
    
    # Identify technologies
    tech_keywords = {
        'app service': 'Azure App Service',
        'storage': 'Azure Storage',
        'database': 'Azure Database',
        'sql': 'Azure SQL',
        'cosmos': 'Azure Cosmos DB',
        'container': 'Azure Container Instances',
        'kubernetes': 'Azure Kubernetes Service',
        'function': 'Azure Functions',
        'vm': 'Virtual Machine',
        'network': 'Azure Network',
        'load balancer': 'Azure Load Balancer'
    }
    
    for keyword, technology in tech_keywords.items():
        if keyword in error_lower:
            plan["identified_technologies"].append(technology)
    
    # Add context technologies
    if context and 'environment_info' in context:
        env_info = context['environment_info']
        if env_info.get('technologies'):
            plan["identified_technologies"].extend(env_info['technologies'])
    
    # Create analysis steps based on identified technologies
    if plan["identified_technologies"]:
        plan["analysis_steps"] = [
            "Check resource status and health",
            "Query relevant logs and metrics",
            "Analyze configuration settings",
            "Check network connectivity if applicable",
            "Verify permissions and access rights"
        ]
    else:
        plan["analysis_steps"] = [
            "Perform general Azure resource analysis",
            "Check common configuration issues",
            "Review logs for error patterns"
        ]
    
    return plan


def _placeholder_analysis(
    session: DebugSession,
    analysis_plan: Dict[str, Any],
    azure_client: AzureAPIClient
) -> Dict[str, Any]:
    """
    Placeholder analysis function.
    
    This will be replaced with the actual autonomous AI agent implementation.
    """
    logger.info(f"[{session.trace_id}] Running placeholder analysis")
    session.add_log("Running placeholder analysis")
    
    # Update session with identified resources and findings
    identified_technologies = analysis_plan.get("identified_technologies", [])
    for tech in identified_technologies:
        session.identified_resources.append(tech)
    
    session.add_finding("Preliminary error analysis completed", "info", "analysis")
    session.add_finding(f"Identified {len(identified_technologies)} potential Azure services", "info", "discovery")
    
    # Simulate some analysis steps
    for step in analysis_plan.get("analysis_steps", []):
        session.add_log(f"Plan step: {step}")
    
    # Update progress
    session.update_progress(25)
    
    # Create debugging process summary
    debugging_process = [
        "Analyzed error description and identified potential Azure services",
        "Created analysis plan based on error patterns",
        f"Session created with trace_id: {session.trace_id}",
        "Ready to execute autonomous debugging with Azure APIs"
    ]
    
    # Create preliminary analysis results
    analysis_results = {
        "error_category": "Azure Service Error",
        "confidence_level": "medium",
        "identified_services": identified_technologies,
        "next_investigation_steps": analysis_plan.get("analysis_steps", []),
        "session_info": session.get_context_for_llm()
    }
    
    actions_to_take = [
        "Complete autonomous AI agent implementation",
        "Add Azure API client for resource analysis", 
        "Implement session management for complex debugging scenarios"
    ]
    
    # Update session next steps
    session.next_steps = actions_to_take
    
    # Get safety status
    safety_status = safety_controller.get_safety_status(session)
    
    # Check if we should continue or stop
    if safety_controller.should_stop(session):
        session.add_log("Analysis stopped due to safety limits", "warning")
        return {
            "status": "fail",
            "trace_id": session.trace_id,
            "message": "Analysis stopped due to safety limits. Please try with a simpler error description.",
            "safety_status": safety_status
        }
    
    message = f"""
Debugging Analysis for Error: {session.error_description[:100]}...

ANALYSIS RESULTS:
- Error Type: Preliminary analysis indicates Azure service-related issue
- Identified Technologies: {', '.join(identified_technologies) if identified_technologies else 'Unknown'}
- Confidence Level: Medium (preliminary analysis)
- Session ID: {session.trace_id}

DEBUGGING PROCESS:
1. Input validation and authentication completed successfully
2. Error analysis plan created based on description patterns
3. Context analysis completed with {len(session.context.get('source_files', []))} source files
4. Debugging session established with memory tracking
5. Safety controls initialized and monitoring
6. Ready for autonomous Azure API analysis

SESSION STATUS:
- Status: {session.status}
- Progress: {session.progress}%
- Function Calls: {session.function_call_count}
- Findings: {len(session.findings)}
- Safety Status: {safety_status['safety_status']}
- Elapsed Time: {safety_status['elapsed_time']:.2f}s / {safety_status['time_limit']}s

SAFETY CONTROLS:
- Function Calls: {safety_status['function_calls']} / {safety_status['function_limit']}
- Analysis Depth: {safety_status['depth']} / {safety_status['depth_limit']}
- Memory Usage: {safety_status['memory_estimate_mb']:.2f}MB / {safety_status['memory_limit_mb']}MB
- API Calls (last minute): {safety_status['api_calls_last_minute']} / {safety_status['api_limit_per_minute']}

ACTIONS TO TAKE:
1. Complete the autonomous AI agent implementation
2. Execute detailed Azure resource analysis
3. Perform log analysis and configuration checking
4. Provide specific remediation steps

NOTE: This is a preliminary analysis. Full autonomous debugging will be available once the AI agent implementation is complete.
    """.strip()
    
    return {
        "status": "continue",
        "trace_id": session.trace_id,
        "message": message,
        "progress": session.progress,
        "analysis_results": analysis_results,
        "debugging_process": debugging_process,
        "actions_to_take": actions_to_take
    }
