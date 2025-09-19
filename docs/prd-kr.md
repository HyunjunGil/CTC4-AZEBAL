# AZEBAL 제품 요구사항 명세서 (PRD)

* **문서 버전:** 1.0
* **작성일:** 2025년 9월 18일
* **작성자:** John (Product Manager)

---

### **## 1. Goals and Background Context (목표 및 배경 컨텍스트)**

#### **1.1 Goals (목표)**
* **비즈니스 목표**:
    * Azure 관련 문제 해결에 소요되는 중복 리소스(시간, 인력)를 절감한다.
    * 파편화된 문제 해결 경험을 조직의 지속 가능한 기술 자산으로 체계화하고 축적한다.
* **사용자 목표**:
    * 개발자가 Azure 관련 에러를 디버깅하고 해결하는 데 소요되는 시간을 획기적으로 감소시킨다.
    * 문제 해결을 위해 동료에게 문의하거나 여러 문서를 검색하는 빈도를 줄여, 개발자가 핵심 업무에 집중할 수 있도록 한다.

#### **1.2 Background Context (배경 컨텍스트)**
현재 KT의 Azure 개발자들은 숙련도 부족, 경험 공유를 위한 통합 공간 부재, 비효율적인 디버깅 환경 등의 문제로 인해 불필요한 시간과 자원을 낭비하고 있다. AZEBAL은 개발자의 IDE에 직접 통합되는 AI 에이전트용 MCP 서버로, 사용자의 권한, 소스 코드, 실시간 Azure 리소스 상태라는 3가지 컨텍스트를 종합적으로 분석하여 개인화되고 즉시 적용 가능한 해결책을 제공한다. 이를 통해 파편화된 문제 해결 방식을 조직의 시스템으로 전환하여, KT의 Azure 기술 대응 능력을 상향 평준화하는 것을 목표로 한다.

#### **1.3 Change Log (변경 기록)**
| 날짜 | 버전 | 설명 | 작성자 |
| :--- | :--- | :--- | :--- |
| 2025-09-18 | 1.0 | 초기 문서 작성 | John (PM) |

---

### **## 2. Requirements (요구사항)**

#### **2.1 Functional (기능 요구사항)**
* **FR1**: 사용자는 `login` 도구를 통해 Microsoft 회사 계정으로 OAuth 2.0 방식의 인증을 수행할 수 있어야 한다.
* **FR2**: `login` 도구는 인증 성공 시, 해당 사용자의 Azure 권한을 조회할 수 있는 AZEBAL 전용 액세스 토큰을 발급해야 한다.
* **FR3**: 사용자는 유효한 액세스 토큰과 에러 요약 정보를 포함하여 `debug_error` 도구를 호출할 수 있어야 한다.
* **FR4**: 시스템은 `debug_error` 요청 시 전달된 에러 메시지를 분석하여, 디버깅에 필요할 것으로 예상되는 소스코드 파일 범위를 사용자에게 제안하고 확인받을 수 있어야 한다.
* **FR5**: 시스템은 사용자의 권한을 기반으로 Azure API를 호출하여, 에러와 관련된 Azure 리소스의 실시간 상태 정보를 수집할 수 있어야 한다.
* **FR6**: 시스템은 수집된 모든 정보(사용자 컨텍스트, 실시간 리소스 상태)를 종합적으로 분석하여, 예상되는 에러 원인과 그 근거를 포함한 응답을 생성해야 한다.

#### **2.2 Non Functional (비기능 요구사항)**
* **NFR1 (성능)**: `debug_error` 요청에 대한 최종 응답까지의 평균 소요 시간은 5분 이내여야 한다.
* **NFR2 (보안)**: 로그인 API를 제외한 모든 API 엔드포인트는 유효한 액세스 토큰을 통해서만 접근할 수 있어야 하며, 모든 데이터는 사용자의 RBAC 정책에 따라 필터링되어야 한다.
* **NFR3 (인프라)**: 시스템은 KT 사내망의 ZTNA 보안 환경 내에서 안정적으로 운영되어야 한다.
* **NFR4 (호환성)**: MCP 서버는 IDE AI 에이전트와의 원활한 통신을 위해 stdio 및 SSE(Server-Sent Events) 프로토콜을 모두 지원해야 한다.
* **NFR5 (개발)**: 시스템의 백엔드는 Python 언어와 FastMCP 라이브러리를 사용하여 구현해야 한다.

---

### **## 3. Technical Assumptions (기술적 가정)**

#### **3.1 Repository Structure (리포지토리 구조)**
* **Monorepo**: AZEBAL 서버와 모든 관련 도구들은 **단일 리포지토리(Monorepo) 내에서 통합 관리**합니다. 이는 초기 개발 단계에서 코드 공유, 종속성 관리, 그리고 통합 빌드/배포를 용이하게 하기 위함입니다.

#### **3.2 Service Architecture (서비스 아키텍처)**
* **Monolithic**: 초기 MVP 단계에서는 빠른 개발과 배포 단순성을 위해, 모든 핵심 기능을 단일 애플리케이션으로 구현하는 **모놀리식(Monolithic) 아키텍처**를 채택합니다. 향후 시스템이 복잡해지고 기능이 확장됨에 따라, 각 도메인을 마이크로서비스로 분리하는 것을 고려할 수 있습니다.

#### **3.3 Testing Requirements (테스트 요구사항)**
* **Unit + Integration**: 모든 핵심 비즈니스 로직(인증, API 호출, 데이터 분석 등)에 대해서는 개별 기능을 검증하는 **단위 테스트(Unit Test)**와, 각 마이크로서비스 간의 연동을 확인하는 **통합 테스트(Integration Test)**를 모두 작성하는 것을 목표로 합니다.
* **Local Testing**: 개발자의 로컬 환경에서는 실제 Azure DB 대신 파일 기반의 임시 DB를 사용하여 빠르고 격리된 테스트가 가능해야 합니다.

---

### **## 4. Epic List (에픽 목록)**

AZEBAL MVP 개발은 기술적 의존성과 가치 전달 단계를 고려하여 두 개의 순차적인 에픽으로 구성합니다.

* **Epic 1: 보안 인증 및 Azure 세션 기반 구축**
    * **목표 (Goal)**: 사용자가 IDE 내에서 MS 계정으로 안전하게 AZEBAL에 인증하고, 이 인증 정보를 바탕으로 AZEBAL이 사용자를 대신하여 Azure API를 성공적으로 호출할 수 있는 기술적 기반을 완벽하게 구축한다.

* **Epic 2: 실시간 에러 분석 엔진 구현**
    * **목표 (Goal)**: Epic 1에서 구축된 인증 기반 위에, 실제 사용자의 에러를 해결해주는 `debug_error` 도구의 핵심 분석 기능을 구현한다.

---

### **## 5. Epic 1: 보안 인증 및 Azure 세션 기반 구축**

> **에픽 목표**: 사용자가 IDE 내에서 MS 계정으로 안전하게 AZEBAL에 인증하고, 이 인증 정보를 바탕으로 AZEBAL이 사용자를 대신하여 Azure API를 성공적으로 호출할 수 있는 기술적 기반을 완벽하게 구축합니다. 이 에픽의 완료는 프로젝트의 가장 큰 기술적 리스크인 '인증 및 권한 연동' 문제를 해결했음을 의미합니다.

#### **Story 1.1: MS 계정을 통한 AZEBAL 로그인**
* **As a** KT 개발자,
* **I want** to log in to AZEBAL using my Microsoft company account via a `login` tool,
* **so that** I can securely prove my identity without creating or managing a separate password.

**Acceptance Criteria (완료 조건):**
1.  사용자가 IDE에서 `login` 도구를 호출하면, AZEBAL 서버가 생성한 유효한 Microsoft 로그인 URL을 응답으로 받는다.
2.  사용자가 해당 URL을 통해 MS 계정 로그인을 성공적으로 완료하면, 브라우저를 통해 AZEBAL 서버로 인증 코드가 전달된다.
3.  AZEBAL 서버는 인증 코드를 사용하여 MS로부터 액세스 토큰을 성공적으로 발급받는다.
4.  전체 프로세스가 완료되면, 사용자는 IDE에서 "로그인 성공" 메시지를 확인한다.

#### **Story 1.2: AZEBAL 전용 액세스 토큰 발급**
* **As an** AZEBAL system,
* **I want** to issue a secure, short-lived AZEBAL-specific access token after a user successfully authenticates,
* **so that** I can manage user sessions and securely verify their identity for subsequent API calls.

**Acceptance Criteria (완료 조건):**
1.  사용자의 MS 계정 인증이 성공하면, AZEBAL 서버는 해당 사용자의 식별 정보가 포함된 자체 액세스 토큰(JWT 등)을 생성한다.
2.  생성된 토큰은 사용자에게 안전하게 전달된다.
3.  서버는 발급된 토큰의 유효성을 검증할 수 있는 메커니즘을 갖춘다.

#### **Story 1.3: 토큰을 이용한 Azure 사용자 권한 확인**
* **As an** AZEBAL system,
* **I want** to use the user's Microsoft authentication to fetch their basic Azure roles and permissions,
* **so that** I can verify the entire authentication chain works and prepare for providing permission-based responses in the future.

**Acceptance Criteria (완료 조건):**
1.  AZEBAL 서버는 사용자의 유효한 토큰을 사용하여, 해당 사용자의 Azure 구독 목록 또는 기본 역할 정보를 조회하는 API를 성공적으로 호출한다.
2.  API 호출 결과가 성공적으로 수신되고 파싱된다.
3.  유효하지 않은 토큰으로 API 호출 시, 예상된 인증 에러가 발생한다.

---

### **## 6. Epic 2: 실시간 에러 분석 엔진 구현**

> **에픽 목표**: Epic 1에서 구축된 인증 기반 위에, IDE AI 에이전트로부터 단일 요청을 받아 자율적으로 에러를 분석하고, 완전한 해결책을 단일 응답으로 제공하는 `debug_error` 도구를 구현한다.

#### **Story 2.1: `debug_error` API 엔드포인트 구현**
* **As an** IDE AI Agent,
* **I want** to call a single `debug_error` endpoint with all necessary context (error info, source code, auth token),
* **so that** I can get a complete debugging analysis in one transaction without multiple interactions.

**Acceptance Criteria (완료 조건):**
1.  AZEBAL 서버에 `debug_error`를 위한 API 엔드포인트가 존재한다.
2.  해당 엔드포인트는 `access_token`, `error_summary`, `extra_source_code` 파라미터를 정상적으로 수신하고 유효성을 검사한다.
3.  유효하지 않은 AZEBAL 액세스 토큰으로 요청 시, 401 Unauthorized 에러를 반환한다.

#### **Story 2.2: 자율적인 컨텍스트 기반 리소스 분석 수행**
* **As an** AZEBAL system,
* **I want** to autonomously perform a series of analysis steps (like multiple Azure API calls) based on the initial context provided,
* **so that** I can gather all necessary data for a diagnosis without asking the user for more information.

**Acceptance Criteria (완료 조건):**
1.  `debug_error` 요청 수신 시, 분석 프로세스 시작을 나타내는 **고유한 'trace_id'를 생성하고 로그에 기록한다.**
2.  분석을 시작하기 전에, 조사할 Azure 리소스 타입과 이름의 목록(**분석 계획**)을 로그에 기록한다. (예: `PLANNING - Check ACR 'myAcrRepo'`, `PLANNING - Check AppContainer 'myApp' status`)
3.  분석 계획에 따라 Azure API를 호출할 때마다, 어떤 리소스를 대상으로 어떤 정보를 조회했는지에 대한 **구체적인 내용을 로그에 기록한다.** (예: `CALLING - Get ACR 'myAcrRepo' permissions`)
4.  Azure API 호출로부터 **성공적으로 데이터를 수집했거나, 또는 예상된 에러(예: 403 Forbidden)를 수신했음을 로그에 기록한다.**
5.  이 모든 과정은 최초 요청 이후 **어떠한 추가적인 사용자 상호작용 없이** 완료되어야 한다.

#### **Story 2.3: 종합적인 분석 보고서 생성 및 단일 응답**
* **As a** KT 개발자,
* **I want** to receive a single, comprehensive response from `debug_error` that includes the analysis results, debugging process, and a clear, actionable solution,
* **so that** my IDE AI agent can interpret it and help me fix the problem immediately.

**Acceptance Criteria (완료 조건):**
1.  AZEBAL의 최종 응답은 단일 API 응답으로 전달된다.
2.  응답 내용은 "분석 결과", "디버깅 과정", "조치해야 할 내용"의 명확한 구조를 가진다.
3.  "조치해야 할 내용"은 사람이 이해하기 쉬우면서도, IDE AI 에이전트(Cursor)가 해석하여 코드 수정 제안과 같은 후속 조치를 취하기에 적합한 평문으로 작성된다. (예: "ACR 권한 확인 결과, value.yaml의 이미지 경로가 Azure의 실제 리포지토리 이름과 일치하지 않으므로 수정이 필요합니다.")

---

### **## 7. Checklist Results Report (체크리스트 결과 보고서)**

**Executive Summary:**
본 AZEBAL PRD는 PM 체크리스트 검토 결과, **전반적인 완성도가 매우 높으며 (Overall Readiness: High)**, MVP 범위가 명확하고 요구사항이 구체적이어서 다음 단계인 아키텍처 설계를 시작하기에 **준비됨(Ready)**으로 판단됩니다. 몇 가지 사소한 보완점이 식별되었으나, 아키텍처 설계 과정에서 충분히 논의 및 구체화가 가능합니다.

**Category Analysis Table:**

| Category | Status | Critical Issues |
| :--- | :--- | :--- |
| 1. Problem Definition & Context | ✅ PASS | 없음 |
| 2. MVP Scope Definition | ✅ PASS | 없음 |
| 3. User Experience Requirements | N/A | GUI가 없는 백엔드 서비스이므로 해당 없음 |
| 4. Functional Requirements | ✅ PASS | 없음 |
| 5. Non-Functional Requirements | ⚠️ PARTIAL | 안정성(Reliability) 요구사항이 명시적으로 기술되지 않음 |
| 6. Epic & Story Structure | ✅ PASS | 없음 |
| 7. Technical Guidance | ⚠️ PARTIAL | 주요 기술 결정에 대한 대안 및 상세 근거(Rationale) 보강 필요 |
| 8. Cross-Functional Requirements | ✅ PASS | 없음 |
| 9. Clarity & Communication | ✅ PASS | 없음 |

**Critical Deficiencies:**
* 없음.

**Recommendations:**
* **Should-fix**: 아키텍처 설계 단계에서 안정성(예: 장애 복구, 재시도 정책)에 대한 구체적인 요구사항과, 모놀리식 구조 채택과 같은 주요 기술 결정에 대한 대안 분석 및 상세 근거를 아키텍처 문서에 명확히 기술할 것을 권장합니다.

**Final Decision:**
* **READY FOR ARCHITECT**: 본 PRD는 아키텍처 설계를 시작하기에 충분한 정보를 담고 있습니다.

---

### **## 8. Next Steps (다음 단계)**

#### **Architect Prompt (아키텍트에게 전달)**
> 안녕하세요, 아키텍트(Winston).
>
> AZEBAL 프로젝트의 최종 제품 요구사항 명세서(PRD)가 완성되었습니다. 이 문서를 기반으로, MVP 구현을 위한 상세 기술 아키텍처 설계를 시작해주십시오.
>
> PRD에 명시된 기능/비기능 요구사항과 기술적 가정(모노레포, 모놀리식)을 반드시 준수하여, 안정적이고 확장 가능한 시스템을 설계해주시기 바랍니다. 특히, Azure API 연동 시 발생할 수 있는 성능 및 비용 문제에 대한 고려와, 강력한 보안 체계 구축에 집중해주십시오.