# Django-Allauth OAuth Setup Guide

## 📋 Overview
Your BookHub application now has Google and Facebook social login integrated! This guide explains how to set up the OAuth credentials and test the implementation.

---

## 🔑 Part 1: Google OAuth Setup

### Step 1: Create Google Cloud Console Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project** → **New Project**
3. Name it: `BookHub Library`
4. Click **Create**

### Step 2: Enable Google+ API

1. In the search bar, type: `Google+ API`
2. Click on the result
3. Click **Enable**

### Step 3: Create OAuth 2.0 Credentials

1. Go to **Credentials** (left sidebar)
2. Click **+ Create Credentials** → **OAuth 2.0 Client ID**
3. You may be prompted to create a consent screen first:
   - Choose **External** user type
   - Fill in basic info (App name, support email, etc.)
   - Add required scopes: `email` and `profile`
   - Add yourself as a test user

4. Return to **Credentials** → **+ Create Credentials** → **OAuth 2.0 Client ID**
5. Application type: **Web application**
6. Name: `BookHub Web`

### Step 4: Configure Redirect URLs

**Authorized JavaScript origins:**
```
http://localhost:8000
http://127.0.0.1:8000
```

**Authorized redirect URIs:**
```
http://localhost:8000/accounts/google/login/callback/
```

### Step 5: Copy Credentials

1. Click the created credential
2. Copy the **Client ID**
3. Copy the **Client Secret**

### Step 6: Add to .env

Open `.env` in your project root and update:

```env
GOOGLE_OAUTH2_KEY=YOUR_CLIENT_ID_HERE
GOOGLE_OAUTH2_SECRET=YOUR_CLIENT_SECRET_HERE
```

Example:
```env
GOOGLE_OAUTH2_KEY=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_OAUTH2_SECRET=GOCSPX-aBcDeFgHiJkLmNoP
```

---

## 🔑 Part 2: Facebook OAuth Setup

### Step 1: Go to Facebook Developers

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Login with your Facebook account (create one if needed)
3. Click **My Apps** → **Create App**

### Step 2: Create App

1. Choose **Consumer** as the app type
2. Fill in app details:
   - App Name: `BookHub Library`
   - App Contact Email: Your email
3. Click **Create App ID**

### Step 3: Add Facebook Login Product

1. In your app dashboard, find **Products** section
2. Click **+ Add Product**
3. Search for **Facebook Login**
4. Click **Set Up**
5. Choose **Web** as platform

### Step 4: Configure App Domains & URLs

1. Go to **Settings** → **Basic**
2. Add **App Domains**:
   ```
   localhost:8000
   127.0.0.1:8000
   ```

3. Go to **Facebook Login** → **Settings**
4. Add **Valid OAuth Redirect URIs**:
   ```
   http://localhost:8000/accounts/facebook/login/callback/
   ```

### Step 5: Copy Credentials

1. Go to **Settings** → **Basic**
2. Copy **App ID**
3. Copy **App Secret** (click Show to reveal)

### Step 6: Add to .env

Open `.env` and update:

```env
FACEBOOK_OAUTH2_KEY=YOUR_APP_ID_HERE
FACEBOOK_OAUTH2_SECRET=YOUR_APP_SECRET_HERE
```

Example:
```env
FACEBOOK_OAUTH2_KEY=1234567890123456
FACEBOOK_OAUTH2_SECRET=abcdef1234567890abcdef1234567890
```

---

## 🔧 Part 3: Register Credentials in Django Admin

### Step 1: Start the Server

```bash
python manage.py runserver
```

### Step 2: Create Superuser (if you don't have one)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Step 3: Access Django Admin

1. Go to `http://localhost:8000/admin/`
2. Login with your superuser account

### Step 4: Add Google Social Application

1. Click **Social applications** → **Add Social application**
2. Fill in:
   - **Provider**: Google
   - **Name**: Google
   - **Client ID**: (paste from Google Cloud Console)
   - **Secret key**: (paste from Google Cloud Console)
   - **Sites**: Select "example.com" (or whatever site is available)
3. Click **Save**

### Step 5: Add Facebook Social Application

1. Click **Social applications** → **Add Social application**
2. Fill in:
   - **Provider**: Facebook
   - **Name**: Facebook
   - **Client ID**: (paste App ID from Facebook)
   - **Secret key**: (paste App Secret from Facebook)
   - **Sites**: Select the same site as Google
3. Click **Save**

---

## 🧪 Part 4: Testing the Implementation

### Test 1: Traditional Email/Password Login

**URL**: `http://localhost:8000/login/`

**Steps**:
1. Enter any existing user's email and password
2. Should login successfully and redirect to home page
3. Should see "Welcome back, [name]!" message

**Expected Result**: ✅ Login works, session created

---

### Test 2: Google OAuth Login

**URL**: `http://localhost:8000/login/`

**Steps**:
1. Click the **Google** button
2. Login with a Google account
3. Grant permissions when prompted
4. Should auto create UserProfile and redirect to home

**Expected Result**: ✅ User created, UserProfile created, logged in

---

### Test 3: Facebook OAuth Login

**URL**: `http://localhost:8000/login/`

**Steps**:
1. Click the **Facebook** button
2. Login with a Facebook account
3. Grant permissions when prompted
4. Should auto create UserProfile and redirect to home

**Expected Result**: ✅ User created, UserProfile created, logged in

---

### Test 4: Duplicate Account Prevention

**Steps**:
1. Create a user with email `john@example.com` via signup form
2. Try to login with Google using the same email
3. Should link to existing account (not create new one)
4. Check in `http://localhost:8000/admin/auth/user/` - only 1 user with that email

**Expected Result**: ✅ No duplicate accounts, social linked to existing user

---

### Test 5: Verify UserProfile Auto-Creation

**Steps**:
1. Login via Google or Facebook with a new account
2. Go to admin: `http://localhost:8000/admin/library/userprofile/`
3. Look for the newly created user
4. Check that phone, address, pincode are empty strings (user can fill later)

**Expected Result**: ✅ UserProfile exists with empty fields

---

### Test 6: Test Signup Page

**URL**: `http://localhost:8000/signup/`

**Steps**:
1. Click **Google** or **Facebook** button
2. Login with social account
3. Should create user and UserProfile directly

**Expected Result**: ✅ Social signup works

---

### Test 7: Logout

**Steps**:
1. You should see a logout link in navigation
2. Click logout
3. Should redirect to home page
4. Should be able to login again

**Expected Result**: ✅ Logout works, session cleared

---

## 📝 Environment Variables Reference

Your `.env` file should look like:

```env
# Django Configuration
DEBUG=True
DJANGO_SECRET_KEY=django-insecure-k%w6daxgzrb96&bbx%=jer@ys452zyqa)7_=9vo8yai07lqfx8
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_ENGINE=django.db.backends.mysql
DB_NAME=bookhub_db
DB_USER=root
DB_PASSWORD=2614
DB_HOST=localhost
DB_PORT=3306

# Google OAuth
GOOGLE_OAUTH2_KEY=your-google-client-id-here
GOOGLE_OAUTH2_SECRET=your-google-client-secret-here

# Facebook OAuth
FACEBOOK_OAUTH2_KEY=your-facebook-app-id-here
FACEBOOK_OAUTH2_SECRET=your-facebook-app-secret-here

# Email Configuration (Optional for password reset)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## 🔐 Security Best Practices

### For Development ✅
- Keep credentials in `.env` file (never commit)
- `.env` is already in `.gitignore`
- `DEBUG=True` is fine for development

### For Production 🔒
Before deploying to production:

1. **Update settings.py** to add security headers:
   ```python
   if not DEBUG:
       SECURE_SSL_REDIRECT = True
       SESSION_COOKIE_SECURE = True
       CSRF_COOKIE_SECURE = True
   ```

2. **Update .env**:
   ```env
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   DJANGO_SECRET_KEY=your-production-secret-key
   ```

3. **Update OAuth Console**:
   - Add production domain to **Authorized JavaScript origins**
   - Update redirect URIs to production domain
   - Example: `https://yourdomain.com/accounts/google/login/callback/`

4. **Enable HTTPS**: Required for OAuth

---

## ✅ Checklist to Verify Setup

- [ ] Installed `django-allauth` and `django-environ`
- [ ] Created `.env` file with all required variables
- [ ] Updated `settings.py` with allauth configuration
- [ ] Ran migrations: `python manage.py migrate`
- [ ] Created Django superuser: `python manage.py createsuperuser`
- [ ] Got Google OAuth credentials from Google Cloud Console
- [ ] Got Facebook OAuth credentials from Facebook Developers
- [ ] Added credentials to `.env` file
- [ ] Registered social applications in Django admin
- [ ] Tested traditional email/password login
- [ ] Tested Google OAuth login
- [ ] Tested Facebook OAuth login
- [ ] Tested duplicate account prevention
- [ ] Verified UserProfile auto-creation

---

## 🆘 Troubleshooting

### Error: "Invalid redirect URL"
**Solution**: Make sure the redirect URI in OAuth provider matches exactly:
- Google: `http://localhost:8000/accounts/google/login/callback/`
- Facebook: `http://localhost:8000/accounts/facebook/login/callback/`

### Error: "Client ID not found"
**Solution**:
1. Verify credentials are in `.env` with correct variable names:
   - `GOOGLE_OAUTH2_KEY` (not `GOOGLE_CLIENT_ID`)
   - `FACEBOOK_OAUTH2_KEY` (not `FACEBOOK_APP_ID`)
2. Check that social application is registered in Django admin
3. Restart the server after adding credentials

### Error: "Email already exists"
**Solution**: This is expected if using an email that already has an account. The system will link the social account to the existing user.

### Error: "The request must contain a 'state' parameter"
**Solution**: This usually means allauth URLs are not configured correctly. Verify:
- `path('accounts/', include('allauth.urls'))` is in `bookhub_backend/urls.py`
- Server was restarted after adding the URL

### Social accounts not linking to existing users
**Solution**: Check `library/adapters.py` is importing correctly in `library/apps.py`. The signals in `library/signals.py` provide redundancy.

---

## 📚 Available Allauth URLs

These URLs are automatically available once you've completed setup:

| URL | Purpose |
|-----|---------|
| `/accounts/login/` | Allauth login page (alternative to /login/) |
| `/accounts/signup/` | Allauth signup page (alternative to /signup/) |
| `/accounts/logout/` | Logout (clears session, redirects to home) |
| `/accounts/email/` | Manage email addresses |
| `/accounts/google/login/` | Direct Google OAuth link |
| `/accounts/facebook/login/` | Direct Facebook OAuth link |
| `/accounts/social/connections/` | Link/unlink multiple social accounts |

---

## 🎉 You're All Set!

Your BookHub platform now supports:
✅ Traditional email/password authentication
✅ Google OAuth login
✅ Facebook OAuth login
✅ Automatic UserProfile creation for all users
✅ Duplicate account prevention via email matching

Happy coding! 🚀
