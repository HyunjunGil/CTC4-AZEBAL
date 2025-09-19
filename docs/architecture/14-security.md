# 14. Security

* **Input Validation**: `Pydantic` for strict validation at the API boundary.
* **Auth**: OAuth 2.0 and RBAC.
* **Secrets**: Azure Key Vault for production, `.env` file for local development.
* **Data Protection**: Encryption at rest (for tokens in Redis) and in transit (TLS 1.2+).
* **Dependencies**: Automated vulnerability scanning with tools like `safety`.
