# Developer Setup & Workflow Guide: AIMOS

## 1. Local Environment Requirements

- **Python**: 3.12 or higher
- **Docker & Docker Compose**: Desktop 4.20+ / Docker Engine 24+
- **PostgreSQL**: 16 (handled via Docker Compose for development)

---

## 2. Setting Up the Local Workspace

```bash
# 1. Navigate to project root
cd aimos

# 2. Setup Environment configuration
cp .env.example .env

# 3. Start PostgreSQL and Backend services with Docker Compose
docker compose up --build -d

# 4. Confirm containers are running
docker compose ps
```

---

## 3. Database Migrations (Alembic)

Migrations run automatically upon container startup. When modifying SQLAlchemy models in `app/models/`:

```bash
# Enter backend directory
cd backend

# Create a new migration revision
alembic revision --autogenerate -m "Add new feature table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

---

## 4. Running Tests & Code Quality Checks

Tests use an isolated, in-memory SQLite database (`aiosqlite`) to execute in milliseconds without dependencies on external services.

```bash
# Navigate to backend directory
cd backend

# Run pytest suite with verbose output
pytest -v

# Run with coverage report
pytest --cov=app tests/
```

---

## 5. Code Style & Conventions

1. **Type Annotations**: Explicit type hints on all function parameters and returns.
2. **Async DB Operations**: Use `await db.execute(...)` and async session lifecycle everywhere.
3. **Repository Pattern**: Keep raw SQL/SQLAlchemy expressions inside `app/repositories/`. Routes and services interact only through repository methods.
4. **Audit Enforcement**: Ensure all mutating service methods invoke `AuditService.log_action()`.
5. **Pydantic Validation**: All API request bodies must use Pydantic models with explicit field constraints.
