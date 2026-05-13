# Blinkit Stock Sentinel

Blinkit Stock Sentinel is an educational Android + FastAPI project for learning how quick-commerce inventory monitoring, wishlist tracking, alerting, analytics, and safe provider integrations can be designed.

> **Ethics notice:** This repository is strictly for education and research. Respect robots.txt, rate limits, and platform ToS. Do not bypass authentication, anti-bot systems, captchas, or security controls. Provider adapters default to deterministic demo data until you configure public, ToS-compliant endpoints.

## Architecture

```mermaid
flowchart LR
  Flutter[Flutter Android APK] --> API[FastAPI API]
  API --> PG[(PostgreSQL)]
  API --> Redis[(Redis Cache/Broker)]
  Beat[Celery Beat] --> Worker[Celery Workers]
  Worker --> Providers[Ethical Provider Adapters]
  Worker --> PG
  Worker --> FCM[Firebase Cloud Messaging]
```

## Backend features

- JWT signup/login and authenticated user APIs.
- Multi-location, wishlist, tracked product, history, analytics, and notification endpoints.
- Async SQLAlchemy architecture with indexed PostgreSQL schema.
- Celery scheduler and worker queue for periodic safe polling.
- Modular providers for Blinkit, Zepto, and Instamart-style integrations with throttling, rotating headers, retries, exponential backoff, and no captcha/login bypass logic.
- SlowAPI request throttling and environment-driven configuration.

## Mobile features

- Flutter Material 3 Android app.
- Splash, login/register, dashboard, product search, wishlist, product detail, location selector, analytics, notification center, and settings screens.
- Dark mode toggle, chart placeholder, push-notification permission declaration, and APK build path.

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

Open API docs at <http://localhost:8000/docs>.

## Build the APK

```bash
cd mobile
flutter pub get
flutter build apk --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1
```

The APK will be emitted under `mobile/build/app/outputs/flutter-apk/`.

## Firebase Cloud Messaging setup

1. Create a Firebase project.
2. Add an Android app with package `com.example.blinkit_stock_sentinel`.
3. Download `google-services.json` into `mobile/android/app/`.
4. Create a service account JSON for backend sending and set `FCM_CREDENTIALS_PATH`.
5. Store user device tokens through the `/auth/me` extension point before sending production pushes.

## Safe provider configuration

Provider classes live under `backend/app/providers/`. The demo implementation returns sample data. If you add real public endpoints, keep:

- `PROVIDER_BASE_DELAY_SECONDS` >= 1.5.
- `PROVIDER_MAX_REQUESTS_PER_MINUTE` conservative.
- No auth bypass, captcha bypass, hidden endpoint abuse, or aggressive parallelism.
- Clear failure logging and opt-out controls.

## API collection

Import `postman/blinkit-stock-sentinel.postman_collection.json` for common auth, search, tracking, and analytics requests.
