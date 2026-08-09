# Product Requirement Document (PRD): AIMOS

## 1. Product Vision & Goals

**AIMOS** (AI Marketing Operating System) is an enterprise-ready, multi-agent artificial intelligence system designed to manage and scale digital marketing campaigns across channels (Meta Ads, TikTok Ads, Google, Shopify).

### Core Operational Workflow
```
Product Intake
  └── Market & Competitor Research (AI Agent)
      └── Marketing Strategy Formulation (AI Agent)
          └── Creative Strategy & Asset Generation (AI Image/Video Generation)
              └── Human Approval Gate 1 (Strategy & Creative Review)
                  └── Ad Campaign Setup & Launch (Platform Adapters)
                      └── Performance Data Ingestion & Analytics
                          └── Optimization Recommendation Generation (AI Engine)
                              └── Human Approval Gate 2 / Policy Engine Check
                                  └── Controlled Ad Campaign Optimization
```

---

## 2. Key Architecture Principles & Safety Constraints

1. **Human-in-the-Loop Financial Control**: The AI agent **NEVER** has direct, unrestricted access to ad spending. Every financial mutation (budget updates, campaign publish, campaign deletion) requires passing through a Policy Engine and explicit Human Approval.
2. **Modular Monolith First**: Avoid premature microservices complexity; start as a cleanly separated modular monolith.
3. **Provider & Platform Abstraction**: External ad platforms (Meta, TikTok), LLMs (OpenAI, Anthropic), and media generators (ComfyUI, Midjourney) must be isolated behind strict adapter interfaces.
4. **Database as Truth**: All domain states, job runs, and agent recommendations are stored in PostgreSQL before execution.
5. **Full Auditability**: Immutable audit logs capture actor identity, action type, before/after states, and execution status.

---

## 3. System Roadmap (Phases)

| Phase | Description | Status |
|---|---|---|
| **Phase 1** | Foundation: FastAPI, PostgreSQL, SQLAlchemy 2.0, Alembic, Docker Compose, Product CRUD, Job model, Audit Logging, Pytest suite | **Completed** |
| **Phase 2** | Orchestration & Messaging: Telegram Bot API integration, Async Job Execution, Native Worker Loop | **Completed** |
| **Phase 3** | Multi-Agent Core: LangGraph Research & Strategy Agents, LLM Provider Abstraction layer | Planned |
| **Phase 4** | Creative Pipeline: ComfyUI / Image & Video generation pipelines, Asset Management | Planned |
| **Phase 5** | Platform Adapters: Meta Marketing API & TikTok Marketing API sandbox integration | Planned |
| **Phase 6** | Safety Engine: Policy Engine, Human-in-the-loop approval workflow, Financial safeguards | Planned |
| **Phase 7** | Frontend Dashboard: Next.js + TypeScript Web UI & Analytics Dashboard | Planned |
