# Deploy to Render - Quick Guide

## Your Frontend is Already Deployed! ✅

**Frontend URL**: https://frontend-3g3y76a8y-aryas-projects-6676c3c7.vercel.app

---

## Now Deploy the Backend (5 minutes)

### Step 1: Go to Render Dashboard

Click this link: **https://dashboard.render.com/blueprints**

### Step 2: Create New Blueprint

1. Click the **"New Blueprint"** button (or "New +" → "Blueprint")
2. If asked, connect your GitHub account
3. Select your repository: **`Automotive-Predictive-Maintainance-System`**
4. Click **"Connect"**

### Step 3: Review Services

Render will show you 3 services to create:

- ✅ **automind-api** (Web Service) - Your FastAPI backend
- ✅ **automind-db** (PostgreSQL Database) - Database
- ✅ **automind-redis** (Redis) - Cache

### Step 4: Click "Apply"

Click the big **"Apply"** button to create all services.

### Step 5: Wait for Deployment (5-10 minutes)

You'll see the services being created. Wait until **automind-api** shows "Live".

### Step 6: Copy Your Backend URL

Once deployed, you'll see your backend URL. It will look like:
```
https://automind-api-XXXX.onrender.com
```

**Copy this URL!** You'll need it for the next step.

---

## Step 7: Configure CORS

1. In Render Dashboard, click on **automind-api** service
2. Go to **"Environment"** tab
3. Click **"Add Environment Variable"**
4. Add this variable:
   - **Key**: `CORS_ORIGINS`
   - **Value**: `https://frontend-3g3y76a8y-aryas-projects-6676c3c7.vercel.app`
5. Click **"Save Changes"**

The service will automatically redeploy (takes ~2 minutes).

---

## Step 8: Update Frontend

Once you have your Render backend URL, run these commands:

```bash
# Update frontend environment variables
vercel env add VITE_API_BASE_URL production
# When prompted, enter: https://YOUR-RENDER-URL.onrender.com/api/v1

vercel env add VITE_WS_URL production
# When prompted, enter: wss://YOUR-RENDER-URL.onrender.com/ws

# Redeploy frontend
vercel --prod
```

Replace `YOUR-RENDER-URL` with your actual Render backend URL!

---

## Step 9: Initialize Database

Once the backend is running:

1. Go to Render Dashboard → **automind-api** service
2. Click **"Shell"** tab
3. Run this command:
   ```bash
   python generate_automotive_data.py
   ```

This will populate your database with demo data.

---

## Step 10: Test Everything!

Visit your frontend:
```
https://frontend-3g3y76a8y-aryas-projects-6676c3c7.vercel.app
```

Login with:
- **Username**: admin
- **Password**: admin123

---

## Quick Troubleshooting

### Backend shows "Failed"
- Check the logs in Render Dashboard
- Make sure all environment variables are set
- Database URL and Redis URL should be automatically set

### Frontend shows CORS errors
- Make sure you added CORS_ORIGINS in Render
- Make sure the URL matches exactly (no trailing slash)

### Login doesn't work
- Make sure database is initialized
- Check backend logs in Render
- Make sure backend health endpoint works: https://YOUR-URL.onrender.com/api/v1/health

---

## Need Help?

Check the full deployment guide: `VERCEL_RENDER_DEPLOYMENT_GUIDE.md`

---

**Current Status:**
- ✅ Repository pushed to GitHub
- ✅ Frontend deployed to Vercel
- ⏳ Backend deployment (waiting for you to click "Apply" in Render)
- ⏳ Final integration

You're almost there!
