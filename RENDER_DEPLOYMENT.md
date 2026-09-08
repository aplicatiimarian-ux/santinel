# SANTINEL Backend Deployment on Render.com

This guide walks you through deploying the SANTINEL FastAPI backend to Render.com to replace the local ngrok tunneling setup.

## Prerequisites

- Render.com account (free tier available)
- PostgreSQL database (cloud-hosted or local)
- GitHub repository (already connected)

## Step-by-Step Deployment

### 1. Create a New Web Service on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** button and select **"Web Service"**
3. Select **"GitHub"** as the source
4. Search for and connect your `santinel` repository
5. Click **"Connect"**

### 2. Configure the Service

Fill in the following:

- **Name:** `santinel-backend`
- **Environment:** `Python 3`
- **Region:** Choose closest to you (default: Oregon)
- **Branch:** `main`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn start_api:app --host 0.0.0.0 --port $PORT`

### 3. Set Environment Variables

Click **"Add Environment Variable"** and add these variables:

| Key | Value | Notes |
|-----|-------|-------|
| `JWT_SECRET` | `27dd8c4f72050ce84f029d5135df2669f6a1609a5e7bb6b172744e90c16c99aeb856dee2595b0b504ab91756116b5fd4` | From your .env |
| `JWT_ACCESS_TTL_MIN` | `15` | Token expiry in minutes |
| `JWT_REFRESH_TTL_DAYS` | `7` | Refresh token expiry |
| `AUTH_DATABASE_URL` | `postgresql://user:password@host:5432/santinel_prod` | **IMPORTANT: Use cloud PostgreSQL URL** |
| `CORS_ORIGINS` | `https://santinel-8a53.vercel.app,https://YOUR_RENDER_URL` | See step 5 below |
| `AUTH_COOKIE_SECURE` | `true` | Enable secure cookies for HTTPS |
| `DEEPGRAM_API_KEY` | `a9331c99ae19aad7a78dbcc76e01491530d2f5a4` | From your .env |
| `DEEPGRAM_STT_MODEL` | `nova-2` | Deepgram model |
| `DEEPGRAM_MIN_CONFIDENCE` | `0.55` | Confidence threshold |

### 4. Deploy

1. Scroll down and click **"Create Web Service"**
2. Wait for deployment to complete (usually 3-5 minutes)
3. You'll see: **"Your service is live at: https://santinel-backend-xxx.onrender.com"**

### 5. Update Frontend

Once deployment completes:

1. Copy your Render backend URL (e.g., `https://santinel-backend-abc123.onrender.com`)
2. Update `CORS_ORIGINS` in Step 3 to include this URL
3. Update `src/authClient.js` with the new URL:

```javascript
export const api = axios.create({ 
  baseURL: 'https://santinel-backend-xxx.onrender.com/api', 
  withCredentials: true 
});
```

4. Commit and push to GitHub:
```bash
git add src/authClient.js
git commit -m "Update backend URL to Render deployment"
git push origin main
```

5. Vercel will auto-redeploy with the new backend URL

### 6. Test the Deployment

**On Windows:**
```powershell
# Test backend health
$url = "https://santinel-backend-xxx.onrender.com"
Invoke-WebRequest -Uri "$url/health" -SkipCertificateCheck
```

**Test login endpoint:**
```powershell
$url = "https://santinel-backend-xxx.onrender.com/api/auth/login"
Invoke-WebRequest -Uri $url -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"test@example.com","password":"test"}' `
  -SkipCertificateCheck
```

### 7. Test on Android

1. Wait 1-2 minutes for Vercel to redeploy with new backend URL
2. Open https://santinel-8a53.vercel.app on Android
3. Try login - should now work!

## Important Notes

### Database Migration

If you're switching from local PostgreSQL to cloud PostgreSQL:

1. **Backup existing data** (if any):
```bash
pg_dump -U postgres -h localhost santinel_prod > backup.sql
```

2. **Create cloud database** (e.g., on Neon, Railway, Supabase, or AWS RDS)

3. **Update `AUTH_DATABASE_URL`** in Render environment variables

4. **Restore data** (if migrating):
```bash
psql "postgresql://cloud_user:password@cloud_host/cloud_db" < backup.sql
```

### Render.com Limitations

- **Free tier:** 0.5 vCPU, 512 MB RAM, 100 GB bandwidth/month
- **Limitations:** Services spin down after 15 min of inactivity (adds 30s startup delay)
- **Cold starts:** First request may take 30-60 seconds

### Upgrade Options

- **Paid tier:** $7/month for always-on service
- **Larger instances:** Available if needed

## Troubleshooting

### Backend not responding
1. Check Render dashboard for errors
2. Check logs: https://dashboard.render.com → santinel-backend → Logs
3. Verify environment variables are set correctly

### Login still fails on Android
1. Verify Vercel redeploy completed
2. Check browser console for error details
3. Verify CORS_ORIGINS includes both Vercel and Render URLs

### Database connection error
1. Verify AUTH_DATABASE_URL format is correct
2. Verify cloud database is accessible from Render
3. Check firewall/security group rules

## Reverting to ngrok

If you need to go back to ngrok:
1. Revert `src/authClient.js` to ngrok URL
2. Push to GitHub
3. Vercel will redeploy
4. Run ngrok locally: `ngrok http localhost:8000`

---

**Next Step:** Once deployment is complete and tested, you can remove the local backend and ngrok entirely!
