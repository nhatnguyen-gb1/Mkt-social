# AIMOS — AI Marketing Operating System

AIMOS is a production-oriented, multi-agent AI Marketing Operating System designed to automate and optimize the end-to-end marketing life cycle—from product research and strategy generation to creative asset production, ad deployment, performance monitoring, and human-guided campaign management.

---

## 🎯 Current Scope (Phase 8 Consolidated Master Architecture & Registries)

Phase 8 completes the **Master System Architecture, Central Registries (Tools, Providers, Agents), Workflow Engine, and Full System Skeleton** for AIMOS.

### Included in Phase 8:
- **FastAPI Core Backend** (Python 3.12+) with SQLite local fallback and PostgreSQL support
- **Telegram Control Bot & Authorization Guard**
- **Async Job Orchestration & Worker Loop**
- **LLM Provider Abstraction & Registry** (`OpenAIProvider`, `AnthropicProvider`, `GeminiProvider`, `MockLLMProvider`)
- **Media Provider Abstraction & Registry** (`OpenAIImageGenerator`, `MockImageGenerator`, `MediaGeneratorFactory`)
- **Ad Platform Adapters & Registry**: `MetaAdsAdapter`, `TikTokAdsAdapter`, `MockPlatformAdapter`
- **Central Tool Registry**: `ToolRegistry` (`RESEARCH`, `MARKETING`, `ADS`, `ECOMMERCE`, `CONTENT`, `AUTOMATION`, `ANALYTICS`)
- **Central Agent Registry**: `AgentRegistry` (`MarketResearchAgent`, `MarketingStrategyAgent`, `CreativeAgent`, `AdsAgent`, `OptimizationAgent`, `AutomationAgent` [SKELETON], `EcommerceAgent` [SKELETON])
- **Master Workflow Engine**: `WorkflowEngine` (`POST /api/v1/workflows/run` executing E2E 6-step marketing lifecycle)
- **Domain Persistence**: `Product`, `Asset`, `Campaign`, `AdSet`, `Ad`, `PolicyRule`, `ApprovalRequest`, `CampaignMetric` database models & APIs
- **Safety & Policy Engine**: `PolicyEngine` (budget caps, restricted keywords, human approval requirement)
- **Analytics & Metrics Sync**: `AnalyticsService` (`POST /analytics/sync/{campaign_id}`, `GET /analytics/campaigns/{campaign_id}`)
- **Master System Map**: Complete architectural data flow diagram in [`docs/SYSTEM_MAP.md`](docs/SYSTEM_MAP.md)
- **Automated Test Suite**: 46/46 tests passing without requiring paid API keys

---

## 🚀 Quick Start

### 1. Running Standalone (Local Development)

```bash
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
# Swagger Docs: http://localhost:8000/docs
```

### 2. Running with Docker Compose

```bash
cp .env.example .env
docker compose up --build -d
# Health check: http://localhost:8000/health
# Swagger Docs: http://localhost:8000/docs
```

---

## 📚 Documentation

- 🗺️ [SYSTEM_MAP — Master System Map & Flowchart](docs/SYSTEM_MAP.md)
- 📄 [PRD — Product Vision & Specs](docs/PRD.md)
- 🗺️ [ROADMAP — Multi-Phase Development Roadmap](docs/ROADMAP.md)
- 🏗️ [ARCHITECTURE — System Design & Principles](docs/ARCHITECTURE.md)
- 🗄️ [DATABASE — Data Models & Schemas](docs/DATABASE.md)
- 🤖 [AI_CORE — LLM Provider & Agent Framework](docs/AI_CORE.md)
- 🎨 [CREATIVE_PIPELINE — Creative Pipeline & Assets](docs/CREATIVE_PIPELINE.md)
- 🔌 [PLATFORM_ADAPTERS — Meta & TikTok Adapters](docs/PLATFORM_ADAPTERS.md)
- 🛡️ [SAFETY_ENGINE — Safety Engine & Approvals](docs/SAFETY_ENGINE.md)
- 📊 [ANALYTICS_OPTIMIZATION — Analytics & Optimization](docs/ANALYTICS_OPTIMIZATION.md)
- 🛠️ [DEVELOPMENT — Developer Guide & Setup](docs/DEVELOPMENT.md)
