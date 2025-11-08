# Vercel + Render Deployment Guide
## Automotive Predictive Maintenance System

This guide will walk you through deploying the application using:
- **Vercel**: Frontend hosting (React + TypeScript)
- **Render**: Backend hosting (FastAPI + PostgreSQL + Redis)

---

## Prerequisites

1. **Accounts Created**:
   - Vercel account (https://vercel.com)
   - Render account (https://render.com)
   - GitHub account with repository access

2. **CLIs Installed**:
   ```bash
   # Install Vercel CLI
   npm install -g vercel

   # Install Render CLI (optional, but recommended)
   npm install -g render-cli
   ```

3. **Logged In**:
   ```bash
   # Login to Vercel
   vercel login

   # Login to Render (if using CLI)
   render login
   ```

---

## Part 1: Deploy Backend to Render

### Option A: Using Render Dashboard (Recommended for First Time)

#### Step 1: Create New Web Service

1. Go to https://dashboard.render.com
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Select: `Automotive-Predictive-Maintainance-System`
5. Render will detect the `render.yaml` file automatically
6. Click "Apply" to create all services (API, PostgreSQL, Redis)

#### Step 2: Configure Environment Variables

After services are created, go to the **automind-api** service:

1. Go to "Environment" tab
2. Add the following environment variables:

```bash
# CORS Configuration (IMPORTANT - will be updated after Vercel deployment)
CORS_ORIGINS=https://your-vercel-app.vercel.app

# Optional: External API Keys (if needed)
OPENAI_API_KEY=sk-your-openai-key-here

# Optional: Email/SMS Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

**Note**: The `DATABASE_URL` and `REDIS_URL` are automatically set by Render from the services.

#### Step 3: Initialize Database

Once the database is running:

1. Go to your **automind-db** PostgreSQL database
2. Click "Connect" → Copy the "External Database URL"
3. Use a PostgreSQL client or psql to run the init script:

```bash
# Using psql (install if needed)
psql "postgresql://automind_db_user:xxx@dpg-xxx.oregon-postgres.render.com/automind_db" -f init.sql

# Or using the web shell in Render dashboard
# Navigate to automind-db → Shell → Paste contents of init.sql
```

4. Or generate demo data:
```bash
# SSH into your web service (via Render dashboard Shell)
python generate_automotive_data.py
```

#### Step 4: Get Backend URL

Once deployed, your backend will be available at:
```
https://automind-api.onrender.com
```

Copy this URL - you'll need it for the frontend deployment!

### Option B: Using Render CLI

```bash
# From project root
render deploy

# Follow the prompts to select services
```

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Update Frontend Environment Variables

First, update the frontend environment file with your Render backend URL:

```bash
# Edit frontend/.env.production
nano frontend/.env.production
```

Replace with your actual Render URLs:
```bash
VITE_API_BASE_URL=https://automind-api.onrender.com/api/v1
VITE_WS_URL=wss://automind-api.onrender.com/ws
VITE_APP_NAME=AutoMind
VITE_APP_VERSION=1.0.0
VITE_ENVIRONMENT=production
```

### Step 2: Deploy to Vercel

```bash
# From project root
vercel

# Follow the prompts:
# ? Set up and deploy "~/Automotive-Predictive-Maintainance-System"? [Y/n] y
# ? Which scope do you want to deploy to? [Select your account]
# ? Link to existing project? [N/y] n
# ? What's your project's name? automind-frontend
# ? In which directory is your code located? ./
# ? Want to override the settings? [y/N] n

# This will deploy to a preview URL first
```

### Step 3: Set Production Environment Variables in Vercel

```bash
# Set environment variables for production
vercel env add VITE_API_BASE_URL production
# When prompted, enter: https://automind-api.onrender.com/api/v1

vercel env add VITE_WS_URL production
# When prompted, enter: wss://automind-api.onrender.com/ws

vercel env add VITE_APP_NAME production
# When prompted, enter: AutoMind

vercel env add VITE_ENVIRONMENT production
# When prompted, enter: production
```

Or use the Vercel Dashboard:
1. Go to https://vercel.com/dashboard
2. Select your project
3. Go to "Settings" → "Environment Variables"
4. Add the variables listed above

### Step 4: Deploy to Production

```bash
# Deploy to production
vercel --prod

# Your app will be available at:
# https://automind-frontend.vercel.app
# Or your custom domain if configured
```

---

## Part 3: Connect Frontend and Backend

### Step 1: Update CORS in Render

Now that you have your Vercel URL, update the backend CORS settings:

1. Go to Render Dashboard → automind-api service
2. Go to "Environment" tab
3. Update `CORS_ORIGINS` variable:

```bash
CORS_ORIGINS=https://automind-frontend.vercel.app,https://automind-frontend-*.vercel.app
```

**Note**: The wildcard pattern `automind-frontend-*.vercel.app` allows preview deployments to work too.

4. Click "Save Changes" - Render will automatically redeploy

### Step 2: Test the Integration

Visit your Vercel URL and test:

1. **Login Page**: Try logging in
   - Username: `admin` / Password: `admin123`
   - Or: `service_tech` / `tech123`

2. **Dashboard**: Should load vehicle data

3. **WebSocket**: Real-time updates should work

4. **API Calls**: Check browser console for any CORS errors

---

## Part 4: Custom Domain Setup (Optional)

### For Frontend (Vercel)

```bash
# Add custom domain via CLI
vercel domains add yourdomain.com

# Or via Dashboard:
# Project Settings → Domains → Add Domain
```

Configure DNS:
```
Type: CNAME
Name: www (or @)
Value: cname.vercel-dns.com
```

### For Backend (Render)

1. Go to automind-api service → "Settings"
2. Scroll to "Custom Domain"
3. Add: `api.yourdomain.com`
4. Configure DNS:
```
Type: CNAME
Name: api
Value: automind-api.onrender.com
```

5. Update environment variables:
```bash
# In Render
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# In Vercel
VITE_API_BASE_URL=https://api.yourdomain.com/api/v1
VITE_WS_URL=wss://api.yourdomain.com/ws
```

---

## Part 5: Verification & Testing

### Health Checks

```bash
# Check backend health
curl https://automind-api.onrender.com/api/v1/health

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  ...
}
```

### Test API Endpoints

```bash
# Test login
curl -X POST https://automind-api.onrender.com/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Test vehicles list
curl https://automind-api.onrender.com/api/v1/vehicles \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Frontend Testing

1. Visit your Vercel URL
2. Open browser DevTools (F12)
3. Check Console for errors
4. Check Network tab for failed requests
5. Test all major features:
   - Login/Logout
   - Dashboard loading
   - Vehicle list
   - Real-time updates
   - Agent monitoring

---

## Monitoring & Logs

### Render Logs

```bash
# View logs via CLI
render logs -s automind-api

# Or via Dashboard:
# Select service → Logs tab
```

### Vercel Logs

```bash
# View deployment logs
vercel logs

# Or via Dashboard:
# Select project → Deployments → Click deployment → View Logs
```

---

## Troubleshooting

### Issue 1: CORS Errors

**Symptoms**: Browser console shows CORS errors

**Solution**:
```bash
# In Render, update CORS_ORIGINS to include your Vercel URL
CORS_ORIGINS=https://your-vercel-app.vercel.app

# Make sure to include protocol (https://)
# No trailing slash
```

### Issue 2: Database Connection Failed

**Symptoms**: Backend logs show database connection errors

**Solution**:
1. Check that PostgreSQL service is running in Render
2. Verify DATABASE_URL is set correctly
3. Run database initialization script
4. Check database logs in Render

### Issue 3: WebSocket Not Connecting

**Symptoms**: Real-time updates don't work

**Solution**:
```bash
# Ensure WebSocket URL uses wss:// (not ws://)
VITE_WS_URL=wss://automind-api.onrender.com/ws

# Check Render service logs for WebSocket errors
```

### Issue 4: Environment Variables Not Loading

**Symptoms**: Frontend shows undefined or incorrect API URL

**Solution**:
```bash
# Redeploy with environment variables
vercel --prod

# Or rebuild in Vercel dashboard
# Deployments → ... → Redeploy
```

### Issue 5: Build Failures

**Frontend Build Error**:
```bash
# Check build logs in Vercel
# Common issues:
# - Missing dependencies (run npm install locally)
# - TypeScript errors (run npm run build locally)
# - Environment variable issues
```

**Backend Build Error**:
```bash
# Check logs in Render
# Common issues:
# - Missing Python dependencies
# - Python version mismatch
# - Import errors
```

---

## Cost Estimation

### Render (Free Tier)
- Web Service: Free (spins down after 15 min inactivity)
- PostgreSQL: Free (1GB storage, expires after 90 days)
- Redis: Free (25MB storage)

### Render (Starter Tier - Recommended for Production)
- Web Service: $7/month (always on)
- PostgreSQL: $7/month (persistent)
- Redis: $10/month (persistent)
- **Total**: ~$24/month

### Vercel
- Hobby: Free (personal projects)
- Pro: $20/month (commercial projects)

**Estimated Total Cost**: $0 (free tier) or $24-44/month (production tier)

---

## Scaling Considerations

### Backend Scaling (Render)

1. **Vertical Scaling**:
   - Upgrade plan to get more RAM/CPU
   - Starter → Standard → Pro

2. **Database Scaling**:
   - Add read replicas
   - Upgrade to larger plan
   - Consider managed DB (AWS RDS, etc.)

3. **Caching**:
   - Upgrade Redis plan
   - Implement CDN for static assets

### Frontend Scaling (Vercel)

- Automatic edge caching
- Global CDN distribution
- Automatic scaling
- No configuration needed!

---

## Maintenance

### Regular Tasks

**Weekly**:
- Check error logs
- Monitor response times
- Review database size

**Monthly**:
- Update dependencies
- Security patches
- Database backups

### Backup Strategy

**Database Backups** (Render):
```bash
# Manual backup
pg_dump $(render config get DATABASE_URL) > backup.sql

# Automated backups available in paid plans
```

**Code Backups**:
- Git repository (already backed up on GitHub)
- Vercel keeps deployment history
- Render keeps build history

---

## Next Steps

1. **Monitor Performance**:
   - Set up monitoring (Sentry, LogRocket)
   - Configure alerts for errors
   - Track user analytics

2. **Security**:
   - Enable 2FA on Vercel and Render
   - Rotate secrets regularly
   - Keep dependencies updated
   - Add rate limiting

3. **Features**:
   - Add custom domain
   - Configure email notifications
   - Set up CI/CD automation
   - Add more agents/features

---

## Support

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **Project Repository**: https://github.com/codebyArya-bit/Automotive-Predictive-Maintainance-System

---

## Quick Reference Commands

```bash
# BACKEND (Render)
render services list                    # List all services
render logs -s automind-api            # View backend logs
render deploy                          # Deploy all services

# FRONTEND (Vercel)
vercel                                 # Deploy to preview
vercel --prod                          # Deploy to production
vercel logs                            # View logs
vercel env ls                          # List environment variables

# Development
npm run dev                            # Run frontend locally
python api_server.py                   # Run backend locally
```

---

*Last Updated: 2025-11-08*
*Version: 1.0.0*
