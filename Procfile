web: sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"
worker: celery -A app.workers.celery_app.celery_app worker --concurrency=2 --loglevel=INFO
beat: celery -A app.workers.celery_app.celery_app beat --loglevel=INFO
