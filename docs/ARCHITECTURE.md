# Architecture Documentation: AIMOS

## 1. Architectural Strategy: Modular Monolith

AIMOS is structured as a **Modular Monolith**. This decision balances low operational overhead during early growth with clean, decoupled internal boundaries that permit extracting microservices in the future if scale requires.

### Core Architectural Layers & Dependency Direction

```
   [ API Layer ] (Routes, Controllers, OpenAPI Schemas)
         │
         ▼
[ Service Layer ] (Business Logic, Policy Enforcements, Audit Hooks)
         │
         ▼
[ Repository Layer ] (Data Access Objects, Generic Async Queries)
         │
         ▼
[ Domain Models & Database ] (SQLAlchemy ORM Entities, Postgres DB)
```

**Rule of Dependency**: Higher-level modules depend on lower-level abstractions. Outer layers (e.g., API routes, Telegram bot controllers) MUST NOT directly access database models or external APIs; all operations pass through business Services and Adapter interfaces.

---

## 2. Component Design & Abstraction Layers

### 2.1 Provider Abstraction Engine (LLMs)
Agents and tools do NOT import provider-specific SDKs (e.g., `openai` or `anthropic`) directly. A unified LLM Adapter interface provides modelagnostic generation:

```
                  ┌───────────────────────┐
                  │   Unified LLM Client  │
                  └───────────┬───────────┘
                              │
            ┌─────────────────┴─────────────────┐
            ▼                                   ▼
┌───────────────────────┐           ┌───────────────────────┐
│ OpenAI Provider       │           │ Anthropic Provider    │
└───────────────────────┘           └───────────────────────┘
```

### 2.2 Integration Adapters (Meta / TikTok Ads)
All ad network integrations implement a strict Adapter contract:
- `create_campaign_draft()`
- `fetch_campaign_insights()`
- `request_budget_adjustment()` (Sends request to Approval Engine, never direct API execution)

### 2.3 Future Agent Architecture (LangGraph Integration)
- Agents run state machine workflows via LangGraph.
- Agents operate in read/recommend mode only.
- Agents call internal services/tools—they DO NOT possess external API credentials.

---

## 3. Financial Safety & Human-in-the-Loop Workflow

```
[ AI Recommendation Agent ]
             │
             ▼
    [ Policy Engine Check ]  ────── (Rejects if budget threshold or rule broken)
             │
             ▼
    [ Human Approval Engine ] ──── (Notifies Admin via Telegram / Web UI)
             │
             ▼ (Approved by Human)
    [ Internal Execution Tool ] ─── (Executes via Platform Adapter)
             │
             ▼
     [ Immutable Audit Log ]
```

---

## 4. Audit Trail Architecture

Every domain mutation (`Product` create/update/delete, `Job` creation, `Approval` state change) triggers an explicit `AuditService` call within the business transaction. Audit entries record actor, target entity, before/after JSON payloads, and timestamps.
