#!/usr/bin/env python3
"""
AZEBAL MCP Server Entry Point

Standalone script to run the AZEBAL MCP server for Cursor integration.
This script handles the Python path setup automatically.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import and run the server
try:
    from src.server import create_mcp_server
    
    def main():
        """Main entry point for the MCP server."""
        # Create and run server with logging disabled for clean stdio communication
        server = create_mcp_server(disable_logs=True)
        server.run()
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Error importing AZEBAL modules: {e}", file=sys.stderr)
    print(f"Project root: {project_root}", file=sys.stderr)
    print(f"Python path: {sys.path}", file=sys.stderr)
    sys.exit(1)
