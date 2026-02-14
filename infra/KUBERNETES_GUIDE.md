# Kubernetes Deployment Guide (Minikube)

## Prerequisites

### 1. Install Minikube
```bash
# macOS
brew install minikube

# Linux
curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Verify
minikube version
```

### 2. Install kubectl
```bash
# macOS
brew install kubectl

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Verify
kubectl version --client
```

### 3. Start Minikube
```bash
# Start with sufficient resources
minikube start --driver=docker --cpus=4 --memory=4096

# Verify
minikube status
```

## Deployment Steps

### 1. Automatic Deployment (Recommended)
```bash
bash infra/k8s/deploy.sh
```

### 2. Manual Deployment

#### Step 1: Create Namespace
```bash
kubectl apply -f infra/k8s/namespace.yaml
kubectl get namespace llmops
```

#### Step 2: Create Persistent Volumes
```bash
# Create directories in Minikube
minikube ssh "sudo mkdir -p /mnt/data/vector-store /mnt/data/logs"
minikube ssh "sudo chmod 777 /mnt/data/vector-store /mnt/data/logs"

# Deploy PVs
kubectl apply -f infra/k8s/persistent-volumes.yaml
kubectl get pv
```

#### Step 3: Build Docker Images
```bash
# Use Minikube's Docker daemon
eval $(minikube docker-env)

# Build images
docker build -f infra/docker/Dockerfile -t llmops-rag-api:latest .
docker build -f infra/docker/Dockerfile.streamlit -t llmops-streamlit:latest .

# Verify
docker images | grep llmops
```

#### Step 4: Deploy Services
```bash
kubectl apply -f infra/k8s/service.yaml
kubectl apply -f infra/k8s/deployment.yaml

# Check deployment status
kubectl get deployments -n llmops
kubectl get pods -n llmops
```

#### Step 5: Wait for Pods
```bash
kubectl rollout status deployment/llmops-rag-api -n llmops
kubectl rollout status deployment/llmops-streamlit -n llmops
```

## Access Services

### Port Forward Method (Recommended)

#### FastAPI Gateway
```bash
kubectl port-forward svc/llmops-rag-api-service 8000:8000 -n llmops
# Access: http://localhost:8000
```

#### Streamlit UI
```bash
kubectl port-forward svc/llmops-streamlit-service 8501:8501 -n llmops
# Access: http://localhost:8501
```

### Using NodePort

```bash
# Get Minikube IP
minikube ip  # e.g., 192.168.49.2

# Access Streamlit on NodePort 30501
http://192.168.49.2:30501
```

### Using Minikube Service Command
```bash
minikube service llmops-streamlit-service -n llmops
# Opens browser automatically
```

## Monitoring & Management

### View Pod Logs
```bash
# Follow API logs
kubectl logs -f deployment/llmops-rag-api -n llmops

# Follow Streamlit logs
kubectl logs -f deployment/llmops-streamlit -n llmops

# Logs from specific pod
kubectl logs -f <pod-name> -n llmops
```

### Describe Resources
```bash
kubectl describe deployment/llmops-rag-api -n llmops
kubectl describe service/llmops-rag-api-service -n llmops
kubectl describe pod/<pod-name> -n llmops
```

### Check Resource Usage
```bash
kubectl top nodes
kubectl top pods -n llmops
```

### Scale Deployments
```bash
# Scale API to 5 replicas
kubectl scale deployment llmops-rag-api --replicas=5 -n llmops

# Scale back to 3
kubectl scale deployment llmops-rag-api --replicas=3 -n llmops
```

### Get All Resources
```bash
kubectl get all -n llmops
```

## Testing

### Run API Tests
```bash
# Port forward first
kubectl port-forward svc/llmops-rag-api-service 8000:8000 -n llmops &

# Run tests
bash infra/docker/test-api.sh http://localhost:8000
```

### Test Pod Connectivity
```bash
# Get pod name
POD=$(kubectl get pods -n llmops -l app=rag-api -o jsonpath='{.items[0].metadata.name}')

# Test from inside pod
kubectl exec -it $POD -n llmops -- curl http://localhost:8000/health
```

## Updates & Rollouts

### Update Image
```bash
# After pushing new image
kubectl set image deployment/llmops-rag-api \
  api-gateway=llmops-rag-api:v1.1 \
  -n llmops

# Check rollout status
kubectl rollout status deployment/llmops-rag-api -n llmops
```

### Rollback Deployment
```bash
kubectl rollout undo deployment/llmops-rag-api -n llmops
kubectl rollout status deployment/llmops-rag-api -n llmops
```

## Cleanup

### Delete All Resources
```bash
kubectl delete -f infra/k8s/ -R

# Or use namespace deletion
kubectl delete namespace llmops
```

### Stop Minikube
```bash
minikube stop

# Full cleanup
minikube delete
```

## Troubleshooting

### Pod won't start
```bash
# Check pod status
kubectl describe pod <pod-name> -n llmops

# Check events
kubectl get events -n llmops
```

### CrashLoopBackOff
```bash
# View logs
kubectl logs <pod-name> -n llmops

# Check resource limits
kubectl describe pod <pod-name> -n llmops
```

### PVC pending
```bash
# Check PV status
kubectl get pv
kubectl get pvc -n llmops
kubectl describe pvc vector-store-pvc -n llmops
```

### Can't connect to service
```bash
# Test DNS
kubectl exec -it <pod-name> -n llmops -- nslookup llmops-rag-api-service

# Port forward and test
kubectl port-forward svc/llmops-rag-api-service 8000:8000 -n llmops
curl http://localhost:8000/health
```

## Advanced: Helm Deployment

For production, consider using Helm:

```bash
# Create Helm chart structure (optional)
helm create llmops

# Deploy with Helm
helm install llmops ./llmops -n llmops --create-namespace
```
