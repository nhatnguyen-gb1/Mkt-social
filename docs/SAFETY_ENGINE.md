# AIMOS Phase 6: Safety Engine & Human-in-the-Loop Documentation

## Overview

Phase 6 of **AIMOS** introduces the **Safety Engine & Human-in-the-Loop Approval Workflow**, establishing strict financial safeguards and content policies to guarantee that AI Agents **never execute direct, unapproved ad spending or publish policy-violating ad content**.

---

## Core Operational Workflow

```
[ Campaign Publish Request ]
            │
            ▼
 [ PolicyEngine Evaluation ] ────► Check rules (MAX_DAILY_BUDGET, RESTRICTED_KEYWORDS)
  ├── Violated ──────────────────► HTTP 400 Bad Request + Audit Log (CAMPAIGN_BLOCKED_BY_POLICY)
  └── Requires Approval ─────────► Status: PENDING_APPROVAL + Create ApprovalRequest
            │
            ▼
[ Human Marketer Approval Gate ]
  ├── Human Approves ────────────► Status: ACTIVE + Publish to Meta/TikTok API/Sandbox
  └── Human Rejects ─────────────► Status: REJECTED + Audit Log (HUMAN_REJECTED)
```

---

## Component Breakdown

### 1. Policy Engine & Policy Rules
- **Engine**: `PolicyEngine` in `app/core/safety/engine.py`
- **Supported Rule Types**:
  - `MAX_DAILY_BUDGET`: Caps daily budget per campaign (e.g. max $500/day).
  - `RESTRICTED_KEYWORDS`: Scans campaign names, headlines, and primary texts for blacklisted words.
  - `REQUIRE_APPROVAL_FOR_PUBLISH`: Enforces mandatory human marketer sign-off.
- **Endpoints**:
  - `POST /api/v1/safety/rules`: Create/update policy rules.
  - `GET /api/v1/safety/rules`: List active policy rules.

### 2. Human-in-the-Loop Approval Workflow
- **Models**: `ApprovalRequest` (`id`, `campaign_id`, `requested_action`, `requested_by`, `status`, `rejection_reason`, `reviewed_by`, `reviewed_at`).
- **Endpoints**:
  - `GET /api/v1/approvals`: List pending approval requests.
  - `POST /api/v1/approvals/{id}/approve`: Marketer approves request (triggers campaign publish).
  - `POST /api/v1/approvals/{id}/reject`: Marketer rejects request with reason.

---

## Running Standalone Local Backend

```powershell
cd C:\Users\MSi\.gemini\antigravity\scratch\aimos\backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```
Swagger UI Documentation: `http://localhost:8000/docs`
