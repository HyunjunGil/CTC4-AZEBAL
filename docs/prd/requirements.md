# 2. Requirements

### **2.1 Functional Requirements**
* **FR1**: Users must be able to authenticate using their Microsoft company account via OAuth 2.0 through the `login` tool.
* **FR2**: The `login` tool must issue an AZEBAL-specific access token that can query the user's Azure permissions upon successful authentication.
* **FR3**: Users must be able to call the `debug_error` tool with a valid access token and error summary information.
* **FR4**: The system must analyze the error message passed during `debug_error` requests and suggest the expected range of source code files needed for debugging to the user for confirmation.
* **FR5**: The system must call Azure APIs based on user permissions to collect real-time status information of Azure resources related to the error.
* **FR6**: The system must comprehensively analyze all collected information (user context, real-time resource status) to generate a response including expected error causes and their rationale.

### **2.2 Non-Functional Requirements**
* **NFR1 (Performance)**: Average response time for `debug_error` requests must be within 5 minutes.
* **NFR2 (Security)**: All API endpoints except the login API must be accessible only through valid access tokens, and all data must be filtered according to the user's RBAC policies.
* **NFR3 (Infrastructure)**: The system must operate stably within KT's internal ZTNA security environment.
* **NFR4 (Compatibility)**: The MCP server must support both stdio and SSE (Server-Sent Events) protocols for seamless communication with IDE AI agents.
* **NFR5 (Development)**: The system's backend must be implemented using Python language and FastMCP library.

---
