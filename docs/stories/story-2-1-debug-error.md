# Story 2.1: `debug_error` Real-time Error Analysis Engine Implementation

**Status:** Ready to Start  
**Epic:** Epic 2 - Real-time Error Analysis Engine Implementation  
**Developer:** James (Full Stack Developer)  
**Prerequisites:** ✅ Story 1.1 (Azure Login) Complete, ✅ Story 2.0 (LLM Engine) Complete

## Story

Based on the Epic 2 requirements, this story encompasses the complete implementation of the `debug_error` tool that autonomously analyzes errors and provides complete solutions in a single response on the authentication foundation built in Epic 1.

This story combines:
- **Story 2.1**: `debug_error` API Endpoint Implementation
- **Story 2.2**: Autonomous Context-based Resource Analysis 
- **Story 2.3**: Comprehensive Analysis Report Generation and Single Response

## Story 2.1: `debug_error` API Endpoint Implementation
* **As an** IDE AI Agent,
* **I want** to call a single `debug_error` endpoint with all necessary context (error info, source code, auth token),
* **so that** I can get a complete debugging analysis in one transaction without multiple interactions.

**Acceptance Criteria:**
1. An API endpoint for `debug_error` exists on the AZEBAL server.
2. The endpoint properly receives and validates the `azebal_token`, `error_description`, and `context` parameters.
3. When requesting with an invalid AZEBAL access token, it returns a 401 Unauthorized error.

## Story 2.2: Autonomous Context-based Resource Analysis
* **As an** AZEBAL system,
* **I want** to autonomously perform a series of analysis steps (like multiple Azure API calls) based on the initial context provided,
* **so that** I can gather all necessary data for a diagnosis without asking the user for more information.

**Acceptance Criteria:**
1. When receiving a `debug_error` request, generate a **unique 'trace_id'** and record it in logs to indicate the start of the analysis process.
2. Before starting analysis, record the list of **Azure resource types and names to investigate (analysis plan)** in logs.
3. When calling Azure APIs according to the analysis plan, record **specific details about which resource was targeted and what information was queried** in logs.
4. Record in logs that **data was successfully collected from Azure API calls or expected errors (e.g., 403 Forbidden) were received**.
5. All these processes must be completed **without any additional user interaction** after the initial request.

## Story 2.3: Comprehensive Analysis Report Generation and Single Response
* **As a** KT developer,
* **I want** to receive a single, comprehensive response from `debug_error` that includes the analysis results, debugging process, and a clear, actionable solution,
* **so that** my IDE AI agent can interpret it and help me fix the problem immediately.

**Acceptance Criteria:**
1. AZEBAL's final response is delivered as a single API response.
2. The response content has a clear structure of "Analysis Results", "Debugging Process", and "Actions to Take".
3. "Actions to Take" is written in plain text that is easy for humans to understand while being suitable for IDE AI agents (Cursor) to interpret and take follow-up actions like code modification suggestions.

## Tasks

### Core Infrastructure
- [ ] Create debug_error MCP tool with proper schema validation
- [ ] Implement in-memory session cache for MVP (SessionMemoryCache)
- [ ] Create trace_id generation and session management
- [ ] Add comprehensive logging system for analysis tracking

### Analysis Engine
- [ ] Implement AI analysis engine with time/depth limits (40s, depth=5)
- [ ] Create Azure API client integration for resource analysis
- [ ] Implement autonomous analysis decision-making logic
- [ ] Add status-based flow control (done/request/continue/fail)

### Security & Validation
- [ ] Add input validation and size limits (error_description: 50KB, source_files: 10MB)
- [ ] Implement sensitive information filtering
- [ ] Add AZEBAL token validation and 401 error handling
- [ ] Create proper error handling for all edge cases

### Testing
- [ ] Write unit tests for debug_error tool
- [ ] Write unit tests for session cache management
- [ ] Write unit tests for analysis engine
- [ ] Write integration tests for complete workflow
- [ ] Write tests for all status scenarios (done/request/continue/fail)

## Dev Agent Record

### Agent Model Used
- Claude Sonnet 4

### Debug Log
- **2025-01-27**: Prerequisites completed successfully
  - Story 1.1 (Azure Login): Authentication system working with real Azure CLI tokens
  - Story 2.0 (LLM Engine): Multi-provider LLM engine implemented and tested
- **2025-01-27**: Ready to start Story 2.1 (debug_error) implementation
  - Robust authentication foundation available
  - Flexible LLM engine ready for complex analysis tasks
  - MCP server infrastructure proven and stable

### Preparation Notes
- ✅ **Authentication Ready**: Azure CLI token validation working perfectly
- ✅ **LLM Engine Ready**: Multi-provider system (Azure OpenAI, OpenAI, Anthropic) operational
- ✅ **Live Testing Confirmed**: ask_llm tool successfully tested in Cursor IDE
- ✅ **Infrastructure Stable**: MCP server proven with existing tools
- 🚀 **Ready for Story 2.1**: All foundations in place for debug_error implementation

### Completion Notes
- Not started yet - ready to begin implementation

### File List
- Will be updated as implementation progresses

### Change Log
- 2025-01-27: Updated status to "Ready to Start" after prerequisites completion
- 2025-01-27: Renumbered from Story 2 to Story 2.1 (with Story 2.0 as LLM preparation)

## Testing
- Unit tests for debug_error MCP tool
- Unit tests for session cache management
- Unit tests for analysis engine with time/depth limits
- Integration tests for complete debug workflow
- Tests for all status response scenarios
- Error handling tests for invalid tokens and edge cases

## Dev Notes
- MVP uses in-memory session cache (no Redis dependency)
- AI analysis limited to 40 seconds and depth of 5 to prevent infinite loops
- Four status responses: "done", "request", "continue", "fail"
- Sensitive information filtering required for security
- Comprehensive logging for audit trail of analysis steps
