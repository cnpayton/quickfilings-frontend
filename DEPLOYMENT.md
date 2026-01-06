# Deployment Guide

## GitHub Pages (Frontend)

### Automatic Deployment

A GitHub Actions workflow is included that automatically deploys to GitHub Pages on every push.

### Manual Setup

1. Go to your repository on GitHub
2. Click **Settings** → **Pages** (in the left sidebar)
3. Under **Source**, select:
   - Source: **GitHub Actions**
4. The workflow will automatically trigger on the next push
5. Your site will be available at: `https://cnpayton.github.io/quickfilings-frontend/`

### Custom Domain (Optional)

1. In **Settings** → **Pages**, add your custom domain
2. Update DNS records:
   - Add a CNAME record pointing to `cnpayton.github.io`
   - Or add A records for GitHub Pages IPs
3. Enable **Enforce HTTPS**

## Backend Deployment (Render.com)

### Option 1: Web UI

1. Create a free account at [render.com](https://render.com)
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `quickfilings-backend` (or choose your own)
   - **Root Directory**: `backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free
5. Click **Create Web Service**
6. Wait 5-10 minutes for first deployment
7. Copy your service URL (e.g., `https://quickfilings-backend-xyz.onrender.com`)

### Option 2: Using render.yaml (Infrastructure as Code)

1. The `backend/render.yaml` file is already configured
2. In Render dashboard, click **New +** → **Blueprint**
3. Connect your repository
4. Render will auto-detect the `render.yaml` and create the service
5. Click **Apply**

### Update Frontend

After deploying the backend:

1. Copy your Render service URL
2. Edit `index.html` around line 458
3. Update the production URL:
   ```javascript
   const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
       ? 'http://localhost:8000'
       : 'https://YOUR-SERVICE-NAME.onrender.com';  // ← Update this
   ```
4. Commit and push the change

## Alternative Backend Hosting

### Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd backend
vercel
```

Configure:
- Framework: Other
- Build Command: (leave empty)
- Output Directory: (leave empty)
- Development Command: `uvicorn main:app --reload`

### Railway

1. Visit [railway.app](https://railway.app)
2. Click **New Project** → **Deploy from GitHub**
3. Select your repository
4. Railway auto-detects Python
5. Set root directory to `backend`
6. Deploy

### Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login and launch
cd backend
fly launch
fly deploy
```

## Environment Variables

No environment variables are required. The backend uses SEC's public API.

For production, you may want to add:

- `ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins
- `LOG_LEVEL`: `debug`, `info`, `warning`, `error`

## Monitoring

### Render
- Free tier sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds
- View logs in Render dashboard

### Uptime Monitoring (Optional)

Use services like:
- [UptimeRobot](https://uptimerobot.com) (free)
- [Cronitor](https://cronitor.io)
- [StatusCake](https://www.statuscake.com)

Configure a ping to your `/health` endpoint every 14 minutes to prevent sleeping.

## Troubleshooting

### GitHub Pages not deploying

1. Check Actions tab for deployment status
2. Ensure Pages is set to "GitHub Actions" source
3. Check workflow permissions in Settings → Actions → General
4. Verify the workflow file is in `.github/workflows/`

### Backend CORS errors

1. Check backend logs for errors
2. Verify CORS middleware is configured
3. Ensure frontend URL is allowed in CORS origins
4. Check browser console for specific error

### Backend 502/503 errors

1. Check Render logs for startup errors
2. Verify requirements.txt has correct dependencies
3. Ensure start command is correct
4. Wait for first-time deployment to complete (~5-10 min)

### "Failed to fetch" in frontend

1. Check browser console for actual error
2. Verify backend URL in index.html
3. Test backend health endpoint directly
4. Check if backend is sleeping (Render free tier)
5. Verify CORS is enabled on backend

## Local Testing

Test the full stack locally before deploying:

```bash
# Terminal 1: Start backend
cd backend
python main.py

# Terminal 2: Start frontend
python -m http.server 8080
```

Visit `http://localhost:8080` and test searching for a company (try "AAPL", "MSFT", "GOOGL").

## Production Checklist

- [ ] Backend deployed and responding to `/health`
- [ ] Frontend deployed to GitHub Pages
- [ ] Frontend has correct backend URL
- [ ] Test search functionality with real ticker
- [ ] Check browser console for errors
- [ ] Test on mobile device
- [ ] Set up uptime monitoring (optional)
- [ ] Add custom domain (optional)

## Need Help?

- Check the GitHub Issues for this repository
- Review Render/GitHub Pages documentation
- Test locally first to isolate the problem
