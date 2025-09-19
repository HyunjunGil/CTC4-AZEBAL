# 11. Error Handling Strategy

* **Model**: Custom Exceptions for business logic, Global Exception Handler for system errors.
* **Logging**: Standard `logging` module with structured JSON format.
* **Patterns**: Exponential backoff retry policy for Azure API calls.
