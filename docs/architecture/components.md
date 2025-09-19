# 5. Components

The AZEBAL monolithic server consists of the following core components logically:

## 5.1. AZEBAL Server (FastMCP Interface)

* **Responsibility**: Serves as a single entry point that receives all requests from IDE AI agents and routes requests to appropriate internal components.

## 5.2. Auth Module (Authentication Module)

* **Responsibility**: Responsible for OAuth 2.0 communication with Microsoft ID Platform and session management through Redis.

## 5.3. LLM Engine (LLM Engine)

* **Responsibility**: Performs core business logic for `debug_error` requests, calls `Azure API Client`, and generates final analysis results.

## 5.4. Azure API Client (Azure API Client)

* **Responsibility**: Encapsulates all communication with KT Azure environment.
