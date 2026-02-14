# Docker and Kubernetes Orchestration for Enterprise LLMOps RAG

Complete containerization and deployment infrastructure for the RAG system.

## 📁 Structure

```
infra/
├── docker/
│   ├── Dockerfile              # FastAPI container
│   ├── Dockerfile.streamlit    # Streamlit container
│   ├── build.sh                # Build script for Docker Compose
│   ├── test-api.sh             # API testing script
│   └── .dockerignore           # Files to exclude from Docker build
│
├── k8s/
│   ├── deployment.yaml         # K8s deployments (API + Streamlit)
│   ├── service.yaml            # K8s services and load balancer
│   ├── persistent-volumes.yaml # Storage configuration
│   ├── namespace.yaml          # Namespace, config, secrets
│   ├── deploy.sh               # Deployment script
│   └── kustomization.yaml      # Kustomize overlay (optional)
│
├── setup.sh                    # Make scripts executable
├── DOCKER_GUIDE.md             # Docker Compose guide
├── KUBERNETES_GUIDE.md         # Minikube/K8s guide
└── CI_CD_GUIDE.md              # GitHub Actions guide
```

## 🚀 Quick Start

### Option 1: Docker Compose (Easiest)
```bash
bash infra/docker/build.sh
# Starts both API and Streamlit on ports 8000 and 8501
```

### Option 2: Kubernetes with Minikube
```bash
bash infra/k8s/deploy.sh
# Deploys to local Minikube cluster
```

### Option 3: CI/CD Pipeline (GitHub Actions)
Push to `main` branch → Automated build, test, and deployment

## 📖 Documentation

- **[DOCKER_GUIDE.md](./DOCKER_GUIDE.md)** - Docker Compose deployment
- **[KUBERNETES_GUIDE.md](./KUBERNETES_GUIDE.md)** - Minikube/K8s deployment
- **[CI_CD_GUIDE.md](./CI_CD_GUIDE.md)** - GitHub Actions CI/CD

## 🐳 Docker Services

### FastAPI Gateway (api_gateway)
- **Port:** 8000
- **Image:** `llmops-rag-api:latest`
- **Features:**
  - 4 Uvicorn workers
  - Health checks enabled
  - Volume persistence for vector store
  - Environment variables: OPENAI_API_KEY, USE_DEMO_MODE

### Streamlit UI (streamlit)
- **Port:** 8501
- **Image:** `llmops-streamlit:latest`
- **Features:**
  - Depends on API health
  - Headless mode
  - API connection via docker network

## ☸️ Kubernetes Architecture

### Deployments
- **llmops-rag-api:** 3 replicas (scalable)
- **llmops-streamlit:** 1 replica (single frontend)

### Services
- **ClusterIP:** api-gateway (internal)
- **NodePort:** Streamlit (port 30501)
- **LoadBalancer:** API (optional, for cloud)

### Storage
- **PersistentVolumeClaim:** vector-store (10Gi)
- **PersistentVolumeClaim:** logs (5Gi)

### Scaling
- **Horizontal Pod Autoscaler:** CPU 70%, Memory 80%
- **Min/Max replicas:** 2-10

## 🔄 CI/CD Pipeline

### GitHub Actions Workflows

**ci-cd.yml** (Main)
1. Test & Lint
2. Build Docker Images
3. Deploy to Minikube
4. Security Scan
5. Slack Notification

**security.yml** (Weekly + PR)
1. Bandit Security Scan
2. Safety Dependency Check

### Environments
- **develop:** Pre-production testing
- **main:** Production deployment

## 📊 Resource Allocation

### FastAPI
- **Request:** 500m CPU, 512Mi RAM
- **Limit:** 1000m CPU, 1Gi RAM

### Streamlit
- **Request:** 250m CPU, 256Mi RAM
- **Limit:** 500m CPU, 512Mi RAM

## 🔐 Security

### Image Security
- Multi-stage builds (smaller images)
- Minimal base image (python:3.12-slim)
- No root process (best practice)

### Network Security
- Namespace isolation (llmops ns)
- Internal ClusterIP services
- Optional LoadBalancer for API

### Secrets Management
- Kubernetes Secrets (OPENAI_API_KEY)
- Environment variables
- .env file (not committed to git)

## 🧪 Testing

### Local Testing
```bash
# Docker
docker-compose up -d
curl http://localhost:8000/health

# Kubernetes
minikube start
bash infra/k8s/deploy.sh
kubectl port-forward svc/llmops-rag-api-service 8000:8000 -n llmops
```

### API Test Suite
```bash
bash infra/docker/test-api.sh http://localhost:8000
```

## 🛠️ Common Commands

### Docker
```bash
# Build
docker-compose build

# Start
docker-compose up -d

# Logs
docker-compose logs -f api

# Stop
docker-compose down
```

### Kubernetes
```bash
# Deploy
kubectl apply -f infra/k8s/

# Status
kubectl get pods -n llmops

# Logs
kubectl logs -f deployment/llmops-rag-api -n llmops

# Port forward
kubectl port-forward svc/llmops-rag-api-service 8000:8000 -n llmops

# Scale
kubectl scale deployment llmops-rag-api --replicas=5 -n llmops
```

### GitHub Actions
```bash
# List workflows
gh workflow list

# Trigger workflow
gh workflow run ci-cd.yml

# View runs
gh run list
```

## 📈 Monitoring & Logs

### Docker Compose
```bash
docker-compose logs -f api
docker stats
```

### Kubernetes
```bash
kubectl logs -f deployment/llmops-rag-api -n llmops
kubectl top pods -n llmops
kubectl get events -n llmops
```

## 🚨 Troubleshooting

### API Won't Start
```bash
# Docker
docker-compose logs api | tail -50
docker-compose restart api

# K8s
kubectl describe pod <pod-name> -n llmops
kubectl logs <pod-name> -n llmops
```

### Can't Connect to Services
```bash
# Docker
docker network inspect docker_llmops-network

# K8s
kubectl get endpoints -n llmops
kubectl exec -it <pod> -n llmops -- curl http://llmops-rag-api-service:8000/health
```

### Persistent Volume Issues
```bash
# Kubernetes
kubectl get pvc -n llmops
kubectl describe pvc vector-store-pvc -n llmops
minikube ssh "ls -la /mnt/data/"
```

## 🎯 Next Steps

### 1. Local Development
- Use Docker Compose for quick iteration
- Mount volumes for hot-reload
- See [DOCKER_GUIDE.md](./DOCKER_GUIDE.md)

### 2. Staging/Testing
- Deploy to Minikube locally
- Test scaling and failover
- See [KUBERNETES_GUIDE.md](./KUBERNETES_GUIDE.md)

### 3. Production
- Set up GitHub Actions (see [CI_CD_GUIDE.md](./CI_CD_GUIDE.md))
- Deploy to EKS/GKE/AKS
- Configure monitoring (Prometheus/Grafana)
- Set up logging (ELK Stack)

### 4. Advanced
- Add Helm charts for templating
- Implement GitOps (ArgoCD)
- Set up service mesh (Istio)
- Add observability (Jaeger, Loki)

## 📝 Environment Configuration

See [../.env](../.env) for configuration:
```env
OPENAI_API_KEY=sk-xxx...
USE_DEMO_MODE=true
```

## 🤝 Contributing

Before submitting changes:
1. Test locally with Docker Compose
2. Run security scan: `bash infra/docker/test-api.sh`
3. Test K8s deployment: `bash infra/k8s/deploy.sh`
4. Push to develop branch for CI/CD

## 📚 Resources

- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Minikube Guide](https://minikube.sigs.k8s.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

**Last Updated:** February 2026
**Version:** 1.0.0
