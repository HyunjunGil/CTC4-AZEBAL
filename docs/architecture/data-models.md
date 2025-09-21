# 4. Data Models

The AZEBAL system uses PostgreSQL for structured data storage and Redis for fast session management.

## 4.1. UserSession (in Redis)

* **Purpose**: After a user successfully authenticates, stores and manages information (tokens, expiration time, etc.) needed for the AZEBAL server to call Azure APIs on behalf of that user **in Redis**.
* **Storage Format**: Stored as **Key-Value** format within Redis.
    * **Key**: `session:{user_object_id}`
    * **Value**: **Hash** or **JSON String** containing all attributes of `UserSession`.
* **Key Attributes**:
    * `user_principal_name` (string): ID that uniquely identifies the user (e.g., UPN).
    * `azure_access_token` (string, encrypted): Azure access token passed by the user, used for Azure API calls. **Must be encrypted before storage.**
    * `expires_at` (datetime): Expiration time of Azure access token. (Integrated with Redis TTL functionality)
    * `created_at` (datetime): Session creation time.
