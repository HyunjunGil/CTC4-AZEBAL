# 3. Tech Stack

## 3.1. Cloud Infrastructure

* **Provider**: Microsoft Azure
* **Key Services**: Azure App Service (for hosting), Azure OpenAI Service, Azure Active Directory (for auth), Azure Cache for Redis, Azure Database for PostgreSQL (for pgvector), Azure Cognitive Search
* **Deployment Regions**: Korea Central

## 3.2. Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Language** | Python | 3.11.x | Primary development language | Rich AI/ML ecosystem and excellent Azure SDK support. |
| **Framework** | FastMCP | Latest stable version | MCP server protocol implementation | PRD requirement. Standardizes communication with IDE agents. |
| **LLM Engine** | Azure OpenAI Service | GPT-4 | Core debugging and reasoning engine | PRD requirement. Highest level of language understanding and reasoning capabilities. |
| **Authentication** | MS ID Platform | OAuth 2.0 | User authentication and authorization | PRD requirement. Integration with KT internal MS accounts, high security. |
| **Session Storage**| Redis | 7.x | User session management | In-memory storage providing fast performance and scalability. |
| **Vector DB** | Azure Cognitive Search + pgvector | Service-based / Latest | (Phase 2) RAG system database | PRD requirement. Excellent integration and scalability as Azure native service. |
| **Local DB** | MariaDB | 10.x | Local environment test database | Provides RDBMS environment similar to production (PostgreSQL) to improve test accuracy. |
| **API Protocol**| stdio & SSE | N/A | IDE agent communication method | PRD requirement. Ensures compatibility with target IDEs like Cursor. |
| **Testing** | Pytest | 8.x | Unit/integration test framework | Python standard test library. Rich plugins and powerful features. |
| **Code Style**| Black, Flake8 | Latest | Code formatting and linting | Enforces consistent code style to improve readability and maintainability. |
| **Dependency Management**| Conda | Latest stable version | Package and Conda virtual environment management | User preference. Strong environment isolation and support for various package management. |
