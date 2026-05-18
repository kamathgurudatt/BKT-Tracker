# Blinkit Stock Sentinel (Internal Android APK) — Complete Setup & Build Guide

This guide explains how to set up, build, validate, and distribute the **Blinkit Stock Sentinel** Android debug APK from scratch for internal use.

> Replace placeholders before running commands:
> - `<YOUR_REPOSITORY_URL>`
> - `<YOUR_REPO_NAME>`
> - `<YOUR_API_BASE_URL>` (example: `https://your-backend.example.com/api/v1`)

---

## 1) Understand the app’s internal access model

**Purpose:** Confirm how authentication works before you deploy.

- This app is designed for **internal/private network use** (office LAN / VPN / private backend).
- The mobile app does **not** ask end users for username/password in normal internal mode.
- Instead, the app verifies backend availability and internal identity by calling:

```http
GET /auth/me
```

- The backend resolves the internal service user and returns user info if the network path/trust boundary is valid.
- Password endpoints are removed/deprecated on backend and return HTTP 410.

**Expected output:** A successful `/auth/me` response means the app can proceed to dashboard and use inventory features.

---

## 2) Clone the repository

**Purpose:** Get project code locally.

```bash
git clone <YOUR_REPOSITORY_URL>
cd <YOUR_REPO_NAME>
```

**Expected output:** Repository files appear locally, including `mobile/`, `backend/`, `.github/workflows/`.

---

## 3) Install required local tooling

**Purpose:** Ensure your machine can build Flutter Android APKs.

Install these:
1. Flutter SDK (stable channel)
2. Android Studio (or Android SDK + command-line tools)
3. Java 17+ (recommended for modern Android toolchains)
4. Git

Verify:

```bash
flutter --version
flutter doctor -v
java -version
git --version
```

**Expected output:**
- Flutter installed and on stable channel.
- `flutter doctor -v` shows no blocking Android/SDK/license errors.

If Android licenses are pending:

```bash
flutter doctor --android-licenses
```

---

## 4) Configure backend API URL strategy

**Purpose:** Point the app to your internal backend.

The app supports runtime base URL via Dart define:

```bash
--dart-define=API_BASE_URL_PROD=<YOUR_API_BASE_URL>
```

### Rules for `<YOUR_API_BASE_URL>`
- Must include protocol (`http://` or `https://`)
- Should end in `/api/v1`
- Example:

```text
https://inventory-internal.company.net/api/v1
```

**Expected output:** APK embeds this URL and uses it for `/auth/me`, search, analytics, and debug endpoints.

---

## 5) Fetch Flutter dependencies

**Purpose:** Download Dart packages before build.

```bash
cd mobile
flutter pub get
```

**Expected output:** `pub get` completes successfully and writes `.dart_tool`/lock state.

---

## 6) Build debug APK locally

**Purpose:** Produce installable internal APK for testing/distribution.

Run from repository root:

```bash
cd mobile
flutter build apk --debug --dart-define=API_BASE_URL_PROD=<YOUR_API_BASE_URL>
```

**Expected output:**
- Build succeeds.
- APK generated at:

```text
mobile/build/app/outputs/flutter-apk/app-debug.apk
```

---

## 7) Validate APK and backend connectivity

**Purpose:** Confirm app can reach backend in real environment.

### Install APK on Android device

Option A (ADB):

```bash
adb install -r mobile/build/app/outputs/flutter-apk/app-debug.apk
```

Option B: Share APK file and install manually on device.

### First-run behavior
- App opens auth/connect screen.
- In internal mode, it auto-attempts backend connect.
- It calls `GET <YOUR_API_BASE_URL>/auth/me`.
- On success, app shows “Connected to internal backend” and navigates to dashboard.

### Quick endpoint smoke test (optional from laptop)

```bash
curl -i <YOUR_API_BASE_URL>/auth/me
```

**Expected output:** HTTP 200 with JSON user payload.

---

## 8) Set up GitHub Actions variable for CI builds

**Purpose:** Ensure automated APK builds use the correct backend URL.

In GitHub:
1. Open repository: `<YOUR_REPO_NAME>`
2. Go to **Settings → Secrets and variables → Actions → Variables**
3. Add repository variable:
   - **Name:** `API_BASE_URL`
   - **Value:** `<YOUR_API_BASE_URL>`

> If your backend requires any internal tokens/certs in future, add them as **Secrets** (not Variables).

**Expected output:** Workflow can resolve `${{ vars.API_BASE_URL }}` at build time.

---

## 9) Understand CI workflow triggers and behavior

**Purpose:** Know exactly when APK artifacts are produced.

Current workflow triggers:
- `push`
- `pull_request`
- `workflow_dispatch` (manual run)

Mobile CI job performs:
1. Checkout code
2. Setup Flutter (stable)
3. `flutter doctor -v`
4. `flutter pub get`
5. `flutter analyze`
6. Build debug APK using:

```bash
cd mobile && flutter build apk --debug --dart-define=API_BASE_URL_PROD=${{ vars.API_BASE_URL }}
```

7. Upload artifact named:

```text
blinkit-stock-sentinel-debug-apk
```

Artifact path:

```text
mobile/build/app/outputs/flutter-apk/app-debug.apk
```

**Expected output:** Every push/PR/manual run yields downloadable APK artifact (if build passes).

---

## 10) Trigger a manual APK build in GitHub Actions

**Purpose:** Generate APK on demand without a new code commit.

Steps:
1. Open GitHub repository `<YOUR_REPO_NAME>`
2. Go to **Actions**
3. Open workflow **CI**
4. Click **Run workflow** (workflow_dispatch)
5. Select branch and start

After completion:
1. Open run summary
2. Download artifact: `blinkit-stock-sentinel-debug-apk`
3. Extract and retrieve `app-debug.apk`

**Expected output:** Fresh APK built with configured `API_BASE_URL` variable.

---

## 11) Internal deployment options for APK

**Purpose:** Distribute APK safely to internal users.

Recommended internal channels:
1. Company MDM/UEM (best for managed devices)
2. Private shared drive / artifact repository
3. Internal chat release post + checksum

For each release, publish:
- APK filename (`app-debug.apk` or renamed internal convention)
- Build date/time
- Git commit SHA
- Backend URL environment label (e.g., prod-internal, staging)
- Installation notes (enable internal app install policy)

**Expected output:** Teams can install the right APK version and connect to correct internal backend.

---

## 12) Suggested release checklist

**Purpose:** Standardize and reduce deployment mistakes.

1. Confirm backend health and `/auth/me` returns 200.
2. Confirm `API_BASE_URL` points to intended environment.
3. Build APK (local or CI).
4. Install on at least one real Android test device.
5. Verify: dashboard load, search, analytics, notifications/debug screens.
6. Publish APK + release note internally.

---

## 13) Troubleshooting common build/runtime issues

### A) `flutter doctor` reports Android toolchain issues
**Cause:** Missing SDK components/licenses.

**Fix:**
```bash
flutter doctor --android-licenses
flutter doctor -v
```
Install missing Android SDK packages in Android Studio.

---

### B) Build fails with Gradle/JDK mismatch
**Cause:** Incompatible Java version.

**Fix:** Use Java 17+ and re-run:
```bash
cd mobile
flutter clean
flutter pub get
flutter build apk --debug --dart-define=API_BASE_URL_PROD=<YOUR_API_BASE_URL>
```

---

### C) App shows connection failure / timeout
**Cause:** Device cannot reach backend (DNS, VPN, firewall, private routing).

**Fix:**
1. Validate URL format includes `/api/v1`
2. Verify device is on VPN/private network
3. Run from laptop/device network:
```bash
curl -i <YOUR_API_BASE_URL>/auth/me
```
4. Check backend logs for inbound requests

---

### D) HTTP 410 from auth endpoints
**Cause:** Attempted legacy password auth endpoint (`/auth/login`, `/auth/token`, etc.).

**Fix:** Use `/auth/me` internal-service flow only.

---

### E) CI build fails because `API_BASE_URL` is empty
**Cause:** Missing repository variable.

**Fix:** Add `API_BASE_URL` in GitHub Actions Variables and rerun workflow.

---

## 14) Optional: one-command local build script

**Purpose:** Reduce manual mistakes.

Create `scripts/build_mobile_debug.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

API_BASE_URL="${1:-<YOUR_API_BASE_URL>}"

cd mobile
flutter pub get
flutter build apk --debug --dart-define=API_BASE_URL_PROD="${API_BASE_URL}"

echo "APK built at: mobile/build/app/outputs/flutter-apk/app-debug.apk"
```

Run:

```bash
bash scripts/build_mobile_debug.sh <YOUR_API_BASE_URL>
```

**Expected output:** Repeatable debug APK build with explicit backend URL.

---

## 15) Minimal quick-start (copy/paste)

```bash
git clone <YOUR_REPOSITORY_URL>
cd <YOUR_REPO_NAME>/mobile
flutter pub get
flutter build apk --debug --dart-define=API_BASE_URL_PROD=<YOUR_API_BASE_URL>
```

APK output:

```text
mobile/build/app/outputs/flutter-apk/app-debug.apk
```

