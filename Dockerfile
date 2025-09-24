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
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy .env file if it exists (for environment variables)
COPY .env* ./

# Copy the entire project
COPY . .

# Ensure proper permissions
RUN chmod +x run_mcp_server.py run_mcp_server_sse.py

# Expose port for HTTP/SSE transport
EXPOSE 8000

# Health check removed - MCP server handles its own health monitoring

# Default command - run with SSE transport (using uvicorn)
CMD ["python", "run_mcp_server_sse.py"]
