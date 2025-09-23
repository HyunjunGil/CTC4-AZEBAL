# AZEBAL - Azure Error Analysis & BreALdown

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![FastMCP](https://img.shields.io/badge/framework-FastMCP-green.svg)](https://github.com/modelcontextprotocol/python-sdk)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**AZEBAL** is an intelligent MCP (Model Context Protocol) server that provides real-time Azure error debugging and analysis directly within your IDE. It integrates with AI agents to analyze Azure-related errors comprehensively by examining user permissions, source code, and real-time Azure resource status.

## 🎯 **Overview**

AZEBAL transforms fragmented Azure debugging approaches into a systematic, AI-powered solution that:

- **Authenticates** users via Azure CLI access tokens (Phase 1 Complete ✅)
- **Analyzes** Azure errors by combining source code context with real-time resource status (Phase 2 - Planned)
- **Provides** actionable debugging insights and solutions directly in your IDE (Phase 2 - Planned)
- **Reduces** development time spent on Azure-related troubleshooting

## 🏗️ **Architecture**

This project follows a **monolithic architecture** for rapid MVP development:

- **FastMCP Server**: Single entry point for IDE AI agent communication
- **Authentication Module**: Azure CLI token-based authentication (Phase 1 Complete ✅)
- **JWT Service**: AZEBAL-specific JWT token management (Phase 1 Complete ✅)
- **LLM Engine**: Multi-provider LLM interface (Azure OpenAI, OpenAI, Anthropic) (Phase 1 Complete ✅)
- **Azure API Client**: Real-time Azure resource queries (Phase 2 - Planned)
- **Session Management**: Redis-based user session storage (Phase 2 - Planned)

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
│   ├── tools/            # MCP tool definitions
│   │   ├── greeting.py   # Test greeting tool
│   │   ├── login.py      # Azure CLI login tool (Phase 1 Complete ✅)
│   │   └── ask_llm.py    # Multi-provider LLM interface (Phase 1 Complete ✅)
│   ├── core/             # Core business logic
│   │   ├── auth.py       # Azure authentication service (Phase 1 Complete ✅)
│   │   ├── jwt_service.py # JWT token management (Phase 1 Complete ✅)
│   │   ├── config.py     # Configuration management (Phase 1 Complete ✅)
│   │   └── engine.py     # LLM analysis engine (Phase 2 - Planned)
│   ├── services/         # External service integrations
│   │   ├── llm_interface.py      # LLM provider interface (Phase 1 Complete ✅)
│   │   ├── llm_factory.py        # LLM provider factory (Phase 1 Complete ✅)
│   │   ├── azure_openai_service.py # Azure OpenAI integration (Phase 1 Complete ✅)
│   │   ├── openai_service.py      # OpenAI integration (Phase 1 Complete ✅)
│   │   ├── anthropic_service.py   # Anthropic Claude integration (Phase 1 Complete ✅)
│   │   └── azure_client.py        # Azure API client (Phase 2 - Planned)
│   └── utils/            # Utility functions
├── tests/                # Test suite
│   ├── unit/             # Unit tests (>80% coverage target)
│   ├── integration/      # Integration tests
│   ├── e2e/              # End-to-end tests
│   └── fixtures/         # Test data and fixtures
├── requirements.txt      # Python dependencies
├── requirements-dev.txt  # Development dependencies
├── environment.yml       # Conda environment specification
├── environment.template  # Environment variables template
├── pytest.ini           # Pytest configuration
└── README.md
```

## 🚀 **Quick Start**

### Prerequisites

- **Python 3.11+**
- **Conda** (for environment management)
- **Azure CLI** (for authentication - Phase 1)
- **Azure Account** with appropriate permissions (Phase 1)
- **Redis Server** (for session storage - Phase 2)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AZEBAL
   ```

2. **Set up Python environment**
   ```bash
   # Create conda environment
   conda env create -f environment.yml
   conda activate azebal
   
   # Or if environment already exists
   conda activate azebal
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp environment.template .env
   # Edit .env with your Azure subscription ID and JWT secret key
   ```

4. **Set up Azure CLI authentication**
   ```bash
   # Login to Azure CLI
   az login
   
   # Get your access token (for testing)
   az account get-access-token
   ```

5. **Run the MCP server**
   ```bash
   # Activate conda environment
   conda activate azebal
   
   # Run with stdio transport (default)
   python run_mcp_server.py
   
   # Or run with SSE/Streamable-HTTP transport
   python run_mcp_server_sse.py
   ```

### Development Setup

1. **Install development dependencies**
   ```bash
   conda activate azebal
   pip install -r requirements-dev.txt
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
# Azure Configuration (Phase 1)
AZURE_SUBSCRIPTION_ID=your-azure-subscription-id

# JWT Configuration (Phase 1)
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Redis Configuration (Phase 2 - Future)
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Azure CLI Setup

1. **Install Azure CLI**:
   ```bash
   # Ubuntu/Debian
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   
   # macOS (using Homebrew)
   brew install azure-cli
   
   # Windows (using PowerShell)
   Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi; Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'
   ```

2. **Login to Azure**:
   ```bash
   az login
   ```

3. **Check Available Subscriptions**:
   ```bash
   # List all available subscriptions
   az account list --output table
   
   # Show current subscription
   az account show
   
   # Get subscription ID only
   az account show --query id --output tsv
   ```

4. **Set Your Subscription** (if needed):
   ```bash
   # Set by subscription ID
   az account set --subscription "your-subscription-id"
   
   # Set by subscription name
   az account set --subscription "Your Subscription Name"
   ```

5. **Get Access Token**:
   ```bash
   # Get access token for current subscription
   az account get-access-token
   
   # Get access token for specific resource
   az account get-access-token --resource https://management.azure.com/
   ```

### **Quick Reference: Azure CLI Commands**

```bash
# Authentication & Account Management
az login                                    # Login to Azure
az logout                                   # Logout from Azure
az account show                             # Show current account info
az account list --output table             # List all subscriptions
az account set --subscription "sub-id"     # Switch subscription

# Access Tokens
az account get-access-token                # Get access token
az account get-access-token --query expiresOn  # Check token expiration

# Subscription Information
az account show --query "{Name:name, Id:id, State:state, TenantId:tenantId}"
az account show --query id --output tsv    # Get subscription ID only
az account show --query name --output tsv  # Get subscription name only

# Troubleshooting
az --version                               # Check Azure CLI version
az account list --all                      # List all subscriptions (including disabled)
az role assignment list --assignee $(az account show --query user.name --output tsv)
```

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

### **Phase 1 Tools (Complete ✅)**
- **`greeting`**: A test tool that returns "hello" (for testing connectivity)
- **`login`**: Authenticate user with Azure CLI access token and get AZEBAL JWT
- **`ask_llm`**: Ask questions to various LLM providers (Azure OpenAI, OpenAI, Anthropic) - no authentication required

#### **Login Tool Usage Example**

```bash
# 1. Get Azure access token
az account get-access-token

# 2. Use the token with AZEBAL login tool
# (This would be called through your IDE MCP client)
```

**Login Tool Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "azebal_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_info": {
    "object_id": "12345678-1234-1234-1234-123456789012",
    "user_principal_name": "user@company.com",
    "tenant_id": "87654321-4321-4321-4321-210987654321",
    "display_name": "John Doe",
    "email": "user@company.com"
  }
}
```

#### **Ask LLM Tool Usage Example**

The `ask_llm` tool provides a simple interface to interact with various LLM providers. It automatically detects and uses available LLM providers based on your configuration.

**Supported LLM Providers:**
- **Azure OpenAI** (GPT-4, GPT-3.5-turbo)
- **OpenAI** (GPT-4, GPT-3.5-turbo)
- **Anthropic** (Claude-3 Sonnet, Claude-3 Haiku)

**Configuration Examples:**

```bash
# Option 1: Azure OpenAI (recommended for enterprise)
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your_azure_openai_api_key"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4"

# Option 2: OpenAI
export OPENAI_API_KEY="sk-proj-your_openai_api_key"
export OPENAI_MODEL_NAME="gpt-4"

# Option 3: Anthropic Claude
export ANTHROPIC_API_KEY="sk-ant-api03-your_anthropic_api_key"
export ANTHROPIC_MODEL_NAME="claude-3-sonnet-20240229"

# Optional: Explicitly choose provider (auto-detect if not set)
export LLM_PROVIDER="anthropic"  # Options: azure_openai, openai, anthropic
```

**Usage Examples:**

```bash
# Basic math question
curl -X POST http://localhost:8000/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0", 
    "id": 1, 
    "method": "tools/call", 
    "params": {
      "name": "ask_llm", 
      "arguments": {
        "question": "What is 15 * 23?"
      }
    }
  }'

# Programming question
curl -X POST http://localhost:8000/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0", 
    "id": 2, 
    "method": "tools/call", 
    "params": {
      "name": "ask_llm", 
      "arguments": {
        "question": "Explain the difference between async and sync functions in Python"
      }
    }
  }'

# General knowledge
curl -X POST http://localhost:8000/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0", 
    "id": 3, 
    "method": "tools/call", 
    "params": {
      "name": "ask_llm", 
      "arguments": {
        "question": "Who was Albert Einstein and what was his most famous theory?"
      }
    }
  }'
```

**Response Format:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "15 * 23 = 345"
}
```

**Auto-Detection Priority:**
1. Azure OpenAI (if both endpoint and API key are configured)
2. OpenAI (if API key is configured)
3. Anthropic (if API key is configured)

**Error Handling:**
- Returns helpful error messages if no LLM provider is configured
- Suggests which providers are available but not properly configured
- Gracefully handles API errors with descriptive messages

### **Phase 2 Tools (Planned)**
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

### **Azure CLI Issues**

1. **Check Azure CLI Installation**:
   ```bash
   # Verify Azure CLI is installed
   az --version
   
   # Check if logged in
   az account show
   ```

2. **Subscription Issues**:
   ```bash
   # List all available subscriptions
   az account list --output table
   
   # Check current subscription
   az account show --query "{Name:name, Id:id, State:state}"
   
   # Switch subscription if needed
   az account set --subscription "your-subscription-id"
   ```

3. **Access Token Issues**:
   ```bash
   # Get fresh access token
   az account get-access-token
   
   # Check token expiration
   az account get-access-token --query expiresOn
   
   # Re-login if token is expired
   az login
   ```

4. **Permission Issues**:
   ```bash
   # Check your role assignments
   az role assignment list --assignee $(az account show --query user.name --output tsv)
   
   # Check if you have access to Azure Resource Manager
   az account get-access-token --resource https://management.azure.com/
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

**Epic 1: Azure CLI Token-based Authentication (Complete ✅)**
- ✅ Implement Azure CLI access token authentication
- ✅ Create AZEBAL JWT token management
- ✅ Validate Azure API connectivity
- ✅ Establish secure user session foundation

**Epic 2: Real-time Error Analysis Engine Implementation (In Progress)**
- 🔄 Develop comprehensive error analysis capabilities
- 🔄 Integrate Azure resource status queries
- 🔄 Implement LLM-powered solution generation
- 🔄 Add Redis session management

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
