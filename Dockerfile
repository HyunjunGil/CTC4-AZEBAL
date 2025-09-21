# AZEBAL MCP Server Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY environment.yml .

# Extract pip dependencies from environment.yml and install them
RUN pip install \
    fastmcp \
    uvicorn \
    click \
    structlog \
    pytest \
    pytest-asyncio \
    pytest-mock \
    pytest-cov \
    requests

# Copy the entire project
COPY . .

# Ensure proper permissions
RUN chmod +x run_mcp_server.py run_mcp_server_sse.py

# Expose port for HTTP/SSE transport
EXPOSE 8000

# Health check removed - MCP server handles its own health monitoring

# Default command - run with SSE transport (using uvicorn)
CMD ["python", "run_mcp_server_sse.py"]
