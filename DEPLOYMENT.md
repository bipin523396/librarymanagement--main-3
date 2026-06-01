# BOOK HUB — Vercel + Render deployment

## Architecture

| Layer | Platform | Role |
|-------|----------|------|
| Frontend URL | **Vercel** | Public URL; proxies all traffic to Render |
| Backend | **Render** | Django + Gunicorn (Docker) |
| Database | **MongoDB Atlas** | Connected via `MONGODB_URI` |

## 1. Render (backend)

1. Create a **Web Service** → connect repo → use **Docker** (`Dockerfile` at repo root).
2. Set environment variables (see `.env.example`):
   - `MONGODB_URI` — Atlas connection string
   - `SECRET_KEY` — long random string
   - `DEBUG=False`
   - `ALLOWED_HOSTS=.onrender.com,.vercel.app`
   - `FRONTEND_URL=https://YOUR-APP.vercel.app`
3. Deploy and note your URL: **`https://librarymanagement-main-3.onrender.com`** (your Render service).
4. Health check: `https://YOUR-SERVICE.onrender.com/en/library/health/`

## 2. Vercel (frontend proxy)

1. Import the same repo in Vercel.
2. Edit **`vercel.json`** — set `destination` to your **exact Render URL**:

```json
"destination": "https://librarymanagement-main-3.onrender.com/$1"
```

3. Redeploy Vercel.

Do **not** use the old Python serverless build (`project_code/api/index.py`); it is replaced by proxy rewrites.

## 3. MongoDB Atlas (fix `bad auth`)

In [Render Environment](https://dashboard.render.com/web/srv-d8e55lcm0tmc73ei3u0g) set **both** keys to the **same** value:

| Key | Value |
|-----|--------|
| `MONGODB_URI` | `mongodb+srv://bipinsagarmatha321_db_user:%40YOUR_PASSWORD@cluster0.3f7teqs.mongodb.net/bookhub_db?retryWrites=true&w=majority&appName=Cluster0` |
| `DJANGO_DATABASE_URL` | *(same as MONGODB_URI)* |
| `MONGODB_NAME` | `bookhub_db` |

Password `@Sagarmatha321` → use `%40` instead of `@` in the URL.

**Atlas checks:**

1. **Database Access** → user `bipinsagarmatha321_db_user` exists, password matches.
2. **Network Access** → allow `0.0.0.0/0` (for Render).
3. Render → **Manual Deploy** → **Clear build cache & deploy**.

**Verify:**

- https://librarymanagement-main-3.onrender.com/en/library/test-db/ → `{"status":"success",...}`
- https://librarymanagement-main-3.onrender.com/en/library/health/ → `"database":"connected"`

On Render shell: `python check_mongo.py`

## 4. Verify

- Render: `/en/library/health/` → `{"status":"ok"}`
- Render: `/en/library/test-db/` → book count
- Vercel: `/en/library/login/` → login page (proxied from Render)

## Common errors

| Error | Fix |
|-------|-----|
| 404 on Vercel | Update `vercel.json` Render URL; redeploy Vercel |
| 503 on Render | Check logs; set `MONGODB_URI`; wait for cold start |
| CSRF / login fails | Set `FRONTEND_URL` on Render; `DEBUG=False` |
| DisallowedHost | Add host to `ALLOWED_HOSTS` |
| Static files missing | Redeploy Render (runs `collectstatic` in Docker) |
