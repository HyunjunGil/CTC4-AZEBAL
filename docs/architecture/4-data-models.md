# 4. Data Models

The AZEBAL system uses PostgreSQL for structured data storage and Redis for fast session management.

## 4.1. UserSession (in Redis)

* **Purpose**: After a user successfully authenticates, stores and manages information (tokens, expiration time, etc.) needed for the AZEBAL server to call Azure APIs on behalf of that user **in Redis**. This model is the core of AZEBAL's stateful session management.
* **Storage Format**: Stored as **Key-Value** format within Redis.
    * **Key**: `session:{session_id}`
    * **Value**: **Hash** or **JSON String** containing all attributes of `UserSession`.
* **Key Attributes**:
    * `user_principal_name` (string): ID that uniquely identifies the user.
    * `ms_access_token` (string, encrypted): Access token issued by Microsoft, used for Azure API calls. **Must be encrypted before storage.**
    * `ms_refresh_token` (string, encrypted): Refresh token for renewing MS access tokens without re-login when expired. **Also encrypted before storage.**
    * `expires_at` (datetime): Expiration time of MS access token. (Integrated with Redis TTL functionality)
    * `created_at` (datetime): Session creation time.
