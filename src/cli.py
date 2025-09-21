"""
AZEBAL CLI

Command-line interface for running the AZEBAL MCP server with different transport methods.
"""

import click
from src.server import create_mcp_server


@click.command()
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport method to use (stdio or sse)",
)
@click.option(
    "--host", default="localhost", help="Host address for SSE transport (ignored for stdio)"
)
@click.option(
    "--port", default=8000, type=int, help="Port number for SSE transport (ignored for stdio)"
)
def main(transport: str, host: str, port: int):
    """Run the AZEBAL MCP server with the specified transport method."""
    server = create_mcp_server()

    if transport == "stdio":
        click.echo("Starting AZEBAL MCP server with stdio transport...")
        server.run()
    elif transport == "sse":
        click.echo(f"Starting AZEBAL MCP server with SSE transport on {host}:{port}...")
        server.run_sse(host=host, port=port)


if __name__ == "__main__":
    main()
