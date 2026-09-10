# TJ Tutoring Academy — Render Backend Deployment

This backend is prepared for Render Web Service + Render Postgres.

## Render service

- Runtime: Python
- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `flask --app run.py db upgrade && exec gunicorn --workers 1 --bind 0.0.0.0:$PORT run:app`
- Health check: `/health`

## Required environment variables

- `DATABASE_URL` — use the Render Postgres connection string.
- `SECRET_KEY` — long random secret.
- `JWT_SECRET_KEY` — separate long random secret.
- `FLASK_ENV=production`
- `CORS_ORIGINS=https://tjtutoring.academy,https://www.tjtutoring.academy`
- `LOG_LEVEL=INFO`
- `LOG_FORMAT=text`
- `NOTIFY_EMAIL=hello@tjtutoring.academy`

The included `render.yaml` can create the web service and a temporary Free Postgres database together.

## Important: testing database

Render Free Postgres is for testing only and expires after 30 days. It also has no backups. Upgrade the database before using it as the permanent production database.

## First deployment test

After deploy, open:

`https://<render-service>.onrender.com/health`

Expected response:

```json
{"status":"ok","service":"tj-tutoring-academy-api"}
```

## Custom API domain

After the service works, add:

`api.tjtutoring.academy`

in Render's Custom Domains section. Render will provide the DNS target. Add the DNS record at the domain's DNS provider, verify it in Render, and wait for TLS to become active.

## Admin account

After migrations complete, create/reset the production admin with:

`ADMIN_EMAIL="..." ADMIN_PASSWORD="..." python reset_admin.py`

Do not commit the admin password or any `.env` file to Git.
