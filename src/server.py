"""
AZEBAL MCP Server

Basic MCP server implementation using FastMCP library.
Supports both stdio and SSE transport methods.
"""

from fastmcp import FastMCP
from src.tools.greeting import greeting_tool
from src.tools.login import login_tool
from src.tools.ask_llm import ask_llm_handler
from src.tools.debug_error import debug_error_tool
from src.core.logging_config import setup_logging, disable_logging


def create_mcp_server(disable_logs: bool = False) -> FastMCP:
    """
    Creates and configures the AZEBAL MCP server.

    Args:
        disable_logs: If True, disable logging to prevent stdio interference
        
    Returns:
        FastMCP: Configured MCP server instance
    """
    # Initialize or disable logging based on mode
    if disable_logs:
        disable_logging()
    else:
        setup_logging(level="INFO", use_stderr=True)
    
    # Create FastMCP server instance
    mcp = FastMCP("AZEBAL")

    # Register the greeting tool
    @mcp.tool()
    def greeting() -> str:
        """A simple greeting tool that returns 'hello'"""
        result = greeting_tool()
        return result["message"]

    # Register the login tool
    @mcp.tool()
    def login(azure_access_token: str) -> dict:
        """
        Authenticate with AZEBAL using Azure CLI access token.
        
        This tool allows users to log into AZEBAL using their existing Azure CLI authentication,
        eliminating the need for separate browser-based login flows.

        PREREQUISITES FOR USERS:
        1. Install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
        2. Login to Azure: Run 'az login' in terminal
        3. Set subscription: Run 'az account set --subscription "Your-Subscription-Name"'
        4. Get access token: Run 'az account get-access-token --query accessToken --output tsv'
        5. Copy the token and pass it to this tool

        COMMON AZURE CLI COMMANDS:
        - Check login status: 'az account show'
        - List subscriptions: 'az account list --output table'
        - Get current subscription: 'az account show --query name --output tsv'
        - Get access token: 'az account get-access-token --query accessToken --output tsv'
        - Login to Azure: 'az login'
        - Set subscription: 'az account set --subscription "Subscription-Name"'

        TROUBLESHOOTING:
        - If "az: command not found": Install Azure CLI first
        - If "Please run 'az login'": User needs to authenticate with Azure first
        - If "No subscriptions found": User may not have access to any Azure subscriptions
        - If token is invalid: Token may be expired, get a fresh one with 'az account get-access-token'

        Args:
            azure_access_token (str): Azure CLI access token obtained from 'az account get-access-token --query accessToken --output tsv'
                                     This token is used to authenticate with Azure Management API and extract user information.

        Returns:
            dict: Authentication result containing:
                - success (bool): Whether authentication was successful
                - message (str): Human-readable status message
                - azebal_token (str, optional): AZEBAL JWT token for session management (if successful)
                - user_info (dict, optional): User information including:
                    - object_id (str): Azure AD Object ID
                    - user_principal_name (str): User Principal Name (email)
                    - tenant_id (str): Azure AD Tenant ID
                    - display_name (str, optional): Display name
                    - email (str, optional): Email address
                - error (str, optional): Error code if authentication failed

        Example Usage:
            # Step 1: User runs in terminal
            az account get-access-token --query accessToken --output tsv
            
            # Step 2: User copies the token and calls this tool
            login("eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIs...")
            
            # Step 3: Tool returns authentication result
            {
                "success": true,
                "message": "Login successful",
                "azebal_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "user_info": {
                    "object_id": "12345678-1234-1234-1234-123456789abc",
                    "user_principal_name": "user@company.com",
                    "tenant_id": "87654321-4321-4321-4321-cba987654321",
                    "display_name": "John Doe",
                    "email": "user@company.com"
                }
            }
        """
        return login_tool(azure_access_token)

    # Register the ask_llm tool
    @mcp.tool()
    async def ask_llm(question: str) -> str:
        """
        Ask any question to the LLM and get a response.
        
        This tool provides a simple interface to ask questions to Azure OpenAI.
        No authentication is required for this tool.
        
        Args:
            question (str): The question to ask the LLM (e.g., 'What is 3 + 3?', 'Who is Albert Einstein?')
            
        Returns:
            str: The LLM's response as plain text
            
        Examples:
            ask_llm("What is 3 + 3?")
            ask_llm("Who is Albert Einstein?")
            ask_llm("Explain the concept of machine learning")
        """
        return await ask_llm_handler({"question": question})

    # Register the debug_error tool
    @mcp.tool()
    async def debug_error(
        azebal_token: str,
        error_description: str,
        context: dict = None
    ) -> dict:
        """
        Autonomous Azure error debugging and analysis tool.
        
        This tool receives error information, autonomously performs debugging analysis
        using Azure APIs and AI reasoning, and returns comprehensive debugging results.
        
        Args:
            azebal_token (str): AZEBAL JWT token for user authentication (required)
            error_description (str): Description of the error to debug (max 50KB)
            context (dict, optional): Additional context including:
                - source_files: List of source files with path, content, relevance, size_bytes
                - environment_info: Environment details like azure_subscription, resource_group, technologies
        
        Returns:
            dict: Debugging result containing:
                - status (str): "done", "request", "continue", or "fail"
                - trace_id (str): Unique identifier for this debugging session
                - message (str): Human-readable analysis results and recommendations
                - progress (int, optional): Progress percentage (0-100)
                - analysis_results (dict, optional): Structured analysis findings
                - debugging_process (list, optional): Step-by-step debugging process
                - actions_to_take (list, optional): Actionable recommendations
        
        Example Usage:
            debug_error(
                azebal_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIs...",
                error_description="Azure App Service deployment failed with 500 error",
                context={
                    "source_files": [
                        {
                            "path": "main.py",
                            "content": "import os\\nfrom flask import Flask...",
                            "relevance": "primary",
                            "size_bytes": 1024
                        }
                    ],
                    "environment_info": {
                        "azure_subscription": "my-subscription",
                        "resource_group": "my-rg",
                        "technologies": ["python", "flask", "app-service"]
                    }
                }
            )
        """
        return await debug_error_tool(azebal_token, error_description, context)

    return mcp


def main():
    """Main entry point for the MCP server."""
    server = create_mcp_server()
    server.run()


if __name__ == "__main__":
    main()
