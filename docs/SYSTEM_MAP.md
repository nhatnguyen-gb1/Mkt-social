# AIMOS Master System Map & Module Architecture (Self-Contained Architecture)

Tài liệu **SYSTEM MAP (Bản Đồ Hệ Thống Tổng Thể)** mô tả kiến trúc độc lập hoàn toàn (**100% Self-Contained**) của hệ thống **AIMOS (AI Marketing Operating System)** từ Phase 1 đến Phase 8.

> 🛡️ **ARCHITECTURAL GUARANTEE**: AIMOS **KHÔNG** phụ thuộc, **KHÔNG** yêu cầu và **KHÔNG** sử dụng n8n làm middleware, job queue hay automation engine. Hệ thống tự vận hành 100% native qua FastAPI, Worker Loop, Telegram Adapter và Native Agents.

---

## 🗺️ 1. AIMOS MASTER FLOWCHART (SƠ ĐỒ LUỒNG DỮ LIỆU NATIVE)

```
                       ┌─────────────────────────┐
                       │   USER (Marketer / CMO) │
                       └────────────┬────────────┘
                                    │
           ┌────────────────────────┴────────────────────────┐
           ▼                                                 ▼
┌───────────────────────────┐                   ┌───────────────────────────┐
│   Telegram Control Bot    │                   │   REST API (Swagger UI)   │
│  (Auth Guard & Commands)  │                   │  (/api/v1/workflows/run)  │
└──────────┬────────────────┘                   └──────────┬────────────────┘
           │                                               │
           └────────────────────────┬──────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │       AIMOS CORE ENGINE       │
                    │ (FastAPI App / Safety Engine) │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   WORKFLOW ENGINE / JOB LOOP  │
                    │  (Multi-Agent Orchestrator)   │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │             AGENT REGISTRY & LANGGRAPH AGENTS           │
       │  ├── MarketResearchAgent  [REAL]                        │
       │  ├── MarketingStrategyAgent [REAL]                       │
       │  ├── CreativeAgent        [REAL]                        │
       │  ├── AdsAgent            [REAL]                        │
       │  ├── OptimizationAgent   [REAL]                        │
       │  ├── AutomationAgent     [SKELETON]                    │
       │  └── EcommerceAgent      [SKELETON]                    │
       └────────────────────────────┬────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │     CENTRAL TOOL REGISTRY     │
                    │ (Lookup, Image, Ads, Ecom)    │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
    ┌───────────────────────────────────────────────────────────────┐
    │                 MASTER VENDOR PROVIDER REGISTRY               │
    │  ├── LLM: OpenAI, Anthropic, Gemini, Mock LLM                 │
    │  ├── Media: DALL-E 3, Mock Image, Stability [SKELETON]        │
    │  ├── Voice: ElevenLabs [SKELETON], Mock Voice [SKELETON]      │
    │  ├── Search: Google Search / Tavily [SKELETON]                │
    │  ├── Ad Platforms: Meta Ads, TikTok Ads, Mock Sandbox         │
    │  └── E-Commerce: Shopify, TikTok Shop [SKELETON]             │
    └───────────────────────────────┬───────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │    EXECUTION & PERSISTENCE    │
                    │  (PostgreSQL / SQLite ./db)   │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
       ┌────────────────────────────┴───────────────────────────┐
       ▼                                                        ▼
┌───────────────────────────┐                      ┌───────────────────────────┐
│     Central Audit Log     │                      │   Telegram Notification   │
│  (Full Traceability DB)   │                      │  (Approval Requests/Alert)│
└───────────────────────────┘                      └───────────────────────────┘
```

---

## 🧩 2. DANH SÁCH TOÀN BỘ PHÂN HỆ VÀ TRẠNG THÁI HIỆN TẠI

| Phân Hệ / Module | Tên File / Path | Trạng Thái | Mô Tả Chức Năng |
|---|---|---|---|
| **Product Intake** | `app/models/product.py` | **`[REAL]`** | Quản lý sản phẩm, thông số sản phẩm, dữ liệu kinh doanh. |
| **Async Job Loop** | `app/services/worker_service.py` | **`[REAL]`** | Hàng chờ xử lý background, tự động retry khi lỗi. |
| **Telegram Guard** | `app/services/telegram_auth_service.py` | **`[REAL]`** | Phân quyền truy cập Telegram theo danh sách Whitelist ID. |
| **LLM Providers** | `app/core/llm/` | **`[REAL + MOCK]`** | OpenAI GPT, Anthropic Claude, Gemini, Mock LLM Provider. |
| **Media Providers** | `app/core/media/` | **`[REAL + MOCK]`** | OpenAI DALL-E 3 sinh ảnh thật, MockImageGenerator. |
| **Platform Adapters**| `app/core/adapters/` | **`[REAL + MOCK]`** | Meta Graph API, TikTok Marketing API, Mock Sandbox. |
| **Safety Engine** | `app/core/safety/engine.py` | **`[REAL]`** | Kiểm tra hạn mức ngân sách, từ khóa cấm, Human Approval Gate. |
| **Approval Flow** | `app/services/approval_service.py` | **`[REAL]`** | Hàng chờ phê duyệt của Marketer trước khi chi tiền thật. |
| **Analytics Engine**| `app/services/analytics_service.py` | **`[REAL]`** | Thu thập chỉ số và tính toán CTR, CPA, ROAS tự động. |
| **Tool Registry** | `app/core/tools/registry.py` | **`[REAL + SKELETON]`** | Quản lý và cung cấp Tool cho các AI Agent theo nhóm. |
| **Provider Registry**| `app/core/providers/registries.py` | **`[REAL + SKELETON]`** | Bộ đăng ký trừu tượng 7 nhóm Vendor Provider. |
| **Agent Registry** | `app/agents/registry.py` | **`[REAL + SKELETON]`** | Đăng ký và quản lý 7 AI Agent trong hệ thống. |
| **Workflow Engine** | `app/core/workflow/engine.py` | **`[REAL]`** | Điều phối luồng công việc liên hoàn 6 bước khép kín. |
| **E-Commerce API** | `app/api/routes/ecommerce.py` | **`[SKELETON]`** | Điểm nối đồng bộ tồn kho Shopify & TikTok Shop. |
