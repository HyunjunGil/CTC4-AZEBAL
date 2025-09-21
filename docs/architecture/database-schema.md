# 8. Database Schema

## 8.1. Redis Schema: `UserSession`

* **Key Format**: `session:{user_object_id}`
* **Data Type**: Hash
* **Value (Hash Fields)**: `user_principal_name`, `azure_access_token` (encrypted), `expires_at`, `created_at`

## 8.2. PostgreSQL Schema (For Phase 2 & Logging)

```sql
-- Table for storing user feedback (Phase 2)
CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_principal_name VARCHAR(255) NOT NULL,
    error_summary TEXT NOT NULL,
    debugging_process TEXT,
    root_cause TEXT,
    solution TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'pending_review',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Audit log table for system usage records
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    trace_id UUID NOT NULL,
    user_principal_name VARCHAR(255) NOT NULL,
    tool_called VARCHAR(100) NOT NULL,
    request_payload JSONB,
    response_payload JSONB,
    execution_time_ms INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```
