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
    from src.core.logging_config import setup_logging
    import uvicorn
    
    def main():
        """Main entry point for the SSE MCP server."""
        # Initialize logging first
        setup_logging(level="INFO")
        
        server = create_mcp_server()
        
        # Get host and port from environment variables or use defaults
        host = os.getenv("MCP_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_PORT", "8000"))
        
        print(f"🚀 Starting AZEBAL MCP server with SSE transport on {host}:{port}")
        
        # FastMCP 2.0.0 uses sse_app() method to get Starlette app
        # Then we run it with uvicorn
        try:
            app = server.sse_app()
            print(f"✅ SSE app created successfully")
            print(f"🌐 Server will be available at: http://{host}:{port}/sse/")
            print(f"📡 MCP endpoint: http://{host}:{port}/sse/")
            
            # Run the Starlette app with uvicorn
            uvicorn.run(
                app,
                host=host,
                port=port,
                log_level="info"
            )
        except Exception as e:
            print(f"⚠️  SSE transport failed: {e}")
            print("Falling back to stdio mode...")
            server.run()
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Error importing AZEBAL modules: {e}", file=sys.stderr)
    print(f"Project root: {project_root}", file=sys.stderr)
    print(f"Python path: {sys.path}", file=sys.stderr)
    sys.exit(1)
