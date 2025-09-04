# AI Fashion Docker Setup Guide

This guide provides comprehensive instructions for setting up the AI Fashion application using Docker.

## Prerequisites

- Docker and Docker Compose installed on your system
- Git (for cloning the repository)
- At least 4GB of available RAM
- At least 2GB of available disk space

## Project Structure

```
AI-Fashion/
├── backend/
│   ├── prods_fastapi/
│   │   ├── main.py           # FastAPI application
│   │   ├── color_utils.py    # Color processing utilities
│   │   └── ...
│   ├── processed_data/       # Data files
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile           # Backend Docker configuration
├── frontend/
│   ├── src/                 # React source code
│   ├── package.json         # Node.js dependencies
│   └── Dockerfile           # Frontend Docker configuration
├── docker-compose.yml       # Multi-container orchestration
└── DOCKER_SETUP.md         # This file
```

## Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd AI-Fashion
```

### 2. Build and Run with Docker Compose
```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode (background)
docker-compose up --build -d
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Manual Docker Commands

### Backend Only
```bash
# Build backend image
docker build -t ai-fashion-backend ./backend

# Run backend container
docker run -p 8000:8000 ai-fashion-backend
```

### Frontend Only
```bash
# Build frontend image
docker build -t ai-fashion-frontend ./frontend

# Run frontend container
docker run -p 3000:3000 ai-fashion-frontend
```

## Development vs Production

### Development Mode
For development with hot reload:
```bash
# Start with volume mounts for live code changes
docker-compose up --build
```

### Production Mode
For production deployment:
```bash
# Build optimized images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

## Environment Variables

### Backend Environment Variables
- `PYTHONPATH=/app` - Python path configuration
- `PYTHONUNBUFFERED=1` - Unbuffered Python output

### Frontend Environment Variables
- `VITE_API_URL=http://localhost:8000` - Backend API URL
- `NODE_ENV=production` - Node.js environment

## Health Checks

The application includes health checks:
- Backend: `http://localhost:8000/` (returns welcome message)
- Frontend: Depends on backend health check

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :8000  # For backend
   lsof -i :3000  # For frontend
   
   # Kill the process or use different ports
   docker-compose down
   ```

2. **Permission Denied (Linux/Mac)**
   ```bash
   # Fix permissions
   sudo chown -R $USER:$USER .
   chmod -R 755 .
   ```

3. **Out of Memory**
   ```bash
   # Increase Docker memory limit in Docker Desktop
   # Or add memory limits to docker-compose.yml
   ```

4. **Module Not Found (Backend)**
   ```bash
   # Rebuild backend image
   docker-compose build --no-cache backend
   ```

5. **Dependencies Not Installing (Frontend)**
   ```bash
   # Clear npm cache and rebuild
   docker-compose build --no-cache frontend
   ```

### Debug Commands

```bash
# View logs
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f frontend

# Access container shell
docker-compose exec backend bash
docker-compose exec frontend sh

# Check container status
docker-compose ps

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
```

## Backend API Endpoints

Once running, the following endpoints are available:

### Core Endpoints
- `GET /` - Welcome message
- `GET /docs` - API documentation

### Product Endpoints
- `GET /products` - H&M products
- `GET /apparel` - Apparel products with filters
- `GET /data/` - Makeup products with pagination

### Color Analysis Endpoints
- `GET /color-suggestions` - Color suggestions by skin tone
- `GET /api/color-recommendations` - Color recommendations
- `GET /makeup-types` - Available makeup types

### Recommendation Endpoints
- `GET /api/random-outfits` - Random outfit recommendations
- `POST /api/recommendations` - Product recommendations

## Performance Optimization

### For Better Performance
1. **Use Multi-stage Builds** (already configured)
2. **Optimize Images**:
   ```bash
   # Remove unused images
   docker image prune -a
   
   # Remove unused volumes
   docker volume prune
   ```

3. **Resource Limits**:
   ```yaml
   # Add to docker-compose.yml
   services:
     backend:
       deploy:
         resources:
           limits:
             cpus: '1'
             memory: 2G
   ```

## Data Management

### Backup Data
```bash
# Backup processed data
docker cp ai-fashion-backend:/app/processed_data ./backup/
```

### Restore Data
```bash
# Restore processed data
docker cp ./backup/processed_data ai-fashion-backend:/app/
```

## Scaling

### Horizontal Scaling
```bash
# Scale backend service
docker-compose up --scale backend=3

# Use load balancer (nginx)
docker-compose -f docker-compose.yml -f docker-compose.scale.yml up
```

## Security Considerations

1. **Environment Variables**: Use `.env` files for sensitive data
2. **Network Security**: Configure custom networks
3. **Container Security**: Run as non-root user
4. **Image Security**: Scan images for vulnerabilities

## Production Deployment

### Using Docker Swarm
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml ai-fashion
```

### Using Kubernetes
```bash
# Convert to Kubernetes manifests
kompose convert

# Apply to cluster
kubectl apply -f .
```

## Monitoring

### Container Monitoring
```bash
# Monitor resource usage
docker stats

# Check container health
docker-compose exec backend curl -f http://localhost:8000/
```

### Logs Management
```bash
# Configure log rotation in docker-compose.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Cleanup

### Remove All Containers and Images
```bash
# Stop and remove containers
docker-compose down

# Remove images
docker rmi ai-fashion-backend ai-fashion-frontend

# Remove volumes (careful - this removes data!)
docker-compose down -v

# Complete cleanup
docker system prune -a
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Docker logs: `docker-compose logs`
3. Ensure all prerequisites are met
4. Check Docker and Docker Compose versions

## Version Information

- Docker: >= 20.10
- Docker Compose: >= 2.0
- Python: 3.11
- Node.js: 18
- FastAPI: 0.115.8
- React: 18.3.1
