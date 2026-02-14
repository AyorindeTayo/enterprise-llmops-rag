# Docker Deployment Guide

## Quick Start with Docker Compose

### 1. Prerequisites
```bash
docker --version  # Docker CE 20.10+
docker-compose --version  # Docker Compose 1.29+
```

### 2. Set Environment Variables
```bash
# Create .env file (already exists in project)
cat .env  # Should contain OPENAI_API_KEY
```

### 3. Build and Start Services
```bash
# Make build script executable
bash infra/docker/build.sh

# Or use docker-compose directly
docker-compose up -d

# Or rebuild without cache
docker-compose up -d --build
```

### 4. Access Services
- **FastAPI (API Gateway):** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Streamlit (UI):** http://localhost:8501

### 5. View Logs
```bash
# Follow API logs
docker-compose logs -f api

# Follow Streamlit logs
docker-compose logs -f streamlit

# View all logs
docker-compose logs
```

### 6. Stop Services
```bash
docker-compose down

# Cleanup volumes too
docker-compose down -v
```

### 7. Run Tests
```bash
bash infra/docker/test-api.sh
```

## Container Details

### FastAPI Container
- **Image:** `llmops-rag-api:latest`
- **Port:** 8000
- **Health Check:** GET /health
- **Resources:**
  - CPU: 500m request, 1000m limit
  - Memory: 512Mi request, 1Gi limit
- **Volumes:** vector_store, logs

### Streamlit Container
- **Image:** `llmops-streamlit:latest`
- **Port:** 8501
- **Depends On:** api (healthy)
- **Resources:**
  - CPU: 250m request, 500m limit
  - Memory: 256Mi request, 512Mi limit

## Troubleshooting

### API not responding
```bash
# Check container status
docker-compose ps

# Restart service
docker-compose restart api

# Check logs
docker-compose logs api | tail -50
```

### Port already in use
```bash
# Change port in docker-compose.yml
# Or kill process on port
lsof -i :8000  # Find process
kill -9 <PID>  # Kill it
```

### Volumes/Persistence issues
```bash
# Check volume status
docker volume ls | grep llmops

# Inspect volume
docker volume inspect docker_vector_store

# Clean volumes
docker volume rm docker_vector_store docker_logs
```

### Streamlit connection issues
```bash
# Streamlit can't reach API
# Check from inside Streamlit container
docker-compose exec streamlit curl http://api:8000/health
```
