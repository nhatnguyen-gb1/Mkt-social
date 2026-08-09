# AIMOS Phase 7: Analytics & Optimization Engine Documentation

## Overview

Phase 7 of **AIMOS** introduces the **Analytics & Automated Optimization Engine**, completing the closed-loop AI marketing lifecycle (Research $\rightarrow$ Strategy $\rightarrow$ Creative $\rightarrow$ Campaign $\rightarrow$ Safety $\rightarrow$ **Analytics & Optimization**).

---

## Architecture & Workflow

```
[ Platform Adapters (Meta Graph API / TikTok API / Sandbox) ]
                               │
                               ▼
        [ AnalyticsService (Metrics Sync Engine) ] ──────► Records snapshots in campaign_metrics
                               │
                               ▼
       [ OptimizationAgent (LangGraph AI Agent) ] ───────► Evaluates Target CPA, CTR, ROAS
                               │
                               ▼
     [ Recommended Actions: SCALE_BUDGET, PAUSE_AD ] ─────► Requires Human Approval Gate (Phase 6)
```

---

## Component Breakdown

### 1. Analytics & Metrics Persistence
- **Model**: `CampaignMetric` in `app/models/analytics.py`
- **Fields**: `campaign_id`, `platform`, `recorded_at`, `impressions`, `clicks`, `spend_usd`, `conversions`, `ctr`, `cpa_usd`, `roas`.
- **Endpoints**:
  - `POST /api/v1/analytics/sync/{campaign_id}`: Sync performance metrics from Meta/TikTok API or Sandbox.
  - `GET /api/v1/analytics/campaigns/{campaign_id}`: Retrieve aggregated summary & history.

### 2. Optimization Agent (`OptimizationAgent`)
- **Purpose**: Evaluates campaign performance metrics against target KPIs and generates actionable optimization proposals:
  - `SCALE_BUDGET`: Scale daily budget for high ROAS campaigns (+20%).
  - `PAUSE_AD`: Pause underperforming ads exceeding target CPA.
  - `REFRESH_CREATIVE`: Recommend new visual prompts when ad fatigue is detected.
- **Endpoint**: `POST /api/v1/agents/optimization`

---

## Running Standalone Local Backend

```powershell
cd C:\Users\MSi\.gemini\antigravity\scratch\aimos\backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```
Swagger UI Documentation: `http://localhost:8000/docs`
