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
   - `worker` with start command `celery -A app.workers.celery_app.celery_app worker --beat --loglevel=INFO`

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
- `SECRET_KEY=<strong-random-string>`
- `DATABASE_URL=<supabase asyncpg URL>`
- `REDIS_URL=<upstash rediss URL>`
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
`GET /health` verifies app + PostgreSQL + Redis.
Expect `{"status":"ok","database":true,"redis":true}`.

Railway applies the repository `railway.json` deploy healthcheck to both the `api` and `worker` services.
The worker Procfile command starts a small HTTP healthcheck listener before Celery so the shared `/health/live` check succeeds without exposing worker functionality.

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
