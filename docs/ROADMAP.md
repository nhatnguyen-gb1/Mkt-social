# AIMOS Master Roadmap

Tài liệu Lộ trình phát triển **AIMOS (AI Marketing Operating System)** từ nền móng ban đầu đến hoàn thiện bộ sườn và chuẩn bị sản phẩm thương mại.

---

## 📌 PHÂN THỜI KỲ TRIỂN KHAI

### Phase 1: Foundation Layer `[HOÀN THÀNH]`
- Setup FastAPI Core, PostgreSQL / SQLite async engine, Alembic Migrations.
- Product CRUD (`products`), Async Job Model (`jobs`), Central Audit Logging (`audit_logs`).

### Phase 2: Telegram Control Bot & Async Orchestration `[HOÀN THÀNH]`
- Telegram Bot Client & Whitelist Security Guard (`telegram_users`).
- Background Worker Loop với chiến lược retry 3 lần.
- n8n Webhook Endpoint cho tích hợp ngoài.

### Phase 3: Multi-Agent Core & LLM Provider Abstraction `[HOÀN THÀNH]`
- LLM Provider Abstraction: `OpenAIProvider`, `AnthropicProvider`, `GeminiProvider`, `MockLLMProvider`.
- LangGraph Agent Architecture & `MarketResearchAgent`.

### Phase 4: Creative Pipeline & Asset Management `[HOÀN THÀNH]`
- Media Generator Provider Abstraction: `OpenAIImageGenerator` (DALL-E 3) & `MockImageGenerator`.
- `MarketingStrategyAgent` & `CreativeAgent`.
- Model `Asset` & Asset persistence APIs (`POST /assets/generate-image`).

### Phase 5: Platform Adapters & Campaign Management `[HOÀN THÀNH]`
- Platform Adapters: `MetaAdsAdapter`, `TikTokAdsAdapter`, `MockPlatformAdapter` (Sandbox 0đ).
- Models: `Campaign`, `AdSet`, `Ad` và APIs quản lý chiến dịch nháp.
- `AdsAgent`: Tự động lập thông số nhắm mục tiêu (Targeting) và cấu trúc chiến dịch.

### Phase 6: Safety Engine & Human-in-the-Loop Workflow `[HOÀN THÀNH]`
- `PolicyEngine`: Hạn mức ngân sách (`MAX_DAILY_BUDGET`), Quét từ khóa cấm (`RESTRICTED_KEYWORDS`).
- `ApprovalRequest` Workflow: Khóa chiến dịch rủi ro và giải phóng khi con người (Marketer) duyệt.

### Phase 7: Analytics & Automated Optimization Engine `[HOÀN THÀNH]`
- `CampaignMetric` Model: Lưu lịch sử chỉ số (Impressions, Clicks, Spend, Conversions).
- `AnalyticsService`: Tự động tính toán CTR, CPA, ROAS.
- `OptimizationAgent`: Đề xuất tăng ngân sách (`SCALE_BUDGET`), tắt ad kém (`PAUSE_AD`), làm mới ảnh (`REFRESH_CREATIVE`).

### Phase 8: Master Architecture Consolidation & Registries `[HOÀN THÀNH]`
- Consolidated Registries: `ToolRegistry`, `MasterProviderRegistry`, `AgentRegistry`.
- `WorkflowEngine`: Điều phối E2E Multi-Agent Marketing Lifecycle Pipeline (6 bước).
- Sơ đồ Master System Map (`docs/SYSTEM_MAP.md`).
- Skeleton Endpoints: E-commerce, Automation Tools.

---

## 🔮 CÁC PHASE TIẾP THEO (TƯƠNG LAI)

### Phase 9: Web UI Dashboard (Frontend)
- Next.js + TypeScript + TailwindCSS Control Center.
- Giao diện kéo thả Workflow, Bảng điều khiển Approval Center, Trực quan hóa Analytics.

### Phase 10: Native E-Commerce & Production Hardening
- Kết nối API thật cho Shopify & TikTok Shop catalog sync.
- Tối ưu hiệu năng, Rate Limiting, CI/CD Deployment.
