# 14. Security

* **Input Validation**: `Pydantic` for strict validation at the API boundary.
* **Auth**: Azure CLI Token Validation and RBAC.
* **Secrets**: Azure Key Vault for production, `.env` file for local development.
* **Data Protection**: Encryption at rest (for tokens in Redis) and in transit (TLS 1.2+).
* **Dependencies**: Automated vulnerability scanning with tools like `safety`.
* **AI Operation Security**: Function parameter sanitization, resource access validation, audit logging for autonomous operations
* **Sensitive Data Protection**: Automatic masking of credentials, connection strings, and API keys in AI responses
* **Session Isolation**: Complete user session separation for multi-tenant security
