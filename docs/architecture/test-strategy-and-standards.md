# 13. Test Strategy and Standards

* **Philosophy**: Test Pyramid model with >80% coverage for core logic.
* **Types**: `Pytest` for Unit Tests (mocking external dependencies), Integration Tests (with local Docker containers for MariaDB/Redis), and E2E Tests (from a test client).
* **CI**: All tests must pass in CI/CD pipeline before merging to `main`.
