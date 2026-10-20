FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

ENV POETRY_VIRTUALENVS_CREATE=false \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN poetry install --no-root --without train --no-interaction --no-ansi && \
    poetry cache clear pypoetry --all -n && \
    rm -rf /root/.cache/pypoetry /root/.cache/pip

RUN apt-get purge -y --auto-remove build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY . /app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]