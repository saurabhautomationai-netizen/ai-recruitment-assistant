# AI Recruitment Assistant (ZERO Recruit)

**An end-to-end Enterprise Autonomous AI Recruitment Platform** — 5-stage interactive candidate Kanban pipeline, resume intelligence parsing, 2D autonomy matrix, job board syndication (75+ boards), staffing agency billing, EEO/OFCCP/GDPR compliance, app marketplace, and automated multi-channel candidate workflows.

Built as a production-grade AI engineering and autonomous recruitment SaaS platform with multi-tenant RBAC, live Supabase synchronization, and Google Stitch design token integration.

---

## 🚀 Live Production Architecture & New Capabilities

```mermaid
flowchart TB
    subgraph Sourcing["1. Autonomous Sourcing & Syndication"]
        A[Job Posting Form] --> B[Job Board Syndication Engine<br/>LinkedIn, Indeed, Naukri, ZipRecruiter]
        B --> C[Public Careers Portal]
        C --> D[Talent Lead Gen Agent<br/>9-Industry Taxonomy]
    end

    subgraph Evaluation["2. AI Evaluation & Candidate Intelligence"]
        E[PDF Resume Ingestion] --> F[Hybrid Stream + Tesseract OCR]
        F --> G[Grounded STAR Rubric Generator<br/>ATS Fit Scoring (0-100%)]
        G --> H[(Supabase: Postgres + pgvector)]
    end

    subgraph Pipeline["3. Interactive Pipeline Management"]
        H --> I[5-Stage Candidate Kanban Board]
        I --> J[Stage Migrations: Shortlisted ➔ Scheduled ➔ Interview ➔ Selected ➔ Rejected]
        I --> K[Deep Resume Inspector Drawer<br/>Skills Match & Domain Benchmarks]
    end

    subgraph Agency["4. Enterprise Staffing & Marketplace"]
        L[Agency Billing & Margin Calculator] --> M[Timesheet Approval & PDF Invoices]
        N[200+ App Marketplace] --> O[DocuSign, Checkr, HackerRank]
        P[Compliance Engine] --> Q[EEO / OFCCP / GDPR Audit Ledgers]
    end
```

---

## 🌟 Key Features & Capabilities

| Feature | Description | Architecture & Design Pattern |
| :--- | :--- | :--- |
| **📋 5-Stage Interactive Candidate Kanban** | Real-time candidate pipeline across **Shortlisted**, **Scheduled for Interview**, **Moved to Interview**, **Selected**, and **Rejected** with 1-click stage transitions. | Reactive Streamlit Kanban, Supabase stage updates, composite element keys, toast feedback. |
| **🔍 Deep AI Resume Intelligence Inspector** | Click any candidate to view **ATS score gauge**, **7-industry domain match %**, structured **executive summary**, matching vs. gap skill badges, and formatted resume viewer. | Structured prompt evaluation, dynamic skill taxonomy, interactive resume downloader. |
| **⚡ 2D Recruitment Autonomy Matrix** | 4-Phase (Sourcing, Screening, Interview, Placement) $	imes$ 3-Tier (Co-Pilot, Agentic, Full Autonomy) interactive command center. | Native `st.html()` responsive grid, status badges, and diagnostic telemetry. |
| **🌐 Massive Job Board Syndication (75+ Boards)** | 1-click syndication to **LinkedIn, Indeed, Naukri.com, ZipRecruiter, Monster, and Glassdoor** with tracking feeds. | RESTful XML/JSON syndication adapter, webhook listeners (`services/job_syndication_service.py`). |
| **💼 Staffing Agency Billing & Invoicing** | Contractor timesheet logging, client bill rates, candidate pay rates, markup margin calculators, and automated PDF invoice generation. | Financial arithmetic engine, timesheet persistence (`services/agency_billing_service.py`). |
| **⚖️ EEO / OFCCP / GDPR Compliance Engine** | Adverse impact calculation, 3-year applicant disposition tracking, immutable audit trails, and 1-click GDPR data purge workflows. | Cryptographic audit logging, compliance record keeper (`services/compliance_service.py`). |
| **🔌 200+ App Marketplace Ecosystem** | Pre-built enterprise connectors for **DocuSign** (offer signing), **Checkr** (background checks), and **HackerRank / Codility** (coding assessments). | Event-driven webhook router (`services/marketplace_integration_service.py`). |
| **🎯 Dynamic 9-Industry Taxonomy** | Specialized assessment criteria across IT, Healthcare, Engineering, HR, BPO, Animation, Finance, Sales, and Legal. | Domain catalog & skill matrix (`services/industry_taxonomy.py`). |
| **🎨 Google Stitch & DESIGN.md Bridge** | Tokenized design standard document for UI/UX sync with Google Stitch and universal MCP servers. | Standardized `DESIGN.md` specification (`mcp_config.json`). |

---

## 🎨 Design System: Executive Forest Green & Pearl White

The user interface follows an **Executive Forest Green** minimalist design language:
- **Primary Brand**: `#162E20` (Forest Green)
- **Canvas / Background**: `#F3F4F1` (Pearl White / Soft Mist)
- **Surface Elevation**: `#FFFFFF` (Crisp White with subtle `1px solid #E8EAE6` borders)
- **Success & ATS Highlights**: `#059669` (Emerald Pulse)
- **Typography**: High-density system typography with high-contrast hierarchical hierarchy.

Full design specifications are maintained in [**`DESIGN.md`**](DESIGN.md).

---

## 🔐 Enterprise Security & Production Hardening

- **AES-256 / Fernet Encryption at Rest (`services/secret_encryption_service.py`):** Automatically encrypts third-party recruiter credentials with SHA-256 key stretching.
- **Anti-XSS & Directory Traversal Sanitizer (`services/sanitization_service.py`):** Strips malicious scripts and neutralizes directory traversal in file uploads.
- **Deterministic Message Idempotency (`services/communication_service.py`):** Cryptographic SHA-256 `Idempotency-Key` headers guarantee zero duplicate notifications on retries.
- **Hybrid Scanned Resume OCR (`services/resume_ocr_service.py`):** Multi-stage PDF parser with `pypdf` text stream extraction and `pytesseract` fallback for scanned resumes.
- **Tiered LLM Resilience Engine (`services/llm_resilience_service.py`):** Multi-model fallback (Gemini Pro ➔ Gemini Flash ➔ 5ms Local Rule Engine) guaranteeing 100% availability.
- **Multi-Tenant RBAC Partitioning (`services/recruiter_partition_service.py`):** Strict data boundary isolation between agency master views and individual recruiter pipelines.

---

## 🧪 Comprehensive Automated Test Suite (76 / 76 Passing - 100%)

The platform is guarded by a comprehensive automated test suite with **76 passed tests**:

```bash
collected 76 items

tests\test_candidate_kanban.py ...                                       [  3%]
tests\test_enterprise_compliance.py ..........                           [ 17%]
tests\test_enterprise_hardening.py .................                     [ 39%]
tests\test_enterprise_real_world.py ..........                           [ 52%]
tests\test_hybrid_interview_and_billing.py .........                     [ 64%]
tests\test_interview_reschedule.py ......                                [ 72%]
tests\test_phase2_features.py ............                               [ 88%]
tests\test_production_features.py ......                                 [ 96%]
tests\test_secure_question_generator.py ...                              [100%]

======================= 76 passed, 3 warnings in 30.84s =======================
```

To run the tests:
```bash
pytest tests -v
```

---

## 📁 Repository Structure

```
ai-recruitment-assistant/
├── DESIGN.md                            # Google Stitch design system & token specification
├── assets/                              # Architecture diagrams & UI screenshots
├── components/                          # Streamlit UI & interactive components
│   ├── candidate_kanban_board.py        # 5-stage interactive candidate Kanban pipeline
│   ├── recruitment_autonomy_matrix.py   # 2D process vs autonomy matrix
│   ├── candidate_card.py                # Candidate profile & stage progression card
│   ├── offer_letter_generator.py        # Branded offer letter generator
│   ├── public_careers_portal.py         # Candidate-facing job application landing page
│   └── self_service_booking.py          # Candidate self-service interview booking
├── services/                            # Core enterprise service layer
│   ├── job_syndication_service.py       # 75+ job board syndication engine
│   ├── agency_billing_service.py        # Timesheets, bill rates, and margin calculators
│   ├── compliance_service.py            # EEO / OFCCP / GDPR regulatory engine
│   ├── marketplace_integration_service.py # 200+ native app marketplace connectors
│   ├── industry_taxonomy.py             # 9-industry skill and role taxonomy
│   ├── secret_encryption_service.py     # AES-256 credential encryption
│   ├── sanitization_service.py          # Anti-XSS input sanitizer
│   ├── communication_service.py         # Multi-channel messaging & idempotency
│   ├── resume_ocr_service.py            # Hybrid PDF stream & scanned OCR parser
│   ├── llm_resilience_service.py        # Tiered multi-model fallback engine
│   ├── supabase_service.py              # Cloud PostgreSQL database adapter
│   └── recruiter_partition_service.py   # Multi-tenant RBAC isolation
├── tests/                               # Comprehensive Automated Test Suite (76 Tests)
├── app.py                               # Streamlit enterprise dashboard entry point
├── requirements.txt                     # Production dependencies
└── README.md                            # Executive documentation & architecture specs
```

---

*Engineered by Saurabh Shinde — Enterprise-Grade Autonomous AI Recruitment & Talent Operations SaaS.*
