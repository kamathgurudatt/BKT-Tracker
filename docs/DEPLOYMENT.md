# Deployment Guide

## Docker Compose

Use `docker compose up --build` for local education. Production deployments should split API, worker, beat, PostgreSQL, and Redis into separately monitored services.

## Environment variables

Copy `.env.example` and replace `SECRET_KEY`, database credentials, Redis URL, SMTP settings, and FCM credentials. Never commit real secrets.

## CI/CD

GitHub Actions runs Python compile checks and Flutter static analysis when Flutter is available on the runner. Add deployment jobs for your cloud provider after configuring encrypted repository secrets.
