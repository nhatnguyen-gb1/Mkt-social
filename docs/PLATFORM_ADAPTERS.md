# AIMOS Phase 5: Platform Adapters & Campaign Management Documentation

## Overview

Phase 5 of **AIMOS** introduces the **Platform Adapters & Campaign Management Skeleton**, establishing the structural foundation for creating, managing, and publishing digital advertising campaigns on Meta Ads (Facebook/Instagram) and TikTok Ads.

---

## Key Architecture & Components

```
[ Product / Strategy / Creative Assets (Phase 1-4) ]
                          │
                          ▼
            [ AdsAgent (LangGraph Agent) ] ──────────► Tự động lập Cấu trúc Chiến dịch
                          │
                          ▼
    [ Campaign & AdSet & Ad Domain Entities ] ──────► Database Models (Draft State)
                          │
                          ▼
    [ Platform Adapter Abstraction Layer ] ─────────► Abstraction Interface
     ├──► MetaAdsAdapter (Facebook Graph API)
     ├──► TikTokAdsAdapter (TikTok Marketing API)
     └──► MockPlatformAdapter (Sandbox mode 0đ chi phí)
```

---

## Component Breakdown

### 1. Platform Adapter Abstraction Layer
- **Interface**: `BasePlatformAdapter` in `app/core/adapters/base.py`
- **Adapters**:
  - `MockPlatformAdapter`: Generates mock external IDs for Meta and TikTok for zero-cost sandbox testing.
  - `MetaAdsAdapter`: Integrates with Meta Graph API v19.0 (`https://graph.facebook.com/v19.0/`). Requires `META_MARKETING_API_TOKEN` and `META_AD_ACCOUNT_ID`.
  - `TikTokAdsAdapter`: Integrates with TikTok Marketing API v1.3 (`https://business-api.tiktok.com/open_api/v1.3/`). Requires `TIKTOK_MARKETING_API_TOKEN`.
- **Factory**: `PlatformAdapterFactory` dynamically selects Meta, TikTok, or Mock adapters with automatic fallback.

### 2. AdsAgent (AI Agent Lập Cấu Trúc Quảng Cáo)
- **Purpose**: Transforms product details, budget allocation, and marketing hooks into optimized campaign parameters, targeting criteria (age, gender, interests), and ad copy.
- **Endpoint**: `POST /api/v1/agents/ads`

### 3. Campaign & AdSet & Ad Entities
- **Models**:
  - `Campaign`: `id`, `product_id`, `name`, `platform`, `objective`, `daily_budget`, `status`, `external_campaign_id`.
  - `AdSet`: `id`, `campaign_id`, `name`, `targeting`, `daily_budget`, `status`, `external_adset_id`.
  - `Ad`: `id`, `ad_set_id`, `asset_id`, `name`, `headline`, `primary_text`, `call_to_action`, `status`, `external_ad_id`.
- **Endpoints**:
  - `POST /api/v1/campaigns`: Create campaign draft in DB.
  - `POST /api/v1/campaigns/{id}/publish`: Publish campaign to platform API/Sandbox.
  - `GET /api/v1/campaigns`: List campaigns.
  - `GET /api/v1/campaigns/{id}`: Get campaign details.

---

## Modules Status (Real vs Mock/Skeleton)

| Module | Status | Notes |
|---|---|---|
| **Product CRUD & DB** | **REAL** | PostgreSQL / SQLite local database |
| **Telegram Control Bot** | **REAL** | Telegram Bot API + Auth whitelist |
| **Async Job Worker** | **REAL** | Background polling loop & retry logic |
| **LLM Provider Abstraction** | **REAL + MOCK** | OpenAI, Anthropic, Gemini (Real) & Mock LLM (Fallback) |
| **Media Generator Provider** | **REAL + MOCK** | DALL-E 3 (Real) & MockImageGenerator (Fallback) |
| **Platform Adapters (Meta/TikTok)** | **REAL + MOCK** | Graph API & TikTok API (Real) & Mock Sandbox (Fallback) |
| **Campaign & Ad Structure** | **REAL** | Full DB persistence & API endpoints |

---

## Running Standalone Local Backend

```powershell
cd C:\Users\MSi\.gemini\antigravity\scratch\aimos\backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```
Swagger UI Docs: `http://localhost:8000/docs`
