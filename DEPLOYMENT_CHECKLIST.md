# 🏁 Enterprise LLMOps RAG - Deployment Checklist & Quick Start

## ✅ Completed Components

### Core System (100% Complete)
- [x] FAISS Vector Database (`vector_store/faiss_store.py`)
- [x] Document Retriever (`services/retriever.py`)
- [x] LLM Service with Demo Mode (`services/llm_service.py`)
- [x] RAG Engine (`rag_engine/__init__.py`)
- [x] Text Embeddings (`embeddings/embed.py`)
- [x] REST API Gateway (`api_gateway/main.py`)
- [x] Streamlit Frontend (`frontend_streamlit/app.py`)
- [x] QA Agent (`agents/qa_agent.py`, `agents/research_agent.py`)

### Infrastructure (100% Complete)
- [x] Docker Compose (`docker-compose.yml`)
- [x] Docker Images (FastAPI + Streamlit Dockerfiles)
- [x] Kubernetes Deployment (`infra/k8s/deployment.yaml`)
- [x] Kubernetes Services (`infra/k8s/service.yaml`)
- [x] Persistent Storage (`infra/k8s/persistent-volumes.yaml`)
- [x] Namespace & Config (`infra/k8s/namespace.yaml`)
- [x] GitHub Actions CI/CD (`.github/workflows/ci-cd.yml`)
- [x] Security Scanning (`.github/workflows/security.yml`)

### Automation & Documentation (100% Complete)
- [x] Docker build script (`infra/docker/build.sh`)
- [x] K8s deployment script (`infra/k8s/deploy.sh`)
- [x] API test script (`infra/docker/test-api.sh`)
- [x] Setup script (`infra/setup.sh`)
- [x] Docker Guide (`infra/DOCKER_GUIDE.md`)
- [x] Kubernetes Guide (`infra/KUBERNETES_GUIDE.md`)
- [x] CI/CD Guide (`infra/CI_CD_GUIDE.md`)
- [x] Infrastructure README (`infra/README.md`)
- [x] Deployment Architecture Doc (`DEPLOYMENT_ARCHITECTURE.md`)

---

## 🚀 Quick Start Guide

### Option 1: Docker Compose (Easiest - 5 minutes)

**Step 1: Setup Environment**
```bash
cd "/mnt/c/Users/Ayorinde/OneDrive/Desktop/end-to-end llmops"

# Copy .env.example to .env and add your OpenAI API key
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-...
nano .env  # or use your editor
```

**Step 2: Build & Start**
```bash
bash infra/docker/build.sh
```

**Step 3: Access the Application**
- API Gateway: http://localhost:8000
- Streamlit UI: http://localhost:8501
- API Docs: http://localhost:8000/docs

**Step 4: Test the API**
```bash
bash infra/docker/test-api.sh http://localhost:8000
```

**Step 5: Stop Services**
```bash
docker-compose down
```

#### Common Docker Commands
```bash
# View logs
docker-compose logs -f api
docker-compose logs -f streamlit

# Restart a service
docker-compose restart api
docker-compose restart streamlit

# Remove everything (fresh start)
docker-compose down -v
```

---

### Option 2: Kubernetes/Minikube (Testing - 10 minutes)

**Step 1: Setup**
```bash
# Make scripts executable
bash infra/setup.sh

# Ensure Minikube is running
minikube start --cpus=4 --memory=4096
```

**Step 2: Configure Environment**
```bash
# Create .env with your OpenAI API key
OPENAI_API_KEY=sk-...  # Your actual key

# Create K8s secret
kubectl create namespace llmops
kubectl create secret generic llmops-secrets \
  --from-literal=OPENAI_API_KEY=$OPENAI_API_KEY \
  -n llmops
```

**Step 3: Deploy**
```bash
bash infra/k8s/deploy.sh
```

**Step 4: Access Application**
```bash
# Get service ports
kubectl get svc -n llmops

# Port forward if needed
kubectl port-forward svc/llmops-rag-api-service 8000:8000 -n llmops &
kubectl port-forward svc/llmops-streamlit-service 8501:8501 -n llmops &
```

**Step 5: Monitor Pods**
```bash
# Watch pods
kubectl get pods -n llmops -w

# View logs
kubectl logs -f deployment/llmops-rag-api -n llmops
kubectl logs -f deployment/llmops-streamlit -n llmops

# Describe pod for errors
kubectl describe pod <pod-name> -n llmops
```

**Step 6: Cleanup**
```bash
kubectl delete namespace llmops
```

#### Useful K8s Commands
```bash
# Check scaling
kubectl get hpa -n llmops

# Manually scale
kubectl scale deployment llmops-rag-api --replicas=5 -n llmops

# Check resource usage
kubectl top nodes
kubectl top pods -n llmops

# Get events
kubectl get events -n llmops
```

---

### Option 3: GitHub Actions CI/CD (Production Ready)

**Step 1: Setup Repository**
```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial deployment infrastructure"
git remote add origin https://github.com/YOUR_USERNAME/end-to-end-llmops.git
git push -u origin main
```

**Step 2: Configure Secrets**
```bash
# Go to GitHub repo → Settings → Secrets and variables → Actions
# Add the following secrets:

OPENAI_API_KEY: sk-...
GITHUB_TOKEN: (auto-created)
```

**Step 3: Configure CI/CD**
Edit `.github/workflows/ci-cd.yml` if needed:
- Change Docker registry (default: ghcr.io)
- Adjust deploy commands for your cloud provider
- Set notification preferences for Slack/Email

**Step 4: Trigger Pipeline**
```bash
# Push to main branch to trigger production deployment
git push origin main

# Or push to develop for staging
git push origin develop
```

**Step 5: Monitor Pipeline**
- Go to Actions tab in GitHub
- Watch real-time pipeline execution
- View logs for each job

---

## 📊 System Components Details

### API Gateway
**Port:** 8000  
**Package:** `api_gateway/main.py`

**Endpoints:**
```
POST   /ask           - Ask questions (RAG powered)
POST   /index         - Index documents  
POST   /search        - Search knowledge base
POST   /upload_pdf    - Upload PDF files
GET    /stats         - System statistics
POST   /clear         - Clear vector store
GET    /health        - Health check
GET    /docs          - Interactive API docs (Swagger)
```

**Environment Variables:**
```
OPENAI_API_KEY          - OpenAI API key (required)
USE_DEMO_MODE          - Use demo answers (true/false)
LOG_LEVEL              - Logging level (INFO/DEBUG)
MAX_WORKERS            - Uvicorn workers (default: 4)
```

### Streamlit Frontend
**Port:** 8501  
**Package:** `frontend_streamlit/app.py`

**Features:**
- Document upload (PDF/TXT)
- Question answering with RAG
- Retrieved sources display
- Model mode toggling
- Response color coding

**Environment Variables:**
```
API_URL               - API Gateway URL (default: localhost:8000)
OPENAI_API_KEY       - For direct embedding calls
STREAMLIT_THEME      - UI theme
```

### Vector Store (FAISS)
**Location:** `vector_store/`

**Features:**
- FlatL2 index (default, best accuracy)
- IVFFlat index (for large-scale, faster)
- Persistent storage with metadata
- Support for ~10M vectors (local), billions with distributed setup

**Storage Structure:**
```
vector_store/
├── documents.index      - FAISS binary index
├── documents.embeddings - Embedding vectors
└── documents.metadata   - Document metadata
```

---

## 🔍 Testing & Validation

### Quick Validation (All in one)
```bash
# Make scripts executable first
bash infra/setup.sh

# Option A: Docker Compose
bash infra/docker/build.sh
sleep 10  # Wait for services to start
bash infra/docker/test-api.sh http://localhost:8000

# Option B: Kubernetes  
minikube start
bash infra/k8s/deploy.sh
sleep 30  # Wait for rollout
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -n llmops \
  -- curl http://llmops-rag-api-service:8000/health
```

### Manual API Testing
```bash
# Health check
curl http://localhost:8000/health

# Index a document
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {"content": "Python is great for data science", "metadata": {"source": "doc1"}}
    ]
  }'

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Python used for?"}'

# View stats
curl http://localhost:8000/stats
```

### Unit Tests
```bash
# Run tests (requires pytest)
cd /mnt/c/Users/Ayorinde/OneDrive/Desktop/end-to-end\ llmops
python -m pytest tests/ -v

# Or using Docker
docker run --rm -v $(pwd):/app python:3.12 \
  bash -c "cd /app && pip install -q -r requirements.txt && python -m pytest tests/ -v"
```

---

## 🐛 Troubleshooting

### Docker Issues

**Error: "Cannot connect to Docker daemon"**
```bash
# Start Docker Desktop or Docker daemon
sudo systemctl start docker  # Linux
open -a Docker  # macOS
```

**Error: "Port already in use"**
```bash
# Kill existing process on port
sudo lsof -ti:8000 | xargs kill -9  # Port 8000
sudo lsof -ti:8501 | xargs kill -9  # Port 8501
```

**Error: "Image build failed"**
```bash
# Clear Docker cache and rebuild
docker-compose down -v
docker system prune -a
bash infra/docker/build.sh
```

### Kubernetes Issues

**Error: "No resources found in llmops namespace"**
```bash
# Create namespace and secrets first
kubectl create namespace llmops
kubectl create secret generic llmops-secrets \
  --from-literal=OPENAI_API_KEY=sk-... -n llmops
```

**Pods stuck in "Pending"**
```bash
# Check Minikube status
minikube status
minikube dashboard  # Visual inspection

# Check node resources
kubectl top nodes
kubectl describe node minikube

# Increase Minikube resources
minikube stop
minikube start --cpus=8 --memory=8192
```

**Error: "ImagePullBackOff"**
```bash
# Build images in Minikube
eval $(minikube docker-env)
docker-compose build
eval $(minikube docker-env -u)

# Or rebuild with correct registry
bash infra/k8s/deploy.sh
```

### API Issues

**Error: "OPENAI_API_KEY not provided"**
```bash
# For Docker Compose
export OPENAI_API_KEY=sk-...
docker-compose up

# For Kubernetes
kubectl create secret generic llmops-secrets \
  --from-literal=OPENAI_API_KEY=sk-... -n llmops

# For local testing
export OPENAI_API_KEY=sk-...
python -c "from api_gateway.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0')"
```

**Error: "Demo mode responses not working"**
```bash
# Enable demo mode
export USE_DEMO_MODE=true

# Or set in docker-compose.yml environment
```

**Error: "Connection refused to API"**
```bash
# Check if service is running
curl http://localhost:8000/health  # Docker Compose
kubectl logs -f deployment/llmops-rag-api -n llmops  # K8s

# Wait for health check
sleep 10 && curl http://localhost:8000/health
```

---

## 📈 Performance Tips

### Docker Compose
```bash
# Use BuildKit for faster builds (modern Docker)
export DOCKER_BUILDKIT=1
docker-compose build

# Resource limits in docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

### Kubernetes
```bash
# Scale based on demand
kubectl autoscale deployment llmops-rag-api --min=2 --max=10 --cpu-percent=70 -n llmops

# Monitor scaling in real-time
kubectl get hpa -n llmops -w
```

### Vector Store
```bash
# For <1M vectors: Use FlatL2 (default)
# For 1-10M vectors: Use IVFFlat (faster, trade-off accuracy)
# For >10M vectors: Use distributed FAISS or specialized vector DB
```

---

## 🔄 Development Workflow

### Local Development
```bash
# Update code locally
nano api_gateway/main.py

# Rebuild and test with Docker Compose
docker-compose down
docker-compose build --no-cache
bash infra/docker/build.sh

# Or direct testing
export OPENAI_API_KEY=sk-...
export USE_DEMO_MODE=true
python -m uvicorn api_gateway.main:app --reload
```

### Testing Changes
```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and test
# ... edit files and test ...

# Push and create PR
git push origin feature/my-feature

# CI/CD runs automatically on develop/main
```

### Deploying to Production
```bash
# Merge to main branch
git checkout main
git merge feature/my-feature
git push origin main

# GitHub Actions automatically:
# 1. Runs tests
# 2. Builds Docker images
# 3. Pushes to registry
# 4. Deploys to K8s cluster
```

---

## 📚 Documentation Map

| Document | Purpose | When to Use |
|----------|---------|------------|
| `README.md` | Project overview | Start here |
| `DEPLOYMENT_ARCHITECTURE.md` | System design & flows | Understand architecture |
| `infra/DOCKER_GUIDE.md` | Docker Compose details | Local development |
| `infra/KUBERNETES_GUIDE.md` | Minikube/K8s details | Staging/testing |
| `infra/CI_CD_GUIDE.md` | GitHub Actions details | Production setup |
| `infra/README.md` | Infrastructure overview | Choose deployment method |
| `requirements.txt` | Python dependencies | Environment setup |

---

## 🎯 Next Steps

### Immediate (This Week)
- [ ] Pick deployment method (Docker Compose recommended for quick start)
- [ ] Set up `.env` with OpenAI API key
- [ ] Run `bash infra/docker/build.sh` or `bash infra/k8s/deploy.sh`
- [ ] Test API endpoints with provided test script
- [ ] Upload some documents to try RAG functionality

### Short Term (This Month)
- [ ] Integrate with your data sources
- [ ] Customize system prompts in `llm_service.py`
- [ ] Tune RAG chunking parameters in `rag_engine/__init__.py`
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure CI/CD secrets in GitHub

### Medium Term (This Quarter)
- [ ] Implement advanced vector search (Milvus/Pinecone)
- [ ] Add multi-model support (Claude, Gemini, etc)
- [ ] Implement caching layer (Redis)
- [ ] Add authentication (JWT, OAuth)
- [ ] Set up centralized logging (ELK, Loki)
- [ ] Enable horizontal scaling with auto-recovery

### Long Term (This Year)
- [ ] Multi-tenant support
- [ ] Advanced RAG techniques (hybrid search, reranking)
- [ ] Custom fine-tuning pipeline
- [ ] Real-time metrics and alerting
- [ ] Disaster recovery and backup strategy
- [ ] Multi-region deployment

---

## 💡 Tips & Best Practices

1. **Always start with demo mode** - Set `USE_DEMO_MODE=true` to test without API costs
2. **Keep `.env` files secure** - Never commit to git, use GitHub Secrets in CI/CD
3. **Use Docker Compose first** - Simplest way to validate everything works
4. **Monitor logs** - Check logs early: `docker-compose logs -f` or `kubectl logs -f`
5. **Start small** - Index a few documents first before adding millions
6. **Test the vector store** - Use `/search` endpoint to verify retrieval quality
7. **Version your data** - Keep track of when you indexed documents
8. **Set rate limits** - Protect against API abuse in production
9. **Use health checks** - Always include `/health` endpoint monitoring
10. **Plan for scaling** - Document your scaling strategy before you need it

---

## 📞 Support & Resources

### Documentation
- OpenAI API: https://platform.openai.com/docs
- FastAPI: https://fastapi.tiangolo.com
- Streamlit: https://docs.streamlit.io
- Kubernetes: https://kubernetes.io/docs
- FAISS: https://github.com/facebookresearch/faiss

### Common Issues
See **Troubleshooting** section above for:
- Docker connection issues
- Port conflicts  
- Kubernetes resource problems
- API authentication errors

### Getting Help
1. Check logs first: `docker-compose logs` or `kubectl logs`
2. Review architecture diagram: `DEPLOYMENT_ARCHITECTURE.md`
3. Check relevant guide: Docker/K8s/CI-CD
4. Verify `.env` file and API key

---

**System Version:** 1.0.0  
**Last Updated:** February 2026  
**Status:** ✅ Production Ready  
**Support Level:** Full
