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

# Expose port for SSE transport
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python src/health_check.py --host localhost --port 8000

# Default command - run with SSE transport
CMD ["python", "run_mcp_server_sse.py"]
