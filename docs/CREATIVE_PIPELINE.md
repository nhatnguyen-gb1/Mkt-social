# AIMOS Phase 4: Creative Pipeline & Asset Management Documentation

## Overview

Phase 4 of **AIMOS** introduces the **Creative Pipeline & Asset Management**, enabling automated marketing strategy formulation, creative ad copy generation, visual prompt design, short-form video scripting, media generator provider abstraction (DALL-E 3, Stability, Mock), and creative asset persistence.

---

## Key Components

### 1. MarketingStrategyAgent
- **Purpose**: Transforms market research and product metadata into actionable brand positioning, target customer segments, channel recommendations, and distinct advertising hooks (`AdConcept`).
- **Endpoint**: `POST /api/v1/agents/strategy`

### 2. CreativeAgent
- **Purpose**: Takes brand strategy and ad concepts to produce detailed AI image generation prompts (`ImagePromptDetail`) and scene-by-scene video ad scripts (`VideoScriptDetail`).
- **Endpoint**: `POST /api/v1/agents/creative`

### 3. Media Generator Provider Abstraction
- **Base Interface**: `BaseImageGenerator` in `app/core/media/base.py`
- **Providers**:
  - `MockImageGenerator`: Deterministic, zero-cost placeholder media generator for standalone dev and automated tests.
  - `OpenAIImageGenerator`: Connects to OpenAI DALL-E 3 API (`https://api.openai.com/v1/images/generations`).
- **Factory**: `MediaGeneratorFactory` dynamically resolves providers based on environment settings and request parameters.

### 4. Asset Entity & Management Service
- **Model**: `Asset` (`id`, `product_id`, `asset_type`, `title`, `file_url`, `prompt`, `asset_metadata`, `status`, `created_at`).
- **Endpoints**:
  - `POST /api/v1/assets/generate-image`: Triggers image generation and saves managed asset.
  - `GET /api/v1/assets`: Lists all creative assets (supports `product_id` filtering).
  - `GET /api/v1/assets/{id}`: Retrieves specific asset details.

---

## Auditability & Testing

- Every asset generation and agent run writes audit records into `audit_logs`.
- 100% of automated tests pass offline using `MockImageGenerator` and `MockLLMProvider` with zero API cost.
