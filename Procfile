web: sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"
worker: sh -c "celery -A app.workers.celery_app.celery_app worker --pool=${CELERY_WORKER_POOL:-prefork} --concurrency=${CELERY_WORKER_CONCURRENCY:-1} --max-tasks-per-child=${CELERY_WORKER_MAX_TASKS_PER_CHILD:-25} --prefetch-multiplier=${CELERY_WORKER_PREFETCH_MULTIPLIER:-1} --loglevel=INFO"
beat: celery -A app.workers.celery_app.celery_app beat --loglevel=INFO
