# 2. High Level Architecture

## 2.1. Technical Summary

AZEBAL adopts a **monolithic architecture implemented within a monorepo** for development speed and deployment simplicity in the initial MVP phase. A single application server built using Python and FastMCP library receives requests from IDE AI agents through a ZTNA security gateway. The server authenticates users by **validating Azure CLI access tokens directly passed by users**, and queries real-time resource information from KT's Azure environment through Azure API clients on behalf of authenticated users. The collected information is processed by a core analysis engine, which then delivers the final diagnostic results back to the IDE agent.

## 2.2. High Level Overview

The core of this architecture is to maximize development efficiency in the MVP phase, as determined in the PRD. The monolithic structure has advantages of simple inter-function calls and easy management through a single deployment pipeline.

The core user interaction flow is as follows:

1. **Authentication**: User passes Azure CLI access token to the `login` tool.
2. **Session Creation**: The `Auth` module validates the token and creates a session in Redis, then issues an AZEBAL-specific JWT token.
3. **Analysis Request**: IDE agent sends `debug_error` request with AZEBAL JWT token.
4. **Analysis and Response**: The `LLM Engine` analyzes the request, queries Azure resource information through `Azure API Client`, and generates the final response.

## 2.3. High Level Project Diagram

```mermaid
graph TD
    subgraph "User Environment"
        A[IDE AI Agent]
    end

    subgraph "KT Internal Network"
        B[ZTNA Security Gateway]
        subgraph "AZEBAL MCP Server (Monolithic Application)"
            C[FastMCP Interface]
            D[Authentication Module]
            E[LLM Engine]
            F[Azure API Client]
        end
    end

    subgraph "External Systems"
        G[MS ID Platform]
        H[KT Azure Environment]
    end

    A -- "gRPC/stdio/SSE Request" --> B
    B -- "Secure Connection" --> C
    C -- "Request Routing" --> D
    C -- "Request Routing" --> E
    D -- "Azure Token Validation" --> G
    E -- "Resource Information Query" --> F
    F -- "Azure API Call" --> H
```

## 2.4. Architectural and Design Patterns

* **Monolithic Architecture**: Adopted for rapid development and simple deployment in the MVP phase. All core functionality is included within a single application.
    * *Rationale*: As determined in the PRD, to reduce initial complexity and focus on core functionality implementation.
* **Repository Pattern**: Applied when implementing `Azure API Client` to separate actual Azure API call logic from business logic (LLM engine).
    * *Rationale*: By abstracting the API call portion, it becomes easy to mock API calls during unit testing and flexibly respond to future API specification changes.
* **Facade Pattern**: The `FastMCP Interface` serves as a single entry point that wraps complex internal modules (authentication, LLM engine, etc.).
    * *Rationale*: External clients (IDE agents) can use all AZEBAL functionality through a simple and consistent interface without needing to know the server's complex internal structure.
