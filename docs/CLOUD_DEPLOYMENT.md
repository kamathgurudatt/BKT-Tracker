# Cloud Deployment (Free-tier friendly)

This guide uses:
- Railway (backend API + worker)
- Supabase (PostgreSQL)
- Upstash (Redis)

## Public URLs
- API base: `https://<your-railway-domain>.up.railway.app/api/v1`
- Swagger: `https://<your-railway-domain>.up.railway.app/docs`
- Health: `https://<your-railway-domain>.up.railway.app/health`

## 1) Railway setup
1. Create Railway account and connect GitHub repo.
2. Create project from repo.
3. Railway auto-detects `railway.json` + Dockerfile.
4. Create two Railway services from same repo:
   - `api` with start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - `worker` with start command `celery -A app.workers.celery_app.celery_app worker --pool=${CELERY_WORKER_POOL:-prefork} --concurrency=${CELERY_WORKER_CONCURRENCY:-1} --max-tasks-per-child=${CELERY_WORKER_MAX_TASKS_PER_CHILD:-25} --prefetch-multiplier=${CELERY_WORKER_PREFETCH_MULTIPLIER:-1} --loglevel=INFO`
   - `beat` with start command `celery -A app.workers.celery_app.celery_app beat --loglevel=INFO`

## 2) Supabase PostgreSQL setup
1. Create Supabase project.
2. Go to Project Settings → Database.
3. Copy **Connection string (URI)**.
4. Convert SQLAlchemy async URL:
   `postgresql+asyncpg://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres?sslmode=require`
5. Set that value as `DATABASE_URL` in Railway (api + worker).

## 3) Upstash Redis setup
1. Create Upstash Redis database.
2. Copy `UPSTASH_REDIS_REST_URL` and standard TLS redis endpoint/password.
3. Set `REDIS_URL` in Railway (api + worker):
   `rediss://default:<password>@<host>:6379`

## 4) Required env vars in Railway
Set these in both services unless noted:
- `ENVIRONMENT=production`
- `APP_NAME=Blinkit Stock Sentinel`
- `API_V1_PREFIX=/api/v1`
- `DATABASE_URL=<supabase asyncpg URL>`
- `REDIS_URL=<upstash rediss URL>`
- `INTERNAL_AUTH_ENABLED=true`
- `INTERNAL_DEVICE_EMAIL=internal.device@blinkitsentinel.app`
- `INTERNAL_DEVICE_FULL_NAME=Internal Device User`
- `INTERNAL_DEVICE_IS_ADMIN=true`
- `CELERY_WORKER_CONCURRENCY=1`
- `CELERY_WORKER_MAX_TASKS_PER_CHILD=25`
- `CELERY_WORKER_PREFETCH_MULTIPLIER=1`
- `FORCE_HTTPS=true`
- `TRUST_PROXY_HEADERS=true`
- `CORS_ORIGINS=["https://<your-railway-domain>.up.railway.app"]`
- `BLINKIT_SEARCH_URL_TEMPLATE=<authorized live endpoint template>`
- `BLINKIT_PRODUCT_URL_TEMPLATE=<authorized live endpoint template>`
- `LIVE_PROVIDER_REQUIRED=true`
- `DEFAULT_POLL_INTERVAL_SECONDS=900`
- `MIN_POLL_INTERVAL_SECONDS=300`
- `STOCK_RESPONSE_MAX_AGE_SECONDS=120`
- `DUPLICATE_ALERT_WINDOW_SECONDS=1800`
- `FCM_CREDENTIALS_PATH=/app/secrets/firebase-service-account.json`

## 5) HTTPS
Railway provides TLS/HTTPS automatically via `*.up.railway.app` domains.

## 6) Health checks
`GET /health/live` verifies process liveness. `GET /health/ready` verifies PostgreSQL, Redis, and provider configuration.

Railway applies the repository `railway.json` deploy healthcheck to both the `api` and `worker` services.
The Celery worker process starts a small HTTP healthcheck listener on `$PORT` during worker startup, so the shared `/health/live` check succeeds even when Railway uses a dashboard-level worker start command instead of the repository Procfile.

## 7) Android APK build
```bash
cd mobile
flutter pub get
flutter build apk --release \
  --dart-define=API_ENV=prod \
  --dart-define=API_BASE_URL_PROD=https://<your-railway-domain>.up.railway.app/api/v1
```

## 8) Live inventory requirements
No mock or synthetic inventory should be served. If live source is unavailable, backend should surface `LIVE INVENTORY SOURCE UNAVAILABLE`.
