#!/bin/bash
# AZEBAL Docker Deployment Script

set -e

echo "🚀 Deploying AZEBAL MCP Server with Docker..."

# Navigate to project root
cd "$(dirname "$0")/.."

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t azebal-mcp:latest .

# Stop and remove existing container if it exists
echo "🛑 Stopping existing container..."
docker stop azebal-mcp-server 2>/dev/null || true
docker rm azebal-mcp-server 2>/dev/null || true

# Run the container
echo "🏃 Starting new container..."
docker run -d \
  --name azebal-mcp-server \
  -p 8000:8000 \
  -e MCP_HOST=0.0.0.0 \
  -e MCP_PORT=8000 \
  --restart unless-stopped \
  azebal-mcp:latest

# Wait for container to be healthy
echo "⏳ Waiting for container to be healthy..."
timeout=60
counter=0

while [ $counter -lt $timeout ]; do
  if docker exec azebal-mcp-server python src/health_check.py --host localhost --port 8000 2>/dev/null; then
    echo "✅ AZEBAL MCP Server is running and healthy!"
    echo "🌐 MCP Server available at: http://localhost:8000/azebal/mcp"
    echo "📊 Container status:"
    docker ps --filter name=azebal-mcp-server
    exit 0
  fi
  sleep 2
  counter=$((counter + 2))
  echo "⏳ Still waiting... ($counter/$timeout seconds)"
done

echo "❌ Container failed to become healthy within $timeout seconds"
echo "📊 Container logs:"
docker logs azebal-mcp-server
exit 1
