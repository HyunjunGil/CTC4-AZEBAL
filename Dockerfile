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

# Install Python dependencies directly with pip
RUN pip install --no-cache-dir \
    fastmcp \
    uvicorn \
    click \
    structlog \
    pytest \
    pytest-asyncio \
    pytest-mock \
    pytest-cov \
    requests \
    PyJWT>=2.8.0 \
    pydantic>=2.5.0 \
    pydantic-settings>=2.1.0 \
    azure-identity>=1.15.0 \
    azure-mgmt-resource>=23.0.0 \
    azure-mgmt-compute>=30.0.0 \
    azure-mgmt-network>=25.0.0 \
    azure-mgmt-storage>=21.0.0 \
    azure-mgmt-containerregistry>=10.0.0 \
    azure-mgmt-containerinstance>=10.0.0 \
    azure-mgmt-web>=7.0.0 \
    openai>=1.0.0 \
    fastapi>=0.104.0 \
    httpx>=0.25.0 \
    cryptography>=41.0.0 \
    python-multipart \
    redis \
    python-dotenv>=1.0.0 \
    tenacity>=8.2.0

# Copy the entire project
COPY . .

# Ensure proper permissions
RUN chmod +x run_mcp_server.py run_mcp_server_sse.py

# Expose port for HTTP/SSE transport
EXPOSE 8000

# Health check removed - MCP server handles its own health monitoring

# Default command - run with SSE transport (using uvicorn)
CMD ["python", "run_mcp_server_sse.py"]
