# 3. Tech Stack

## 3.1. Cloud Infrastructure

* **Provider**: Microsoft Azure
* **Key Services**: Azure App Service (for hosting), Azure OpenAI Service, Azure Active Directory (for auth), Azure Cache for Redis, Azure Database for PostgreSQL (for pgvector), Azure Cognitive Search
* **Deployment Regions**: Korea Central

## 3.2. Core Technology Stack

### 3.2.1. Primary Technologies

| Category | Technology | Version | Purpose | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Language** | Python | 3.11.x | Primary development language | Rich AI/ML ecosystem and excellent Azure SDK support |
| **Framework** | FastMCP | Latest stable | MCP server protocol implementation | PRD requirement. Standardizes communication with IDE agents |
| **LLM Engine** | Azure OpenAI Service | GPT-4 | Core debugging and reasoning engine | PRD requirement. Highest level of language understanding |
| **Authentication** | MS ID Platform | OAuth 2.0 | User authentication and authorization | PRD requirement. Integration with KT internal MS accounts |
| **Session Storage** | Redis | 7.x | User session management | In-memory storage providing fast performance and scalability |
| **Vector DB** | Azure Cognitive Search + pgvector | Service-based / Latest | (Phase 2) RAG system database | PRD requirement. Excellent integration and scalability |
| **Local DB** | MariaDB | 10.x | Local environment test database | Provides RDBMS environment similar to production |
| **API Protocol** | stdio & SSE | N/A | IDE agent communication method | PRD requirement. Ensures compatibility with target IDEs |
| **Testing** | Pytest | 8.x | Unit/integration test framework | Python standard test library with rich plugins |
| **Code Style** | Black, Flake8, isort, mypy | Latest | Code formatting and linting | Enforces consistent code style and type safety |
| **Dependency Management** | Conda | Latest stable | Package and environment management | Strong environment isolation and package management |

### 3.2.2. Development Dependencies

| Package | Version | Purpose | Usage |
| :--- | :--- | :--- | :--- |
| **black** | Latest | Code formatting | Auto-format Python code |
| **flake8** | Latest | Linting | Static code analysis |
| **isort** | Latest | Import sorting | Organize and sort imports |
| **mypy** | Latest | Type checking | Static type analysis |
| **pytest** | >=8.0 | Testing framework | Unit and integration tests |
| **pytest-cov** | Latest | Coverage reporting | Test coverage analysis |
| **pytest-asyncio** | Latest | Async testing | Test async/await code |
| **pytest-mock** | Latest | Mocking utilities | Mock external dependencies |
| **pre-commit** | >=3.5.0 | Git hooks | Pre-commit code quality checks |
| **safety** | >=2.3.0 | Security scanning | Check for known vulnerabilities |
| **bandit** | >=1.7.0 | Security linting | Security-focused static analysis |

### 3.2.3. Runtime Dependencies

| Package | Version | Purpose | Usage |
| :--- | :--- | :--- | :--- |
| **fastmcp** | Latest | MCP server framework | Core MCP protocol implementation |
| **azure-identity** | >=1.15.0 | Azure authentication | Azure service authentication |
| **azure-mgmt-*** | Latest | Azure management | Azure resource management |
| **openai** | >=1.0.0 | OpenAI client | OpenAI API integration |
| **azure-openai** | Latest | Azure OpenAI client | Azure OpenAI service integration |
| **fastapi** | >=0.104.0 | Web framework | HTTP API framework |
| **uvicorn** | >=0.24.0 | ASGI server | FastAPI server implementation |
| **httpx** | >=0.25.0 | HTTP client | Async HTTP client |
| **pydantic** | >=2.5.0 | Data validation | Data validation and serialization |
| **pydantic-settings** | >=2.1.0 | Settings management | Configuration management |
| **structlog** | >=23.0.0 | Structured logging | Advanced logging capabilities |
| **tenacity** | >=8.2.0 | Retry logic | Retry mechanisms for external calls |
| **click** | >=8.1.0 | CLI framework | Command-line interface |
| **cryptography** | >=41.0.0 | Cryptographic operations | Security and encryption |
| **PyJWT** | >=2.8.0 | JWT handling | JSON Web Token processing |
| **python-multipart** | Latest | Form data parsing | Multipart form data handling |
| **mariadb** | >=1.1.8 | MariaDB connector | Database connectivity |
| **psycopg2-binary** | >=2.9.0 | PostgreSQL connector | PostgreSQL database connectivity |
| **SQLAlchemy** | >=2.0.0 | ORM | Database ORM and query building |
| **alembic** | >=1.12.0 | Database migrations | Database schema migrations |
| **python-dotenv** | >=1.0.0 | Environment variables | .env file loading |
| **redis-py** | Latest | Redis client | Redis database connectivity |

## 3.3. Architecture Patterns

### 3.3.1. Design Patterns
- **Dependency Injection**: For testability and loose coupling
- **Repository Pattern**: For data access abstraction
- **Service Layer Pattern**: For business logic encapsulation
- **Factory Pattern**: For object creation and configuration
- **Observer Pattern**: For event handling and notifications
- **Strategy Pattern**: For algorithm selection and configuration

### 3.3.2. Async Programming
- **Async/Await**: For I/O-bound operations
- **Async Context Managers**: For resource management
- **Async Generators**: For streaming data processing
- **Concurrent Execution**: Using asyncio.gather() for parallel operations

### 3.3.3. Error Handling
- **Custom Exception Hierarchy**: Domain-specific error types
- **Exception Chaining**: Using `raise ... from e` syntax
- **Structured Logging**: With correlation IDs and context
- **Circuit Breaker Pattern**: For external service resilience

## 3.4. Development Environment

### 3.4.1. Environment Management
```bash
# Create conda environment
conda env create -f environment.yml

# Activate environment
conda activate azebal

# Update environment
conda env update -f environment.yml

# Export environment
conda env export > environment.yml
```

### 3.4.2. Code Quality Tools
```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/
mypy src/

# Run tests
pytest tests/ --cov=src --cov-report=html

# Security checks
safety check
bandit -r src/
```

### 3.4.3. Pre-commit Configuration
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ['-r', 'src/']
```

## 3.5. Testing Strategy

### 3.5.1. Test Types
- **Unit Tests**: Fast, isolated tests for individual functions
- **Integration Tests**: Tests for component interactions
- **End-to-End Tests**: Full system workflow tests
- **Contract Tests**: API contract validation
- **Performance Tests**: Load and stress testing

### 3.5.2. Test Configuration
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts = --verbose --tb=short --strict-markers --cov=src --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
```

## 3.6. Deployment and Infrastructure

### 3.6.1. Container Configuration
- **Base Image**: Python 3.11-slim
- **Multi-stage Build**: Separate build and runtime stages
- **Non-root User**: Security best practice
- **Health Checks**: Container health monitoring
- **Resource Limits**: CPU and memory constraints

### 3.6.2. Environment Configuration
- **Development**: Local development with mock services
- **Staging**: Pre-production testing environment
- **Production**: Live Azure environment with full services

### 3.6.3. Monitoring and Observability
- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Metrics Collection**: Application performance metrics
- **Health Endpoints**: Service health monitoring
- **Error Tracking**: Centralized error reporting and alerting

## 3.7. Security Considerations

### 3.7.1. Authentication and Authorization
- **OAuth 2.0**: Microsoft Identity Platform integration
- **JWT Tokens**: Stateless authentication
- **Role-based Access Control**: Granular permission management
- **Token Refresh**: Automatic token renewal

### 3.7.2. Data Protection
- **Encryption at Rest**: Azure storage encryption
- **Encryption in Transit**: TLS/SSL for all communications
- **Secrets Management**: Azure Key Vault for sensitive data
- **Input Validation**: Pydantic models for data validation

### 3.7.3. Network Security
- **VNet Integration**: Azure Virtual Network
- **Private Endpoints**: Secure service communication
- **Firewall Rules**: Network access control
- **DDoS Protection**: Azure DDoS Protection Standard

## 3.8. Performance Optimization

### 3.8.1. Caching Strategy
- **Redis Caching**: Session and data caching
- **Application-level Caching**: In-memory caching for frequent data
- **CDN**: Content delivery network for static assets
- **Database Query Optimization**: Efficient query patterns

### 3.8.2. Scalability
- **Horizontal Scaling**: Multiple service instances
- **Load Balancing**: Azure Application Gateway
- **Auto-scaling**: Automatic resource adjustment
- **Connection Pooling**: Database connection management

### 3.8.3. Monitoring
- **Application Insights**: Azure monitoring service
- **Custom Metrics**: Business-specific metrics
- **Alerting**: Proactive issue detection
- **Performance Profiling**: Code performance analysis
