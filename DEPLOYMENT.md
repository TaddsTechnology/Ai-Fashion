# AI Fashion - Separate Backend & Frontend Deployment Guide

This guide will help you deploy the AI Fashion application with separate backend and frontend services on Render.

## 🚀 Backend Deployment (Deploy First)

### Step 1: Create Backend Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository: `https://github.com/TaddsTechnology/Ai-Fashion.git`

### Step 2: Configure Backend Service

**Basic Settings:**
- **Name**: `ai-fashion-backend` (or your preferred name)
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: 
  ```bash
  cd prods_fastapi && pip install -r requirements-render.txt
  ```
- **Start Command**: 
  ```bash
  cd prods_fastapi && python main.py
  ```

### Step 3: Environment Variables for Backend

Add these environment variables in Render:

```bash
PORT=10000
DATABASE_URL=postgresql://neondb_owner:npg_OUMg09DpBurh@ep-rough-thunder-adqlho94-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require
PYTHON_VERSION=3.9
PYTHONPATH=/opt/render/project/src/backend/prods_fastapi
```

### Step 4: Deploy Backend

1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Note your backend URL: `https://your-backend-name.onrender.com`
4. Test health check: `https://your-backend-name.onrender.com/health`

---

## 🎨 Frontend Deployment (Deploy After Backend)

### Step 1: Update Frontend Configuration

1. Copy `frontend/.env.example` to `frontend/.env`
2. Update with your backend URL:
   ```bash
   VITE_API_BASE_URL=https://your-backend-name.onrender.com
   ```

### Step 2: Create Frontend Service on Render

1. Go to Render Dashboard
2. Click "New +" → "Static Site"
3. Connect the same GitHub repository

### Step 3: Configure Frontend Service

**Basic Settings:**
- **Name**: `ai-fashion-frontend`
- **Branch**: `main`
- **Root Directory**: `frontend`

**Build Settings:**
- **Build Command**: `npm install && npm run build`
- **Publish Directory**: `dist`

### Step 4: Environment Variables for Frontend

```bash
VITE_API_BASE_URL=https://your-backend-name.onrender.com
```

### Step 5: Deploy Frontend

1. Click "Create Static Site"
2. Wait for deployment (2-5 minutes)
3. Your frontend URL: `https://your-frontend-name.onrender.com`

---

## 🔗 API Endpoints Available

Once deployed, your backend will provide these endpoints:

### Core Endpoints
- `GET /health` - Health check
- `POST /analyze-skin-tone` - Upload image for skin tone analysis
- `GET /api/color-recommendations` - Get color recommendations
- `GET /api/v2/color-recommendations/enhanced` - Enhanced MST recommendations

### MST Database Endpoints
- `GET /api/v2/mst-info` - Available MST data info
- `GET /api/v2/seasonal-analysis` - Seasonal color analysis
- `GET /api/v2/styling-guide` - Comprehensive styling guide
- `GET /api/v2/quick-palette` - Quick color palette

---

## 🛠 Troubleshooting

### Backend Issues
- **Build fails**: Check `requirements-render.txt` compatibility
- **Database error**: Verify `DATABASE_URL` environment variable
- **Port issues**: Ensure `PORT=10000` is set

### Frontend Issues
- **API calls fail**: Check `VITE_API_BASE_URL` in frontend environment
- **CORS errors**: Backend already configured for CORS
- **Build fails**: Ensure Node.js version compatibility

### Quick Tests
```bash
# Test backend health
curl https://your-backend-name.onrender.com/health

# Test MST info
curl https://your-backend-name.onrender.com/api/v2/mst-info

# Test color recommendations
curl "https://your-backend-name.onrender.com/api/color-recommendations?skin_tone=Monk%205"
```

---

## 📊 What's Included

### Backend Features
- **652 colors** across 10 MST skin tone entries
- **PostgreSQL database** with comprehensive color data
- **Real-time recommendations** with fallback support
- **Occasion-specific palettes** (work, casual, party, formal)
- **Styling advice** (metals, denim, patterns)
- **Image processing** with MediaPipe and OpenCV
- **Rate limiting** and error tracking

### Frontend Features
- **Skin tone analysis** via camera or upload
- **Interactive color palettes**
- **Responsive design**
- **Real-time API integration**

---

## 🔄 Auto-Deploy Setup

Both services are configured for auto-deploy from the `main` branch:
1. Make changes to your code
2. Push to GitHub main branch
3. Render automatically rebuilds and deploys

---

## 💡 Next Steps

1. **Deploy Backend First** - Get your backend URL
2. **Update Frontend Config** - Add backend URL to frontend env
3. **Deploy Frontend** - Deploy with updated configuration
4. **Test Integration** - Verify frontend can communicate with backend
5. **Update CORS** - Add your frontend domain to backend CORS settings if needed

Your AI Fashion application will be fully operational with separate, scalable services!
