FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recomends \
    curl \
    build-essenital \
    && rm -rf /var/lib/apt/lists/*


ENV POETRY_VERSION=2.0.0 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONUNBUFFERED=1

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN curl -sSL https://install.python.poetry.org | python3 -

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN poetry install --no-root --no-interaction --no-ansi

COPY . /app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
