# AZEBAL - Azure Error Analysis & BreALdown

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![FastMCP](https://img.shields.io/badge/framework-FastMCP-green.svg)](https://github.com/modelcontextprotocol/python-sdk)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**AZEBAL** is an intelligent MCP (Model Context Protocol) server that provides real-time Azure error debugging and analysis directly within your IDE. It integrates with AI agents to analyze Azure-related errors comprehensively by examining user permissions, source code, and real-time Azure resource status.

## 🎯 **Overview**

AZEBAL transforms fragmented Azure debugging approaches into a systematic, AI-powered solution that:

- **Authenticates** users via Microsoft OAuth 2.0 using their company accounts
- **Analyzes** Azure errors by combining source code context with real-time resource status
- **Provides** actionable debugging insights and solutions directly in your IDE
- **Reduces** development time spent on Azure-related troubleshooting

## 🏗️ **Architecture**

This project follows a **monolithic architecture** for rapid MVP development:

- **FastMCP Server**: Single entry point for IDE AI agent communication
- **Authentication Module**: OAuth 2.0 integration with Microsoft ID Platform  
- **LLM Engine**: Core error analysis using Azure OpenAI
- **Azure API Client**: Real-time Azure resource queries
- **Session Management**: Redis-based user session storage

## 📁 **Project Structure**

```
azebal/
├── .vscode/                # VSCode configuration
├── docs/                   # Project documentation
│   ├── architecture/       # Detailed architecture docs
│   ├── prd/               # Product Requirements Document
│   └── stories/           # User stories
├── scripts/               # Build and deployment scripts
├── src/                   # Source code
│   ├── __init__.py
│   ├── main.py           # MCP server entry point
│   ├── tools/            # MCP tool definitions (login, debug_error)
│   │   ├── definitions.py
│   │   └── schemas.py
│   ├── core/             # Core business logic
│   │   ├── auth.py       # Authentication management
│   │   ├── engine.py     # LLM analysis engine
│   │   └── config.py     # Configuration management
│   ├── services/         # External service integrations
│   │   └── azure_client.py
│   └── utils/            # Utility functions
├── tests/                # Test suite
│   ├── unit/             # Unit tests (>80% coverage target)
│   ├── integration/      # Integration tests
│   ├── e2e/              # End-to-end tests
│   └── fixtures/         # Test data and fixtures
├── environment.yml       # Conda environment specification
├── environment.template  # Environment variables template
├── pytest.ini           # Pytest configuration
└── README.md
```

## 🚀 **Quick Start**

### Prerequisites

- **Python 3.11+**
- **Conda** (recommended for environment management)
- **Microsoft Azure Account** with appropriate permissions
- **Redis Server** (for local development)
- **MariaDB** (for local development testing)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AZEBAL
   ```

2. **Create conda environment**
   ```bash
   conda env create -f environment.yml
   conda activate azebal
   ```

3. **Configure environment**
   ```bash
   cp environment.template .env
   # Edit .env with your actual Azure and Microsoft credentials
   ```

4. **Set up local services**
   ```bash
   # Start Redis (using Docker)
   docker run -d --name azebal-redis -p 6379:6379 redis:7-alpine
   
   # Start MariaDB (using Docker)
   docker run -d --name azebal-mariadb \
     -p 3306:3306 \
     -e MYSQL_ROOT_PASSWORD=password \
     -e MYSQL_DATABASE=azebal_dev \
     -e MYSQL_USER=azebal \
     -e MYSQL_PASSWORD=password \
     mariadb:10
   ```

5. **Run the MCP server**
   ```bash
   # Run with stdio transport (default)
   python run_mcp_server.py
   
   # Or run with SSE/Streamable-HTTP transport
   python run_mcp_server_sse.py
   ```

### Development Setup

1. **Install development dependencies**
   ```bash
   conda activate azebal
   pip install -e .
   ```

2. **Run tests**
   ```bash
   # Run all tests
   pytest
   
   # Run with coverage
   pytest --cov=src --cov-report=html
   
   # Run specific test categories
   pytest -m unit      # Unit tests only
   pytest -m integration  # Integration tests only
   ```

3. **Code formatting and linting**
   ```bash
   # Format code
   black src/ tests/
   
   # Check linting
   flake8 src/ tests/
   
   # Type checking
   mypy src/
   ```

## 🔧 **Configuration**

### Environment Variables

Key configuration variables (see `environment.template` for complete list):

```bash
# Microsoft Authentication
MS_CLIENT_ID=your_microsoft_app_client_id
MS_CLIENT_SECRET=your_microsoft_app_client_secret
MS_TENANT_ID=your_microsoft_tenant_id

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_openai_api_key

# Database
REDIS_HOST=localhost
DB_HOST=localhost
DB_NAME=azebal_dev
```

### Microsoft App Registration

1. Register a new application in Azure AD
2. Configure redirect URI: `http://localhost:8000/auth/callback`
3. Grant necessary API permissions for Azure Resource Manager
4. Generate client secret and note the application ID

## 🎮 **Usage**

AZEBAL supports two distinct transport methods for different use cases. Choose the method that best fits your needs:

## 📡 **Transport Methods**

### 1. **stdio Transport** (Recommended for IDE Integration)

**Best for**: Cursor IDE, VSCode, and other IDE integrations
**Communication**: Direct process communication
**Setup**: Simple command-based configuration

### 2. **HTTP Transport** (Recommended for Web/Production)

**Best for**: Web applications, Docker deployments, production environments
**Communication**: HTTP with streamable transport
**Setup**: URL-based configuration

---

## 🔌 **stdio Transport Setup**

### **Step 1: Start the stdio Server**

```bash
# Activate conda environment
conda activate azebal

# Navigate to AZEBAL directory
cd /path/to/your/AZEBAL

# Start stdio server
python run_mcp_server.py
```

### **Step 2: Configure Cursor IDE**

1. **Open Cursor MCP configuration file**:
   - **macOS/Linux**: `~/.cursor/mcp.json`
   - **Windows**: `%APPDATA%\Cursor\mcp.json`

2. **Add stdio configuration**:
   ```json
   {
     "mcpServers": {
       "azebal": {
         "command": "python",
         "args": ["/path/to/your/AZEBAL/run_mcp_server.py"],
         "cwd": "/path/to/your/AZEBAL"
       }
     }
   }
   ```

   **Important**: Replace `/path/to/your/AZEBAL` with your actual absolute path

### **Step 3: Test stdio Connection**

1. **Restart Cursor IDE**
2. **Open any file in Cursor**
3. **Start a chat with the AI assistant**
4. **Test the connection**:
   ```
   Can you use the greeting tool from AZEBAL?
   ```

**Expected Result**: The AI should return "hello" from the greeting function

### **Step 4: Verify stdio Setup**

```bash
# Test server creation manually
python -c "from src.server import create_mcp_server; server = create_mcp_server(); print('✅ stdio Server OK')"

# Check if server runs without errors
python run_mcp_server.py
# (Should start and wait for input, press Ctrl+C to stop)
```

---

## 🌐 **HTTP Transport Setup**

### **Step 1: Start the HTTP Server**

```bash
# Activate conda environment
conda activate azebal

# Navigate to AZEBAL directory
cd /path/to/your/AZEBAL

# Start HTTP server
python run_mcp_server_sse.py
```

**Server will start on**: `http://localhost:8000/sse/`

### **Step 2: Configure Cursor IDE (HTTP Mode)**

1. **Open Cursor MCP configuration file**:
   - **macOS/Linux**: `~/.cursor/mcp.json`
   - **Windows**: `%APPDATA%\Cursor\mcp.json`

2. **Add HTTP configuration**:
   ```json
   {
     "mcpServers": {
       "azebal": {
         "type": "http",
         "url": "http://localhost:8000/sse/",
         "headers": {}
       }
     }
   }
   ```

### **Step 3: Test HTTP Connection**

1. **Restart Cursor IDE**
2. **Open any file in Cursor**
3. **Start a chat with the AI assistant**
4. **Test the connection**:
   ```
   Can you use the greeting tool from AZEBAL?
   ```

**Expected Result**: The AI should return "hello" from the greeting function

### **Step 4: Verify HTTP Setup**

```bash
# Test MCP endpoint directly
curl -X POST http://localhost:8000/sse/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}'

# Test greeting tool
curl -X POST http://localhost:8000/sse/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "greeting", "arguments": {}}}'
```

**Expected Results**:
- Initialize call should return server capabilities
- Greeting tool call should return "hello"

---

## 🐳 **Docker Deployment (HTTP Transport Only)**

### **Quick Start with Docker**

```bash
# Build Docker image
docker build -t azebal-mcp:latest .

# Run container with HTTP transport
docker run -d --name azebal-mcp-server \
  -p 8000:8000 \
  -e MCP_HOST=0.0.0.0 \
  -e MCP_PORT=8000 \
  --restart unless-stopped \
  azebal-mcp:latest

# Verify container is running
docker ps --filter name=azebal-mcp-server

# Check logs
docker logs azebal-mcp-server
```

### **Using Docker Compose (Recommended)**

```bash
# Start with docker-compose
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f azebal-mcp

# Stop services
docker-compose down
```

### **Test Docker Deployment**

```bash
# Test MCP endpoint
curl -X POST http://localhost:8000/sse/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}'

# Test greeting tool
curl -X POST http://localhost:8000/sse/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "greeting", "arguments": {}}}'
```

---

## 🛠️ **Available Tools**

### **Current Tools**
- **`greeting`**: A test tool that returns "hello" (for testing connectivity)

### **Planned Tools**
- **`login`**: Authenticate user and establish Azure session
- **`debug_error`**: Comprehensive Azure error analysis and debugging

---

## 🔧 **Troubleshooting**

### **stdio Transport Issues**

1. **Verify Python Environment**:
   ```bash
   conda activate azebal
   cd /path/to/AZEBAL
   python run_mcp_server.py
   ```

2. **Check File Paths**:
   - Ensure absolute paths in `mcp.json`
   - Use forward slashes on Windows
   - Verify `cwd` points to correct directory

3. **Test Server Creation**:
   ```bash
   python -c "from src.server import create_mcp_server; server = create_mcp_server(); print('✅ Server OK')"
   ```

### **HTTP Transport Issues**

1. **Verify Server is Running**:
   ```bash
   # Check if port 8000 is in use
   lsof -i :8000  # macOS/Linux
   netstat -an | findstr :8000  # Windows
   ```

2. **Test HTTP Endpoint**:
   ```bash
   curl -X POST http://localhost:8000/sse/ \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}'
   ```

3. **Check Server Logs**:
   ```bash
   # For local server
   python run_mcp_server_sse.py
   
   # For Docker
   docker logs azebal-mcp-server
   ```

### **Cursor IDE Issues**

1. **Verify Configuration**:
   ```bash
   # Check mcp.json exists and is valid JSON
   cat ~/.cursor/mcp.json  # macOS/Linux
   type %APPDATA%\Cursor\mcp.json  # Windows
   ```

2. **Check Cursor Logs**:
   - Open Cursor Developer Tools (`Cmd+Shift+I` on macOS, `Ctrl+Shift+I` on Windows/Linux)
   - Look for MCP-related error messages in the console

3. **Restart Cursor**:
   - Close Cursor completely
   - Restart Cursor IDE
   - Test connection again

### **Docker Issues**

```bash
# Check container status
docker ps -a --filter name=azebal-mcp-server

# View container logs
docker logs azebal-mcp-server

# Check container health
docker inspect azebal-mcp-server | grep -A 5 "Health"

# Restart container
docker restart azebal-mcp-server

# Remove and recreate container
docker stop azebal-mcp-server && docker rm azebal-mcp-server
docker run -d --name azebal-mcp-server -p 8000:8000 azebal-mcp:latest
```

## 🧪 **Testing**

The project follows a test pyramid approach:

- **Unit Tests**: Fast, isolated component tests (>80% coverage)
- **Integration Tests**: Component interaction verification
- **E2E Tests**: Complete workflow testing

```bash
# Run test suite with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test types
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests  
pytest tests/e2e/          # End-to-end tests
```

## 📚 **Documentation**

- **[Product Requirements Document](docs/prd.md)** - Complete project requirements and scope
- **[Architecture Document](docs/architect.md)** - Detailed technical architecture
- **[Architecture Details](docs/architecture/)** - Individual architecture components

## 🛠️ **Development**

### Code Standards

- **Style**: Black formatting, Flake8 linting
- **Type Hints**: 100% type annotation coverage required
- **Testing**: Pytest with >80% coverage for core logic
- **Documentation**: Comprehensive docstrings and README updates

### Epic Development Plan

**Epic 1: Security Authentication and Azure Session Foundation**
- Implement Microsoft OAuth 2.0 authentication flow
- Establish secure session management
- Validate Azure API connectivity

**Epic 2: Real-time Error Analysis Engine Implementation**
- Develop comprehensive error analysis capabilities
- Integrate Azure resource status queries
- Implement LLM-powered solution generation

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Ensure all tests pass and code follows the established standards before submitting.

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋 **Support**

For questions or support:
- Check the [documentation](docs/)
- Review [existing issues](../../issues)
- Create a [new issue](../../issues/new) if needed

---

**Built with ❤️ using the BMad methodology for AI-driven development**
