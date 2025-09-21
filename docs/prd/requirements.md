# 2. Requirements

### **2.1 Functional Requirements**
* **FR1**: Users must be able to authenticate using Azure CLI access tokens obtained from their local environment through the `login` tool.
* **FR2**: The `login` tool must validate the provided Azure access token and issue an AZEBAL-specific JWT token upon successful validation.
* **FR3**: Users must be able to call the `debug_error` tool with a valid AZEBAL JWT token, error summary information, and related source code.
* **FR4**: The system must call Azure APIs based on user permissions (Azure access token-based) to collect real-time status information of Azure resources related to the error.
* **FR5**: The system must comprehensively analyze all collected information to generate a single response including expected error causes, debugging process, and actionable solutions.

### **2.2 Non-Functional Requirements**
* **NFR1 (Performance)**: Average response time for `debug_error` requests must be within 5 minutes.
* **NFR2 (Security)**: All API endpoints except the login API must be accessible only through valid access tokens, and all data must be filtered according to the user's RBAC policies.
* **NFR3 (Infrastructure)**: The system must operate stably within KT's internal ZTNA security environment.
* **NFR4 (Compatibility)**: The MCP server must support both stdio and SSE (Server-Sent Events) protocols for seamless communication with IDE AI agents.
* **NFR5 (Development)**: The system's backend must be implemented using Python language and FastMCP library.

---
