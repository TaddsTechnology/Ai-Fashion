# 🐳 AI Fashion App - Pre-built Docker Image Deployment

This guide will help you build Docker images locally and deploy them to Render using the "Deploy an existing image" option.

## 📋 Prerequisites

1. **Docker Desktop** installed and running
2. **Docker Hub account** (free at https://hub.docker.com)
3. **Render account** (free at https://render.com)

## 🚀 Step-by-Step Deployment

### Step 1: Prepare Docker Environment

1. **Start Docker Desktop**
   - Make sure Docker Desktop is running on your Windows machine

2. **Create Docker Hub Account** (if you don't have one)
   - Go to https://hub.docker.com
   - Sign up for a free account
   - Remember your username - you'll need it!

### Step 2: Build and Push Docker Images

1. **Open PowerShell as Administrator** in your project directory:
   ```powershell
   cd "C:\Users\jvs\Desktop\MVC\Ai-Fashion"
   ```

2. **Run the build script:**
   ```powershell
   .\build-docker-images.ps1
   ```
   
   The script will:
   - Prompt for your Docker Hub username
   - Ask you to login to Docker Hub
   - Build both frontend and backend images
   - Push them to Docker Hub
   - Display the image URLs you need for Render

3. **Example output:**
   ```
   📝 Your Docker Images:
      Backend:  yourusername/ai-fashion-backend:latest
      Frontend: yourusername/ai-fashion-frontend:latest
   ```

### Step 3: Deploy Backend on Render

1. **Go to Render Dashboard:** https://dashboard.render.com

2. **Create Backend Service:**
   - Click **"New +"** → **"Web Service"**
   - Select **"Deploy an existing image"**
   - **Image URL:** `yourusername/ai-fashion-backend:latest` (from step 2)
   - **Name:** `ai-fashion-backend`
   - **Plan:** Free or Starter
   - **Region:** Choose closest to your users

3. **Configure Backend Environment Variables:**
   ```
   PYTHONPATH=/app
   PYTHONUNBUFFERED=1
   ENV=production
   ```

4. **Advanced Settings:**
   - **Port:** 8000 (auto-detected)
   - **Health Check Path:** `/health`
   - **Auto Deploy:** Yes

5. **Click "Create Web Service"**

6. **Wait for deployment** (usually 5-10 minutes)

7. **Copy the Backend URL** (e.g., `https://ai-fashion-backend-xyz.render.com`)

### Step 4: Deploy Frontend on Render

1. **Create Frontend Service:**
   - Click **"New +"** → **"Web Service"**
   - Select **"Deploy an existing image"**
   - **Image URL:** `yourusername/ai-fashion-frontend:latest` (from step 2)
   - **Name:** `ai-fashion-frontend`
   - **Plan:** Free or Starter
   - **Region:** Same as backend

2. **Configure Frontend Environment Variables:**
   ```
   NODE_ENV=production
   VITE_API_URL=https://ai-fashion-backend-xyz.render.com
   ```
   ⚠️ **Important:** Replace `ai-fashion-backend-xyz.render.com` with your actual backend URL from Step 3

3. **Advanced Settings:**
   - **Port:** 3000 (auto-detected)
   - **Health Check Path:** `/`
   - **Auto Deploy:** Yes

4. **Click "Create Web Service"**

5. **Wait for deployment** (usually 3-5 minutes)

### Step 5: Test Your Deployment

1. **Access your frontend** at the Render URL (e.g., `https://ai-fashion-frontend-abc.render.com`)

2. **Test the API connection:**
   - Try uploading an image for skin tone analysis
   - Check if product recommendations are loading
   - Verify all features work properly

## 🔧 Updating Your Application

When you make changes to your code:

1. **Rebuild and push new images:**
   ```powershell
   .\build-docker-images.ps1 -Version "v1.1"
   ```

2. **Update Render services:**
   - Go to your service settings
   - Update the image URL with the new version
   - Click "Deploy"

## 🎯 Image URLs Format

Your images will be available at:
- **Backend:** `yourusername/ai-fashion-backend:latest`
- **Frontend:** `yourusername/ai-fashion-frontend:latest`

## 📊 Monitoring and Logs

1. **View Logs:**
   - Go to Render Dashboard
   - Click on your service
   - Click "Logs" tab

2. **Monitor Performance:**
   - Check the "Metrics" tab
   - Monitor CPU and Memory usage

## 🛠️ Troubleshooting

### Common Issues:

1. **Docker Build Fails:**
   - Check if Docker Desktop is running
   - Ensure you have enough disk space
   - Try cleaning Docker: `docker system prune`

2. **Push to Docker Hub Fails:**
   - Verify you're logged in: `docker login`
   - Check your Docker Hub username
   - Ensure repository exists (will be created automatically)

3. **Render Deployment Fails:**
   - Verify image URL is correct
   - Check if image is public on Docker Hub
   - Review deployment logs in Render dashboard

4. **CORS Errors:**
   - Ensure backend URL is correctly set in frontend environment variables
   - Check that backend is running and accessible

5. **Frontend Can't Connect to Backend:**
   - Verify `VITE_API_URL` environment variable
   - Ensure backend service is running
   - Check network connectivity

## 🔒 Security Tips

1. **Keep images private** (upgrade Docker Hub plan if needed)
2. **Use environment variables** for sensitive data
3. **Enable HTTPS** (Render provides this automatically)
4. **Regular updates** of dependencies

## 💰 Cost Considerations

- **Free Tier:** Both services can run on free tier
- **Limitations:** 
  - Services sleep after 15 minutes of inactivity
  - Limited build minutes
  - Slower performance

- **Paid Plans:** 
  - No sleeping
  - Better performance
  - More resources

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Render documentation: https://render.com/docs
3. Check Docker Hub documentation: https://docs.docker.com

---

🎉 **Congratulations!** Your AI Fashion app should now be running on Render using pre-built Docker images!
