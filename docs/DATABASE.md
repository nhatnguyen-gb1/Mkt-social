# Database Documentation: AIMOS

## 1. Relational Database Choice

- **Database Engine**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0 (Async engine via `asyncpg`)
- **Migration Tool**: Alembic (Async migration runner)

---

## 2. Entity Schemas (Phase 1 Foundation)

### 2.1 Product Entity (`products`)

Represents a product or brand onboarded into AIMOS for marketing campaigns.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | Primary Key | Unique product identifier |
| `name` | String(255) | Not Null, Indexed | Product name or brand title |
| `description` | Text | Nullable | Product details & selling points |
| `source_url` | String(2048) | Nullable | Target landing page or store URL |
| `category` | String(100) | Nullable, Indexed | Product niche or vertical |
| `target_market` | String(100) | Nullable | Target audience demographic |
| `status` | String(50) | Not Null, Default 'DRAFT', Indexed | State: `DRAFT`, `ACTIVE`, `ARCHIVED` |
| `created_at` | DateTime(TZ) | Not Null, Indexed | UTC timestamp of creation |
| `updated_at` | DateTime(TZ) | Not Null | UTC timestamp of last update |

---

### 2.2 Job Entity (`jobs`)

Represents an asynchronous orchestration task (e.g. market research run, creative generation job, campaign creation).

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | Primary Key | Unique job identifier |
| `job_type` | String(100) | Not Null, Indexed | Task classification (e.g., `RESEARCH`, `CREATIVE`) |
| `status` | String(50) | Not Null, Default 'PENDING', Indexed | State: `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED` |
| `entity_type` | String(100) | Nullable, Indexed | Associated domain entity (e.g. `Product`) |
| `entity_id` | UUID | Nullable, Indexed | Foreign UUID of associated domain entity |
| `input_data` | JSON / JSONB | Nullable | Input parameters and state payload |
| `output_data` | JSON / JSONB | Nullable | Execution result data |
| `error_message` | Text | Nullable | Failure stack trace or error detail |
| `created_at` | DateTime(TZ) | Not Null, Indexed | UTC creation timestamp |
| `updated_at` | DateTime(TZ) | Not Null | UTC update timestamp |

---

### 2.3 AuditLog Entity (`audit_logs`)

Represents an immutable record of system actions, user commands, and agent decisions.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | Primary Key | Unique log entry identifier |
| `actor_type` | String(50) | Not Null, Default 'SYSTEM' | Source: `USER`, `SYSTEM`, `AGENT` |
| `actor_id` | String(255) | Nullable | ID of user or agent performing action |
| `action` | String(100) | Not Null, Indexed | Action verb (e.g. `PRODUCT_CREATED`, `JOB_COMPLETED`) |
| `entity_type` | String(100) | Not Null, Indexed | Target entity type (e.g. `Product`, `Job`) |
| `entity_id` | UUID | Nullable, Indexed | Target entity UUID |
| `input_data` | JSON / JSONB | Nullable | Context or request snapshot |
| `output_data` | JSON / JSONB | Nullable | Result snapshot |
| `status` | String(50) | Not Null, Default 'SUCCESS' | Status: `SUCCESS`, `FAILURE` |
| `created_at` | DateTime(TZ) | Not Null, Indexed | Immutable UTC timestamp |

---

## 3. Database Indexes

To ensure high performance at scale, indexes are applied on:
- Primary Keys (`id` UUID)
- Lookup columns (`name`, `category`, `status`, `job_type`, `action`, `entity_type`, `entity_id`)
- Timestamps (`created_at`) for time-range queries and audit ordering
