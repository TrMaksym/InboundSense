# ⚡ InboundSense NLP Pipeline

![CI Pipeline](https://img.shields.io/badge/CI%20Pipeline-passing-brightgreen?style=flat-square)
![Coverage](https://img.shields.io/badge/Coverage-80%25-brightgreen?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-teal?style=flat-square)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%20%7C%20pgvector-29658e?style=flat-square)
![Celery](https://img.shields.io/badge/Celery-5.3-37814a?style=flat-square)

An asynchronous, distributed NLP processing and event-driven classification pipeline built with FastAPI, utilizing Celery task queues, local embedding generation via ONNX Runtime, and dense vector similarity indexing with pgvector.

---

## ⚡ Key Features

* **Event Ingestion & Processing:** Asynchronous REST endpoints accepting high-throughput inbound text payloads with non-blocking status tracking.
* **Semantic Vector Search:** Dense vector embeddings stored and indexed in PostgreSQL using `pgvector` with HNSW indexing for low-latency similarity queries.
* **Local ML Inference (ONNX):** Hardware-optimized transformer inference using `onnxruntime` and `tokenizers`, avoiding heavy PyTorch runtime overhead.
* **Text Chunking & Preprocessing:** Dynamic semantic chunking supporting variable token boundaries and metadata sanitization via `selectolax`.
* **Background Tasks (Celery & Redis):** Asynchronous ingestion pipelines with automated task retry, exponential backoff, and dedicated worker pools.
* **Database & Concurrency:** Asynchronous database engine powered by `SQLAlchemy 2.0` and `asyncpg` connection pooling.
* **Pipeline Analytics & Metrics:** Real-time aggregation of total events, chunk statistics, status breakdowns, and category distributions via dedicated async endpoints.
* **Automated CI/CD Quality Checks:** GitHub Actions pipeline executing integration suites with real health-checked PostgreSQL (`pgvector`) and Redis containers.

---

## 🛠 Tech Stack

* **Core:** Python, FastAPI, Pydantic v2, Uvicorn
* **Database:** PostgreSQL 16 (Production / Docker), pgvector, SQLAlchemy 2.0 (Async), asyncpg, Alembic
* **Tasks & Caching:** Celery, Redis
* **ML & NLP Engine:** ONNX Runtime, HuggingFace Tokenizers, fastembed
* **Testing:** pytest, pytest-asyncio, pytest-cov (12 unit/integration tests, 80% coverage)
* **DevOps & CI:** Docker, Docker Compose, GitHub Actions

---

## 📡 API Endpoints Overview

| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Service health status check | Public |
| `POST` | `/api/v1/events/` | Ingest inbound text message & dispatch classification | Public |
| `GET` | `/api/v1/events/{id}/` | Retrieve event details, processing state & tags | Public |
| `POST` | `/api/v1/search/` | Semantic similarity vector search across embeddings | Public |
| `POST` | `/api/v1/chunks/` | Chunk long-form document into vector segments | Public |
| `GET` | `/api/v1/chunks/{source_id}/` | Retrieve indexed chunks for a specific document | Public |
| `GET` | `/api/v1/analytics/stats/` | Pipeline processing volume and latency metrics | Public |
| `GET` | `/api/v1/stream/search/` | Server-Sent Events (SSE) streaming semantic responses | Public |

---

## 🚀 Getting Started

### Option 1: Run with Docker Compose (Recommended)

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/TrMaksym/InboundSense.git](https://github.com/TrMaksym/InboundSense.git)
   cd InboundSense
   ```

2. **Create a `.env` file in the root directory:**
   ```env
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=inboundsense_db
   POSTGRES_HOST=db
   POSTGRES_PORT=5432
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/inboundsense_db
   REDIS_HOST=redis
   REDIS_PORT=6379
   REDIS_URL=redis://redis:6379/0
   CELERY_BROKER_URL=redis://redis:6379/0
   CELERY_RESULT_BACKEND=redis://redis:6379/0
   ENVIRONMENT=development
   ```

3. **Build and launch services:**
   ```bash
   docker compose up --build -d
   ```

4. **Run migrations:**
   ```bash
   docker compose exec api alembic upgrade head
   ```

The API will be available at `http://localhost:8000`.

### Option 2: Local Setup

1. **Install dependencies via Poetry:**
   ```bash
   poetry install --with dev
   ```

2. **Ensure database and cache services are running:**
   ```bash
   docker compose up -d db redis
   ```

3. **Run migrations:**
   ```bash
   poetry run alembic upgrade head
   ```

4. **Start development server:**
   ```bash
   poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Start Celery worker:**
   ```bash
   poetry run celery -A app.core.celery_app worker --loglevel=info
   ```

---

## 🧪 Testing & Quality Assurance

All third-party integrations (PostgreSQL pgvector similarity calculations, Redis queues, and ONNX Runtime inference pipelines) are isolated through asynchronous test fixtures and mocks.

Run the test suite with coverage report:
```bash
docker compose exec api pytest --cov=app --cov-report=term-missing
```

```text
Name                          Stmts   Miss  Cover   Missing
-----------------------------------------------------------
app/__init__.py                   0      0   100%
app/api/__init__.py               0      0   100%
app/api/v1/__init__.py            0      0   100%
app/api/v1/analytics.py          17      4    76%   16-18, 26, 33
app/api/v1/chunks.py             35     18    49%   22-27, 39-41, 52-77
app/api/v1/events.py             25      9    64%   21-25, 29-34
app/api/v1/search.py             28      9    68%   25, 38-57
app/api/v1/source.py             23     11    52%   18-22, 26-31
app/api/v1/stream.py             13      0   100%
app/core/celery_app.py            7      0   100%
app/core/config.py               21      0   100%
app/core/logger.py                4      0   100%
app/db/base.py                    3      0   100%
app/db/models.py                 51      0   100%
app/db/session.py                 9      0   100%
app/main.py                      29      4    86%   21-24
app/schemas/analytics.py          6      0   100%
app/schemas/chunk.py             20      0   100%
app/schemas/event.py             19      0   100%
app/schemas/search.py            17      0   100%
app/schemas/source.py            17      0   100%
app/services/ml_engine.py        35      1    97%   43
app/services/nlp.py              48     11    77%   60-91
app/services/rag_service.py      24      2    92%   27-28
app/services/scraper.py          25      9    64%   36, 43-50
app/services/tasks.py            41     27    34%   16-38, 47-66, 71
-----------------------------------------------------------
TOTAL                           517    105    80%
====================== 12 passed, 1 warning in 7.22s ======================
```

---

## 📖 API Documentation

Interactive OpenAPI schemas are available out of the box:
* **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
* **OpenAPI Raw Schema:** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)