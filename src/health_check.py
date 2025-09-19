"""
Health Check for AZEBAL MCP Server

Simple health check endpoint for Docker health monitoring.
"""

import sys
import requests
import argparse


def check_health(host: str = "localhost", port: int = 8000) -> bool:
    """
    Check if the AZEBAL MCP server is responding.
    
    Args:
        host: Server host
        port: Server port
        
    Returns:
        bool: True if server is healthy, False otherwise
    """
    try:
        # Try to connect to the AZEBAL MCP endpoint with proper MCP headers
        headers = {
            'Accept': 'application/json, text/event-stream',
            'Content-Type': 'application/json'
        }
        response = requests.get(f"http://{host}:{port}/azebal/mcp", 
                              headers=headers, timeout=5)
        
        # For MCP streamable-http, we expect either:
        # - 200 OK (if session is properly established)
        # - 400 Bad Request with "Missing session ID" (server is running but needs session)
        # - 406 Not Acceptable (wrong headers - server not running properly)
        
        if response.status_code == 200:
            return True
        elif response.status_code == 400:
            # Check if it's the expected "Missing session ID" error
            try:
                error_data = response.json()
                if "Missing session ID" in error_data.get("error", {}).get("message", ""):
                    return True  # Server is running, just needs proper session
            except:
                pass
        elif response.status_code == 406:
            # Wrong headers - server might not be running properly
            return False
            
        return False
    except Exception as e:
        print(f"Health check failed: {e}")
        return False


def main():
    """Main health check entry point."""
    parser = argparse.ArgumentParser(description="Health check for AZEBAL MCP server")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    
    args = parser.parse_args()
    
    if check_health(args.host, args.port):
        print("✅ AZEBAL MCP server is healthy")
        sys.exit(0)
    else:
        print("❌ AZEBAL MCP server is not responding")
        sys.exit(1)


if __name__ == "__main__":
    main()
