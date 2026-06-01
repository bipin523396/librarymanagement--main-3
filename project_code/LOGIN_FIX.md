# Login fix guide (Render)

## What was broken

1. **No error messages on login page** — failed logins looked like "nothing happened".
2. **`update_last_login`** could crash MongoDB user saves (now disconnected in `apps.py`).
3. **Auth** improved for email + username login (`MongoModelBackend`).
4. **Database** must work before any user can log in.

## Step 1 — Push code and redeploy Render

Push latest code, then **Manual Deploy** on Render.

## Step 2 — Fix MongoDB on Render

Open: https://librarymanagement-main-3.onrender.com/en/library/test-db/

Must show: `"status": "success"`

If not, fix `MONGODB_URI` and `DJANGO_DATABASE_URL` in Render Environment (same value, password `@` → `%40`).

## Step 3 — Create admin user on Render Shell

Render Dashboard → your service → **Shell**:

```bash
cd project_code
python manage.py bootstrap_admin --email YOUR_EMAIL@gmail.com --password YOUR_PASSWORD
```

Example:

```bash
python manage.py bootstrap_admin --email bipinsagarmatha123@gmail.com --password MySecurePass123
```

## Step 4 — Login

https://librarymanagement-main-3.onrender.com/en/library/login/

Use **exactly** the email and password from Step 3.

- **Admin** (superuser) → Admin dashboard  
- **Delivery staff** account → Delivery dashboard  
- **Normal user** → Home page  

## If login still fails

| Symptom | Fix |
|---------|-----|
| Red box "Invalid username or password" | Wrong password or user not created — run `bootstrap_admin` again |
| 403 Forbidden | Redeploy latest code (CSRF fix for Render host) |
| Page reloads, no message | Redeploy — messages now show on login page |
| Works then logged out on refresh | Clear cookies; use same browser tab |

## Verify in Render logs

After deploy you should see:

```
✅ update_last_login disconnected for MongoDB compatibility
MongoDB: user=bipinsagarmatha321_db_user uri=mongodb+srv://...
```
