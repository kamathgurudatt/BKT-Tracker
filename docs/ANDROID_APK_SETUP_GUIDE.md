# Blinkit Stock Sentinel — Advanced From-Scratch Rebuild Guide (Internal APK)

> **Important intent of this guide**
> This is an **advanced rebuild playbook** for teams who want to **recreate the project from scratch** while preserving the same backend links/credentials and runtime behavior.
>
> Replace these placeholders everywhere:
> - `<YOUR_REPOSITORY_URL>`
> - `<YOUR_NEW_REPO_NAME>`
> - `<YOUR_API_BASE_URL>` (must end with `/api/v1`)
> - `<YOUR_ORG_NAME>`

---

## 1) Decide your rebuild strategy (hard reset vs parallel rebuild)

**Purpose:** Avoid accidental data loss.

You have two valid patterns:

1. **Hard Reset (destructive):** Delete all tracked files and recreate project structure in-place.
2. **Parallel Rebuild (recommended):** Build from scratch in a new repo, then archive old repo.

### Hard reset commands (destructive)

```bash
# from repository root
git checkout -b rebuild/advanced-from-scratch

git rm -r .
# optionally remove ignored/generated files
# git clean -fdx
```

**Expected output:** Git index is empty (all tracked files staged for deletion).

---

## 2) Recreate top-level repository structure

**Purpose:** Build clean baseline for backend + mobile + docs + CI.

```bash
mkdir -p backend/app backend/tests mobile/lib mobile/android .github/workflows docs scripts postman
```

Add core files:

```bash
touch README.md LICENSE .gitignore docker-compose.yml pyproject.toml
```

**Expected output:** Empty but organized repository scaffold ready for code restore/rewrite.

---

## 3) Recreate Flutter app shell (Material 3)

**Purpose:** Generate a clean Android-capable Flutter app.

```bash
flutter create --platforms=android mobile
```

Then edit `mobile/lib/main.dart` to enable Material 3 and app routes.

**Expected output:** `mobile/` contains Android + Flutter app baseline and builds successfully.

---

## 4) Recreate API client with runtime backend URL

**Purpose:** Preserve private-network backend connectivity while rebuilding code.

Update `mobile/lib/services/api_client.dart` with:

- `String.fromEnvironment('API_BASE_URL_PROD', defaultValue: '<YOUR_API_BASE_URL>')`
- URL normalization/validation
- `/auth/me` connectivity check
- robust timeout + JSON parsing errors

Build-time define remains:

```bash
--dart-define=API_BASE_URL_PROD=<YOUR_API_BASE_URL>
```

**Expected output:** New app build points to your backend without hardcoding environment-specific URLs in source.

---

## 5) Recreate authentication-free app flow

**Purpose:** Keep internal service-user model exactly aligned with backend policy.

In `mobile/lib/screens/auth_screen.dart`:

1. Remove username/password input UI.
2. Show internal access explanation.
3. On continue (or auto-connect), call `GET /auth/me`.
4. Navigate to dashboard on success.
5. Show clear error toast/snackbar on failure.

**Expected output:** User never logs in with credentials; connectivity + trust boundary determine access.

---

## 6) Recreate backend auth behavior (`/auth/me` only)

**Purpose:** Match internal-only access architecture.

In FastAPI route file `backend/app/api/routes/auth.py`:

- Keep `GET /auth/me` returning current internal user.
- Ensure legacy password endpoints (`/signup`, `/login`, `/token`) return HTTP 410 with a deprecation message.

**Expected output:** Mobile app can validate access via `/auth/me`; password auth is explicitly disabled.

---

## 7) Recreate CI workflow for APK artifacts

**Purpose:** Auto-produce APK on every push/PR/manual run.

Create `.github/workflows/ci.yml` with trigger block:

```yaml
on:
  push:
  pull_request:
  workflow_dispatch:
```

Mobile build step should run:

```bash
cd mobile && flutter build apk --debug --dart-define=API_BASE_URL_PROD=${{ vars.API_BASE_URL }}
```

Upload artifact as:

```text
blinkit-stock-sentinel-debug-apk
```

Path:

```text
mobile/build/app/outputs/flutter-apk/app-debug.apk
```

**Expected output:** Downloadable debug APK artifact per pipeline run.

---

## 8) Recreate repository variables and secrets

**Purpose:** Wire CI to your backend endpoint safely.

GitHub → **Settings → Secrets and variables → Actions**

Add variable:
- `API_BASE_URL` = `<YOUR_API_BASE_URL>`

Optional future secrets (only if backend later requires them):
- `INTERNAL_API_TOKEN`
- `VPN_CA_CERT`
- `SENTRY_DSN`

**Expected output:** CI uses environment-specific backend URL without committing it directly.

---

## 9) Build the APK locally (from clean rebuild)

**Purpose:** Validate rebuilt project works before CI.

```bash
cd mobile
flutter pub get
flutter analyze
flutter build apk --debug --dart-define=API_BASE_URL_PROD=<YOUR_API_BASE_URL>
```

Output APK:

```text
mobile/build/app/outputs/flutter-apk/app-debug.apk
```

**Expected output:** Successful debug APK generation from fully rebuilt codebase.

---

## 10) Validate internal connectivity on device

**Purpose:** Ensure real device can access private backend.

Install:

```bash
adb install -r mobile/build/app/outputs/flutter-apk/app-debug.apk
```

Validate:
1. Device on VPN/private network.
2. App opens and checks `/auth/me`.
3. Dashboard loads after successful response.

Smoke test backend manually:

```bash
curl -i <YOUR_API_BASE_URL>/auth/me
```

**Expected output:** HTTP 200 JSON and successful app navigation.

---

## 11) Trigger CI manually and retrieve artifact

**Purpose:** Verify cloud build parity with local build.

1. Push branch:

```bash
git add .
git commit -m "rebuild: advanced from-scratch project recreation"
git push origin rebuild/advanced-from-scratch
```

2. In GitHub Actions, run **CI** manually (`workflow_dispatch`) if needed.
3. Download artifact `blinkit-stock-sentinel-debug-apk`.

**Expected output:** CI-generated APK available for internal distribution.

---

## 12) Internal deployment playbook

**Purpose:** Distribute safely to internal testers/users.

Recommended:
1. MDM/UEM managed rollout
2. Private artifact repository
3. Signed internal release note in company chat/wiki

Always include with each APK:
- Commit SHA
- Build date/time (UTC)
- Backend environment label
- Required network condition (VPN/LAN)
- Known issues + rollback note

**Expected output:** Controlled internal release with traceability.

---

## 13) Advanced troubleshooting matrix

### A) `flutter doctor` has Android toolchain errors

```bash
flutter doctor --android-licenses
flutter doctor -v
```

Install missing SDK packages in Android Studio.

### B) Gradle/JDK mismatch

Use Java 17+:

```bash
java -version
cd mobile && flutter clean && flutter pub get
```

Rebuild APK.

### C) App cannot reach backend

- Verify URL includes `/api/v1`
- Verify DNS/VPN/private route
- Run:

```bash
curl -i <YOUR_API_BASE_URL>/auth/me
```

### D) 410 errors on `/auth/login` or `/auth/token`

Expected in this architecture. Use `/auth/me` only.

### E) CI build fails with missing API URL

Set repo variable:
- `API_BASE_URL = <YOUR_API_BASE_URL>`

Re-run workflow.

---

## 14) One-command rebuild helper script

Create `scripts/build_debug_apk.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

API_BASE_URL="${1:-<YOUR_API_BASE_URL>}"

cd mobile
flutter pub get
flutter analyze
flutter build apk --debug --dart-define=API_BASE_URL_PROD="${API_BASE_URL}"

echo "APK: $(pwd)/build/app/outputs/flutter-apk/app-debug.apk"
```

Run:

```bash
bash scripts/build_debug_apk.sh <YOUR_API_BASE_URL>
```

---

## 15) Quick start (advanced rebuild mode)

```bash
git clone <YOUR_REPOSITORY_URL>
cd <YOUR_NEW_REPO_NAME>

# optional destructive reset path
git checkout -b rebuild/advanced-from-scratch
git rm -r .

# recreate Flutter app
flutter create --platforms=android mobile

# build
cd mobile
flutter pub get
flutter build apk --debug --dart-define=API_BASE_URL_PROD=<YOUR_API_BASE_URL>
```

APK output:

```text
mobile/build/app/outputs/flutter-apk/app-debug.apk
```
