# Render setup (confirmed working)

Use these settings in [Render Dashboard](https://dashboard.render.com/web/srv-d8e55lcm0tmc73ei3u0g):

| Field | Value |
|-------|--------|
| **Root Directory** | `project_code` |
| **Build Command** | `pip install -r requirements.txt && python manage.py collectstatic --noinput` |
| **Start Command** | `gunicorn bookhub_backend.wsgi:application` |
| **Instance Type** | Free |

## Environment variables

| KEY | VALUE |
|-----|--------|
| `MONGODB_URI` | your `mongodb+srv://bipinsagarmatha321_db_user:%40...@cluster0...` URI |
| `DJANGO_DATABASE_URL` | same as `MONGODB_URI` |
| `SECRET_KEY` | `django-insecure-bookhub-secret-key-2026` (or generate a new one) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.vercel.app,.onrender.com` |
| `MONGODB_NAME` | `bookhub_db` |
| `FRONTEND_URL` | `https://librarymanagement-main-3.vercel.app` |

## Live URL

https://librarymanagement-main-3.onrender.com

## Test after deploy

- Login: https://librarymanagement-main-3.onrender.com/en/library/login/
- Home: https://librarymanagement-main-3.onrender.com/

Push latest GitHub code to enable `/en/library/health/` and `/en/library/test-db/`.
