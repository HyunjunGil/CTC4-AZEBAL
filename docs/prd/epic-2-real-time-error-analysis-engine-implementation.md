# 6. Epic 2: Real-time Error Analysis Engine Implementation

> **Epic Goal**: Implement the `debug_error` tool that autonomously analyzes errors and provides complete solutions in a single response on the authentication foundation built in Epic 1, receiving a single request from the IDE AI agent.

## **Story 2.1: `debug_error` API Endpoint Implementation**
* **As an** IDE AI Agent,
* **I want** to call a single `debug_error` endpoint with all necessary context (error info, source code, auth token),
* **so that** I can get a complete debugging analysis in one transaction without multiple interactions.

**Acceptance Criteria:**
1. An API endpoint for `debug_error` exists on the AZEBAL server.
2. The endpoint properly receives and validates the `access_token`, `error_summary`, and `extra_source_code` parameters.
3. When requesting with an invalid AZEBAL access token, it returns a 401 Unauthorized error.

## **Story 2.2: Autonomous Context-based Resource Analysis**
* **As an** AZEBAL system,
* **I want** to autonomously perform a series of analysis steps (like multiple Azure API calls) based on the initial context provided,
* **so that** I can gather all necessary data for a diagnosis without asking the user for more information.

**Acceptance Criteria:**
1. When receiving a `debug_error` request, generate a **unique 'trace_id'** and record it in logs to indicate the start of the analysis process.
2. Before starting analysis, record the list of **Azure resource types and names to investigate (analysis plan)** in logs.
3. When calling Azure APIs according to the analysis plan, record **specific details about which resource was targeted and what information was queried** in logs.
4. Record in logs that **data was successfully collected from Azure API calls or expected errors (e.g., 403 Forbidden) were received**.
5. All these processes must be completed **without any additional user interaction** after the initial request.

## **Story 2.3: Comprehensive Analysis Report Generation and Single Response**
* **As a** KT developer,
* **I want** to receive a single, comprehensive response from `debug_error` that includes the analysis results, debugging process, and a clear, actionable solution,
* **so that** my IDE AI agent can interpret it and help me fix the problem immediately.

**Acceptance Criteria:**
1. AZEBAL's final response is delivered as a single API response.
2. The response content has a clear structure of "Analysis Results", "Debugging Process", and "Actions to Take".
3. "Actions to Take" is written in plain text that is easy for humans to understand while being suitable for IDE AI agents (Cursor) to interpret and take follow-up actions like code modification suggestions.


---
