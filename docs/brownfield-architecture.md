# AZEBAL Brownfield Architecture Document

## Introduction

This document captures the **CURRENT STATE** of the AZEBAL codebase, including technical debt, workarounds, and real-world patterns. It serves as a reference for AI agents working on enhancements.

### Document Scope

**Focused on areas relevant to: MCP server implementation with custom URL structure and Docker deployment**

### Change Log

| Date   | Version | Description                 | Author    |
| ------ | ------- | --------------------------- | --------- |
| 2025-09-19 | 1.0     | Initial brownfield analysis | BMad Master |

## Quick Reference - Key Files and Entry Points

### Critical Files for Understanding the System

- **Main Entry Points**: `run_mcp_server.py` (stdio), `run_mcp_server_sse.py` (HTTP)
- **Core Server**: `src/server.py` - FastMCP server implementation
- **Tool Implementation**: `src/tools/greeting.py` - Current working tool
- **Health Check**: `src/health_check.py` - Docker health monitoring
- **Docker Config**: `Dockerfile`, `docker-compose.yml` - Container deployment
- **Configuration**: `environment.yml` - Dependencies and environment setup

### Enhancement Impact Areas

**Current Implementation Status**: Basic MCP server with greeting tool only
- **Completed**: MCP server foundation, Docker deployment, URL structure migration
- **Missing**: Authentication module, LLM engine, Azure API client, core business logic

## High Level Architecture

### Technical Summary

**Current State**: Basic MCP server implementation using FastMCP framework with minimal functionality. The system currently only provides a greeting tool as a proof-of-concept for MCP integration.

### Actual Tech Stack (from environment.yml)

| Category  | Technology | Version | Notes                      |
| --------- | ---------- | ------- | -------------------------- |
| Runtime   | Python     | 3.11.*  | Conda-managed environment  |
| Framework | FastMCP    | Latest  | MCP server implementation  |
| Transport | stdio/HTTP | N/A     | Dual transport support     |
| Testing   | pytest     | 8.x     | 80% coverage requirement   |
| Container | Docker     | Latest  | Production deployment       |
| Database  | None       | N/A     | **MISSING** - Redis/MariaDB not implemented |

### Repository Structure Reality Check

- **Type**: Monorepo
- **Package Manager**: Conda + pip
- **Notable**: Well-structured but minimal implementation

## Source Tree and Module Organization

### Project Structure (Actual)

```text
azebal/
├── src/
│   ├── server.py              # FastMCP server implementation
│   ├── tools/
│   │   └── greeting.py        # ONLY tool currently implemented
│   ├── core/                  # EMPTY - planned auth/engine modules
│   ├── services/              # EMPTY - planned Azure client
│   ├── utils/                 # EMPTY - planned utilities
│   ├── health_check.py        # Docker health check
│   ├── cli.py                 # CLI interface (unused)
│   └── main.py                # Entry point (unused)
├── tests/
│   ├── unit/
│   │   ├── test_greeting_tool.py  # Basic tool tests
│   │   └── test_server.py         # Basic server tests
│   ├── integration/           # EMPTY
│   └── e2e/                   # EMPTY
├── docs/                      # Comprehensive documentation
├── run_mcp_server.py          # stdio entry point
├── run_mcp_server_sse.py      # HTTP entry point with custom URL
├── Dockerfile                 # Production container
├── docker-compose.yml         # Development setup
└── environment.yml            # Dependencies
```

### Key Modules and Their Purpose

- **MCP Server**: `src/server.py` - FastMCP server with greeting tool
- **Greeting Tool**: `src/tools/greeting.py` - Simple test tool returning "hello"
- **Health Check**: `src/health_check.py` - Docker health monitoring for `/azebal/mcp` endpoint
- **Entry Points**: `run_mcp_server*.py` - Transport-specific server launchers

## Data Models and APIs

### Data Models

**CURRENT STATE**: No data models implemented
- **Planned**: UserSession (Redis), feedback (PostgreSQL)
- **Missing**: All database integration, session management

### API Specifications

- **MCP Protocol**: FastMCP implementation
- **Current Endpoint**: `http://localhost:8000/azebal/mcp` (custom URL structure)
- **Available Tools**: `greeting` only
- **Missing**: `login`, `debug_error` tools from PRD

## Technical Debt and Known Issues

### Critical Technical Debt

1. **Missing Core Modules**: All business logic modules (auth, LLM engine, Azure client) are empty
2. **No Database Integration**: Redis and MariaDB not implemented despite being in docker-compose.yml
3. **Incomplete CLI**: `src/cli.py` exists but uses deprecated `run_sse()` method
4. **Test Coverage Gap**: Only basic unit tests, no integration or E2E tests
5. **Environment Configuration**: No `.env` file management or configuration loading

### Workarounds and Gotchas

- **URL Structure**: Recently migrated from `/mcp` to `/azebal/mcp` - all configs updated
- **Transport Fallback**: SSE transport falls back to stdio if streamable-http fails
- **Docker Health Check**: Uses HTTP endpoint instead of MCP protocol for health monitoring
- **Python Path**: Manual path manipulation in entry point scripts instead of proper package structure

## Integration Points and External Dependencies

### External Services

| Service  | Purpose  | Integration Type | Key Files                      | Status |
| -------- | -------- | ---------------- | ------------------------------ | ------ |
| FastMCP  | MCP Protocol | Library | `src/server.py` | ✅ Implemented |
| Docker   | Containerization | Runtime | `Dockerfile` | ✅ Implemented |
| Azure APIs | Planned | REST API | `src/services/` | ❌ Not implemented |
| Microsoft Auth | Planned | OAuth 2.0 | `src/core/` | ❌ Not implemented |

### Internal Integration Points

- **MCP Transport**: stdio and HTTP with custom URL structure
- **Docker Deployment**: Containerized with health checks
- **Testing**: pytest framework with coverage requirements

## Development and Deployment

### Local Development Setup

1. **Conda Environment**: `conda env create -f environment.yml`
2. **Server Launch**: `python run_mcp_server.py` (stdio) or `python run_mcp_server_sse.py` (HTTP)
3. **Docker Development**: `docker-compose up` (commented out Redis/MariaDB)

### Build and Deployment Process

- **Docker Build**: `docker build -t azebal-mcp:latest .`
- **Container Run**: `docker run -d --name azebal-mcp-server -p 8000:8000 azebal-mcp:latest`
- **Health Check**: HTTP GET to `http://localhost:8000/azebal/mcp`

## Testing Reality

### Current Test Coverage

- **Unit Tests**: 2 test files, basic coverage
- **Integration Tests**: None implemented
- **E2E Tests**: None implemented
- **Coverage Target**: 80% (not measured)

### Running Tests

```bash
pytest                    # Runs unit tests
pytest --cov=src         # Runs with coverage
```

## Enhancement PRD Provided - Impact Analysis

### Files That Will Need Modification

Based on the PRD requirements, these files will be affected:

- `src/server.py` - Add login and debug_error tools
- `src/core/auth.py` - **CREATE** - OAuth 2.0 authentication
- `src/core/engine.py` - **CREATE** - LLM analysis engine
- `src/services/azure_client.py` - **CREATE** - Azure API integration
- `src/tools/` - **ADD** - login.py, debug_error.py tools
- `environment.yml` - Add Azure SDK dependencies
- `docker-compose.yml` - Enable Redis and MariaDB services

### New Files/Modules Needed

- `src/core/config.py` - Configuration management
- `src/utils/` - Utility functions
- `src/models/` - Data models
- `.env.example` - Environment template
- Database migration scripts

### Integration Considerations

- Must integrate with existing FastMCP server structure
- Docker health check needs to work with new tools
- URL structure `/azebal/mcp` must be maintained
- Test coverage must reach 80% target

## Appendix - Useful Commands and Scripts

### Frequently Used Commands

```bash
# Development
conda activate azebal
python run_mcp_server.py              # stdio transport
python run_mcp_server_sse.py          # HTTP transport

# Docker
docker build -t azebal-mcp:latest .
docker run -d --name azebal-mcp-server -p 8000:8000 azebal-mcp:latest

# Testing
pytest
pytest --cov=src
```

### Debugging and Troubleshooting

- **Logs**: Check Docker logs with `docker logs azebal-mcp-server`
- **Health Check**: `curl http://localhost:8000/azebal/mcp`
- **MCP Test**: Use Cursor IDE with updated `mcp.json` configuration

---

**This document reflects the ACTUAL current state of the AZEBAL project as of September 19, 2025. The system is in early MVP stage with basic MCP server functionality and requires significant development to meet PRD requirements.**
