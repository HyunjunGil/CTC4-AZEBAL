# 9. Source Tree

## 9.1. Project Structure Overview

```plaintext
AZEBAL/
├── .bmad-core/                    # BMAD framework core files
├── .cursor/                       # Cursor IDE configuration
│   └── rules/
│       └── mcp.mdc
├── docs/                          # Project documentation
│   ├── architecture/              # Architecture documentation
│   │   ├── 1-introduction.md
│   │   ├── 2-high-level-architecture.md
│   │   ├── 3-tech-stack.md
│   │   ├── 4-data-models.md
│   │   ├── 5-components.md
│   │   ├── 6-external-apis.md
│   │   ├── 7-core-workflows.md
│   │   ├── 8-database-schema.md
│   │   ├── 9-source-tree.md
│   │   ├── 10-infrastructure-and-deployment.md
│   │   ├── 11-error-handling-strategy.md
│   │   ├── 12-coding-standards.md
│   │   ├── 13-test-strategy-and-standards.md
│   │   ├── 14-security.md
│   │   ├── 15-checklist-results-report.md
│   │   ├── 16-next-steps.md
│   │   └── index.md
│   ├── prd/                       # Product Requirements Documentation
│   │   ├── 1-goals-and-background-context.md
│   │   ├── 2-requirements.md
│   │   ├── 3-technical-assumptions.md
│   │   ├── 4-epic-list.md
│   │   ├── 5-epic-1-security-authentication-and-azure-session-foundation.md
│   │   ├── 6-epic-2-real-time-error-analysis-engine-implementation.md
│   │   ├── 7-checklist-results-report.md
│   │   ├── 8-next-steps.md
│   │   └── index.md
│   ├── stories/                   # User stories and development tasks
│   ├── architect.md               # Architecture overview
│   ├── architect-kr.md            # Architecture overview (Korean)
│   ├── brownfield-architecture.md # Brownfield architecture analysis
│   ├── prd.md                     # Product Requirements Document
│   ├── prd-kr.md                  # Product Requirements Document (Korean)
│   ├── IMPLEMENTATION_PLAN.md     # Implementation planning
│   └── PROJECT_SETUP_SUMMARY.md   # Project setup summary
├── images/                        # Documentation images
│   └── high-level-architecture.png
├── scripts/                       # Deployment and utility scripts
│   └── deploy_docker.sh
├── src/                           # Source code
│   ├── __init__.py
│   ├── main.py                    # Main entry point
│   ├── server.py                  # MCP server implementation
│   ├── cli.py                     # Command-line interface
│   ├── health_check.py            # Health check endpoint
│   ├── core/                      # Core business logic
│   │   ├── __init__.py
│   │   ├── auth.py                # Authentication logic
│   │   ├── engine.py              # Core engine implementation
│   │   └── config.py              # Configuration management
│   ├── services/                  # External service integrations
│   │   ├── __init__.py
│   │   └── azure_client.py        # Azure service client
│   ├── tools/                     # MCP tools implementation
│   │   ├── __init__.py
│   │   └── greeting.py            # Greeting tool example
│   └── utils/                     # Utility functions
│       └── __init__.py
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py                # Pytest configuration
│   ├── unit/                      # Unit tests
│   │   ├── __init__.py
│   │   ├── test_greeting_tool.py
│   │   └── test_server.py
│   ├── integration/               # Integration tests
│   │   └── __init__.py
│   ├── e2e/                       # End-to-end tests
│   │   └── __init__.py
│   └── fixtures/                  # Test fixtures
│       └── __init__.py
├── web-bundles/                   # BMAD web bundles
│   ├── agents/                    # Agent definitions
│   │   ├── analyst.txt
│   │   ├── architect.txt
│   │   ├── bmad-master.txt
│   │   ├── bmad-orchestrator.txt
│   │   ├── dev.txt
│   │   ├── pm.txt
│   │   ├── po.txt
│   │   ├── qa.txt
│   │   └── sm.txt
│   ├── teams/                     # Team definitions
│   │   ├── team-all.txt
│   │   ├── team-fullstack.txt
│   │   ├── team-ide-minimal.txt
│   │   └── team-no-ui.txt
│   └── expansion-packs/           # Expansion packs
│       ├── bmad-2d-phaser-game-dev/
│       ├── bmad-2d-unity-game-dev/
│       ├── bmad-creative-writing/
│       ├── bmad-godot-game-dev/
│       └── bmad-infrastructure-devops/
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
├── .mcp.json                      # MCP configuration
├── docker-compose.yml             # Docker Compose configuration
├── Dockerfile                     # Docker container definition
├── environment.yml                # Conda environment specification
├── pytest.ini                    # Pytest configuration
├── README.md                      # Project documentation
├── run_mcp_server.py             # MCP server runner
├── run_mcp_server_sse.py         # MCP server SSE runner
└── server.log                    # Server log file
```

## 9.2. Source Code Organization

### 9.2.1. Core Module (`src/core/`)
The core module contains the fundamental business logic and configuration management.

| File | Purpose | Dependencies |
| :--- | :--- | :--- |
| `__init__.py` | Module initialization | - |
| `auth.py` | Authentication and authorization logic | `azure-identity`, `PyJWT` |
| `engine.py` | Core debugging and reasoning engine | `azure-openai`, `structlog` |
| `config.py` | Configuration management and validation | `pydantic-settings`, `python-dotenv` |

### 9.2.2. Services Module (`src/services/`)
External service integrations and API clients.

| File | Purpose | Dependencies |
| :--- | :--- | :--- |
| `__init__.py` | Module initialization | - |
| `azure_client.py` | Azure service client implementation | `azure-identity`, `azure-mgmt-*` |

### 9.2.3. Tools Module (`src/tools/`)
MCP tool implementations for IDE agent communication.

| File | Purpose | Dependencies |
| :--- | :--- | :--- |
| `__init__.py` | Module initialization | - |
| `greeting.py` | Example greeting tool | `fastmcp` |

### 9.2.4. Utils Module (`src/utils/`)
Utility functions and helper classes.

| File | Purpose | Dependencies |
| :--- | :--- | :--- |
| `__init__.py` | Module initialization | - |

## 9.3. Test Organization

### 9.3.1. Unit Tests (`tests/unit/`)
Fast, isolated tests for individual functions and classes.

| File | Purpose | Coverage |
| :--- | :--- | :--- |
| `test_greeting_tool.py` | Greeting tool functionality | `src/tools/greeting.py` |
| `test_server.py` | MCP server functionality | `src/server.py` |

### 9.3.2. Integration Tests (`tests/integration/`)
Tests for component interactions and external service integrations.

### 9.3.3. End-to-End Tests (`tests/e2e/`)
Full system workflow tests and user journey validation.

### 9.3.4. Test Fixtures (`tests/fixtures/`)
Reusable test data and mock objects.

## 9.4. Configuration Files

### 9.4.1. Environment Configuration
- **`.env.example`**: Template for environment variables
- **`environment.yml`**: Conda environment specification
- **`pytest.ini`**: Pytest configuration and test markers

### 9.4.2. Docker Configuration
- **`Dockerfile`**: Multi-stage container build definition
- **`docker-compose.yml`**: Local development environment setup

### 9.4.3. IDE Configuration
- **`.cursor/rules/`**: Cursor IDE rules and agent definitions
- **`.mcp.json`**: MCP server configuration

## 9.5. Documentation Structure

### 9.5.1. Architecture Documentation (`docs/architecture/`)
Comprehensive system architecture documentation including:
- High-level architecture overview
- Technology stack specifications
- Component design and interactions
- Data models and schemas
- Security and deployment strategies

### 9.5.2. Product Requirements (`docs/prd/`)
Product requirements and feature specifications including:
- Goals and background context
- Detailed requirements
- Epic breakdown and user stories
- Technical assumptions and constraints

### 9.5.3. User Stories (`docs/stories/`)
Development tasks and user story implementations.

## 9.6. Web Bundles Structure

### 9.6.1. Agent Definitions (`web-bundles/agents/`)
BMAD agent persona definitions for different roles:
- **architect.txt**: System architecture specialist
- **dev.txt**: Full-stack developer
- **qa.txt**: Quality assurance specialist
- **pm.txt**: Product manager
- **po.txt**: Product owner
- **sm.txt**: Scrum master
- **analyst.txt**: Business analyst

### 9.6.2. Team Definitions (`web-bundles/teams/`)
Pre-configured team compositions for different project types.

### 9.6.3. Expansion Packs (`web-bundles/expansion-packs/`)
Specialized agent teams for specific domains:
- Game development (Phaser, Unity, Godot)
- Creative writing
- Infrastructure and DevOps

## 9.7. File Naming Conventions

### 9.7.1. Python Files
- **Modules**: `snake_case.py`
- **Classes**: `PascalCase` within files
- **Functions**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`

### 9.7.2. Test Files
- **Unit tests**: `test_*.py`
- **Integration tests**: `test_*_integration.py`
- **E2E tests**: `test_*_e2e.py`

### 9.7.3. Configuration Files
- **Environment**: `.env*`
- **Docker**: `Dockerfile`, `docker-compose.yml`
- **Python**: `pyproject.toml`, `setup.cfg`
- **Testing**: `pytest.ini`, `conftest.py`

## 9.8. Import Organization

### 9.8.1. Import Order
1. Standard library imports
2. Third-party imports
3. Local application imports

### 9.8.2. Import Examples
```python
# Standard library
import os
import sys
from typing import Dict, List, Optional

# Third-party
import structlog
from fastapi import FastAPI
from pydantic import BaseModel

# Local imports
from src.core.config import settings
from src.services.azure_client import AzureClient
```

## 9.9. Module Dependencies

### 9.9.1. Dependency Graph
```
src/main.py
├── src/cli.py
├── src/server.py
│   ├── src/tools/greeting.py
│   └── src/core/config.py
└── src/health_check.py
    └── src/core/config.py

src/core/
├── src/core/config.py (no internal dependencies)
├── src/core/auth.py
│   └── src/core/config.py
└── src/core/engine.py
    ├── src/core/config.py
    └── src/services/azure_client.py

src/services/
└── src/services/azure_client.py
    └── src/core/config.py

src/tools/
└── src/tools/greeting.py (no internal dependencies)
```

### 9.9.2. Circular Dependency Prevention
- Core modules should not import from higher-level modules
- Services can import from core but not from tools
- Tools should be self-contained with minimal dependencies
- Use dependency injection to break circular dependencies

## 9.10. Development Guidelines

### 9.10.1. Adding New Modules
1. Create the module file with proper `__init__.py`
2. Add type hints and docstrings
3. Write comprehensive tests
4. Update this documentation
5. Follow the established naming conventions

### 9.10.2. Module Responsibilities
- **Core**: Business logic, configuration, authentication
- **Services**: External API integrations, data access
- **Tools**: MCP tool implementations, IDE agent interfaces
- **Utils**: Shared utilities, helper functions

### 9.10.3. Testing Requirements
- Each module must have corresponding test files
- Maintain minimum 80% code coverage
- Include unit, integration, and E2E tests as appropriate
- Use fixtures for common test data and mocks
