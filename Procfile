web: sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"
worker: celery -A app.workers.celery_app.celery_app worker --beat --concurrency=2 --loglevel=INFO
