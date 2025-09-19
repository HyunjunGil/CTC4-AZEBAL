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
        # Try to connect to the AZEBAL MCP endpoint
        response = requests.get(f"http://{host}:{port}/azebal/mcp", timeout=5)
        return response.status_code == 200
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
