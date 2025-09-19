# 6. Epic 2: Real-time Error Analysis Engine Implementation

> **Epic Goal**: Implement the `debug_error` tool that autonomously analyzes errors and provides complete solutions in a single response on the authentication foundation built in Epic 1, receiving a single request from the IDE AI agent.

### **Story 2: Complete Error Analysis and Debugging Solution**
* **As a** KT developer,
* **I want** to call a single `debug_error` endpoint with all necessary context (error info, source code, auth token) and receive a comprehensive analysis that autonomously investigates Azure resources and provides actionable solutions,
* **so that** I can get a complete debugging analysis in one transaction without multiple interactions, and my IDE AI agent can interpret the results to help me fix the problem immediately.

**Acceptance Criteria:**
1. An API endpoint for `debug_error` exists on the AZEBAL server.
2. The endpoint properly receives and validates the `access_token`, `error_summary`, and `extra_source_code` parameters.
3. When requesting with an invalid AZEBAL access token, it returns a 401 Unauthorized error.
4. When receiving a `debug_error` request, generate a **unique 'trace_id'** and record it in logs to indicate the start of the analysis process.
5. Before starting analysis, record the list of **Azure resource types and names to investigate (analysis plan)** in logs. (e.g., `PLANNING - Check ACR 'myAcrRepo'`, `PLANNING - Check AppContainer 'myApp' status`)
6. When calling Azure APIs according to the analysis plan, record **specific details about which resource was targeted and what information was queried** in logs. (e.g., `CALLING - Get ACR 'myAcrRepo' permissions`)
7. Record in logs that **data was successfully collected from Azure API calls or expected errors (e.g., 403 Forbidden) were received**.
8. All these processes must be completed **without any additional user interaction** after the initial request.
9. AZEBAL's final response is delivered as a single API response.
10. The response content has a clear structure of "Analysis Results", "Debugging Process", and "Actions to Take".
11. "Actions to Take" is written in plain text that is easy for humans to understand while being suitable for IDE AI agents (Cursor) to interpret and take follow-up actions like code modification suggestions. (e.g., "ACR permission check results show that the image path in value.yaml does not match the actual repository name in Azure, so modification is needed.")

**Test Cases:**
* **TC2.1**: Verify that `debug_error` endpoint exists and accepts required parameters
* **TC2.2**: Verify that invalid access tokens return 401 Unauthorized error
* **TC2.3**: Verify that valid requests generate unique trace_id and log the start of analysis
* **TC2.4**: Verify that analysis plan is created and logged before Azure API calls
* **TC2.5**: Verify that Azure API calls are made according to the analysis plan
* **TC2.6**: Verify that Azure API responses are properly logged (success and error cases)
* **TC2.7**: Verify that the entire process completes without additional user interaction
* **TC2.8**: Verify that final response has proper structure (Analysis Results, Debugging Process, Actions to Take)
* **TC2.9**: Verify that Actions to Take are written in plain text suitable for IDE AI agents
* **TC2.10**: Verify end-to-end debug_error flow with real Azure resources

**Out of Scope:**
* Advanced machine learning models for error pattern recognition beyond basic analysis
* Integration with external debugging tools or third-party analysis services
* Real-time monitoring and alerting capabilities
* Historical error tracking and trend analysis
* Custom error resolution templates or knowledge base integration
* Multi-tenant error analysis or cross-user error correlation
* Advanced visualization of debugging results

**Notes:**
* This story combines the complete error analysis flow from API endpoint through final response generation
* The autonomous analysis capability is critical - no user interaction should be required after the initial request
* Comprehensive logging is essential for debugging and monitoring the analysis process
* The response format must be optimized for both human readability and AI agent interpretation
* Consider implementing timeout mechanisms for long-running Azure API calls
* Error handling should gracefully handle Azure API failures and provide meaningful feedback

---
