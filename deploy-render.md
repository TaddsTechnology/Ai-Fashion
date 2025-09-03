# AI Fashion App - Render Deployment Guide

## Overview
This guide will help you deploy your AI Fashion application on Render using Docker images. The application consists of two services:
- **Backend**: FastAPI server (Python)
- **Frontend**: React/Vite application

## Prerequisites
1. GitHub repository with your code
2. Render account (free tier available)
3. Docker images built and pushed to a registry (optional for direct deployment)

## Deployment Options

### Option 1: Direct Docker Deployment from Repository (Recommended)

#### Step 1: Deploy Backend
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the backend service:
   - **Name**: `ai-fashion-backend`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `./backend/Dockerfile`
   - **Docker Context**: `./backend`
   - **Plan**: Free (or paid plan for better performance)
   - **Advanced Settings**:
     - **Port**: `8000`
     - **Health Check Path**: `/`
     - **Environment Variables**:
       ```
       PYTHONPATH=/app
       PYTHONUNBUFFERED=1
       ENV=production
       ```

#### Step 2: Deploy Frontend
1. In Render Dashboard, click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure the frontend service:
   - **Name**: `ai-fashion-frontend`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `./frontend/Dockerfile`
   - **Docker Context**: `./frontend`
   - **Plan**: Free (or paid plan)
   - **Advanced Settings**:
     - **Port**: `3000`
     - **Health Check Path**: `/`
     - **Environment Variables**:
       ```
       NODE_ENV=production
       VITE_API_URL=https://YOUR_BACKEND_URL.render.com
       ```

#### Step 3: Update Frontend Configuration
After backend deployment completes:
1. Copy the backend URL from Render dashboard
2. Update the frontend environment variable `VITE_API_URL` with the actual backend URL
3. Redeploy the frontend

### Option 2: Using Pre-built Docker Images

If you prefer to build and push Docker images to a registry first:

#### Build and Push Images
```bash
# Build backend image
docker build -t your-registry/ai-fashion-backend:latest ./backend

# Build frontend image
docker build -t your-registry/ai-fashion-frontend:latest ./frontend

# Push to registry
docker push your-registry/ai-fashion-backend:latest
docker push your-registry/ai-fashion-frontend:latest
```

#### Deploy on Render
1. Create new web service
2. Select "Deploy an existing image"
3. Enter your image URL: `your-registry/ai-fashion-backend:latest`
4. Configure environment variables as above

## Environment Configuration

### Backend Environment Variables
- `PYTHONPATH=/app`
- `PYTHONUNBUFFERED=1`
- `ENV=production`
- `PORT=8000` (automatically set by Render)

### Frontend Environment Variables
- `NODE_ENV=production`
- `VITE_API_URL=https://your-backend-url.render.com`
- `PORT=3000` (automatically set by Render)

## Important Notes

1. **Free Tier Limitations**:
   - Services spin down after 15 minutes of inactivity
   - Limited build minutes per month
   - Consider upgrading for production use

2. **CORS Configuration**:
   - Make sure your backend allows requests from your frontend domain
   - Update CORS settings in your FastAPI application

3. **API URL Updates**:
   - Always update the `VITE_API_URL` in frontend with the actual backend URL
   - Frontend builds are static, so API URL changes require rebuild

4. **Health Checks**:
   - Backend health check: `GET /`
   - Frontend health check: `GET /` (any valid route)

## Troubleshooting

### Common Issues:
1. **Build Failures**: Check Dockerfile paths and context
2. **CORS Errors**: Verify backend CORS configuration
3. **API Connection**: Ensure frontend has correct backend URL
4. **Port Issues**: Use PORT environment variable, don't hardcode ports

### Logs:
- Check deployment logs in Render dashboard
- Use `docker logs <container>` for local testing

## Cost Optimization

For production deployment:
- Use paid plans for better performance and no downtime
- Consider using a single plan for both services if resource requirements are low
- Implement proper caching and optimization

## Security Considerations

- Use environment variables for sensitive data
- Implement proper authentication
- Use HTTPS (automatically provided by Render)
- Regularly update dependencies

## Next Steps

After successful deployment:
1. Set up custom domain (optional)
2. Configure monitoring and alerts
3. Implement CI/CD pipeline
4. Set up database if needed
5. Configure backup strategy
