# Render deploy — exact settings (BOOK HUB)

Use these when creating or redeploying **librarymanagement-main-3** on [Render](https://dashboard.render.com).

**Live URLs after deploy**

| What | URL |
|------|-----|
| Website | https://librarymanagement-main-3.onrender.com |
| Login | https://librarymanagement-main-3.onrender.com/en/library/login/ |
| Health check | https://librarymanagement-main-3.onrender.com/en/library/health/ |
| Database test | https://librarymanagement-main-3.onrender.com/en/library/test-db/ |

---

## Service settings

| Field | Value |
|-------|--------|
| **Root Directory** | `project_code` |
| **Build Command** | `pip install -r requirements.txt && python manage.py collectstatic --noinput` |
| **Start Command** | `gunicorn bookhub_backend.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |
| **Health Check Path** | `/en/library/health/` |

---

## Environment variables (add all 6)

| # | KEY | VALUE |
|---|-----|--------|
| 1 | `MONGODB_URI` | `mongodb+srv://bipinsagarmatha321_db_user:BookHubRender2026@cluster0.3f7teqs.mongodb.net/bookhub_db?retryWrites=true&w=majority&appName=Cluster0` |
| 2 | `DJANGO_DATABASE_URL` | **Same exact URI as `MONGODB_URI`** |
| 3 | `MONGODB_NAME` | `bookhub_db` |
| 4 | `DEBUG` | `False` |
| 5 | `SECRET_KEY` | `bookhub-super-secret-key-2026-render` |
| 6 | `FRONTEND_URL` | `https://librarymanagement-main-3.onrender.com` |

Optional but recommended:

| KEY | VALUE |
|-----|--------|
| `ALLOWED_HOSTS` | `.onrender.com,librarymanagement-main-3.onrender.com` |

**Atlas (before deploy):**

1. [MongoDB Atlas](https://cloud.mongodb.com) → **Database Access** → user `bipinsagarmatha321_db_user` → password **`BookHubRender2026`**
2. **Network Access** → add **`0.0.0.0/0`**

---

## Deploy

1. Add all settings and env vars above.
2. Click **Deploy Web Service** (or **Manual Deploy** → **Clear build cache & deploy**).
3. Wait until status is **Your service is live**.

---

## Test after deploy

1. **Website:** https://librarymanagement-main-3.onrender.com — books should appear (not “No books found”).
2. **Database:** https://librarymanagement-main-3.onrender.com/en/library/test-db/

   **Want:**

   ```json
   {"status": "success", "message": "Connected to DB. Book count: ..."}
   ```

   **If you see** `bad auth` or `authentication failed` → Atlas password does not match the URI on Render. Fix Atlas + env vars, save, redeploy.

---

## Create admin (only after database test succeeds)

Render → service → **Shell**:

```bash
cd project_code
python manage.py bootstrap_admin --email bipinsagarmatha123@gmail.com --password "Test123@"
```

---

## Login

https://librarymanagement-main-3.onrender.com/en/library/login/

| Field | Value |
|-------|--------|
| Email | `bipinsagarmatha123@gmail.com` |
| Password | `Test123@` |

---

## Architecture

```
Frontend (templates)  ✅  — loads on Render
Backend (Django)      ✅  — gunicorn + API/views
Database (MongoDB)    ❌ until test-db shows "success"
```

When the database connects, admin dashboard, delivery dashboard, login, rentals, users, categories, and search all get data from MongoDB.
