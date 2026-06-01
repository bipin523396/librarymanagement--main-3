# Render deploy — exact settings (BOOK HUB)

**Passwords are set only in MongoDB Atlas + Render — not in code.**

**Live URLs**

| What | URL |
|------|-----|
| Website | https://librarymanagement-main-3.onrender.com |
| Login | https://librarymanagement-main-3.onrender.com/en/library/login/ |
| Database test | https://librarymanagement-main-3.onrender.com/en/library/test-db/ |

---

## STEP 1 — MongoDB Atlas

1. [MongoDB Atlas](https://cloud.mongodb.com) → **Database Access** → user **`bookhub_user`**
2. **Edit Password** → set to: **`Sagarmatha321`**
3. **Update User**
4. **Network Access** → **`0.0.0.0/0`** allowed

---

## STEP 2 — Render environment variables

[Render service](https://dashboard.render.com/web/srv-d8e55lcm0tmc73ei3u0g) → **Environment**

| KEY | VALUE |
|-----|--------|
| `MONGODB_URI` | `mongodb+srv://bookhub_user:Sagarmatha321@cluster0.3f7teqs.mongodb.net/bookhub_db?retryWrites=true&w=majority&appName=Cluster0` |
| `DJANGO_DATABASE_URL` | **Same exact URI as `MONGODB_URI`** |
| `MONGODB_NAME` | `bookhub_db` |
| `DEBUG` | `False` |

**Service settings**

| Field | Value |
|-------|--------|
| Root Directory | `project_code` |
| Build Command | `pip install -r requirements.txt && python manage.py collectstatic --noinput` |
| Start Command | `bash start.sh` |
| Health Check Path | `/health/` |

---

## STEP 3 — Deploy

**Manual Deploy** → **Clear build cache & deploy** → wait until **Live**

---

## STEP 4 — Test

Open: https://librarymanagement-main-3.onrender.com/en/library/test-db/

**Success:**

```json
{"status": "success", "message": "Connected to DB. Book count: ..."}
```

Then create admin (Render Shell):

```bash
cd project_code
python manage.py bootstrap_admin --email bipinsagarmatha123@gmail.com --password "Test123@"
```

Login: https://librarymanagement-main-3.onrender.com/en/library/login/

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `no-server` on all URLs | Render → **Resume** → redeploy |
| `bad auth` on test-db | Atlas password must match URI (`Sagarmatha321`) |
| Login fails | Run `bootstrap_admin` on Render Shell |
