# Railway troubleshooting: password removal and worker crashes

This app is intended for internal use behind a VPN/private network. Password-based auth has been removed from the backend; the API now resolves every request to a configured internal service user so existing `user_id` ownership checks still work.

## 1. Password validation error: `Password must be 72 bytes or fewer`

### Root cause

The backend previously exposed `/auth/signup`, `/auth/login`, and `/auth/token` endpoints backed by `passlib[bcrypt]`. Bcrypt accepts at most 72 bytes of password input. Even when the frontend treated the password field as a placeholder, backend schemas and exception handlers still validated and hashed the field, so normal workflows could fail on a password-only constraint that the product did not need.

### Code-level fix in this repo

- Removed password fields and validators from API schemas.
- Removed password hashing and JWT verification from the request dependency path.
- Removed `passlib[bcrypt]` and `python-jose` from backend runtime requirements.
- Removed `hashed_password` from the SQLAlchemy `User` model and bootstrap SQL schema.
- Kept `/auth/me` as the only active auth endpoint. Deprecated password endpoints now return HTTP `410 Gone` and are hidden from OpenAPI.

### Railway / database migration steps

Run `docs/sql/20260518_remove_password_auth.sql` once against the Railway PostgreSQL database after deploying the code:

```sql
ALTER TABLE users DROP COLUMN IF EXISTS hashed_password;
```

Set these Railway variables on the API, worker, and beat services:

```bash
INTERNAL_AUTH_ENABLED=true
INTERNAL_DEVICE_EMAIL=internal.device@blinkitsentinel.app
INTERNAL_DEVICE_FULL_NAME="Internal Device User"
INTERNAL_DEVICE_IS_ADMIN=true
```

Then remove any frontend password inputs or calls to `/auth/signup`, `/auth/login`, or `/auth/token`. The frontend should call `/api/v1/auth/me` only when it needs the current internal user.

### Prevention

- Do not add password fields to internal-only forms unless the product explicitly adopts password auth.
- Keep auth at the ingress layer: Railway private networking, corporate VPN, SSO proxy, or IP allow-listing.
- Add a regression test that posts representative business forms without any password field and asserts no auth/password validation errors are returned.
- Keep `passlib`, `bcrypt`, `argon2`, and JWT libraries out of runtime dependencies unless a formal auth design requires them.

## 2. Railway worker crash: segmentation fault / worker offline loops

### Likely root cause

The worker runs Celery tasks that can touch native extensions and browser automation dependencies. Segmentation faults are usually outside Python exception handling and commonly come from one of these conditions:

1. Chromium/Playwright launched without required OS libraries in a slim image.
2. Too much worker concurrency for the Railway memory limit.
3. Native memory fragmentation or leaks in long-lived child processes.
4. Prefetching too many jobs and exceeding memory during bursty polling.
5. A child process dying while a task is acknowledged too early.

### Short-term Railway patch

Set these worker variables immediately:

```bash
PYTHONFAULTHANDLER=1
MALLOC_ARENA_MAX=2
CELERY_WORKER_POOL=prefork
CELERY_WORKER_CONCURRENCY=1
CELERY_WORKER_MAX_TASKS_PER_CHILD=25
CELERY_WORKER_PREFETCH_MULTIPLIER=1
CELERY_TASK_TIME_LIMIT_SECONDS=600
CELERY_TASK_SOFT_TIME_LIMIT_SECONDS=540
```

Use this Railway worker start command if Railway is not using the repository `Procfile`:

```bash
celery -A app.workers.celery_app.celery_app worker --pool=${CELERY_WORKER_POOL:-prefork} --concurrency=${CELERY_WORKER_CONCURRENCY:-1} --max-tasks-per-child=${CELERY_WORKER_MAX_TASKS_PER_CHILD:-25} --prefetch-multiplier=${CELERY_WORKER_PREFETCH_MULTIPLIER:-1} --loglevel=INFO
```

Keep beat as a separate Railway service:

```bash
celery -A app.workers.celery_app.celery_app beat --loglevel=INFO
```

### Long-term fix in this repo

- The Docker image now installs Chromium with Playwright OS dependencies via `python -m playwright install --with-deps chromium`.
- The image enables `PYTHONFAULTHANDLER=1` and limits glibc arenas with `MALLOC_ARENA_MAX=2`.
- Celery now reads pool, concurrency, prefetch, time limit, and child-recycling settings from environment variables.
- The default worker concurrency is 1 and child processes recycle after 25 tasks.
- `task_acks_late` and `task_reject_on_worker_lost` are enabled so Redis can requeue work if a child process crashes.

### Debugging checklist

1. Confirm whether the crash is a true segfault or an OOM kill.
   - Segfault: logs include `Segmentation fault (core dumped)`.
   - OOM: Railway metrics show memory at/near limit and logs may show exit code 137.
2. Capture the exact task being processed before the crash by checking the last `poll_job` or provider log entry.
3. Temporarily set `CELERY_WORKER_CONCURRENCY=1` and `CELERY_WORKER_MAX_TASKS_PER_CHILD=1`. If crashes stop, the issue is likely memory growth or native state reuse.
4. If browser tasks trigger the crash, move Playwright work to a dedicated worker service with concurrency 1, separate from lightweight database/HTTP polling tasks.
5. If crashes persist with concurrency 1 and fresh child processes, pin or upgrade native dependencies (`playwright`, `asyncpg`) and rebuild the image from scratch.
6. Increase Railway memory only after bounding concurrency; more memory hides leaks but does not fix unsafe parallelism.

### Prevention

- Keep worker and beat as separate services.
- Keep browser automation in a dedicated queue if it becomes a regular workload.
- Alert on worker restarts and memory usage, not only API health.
- Load-test representative large jobs before increasing concurrency.
- Avoid `python:*-alpine` for Playwright/Chromium workloads; Alpine uses musl and often increases native-module compatibility risk.
