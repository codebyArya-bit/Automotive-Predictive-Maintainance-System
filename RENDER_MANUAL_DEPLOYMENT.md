# Render Manual Deployment Guide (SQLite - No Database Needed)

## 🚀 Quick Manual Deployment (5 Minutes)

### Step 1: Create New Web Service

Go to: https://dashboard.render.com/

1. Click **"New +"** button (top right)
2. Select **"Web Service"**
3. Click **"Build and deploy from a Git repository"**
4. Find and click **"Connect"** next to: `Automotive-Predictive-Maintainance-System`

---

### Step 2: Basic Configuration

Fill in these fields:

| Field | Value |
|-------|-------|
| **Name** | `automind-api` |
| **Region** | (Select closest to you, e.g., Oregon (US West)) |
| **Branch** | `main` |
| **Runtime** | **Python 3** |
| **Root Directory** | (leave blank) |

---

### Step 3: Build & Start Commands

**Build Command** (copy exactly):
```bash
pip install -r requirements.txt
```

**Start Command** (copy exactly):
```bash
python startup.py && gunicorn api_server:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120
```

---

### Step 4: Select Plan

**Instance Type**: **Free** ✅

---

### Step 5: Environment Variables

Scroll down to **"Environment Variables"** section.

Click **"Add Environment Variable"** and add these one by one:

#### Required Variables:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | `sqlite:///./automotive_ai.db` |
| `USE_SQLITE` | `true` |
| `CORS_ORIGINS` | `https://automind-ai.vercel.app` |
| `PYTHON_VERSION` | `3.9.16` |
| `APP_ENV` | `production` |
| `DEBUG` | `false` |
| `JWT_ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |
| `LOG_LEVEL` | `INFO` |
| `MAX_RETRIES` | `3` |
| `CIRCUIT_BREAKER_THRESHOLD` | `5` |
| `HEALTH_CHECK_INTERVAL` | `30` |

#### Auto-Generated Variables:

For these two, click the **"Generate"** button instead of entering a value:

| Key | Action |
|-----|--------|
| `SECRET_KEY` | Click **"Generate"** |
| `JWT_SECRET_KEY` | Click **"Generate"** |

---

### Step 6: Advanced Settings (Optional)

Scroll to **"Advanced"** section (you can skip this or configure):

- **Health Check Path**: `/api/v1/health`
- **Auto-Deploy**: Yes (recommended)

---

### Step 7: Deploy!

Click the big **"Create Web Service"** button at the bottom.

⏱️ **Wait 5-10 minutes** for deployment to complete.

---

## After Deployment

### Your Backend URL

Once deployed, you'll see your backend URL at the top:
```
https://automind-api.onrender.com
```

**Copy this URL!** You'll need it for the frontend integration.

---

### Test Your Backend

Visit this URL to test:
```
https://automind-api.onrender.com/api/v1/health
```

You should see:
```json
{
  "status": "healthy",
  "database": "connected",
  ...
}
```

---

## What You Get (FREE):

✅ Full FastAPI backend
✅ SQLite database (file-based)
✅ All API endpoints working
✅ Authentication system
✅ Multi-agent system
✅ Dashboard & monitoring
✅ Real-time updates

**Limitation**: Service spins down after 15 min of inactivity. First request after sleep takes ~30 seconds.

---

## Next Steps

Once deployed:

1. ✅ Copy your backend URL
2. ✅ Share it with me
3. ✅ I'll update your frontend automatically
4. ✅ Complete integration
5. ✅ You'll have a working app!

---

**Cost**: $0 (completely FREE!) 🎉
