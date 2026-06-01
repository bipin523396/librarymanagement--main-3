# BOOK HUB — Library Management System

Django app with MongoDB (Djongo), admin dashboard, delivery portal, and rentals.

## Production (Render)

- **Site:** https://librarymanagement-main-3.onrender.com
- **Deploy guide:** [RENDER_DEPLOY.md](RENDER_DEPLOY.md)
- **Login help:** [project_code/LOGIN_FIX.md](project_code/LOGIN_FIX.md)

## Local development

```bash
cd project_code
python -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit MongoDB URI
python manage.py migrate
python manage.py runserver
```

Open: http://127.0.0.1:8000/en/library/

## Create admin (local or Render shell)

```bash
python manage.py bootstrap_admin --email you@example.com --password YourPass123
```
