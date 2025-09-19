#!/usr/bin/env python3
"""
AZEBAL MCP Server SSE Entry Point

Standalone script to run the AZEBAL MCP server with SSE transport for Docker deployment.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run the server
try:
    from src.server import create_mcp_server
    import uvicorn
    
    def main():
        """Main entry point for the SSE MCP server."""
        server = create_mcp_server()
        
        # Get host and port from environment variables or use defaults
        host = os.getenv("MCP_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_PORT", "8000"))
        
        print(f"🚀 Starting AZEBAL MCP server with SSE transport on {host}:{port}")
        
        # FastMCP uses run() or run_async() for different transports
        # SSE is deprecated, but we'll use streamable-http instead which is preferred
        try:
            # Use streamable-http transport with custom path
            server.run(transport="streamable-http", host=host, port=port, path="/azebal/mcp")
        except Exception as e:
            print(f"⚠️  Streamable HTTP failed: {e}")
            print("Trying SSE transport (deprecated)...")
            try:
                server.run(transport="sse", host=host, port=port)
            except Exception as e2:
                print(f"⚠️  SSE also failed: {e2}")
                print("Falling back to stdio mode...")
                server.run()
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Error importing AZEBAL modules: {e}", file=sys.stderr)
    print(f"Project root: {project_root}", file=sys.stderr)
    print(f"Python path: {sys.path}", file=sys.stderr)
    sys.exit(1)
