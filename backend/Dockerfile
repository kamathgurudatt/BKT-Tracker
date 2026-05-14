FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

COPY . /src

RUN set -eu; \
    if [ -f /src/requirements.txt ] && [ -d /src/app ]; then \
        REQUIREMENTS_PATH=/src/requirements.txt; APP_PATH=/src/app; \
    elif [ -f /src/backend/requirements.txt ] && [ -d /src/backend/app ]; then \
        REQUIREMENTS_PATH=/src/backend/requirements.txt; APP_PATH=/src/backend/app; \
    else \
        echo "Expected requirements/app in either /src or /src/backend"; \
        exit 1; \
    fi; \
    pip install -r "$REQUIREMENTS_PATH"; \
    python -m playwright install chromium; \
    cp -R "$APP_PATH" /app/app

EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
