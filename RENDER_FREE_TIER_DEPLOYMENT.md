# Render Free Tier Deployment Guide

Perfect! The configuration is now updated for Render's **FREE TIER**.

## What's Included in Free Tier ✅

- ✅ **Web Service** (automind-api) - FREE
  - Spins down after 15 minutes of inactivity
  - Cold start takes ~30 seconds on first request
  - Perfect for demos and testing!

- ✅ **PostgreSQL Database** - FREE
  - 1 GB storage
  - Expires after 90 days (can be recreated)
  - More than enough for this project

- ✅ **Redis Cache** - FREE
  - 25 MB storage
  - Perfect for session management

**Total Cost: $0/month** 🎉

---

## Deploy Now (5 Minutes)

### Step 1: Go to Render Dashboard

**Click here**: https://dashboard.render.com/blueprints

### Step 2: Connect GitHub Repository

1. Click **"New Blueprint"** (or "New +" → "Blueprint")
2. Connect your GitHub account (if not already)
3. Find and select: **`Automotive-Predictive-Maintainance-System`**
4. Click **"Connect"**

### Step 3: Review Services

Render will detect your `render.yaml` and show:

```
✅ automind-api (Web Service) - FREE plan
✅ automind-db (PostgreSQL) - FREE plan
✅ automind-redis (Redis) - FREE plan
```

All using **FREE TIER** - no credit card required!

### Step 4: Click "Apply"

Click the **"Apply"** button to start deployment.

⏱️ **Wait 5-10 minutes** for all services to deploy.

### Step 5: Get Your Backend URL

Once deployed:
1. Click on the **automind-api** service
2. Copy the URL (e.g., `https://automind-api-xxxx.onrender.com`)
3. **Share this URL with me** and I'll complete the integration!

---

## Important Free Tier Notes

### 🔄 Cold Starts
The backend spins down after 15 minutes of inactivity. First request after sleep takes ~30 seconds to wake up.

**Solution**: Just wait 30 seconds on first load. Subsequent requests are instant!

### 📅 Database Expiry
Free PostgreSQL databases expire after 90 days.

**Solution**: Export data before expiry, or upgrade to paid tier ($7/month).

### 💾 Storage Limits
- Database: 1 GB (plenty for thousands of vehicles)
- Redis: 25 MB (enough for active sessions)

---

## After Deployment

Once you have your backend URL, I will automatically:

1. ✅ Configure CORS in Render
2. ✅ Update Vercel environment variables
3. ✅ Redeploy frontend with correct endpoints
4. ✅ Initialize database with demo data
5. ✅ Test the complete integration
6. ✅ Give you the working application!

---

## Alternative: Manual Web Service (If Blueprint Doesn't Work)

If the Blueprint deployment has issues, you can deploy manually:

### 1. Create PostgreSQL Database
- Go to Render Dashboard → New → PostgreSQL
- Name: `automind-db`
- Plan: **Free**
- Click "Create Database"
- Copy the **Internal Database URL**

### 2. Create Redis
- Go to Render Dashboard → New → Redis
- Name: `automind-redis`
- Plan: **Free**
- Click "Create Redis"
- Copy the **Internal Redis URL**

### 3. Create Web Service
- Go to Render Dashboard → New → Web Service
- Connect your GitHub repository
- Select: `Automotive-Predictive-Maintainance-System`
- Settings:
  - **Name**: `automind-api`
  - **Runtime**: Python
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `gunicorn api_server:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120`
  - **Plan**: **Free**

### 4. Add Environment Variables
Add these in the Environment tab:

```bash
DATABASE_URL=<paste Internal Database URL>
REDIS_URL=<paste Internal Redis URL>
PYTHON_VERSION=3.9.16
APP_ENV=production
DEBUG=false
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
MAX_RETRIES=3
CIRCUIT_BREAKER_THRESHOLD=5
LOG_LEVEL=INFO
CORS_ORIGINS=https://frontend-3g3y76a8y-aryas-projects-6676c3c7.vercel.app
SECRET_KEY=<generate random string>
JWT_SECRET_KEY=<generate random string>
```

### 5. Deploy
Click "Create Web Service" and wait for deployment!

---

## Need Help?

Just share your Render backend URL once it's deployed, and I'll handle everything else!

**Your frontend is already live**: https://frontend-3g3y76a8y-aryas-projects-6676c3c7.vercel.app

---

**Total Cost: $0** 🎉
**Deployment Time: ~10 minutes** ⏱️
