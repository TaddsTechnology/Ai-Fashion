# AI-Fashion Docker Deployment

This guide explains how to run the AI-Fashion application using Docker containers for simplified deployment and development.

## Prerequisites

- Docker Desktop (for Windows/Mac) or Docker Engine (for Linux)
- Docker Compose (usually included with Docker Desktop)
- At least 4GB of available RAM
- At least 2GB of free disk space

## Quick Start

1. **Clone or navigate to the project directory:**
   ```bash
   cd AI-Fashion
   ```

2. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

4. **Stop the application:**
   ```bash
   docker-compose down
   ```

## Detailed Commands

### Building Images
```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend

# Build with no cache (clean build)
docker-compose build --no-cache
```

### Running Services
```bash
# Start all services in foreground
docker-compose up

# Start all services in background (detached)
docker-compose up -d

# Start specific service
docker-compose up backend
docker-compose up frontend

# View logs
docker-compose logs
docker-compose logs backend
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f
```

### Managing Containers
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart services
docker-compose restart

# View running containers
docker-compose ps

# Execute commands in running containers
docker-compose exec backend bash
docker-compose exec frontend sh
```

## Service Details

### Backend Service
- **Container Name:** ai-fashion-backend
- **Port:** 8000
- **Base Image:** python:3.11-slim
- **Key Dependencies:** FastAPI, TensorFlow, OpenCV, scikit-learn
- **Health Check:** Endpoint at `/health`
- **Volume Mounts:** Backend code for hot-reload during development

### Frontend Service
- **Container Name:** ai-fashion-frontend
- **Port:** 3000
- **Base Image:** node:18-alpine
- **Key Dependencies:** React, Vite, Tailwind CSS
- **Environment:** Production build served via preview server
- **Volume Mounts:** Frontend code for development

## Environment Variables

### Backend
- `PYTHONPATH=/app` - Python module path
- `PYTHONUNBUFFERED=1` - Unbuffered Python output

### Frontend
- `VITE_API_URL=http://localhost:8000` - Backend API URL
- `NODE_ENV=production` - Node.js environment

## Development Workflow

### Hot Reload Development
The containers are configured with volume mounts to enable hot reload during development:

1. **Start in development mode:**
   ```bash
   docker-compose up
   ```

2. **Make changes to your code** - Changes will be automatically reflected in the running containers.

3. **Backend changes** will trigger FastAPI's auto-reload feature.

4. **Frontend changes** will trigger Vite's hot module replacement.

### Debugging
```bash
# Access backend container shell
docker-compose exec backend bash

# Access frontend container shell
docker-compose exec frontend sh

# View container logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Check container status
docker-compose ps
```

## Data Persistence

The application uses volume mounts for development, ensuring your code changes persist. The containers exclude:
- `venv` directory for backend (Python virtual environment)
- `node_modules` directory for frontend (Node.js dependencies)

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Check what's using the port
   netstat -an | findstr :8000
   netstat -an | findstr :3000
   
   # Stop conflicting services or change ports in docker-compose.yml
   ```

2. **Permission issues (Linux/Mac):**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

3. **Out of disk space:**
   ```bash
   # Clean up Docker
   docker system prune -a
   docker volume prune
   ```

4. **Backend health check failing:**
   ```bash
   # Check backend logs
   docker-compose logs backend
   
   # Verify backend is responding
   curl http://localhost:8000/health
   ```

### Rebuilding from Scratch
```bash
# Stop all containers
docker-compose down

# Remove all containers, networks, and volumes
docker-compose down -v --remove-orphans

# Remove all images
docker-compose down --rmi all

# Clean build
docker-compose build --no-cache

# Start fresh
docker-compose up
```

## Production Deployment

For production deployment, consider:

1. **Environment-specific configuration:**
   - Create separate `docker-compose.prod.yml`
   - Use environment variables for configuration
   - Implement proper secrets management

2. **Performance optimizations:**
   - Use multi-stage builds for smaller images
   - Implement proper caching strategies
   - Use production-grade web servers (nginx, gunicorn)

3. **Security considerations:**
   - Run containers as non-root users
   - Use specific image tags instead of `latest`
   - Implement proper network security

4. **Monitoring and logging:**
   - Add logging aggregation
   - Implement health checks
   - Set up monitoring and alerting

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    AI-Fashion Application                    │
├─────────────────────────────────────────────────────────────┤
│  Frontend Container (Port 3000)                            │
│  ├─ React + Vite                                           │
│  ├─ Tailwind CSS                                           │
│  └─ Production Build                                       │
├─────────────────────────────────────────────────────────────┤
│  Backend Container (Port 8000)                             │
│  ├─ FastAPI Server                                         │
│  ├─ TensorFlow ML Models                                   │
│  ├─ OpenCV Image Processing                                │
│  └─ Product & Color APIs                                   │
├─────────────────────────────────────────────────────────────┤
│  Docker Network: ai-fashion-network                        │
└─────────────────────────────────────────────────────────────┘
```

## Next Steps

After successfully running the containerized application:

1. **Test all functionality** to ensure everything works correctly
2. **Customize configuration** for your specific needs
3. **Set up CI/CD pipeline** for automated deployment
4. **Implement monitoring** and logging for production use
5. **Consider orchestration** with Kubernetes for scaling

For any issues or questions, refer to the main project README.md or check the Docker logs for detailed error information.
