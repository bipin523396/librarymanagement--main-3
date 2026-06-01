# Deploy BOOK HUB on Render (only)

Live URL: **https://librarymanagement-main-3.onrender.com**

## Option A — Connect GitHub (recommended)

1. [Render Dashboard](https://dashboard.render.com/) → **New** → **Blueprint** (or open existing service).
2. Connect repo: `bipin523396/librarymanagement--main-3`.
3. Render reads `render.yaml` automatically.

## Option B — Manual Web Service

| Setting | Value |
|---------|--------|
| **Root Directory** | `project_code` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt && python manage.py collectstatic --noinput` |
| **Start Command** | `gunicorn bookhub_backend.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120` |
| **Health Check Path** | `/en/library/health/` |

## Required environment variables

| Key | Value |
|-----|--------|
| `MONGODB_URI` | `mongodb+srv://USER:%40PASSWORD@cluster0.3f7teqs.mongodb.net/bookhub_db?retryWrites=true&w=majority&appName=Cluster0` |
| `DJANGO_DATABASE_URL` | Same as `MONGODB_URI` |
| `MONGODB_NAME` | `bookhub_db` |
| `SECRET_KEY` | Long random string |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.onrender.com,localhost,127.0.0.1` |

Password `@Sagarmatha321` → use `%40Sagarmatha321` in the URL.

## After first deploy

**Shell** on Render:

```bash
python manage.py bootstrap_admin --email YOUR_EMAIL@gmail.com --password YOUR_PASSWORD
```

Then login: `/en/library/login/`

## Verify

- Health: `/en/library/health/`
- Database: `/en/library/test-db/` → `"status":"success"`
- Login: `/en/library/login/`

See also: `project_code/LOGIN_FIX.md`
