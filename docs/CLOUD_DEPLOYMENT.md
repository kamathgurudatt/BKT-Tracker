# Cloud Deployment (Render-first)

## 1) Public backend URL
After deploy, your API base URL is:
- `https://<your-render-service>.onrender.com/api/v1`

## 2) Swagger docs URL
- `https://<your-render-service>.onrender.com/docs`

## 3) Health check URL
- `https://<your-render-service>.onrender.com/health`

## 4) Render setup
1. Create PostgreSQL: `blinkit-stock-postgres`.
2. Create Redis (Render Redis or Upstash).
3. Create API web service from repo using `render.yaml`.
4. Create worker service from repo using `render.yaml`.
5. Set required environment variables from `.env.example`.
6. Add persistent secret file for Firebase service account and set `FCM_CREDENTIALS_PATH`.

## 5) Required production environment variables
- `DATABASE_URL`
- `REDIS_URL`
- `SECRET_KEY`
- `BLINKIT_SEARCH_URL_TEMPLATE`
- `BLINKIT_PRODUCT_URL_TEMPLATE`
- `LIVE_PROVIDER_REQUIRED=true`
- `FCM_CREDENTIALS_PATH`
- `CORS_ORIGINS` (JSON array)
- `FORCE_HTTPS=true`
- `TRUST_PROXY_HEADERS=true`

## 6) Worker behavior
Worker process:
- pulls due jobs from PostgreSQL
- polls live provider endpoints
- logs request metadata and failures
- records snapshots and change events
- sends notifications after verified transitions

## 7) Firebase production setup
1. Firebase Console → project creation.
2. Add Android app `com.example.blinkit_stock_sentinel`.
3. Download `google-services.json` to `mobile/android/app/`.
4. Generate service account key JSON for FCM Admin SDK.
5. Upload key JSON to Render secret file store and map `FCM_CREDENTIALS_PATH`.
6. Ensure device tokens are captured in user profile and persisted.

## 8) APK build instructions
Production build:
```bash
cd mobile
flutter pub get
flutter build apk --release \
  --dart-define=API_ENV=prod \
  --dart-define=API_BASE_URL_PROD=https://<your-render-service>.onrender.com/api/v1
```
Staging build:
```bash
flutter build apk --release \
  --dart-define=API_ENV=staging \
  --dart-define=API_BASE_URL_STAGING=https://<your-staging-service>.onrender.com/api/v1
```

## 9) Production admin credentials setup
1. Create initial admin via DB seed/manual SQL update (`users.role='admin'`).
2. Rotate password after first login.
3. Keep admin JWT lifetime short and monitor access logs.

## 10) CI/CD flow
- `.github/workflows/ci.yml`: lint, compile, Flutter analyze, APK build.
- `.github/workflows/deploy-render.yml`: triggers Render deploy hooks for API + worker on `main` push.

## 11) Live inventory guarantee
If provider templates are absent or live calls fail, APIs must surface:
- `LIVE INVENTORY SOURCE UNAVAILABLE`

No static or synthetic inventory injection is used.
