# Render Deployment Configurations

## Backend Web Service Configuration

### Service Settings
- **Name**: `ai-fashion-backend`
- **Environment**: `Python 3`
- **Region**: `US East (Ohio)` or closest to your users
- **Branch**: `main`
- **Root Directory**: `backend`

### Build & Deploy Commands
```bash
# Build Command
cd prods_fastapi && pip install -r requirements-render.txt

# Start Command  
cd prods_fastapi && python main.py
```

### Environment Variables
```bash
PORT=10000
DATABASE_URL=postgresql://neondb_owner:npg_OUMg09DpBurh@ep-rough-thunder-adqlho94-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require
PYTHON_VERSION=3.9
PYTHONPATH=/opt/render/project/src/backend/prods_fastapi
```

### Health Check Path
```
/health
```

---

## Frontend Static Site Configuration

### Service Settings
- **Name**: `ai-fashion-frontend`
- **Environment**: `Static Site`
- **Branch**: `main`
- **Root Directory**: `frontend`

### Build Settings
```bash
# Build Command
npm install && npm run build

# Publish Directory
dist
```

### Environment Variables
```bash
# Replace with your actual backend URL after backend deployment
VITE_API_BASE_URL=https://ai-fashion-backend.onrender.com
VITE_DEBUG_API=false
```

### Custom Headers (Optional)
```yaml
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
```

---

## Deployment Steps

### 1. Backend First
1. Deploy backend service using above configuration
2. Wait for deployment to complete
3. Note the backend URL (e.g., `https://ai-fashion-backend.onrender.com`)
4. Test backend health: `curl https://your-backend-url/health`

### 2. Frontend Second  
1. Update frontend environment variable `VITE_API_BASE_URL` with your backend URL
2. Deploy frontend service using above configuration
3. Test frontend-backend connection

### 3. Verification
- Backend health: `https://your-backend-url/health`
- MST info: `https://your-backend-url/api/v2/mst-info`
- Frontend: `https://your-frontend-url`

---

## Auto-Deploy
Both services will auto-deploy when you push to the `main` branch.
