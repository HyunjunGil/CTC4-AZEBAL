# 3. Technical Assumptions

### **3.1 Repository Structure**
* **Monorepo**: AZEBAL server and all related tools are **managed within a single repository (Monorepo)**. This facilitates code sharing, dependency management, and integrated build/deployment during the initial development phase.

### **3.2 Service Architecture**
* **Monolithic**: For rapid development and deployment simplicity in the initial MVP phase, we adopt a **monolithic architecture** that implements all core functionality in a single application. As the system becomes more complex and features expand in the future, we can consider separating each domain into microservices.

### **3.3 Testing Requirements**
* **Unit + Integration**: For all core business logic (authentication, API calls, data analysis, etc.), we aim to write both **Unit Tests** that verify individual functionality and **Integration Tests** that check interconnections between each microservice.
* **Local Testing**: In the developer's local environment, a file-based temporary DB should be used instead of the actual Azure DB to enable fast and isolated testing.

---
