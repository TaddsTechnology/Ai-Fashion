# Fashion Color API - Deployment Guide

## 🐳 Docker Hub Repository
**Image**: `newbie028/fashion-color-api:latest`
**Tagged Version**: `newbie028/fashion-color-api:v1.0`

## 📦 What's Included
- FastAPI color recommendation API
- PostgreSQL integration with your fashion_jvy9 database
- 715+ color records with skin tone recommendations
- Monk-inspired colors for minimalist styling
- RESTful endpoints for color fetching

## 🚀 Quick Deployment

### Option 1: Docker Run
```bash
docker run -p 8000:8000 newbie028/fashion-color-api:latest
```

### Option 2: Docker Compose
Create a `docker-compose.yml` file:
```yaml
version: '3.8'
services:
  fashion-color-api:
    image: newbie028/fashion-color-api:latest
    ports:
      - "8000:8000"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Then run:
```bash
docker-compose up -d
```

### Option 3: Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fashion-color-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fashion-color-api
  template:
    metadata:
      labels:
        app: fashion-color-api
    spec:
      containers:
      - name: fashion-color-api
        image: newbie028/fashion-color-api:latest
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 30
---
apiVersion: v1
kind: Service
metadata:
  name: fashion-color-api-service
spec:
  selector:
    app: fashion-color-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

## 🔗 API Endpoints

Once deployed, your API will be available at:

### Base URL
- Local: `http://localhost:8000`
- Production: `http://your-domain:8000`

### Available Endpoints
1. **GET /** - API documentation and welcome
2. **GET /colors/skin-tone/{skin_tone}** - Get colors for specific skin tone
   - Examples: `/colors/skin-tone/Fair`, `/colors/skin-tone/Medium`
3. **GET /colors/recommendations/{skin_tone}** - Get recommended colors only
4. **GET /colors/monk** - Get monk-inspired colors
5. **GET /colors/hex/{hex_code}** - Get color info by hex code
6. **GET /colors/all** - Get all colors with optional filters

### Example API Calls
```bash
# Get colors for fair skin
curl http://localhost:8000/colors/skin-tone/Fair

# Get top 5 recommendations for medium skin
curl http://localhost:8000/colors/recommendations/Medium?limit=5

# Get monk colors
curl http://localhost:8000/colors/monk

# Get color info by hex code
curl http://localhost:8000/colors/hex/FF7F50

# Get all recommended colors
curl http://localhost:8000/colors/all?category=recommended&limit=50
```

## 🌐 Cloud Platform Deployment

### AWS ECS
```bash
# Create ECR repository
aws ecr create-repository --repository-name fashion-color-api

# Get login token
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com

# Tag and push
docker tag newbie028/fashion-color-api:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/fashion-color-api:latest
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/fashion-color-api:latest
```

### Google Cloud Run
```bash
# Deploy to Cloud Run
gcloud run deploy fashion-color-api \
  --image newbie028/fashion-color-api:latest \
  --platform managed \
  --region us-central1 \
  --port 8000
```

### Azure Container Instances
```bash
az container create \
  --resource-group myResourceGroup \
  --name fashion-color-api \
  --image newbie028/fashion-color-api:latest \
  --ports 8000 \
  --dns-name-label fashion-color-api
```

## 💾 Database Connection
The API connects to your PostgreSQL database:
- **Host**: `dpg-d1vhvpbuibrs739dkn3g-a.oregon-postgres.render.com`
- **Database**: `fashion_jvy9`
- **Total Records**: 715+ colors

## 📊 Features
- ✅ Skin tone-based color recommendations
- ✅ Seasonal palette support
- ✅ Monk-inspired minimalist colors
- ✅ RESTful API with JSON responses
- ✅ Health check endpoints
- ✅ Docker containerized
- ✅ Scalable and production-ready

## 🛠️ Maintenance
To update the API:
1. Pull the latest image: `docker pull newbie028/fashion-color-api:latest`
2. Restart containers: `docker-compose up -d`

## 📝 Notes
- API runs on port 8000
- Health check available at `/`
- All responses in JSON format
- PostgreSQL connection is SSL-enabled
- Container includes all necessary dependencies

Your Fashion Color API is now successfully deployed to Docker Hub and ready for production use! 🎨✨
