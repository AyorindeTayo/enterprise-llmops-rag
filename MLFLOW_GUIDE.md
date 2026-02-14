# MLflow Integration Guide

## Overview
MLflow has been integrated into the LLMOps RAG project for experiment tracking, model registry, and artifact management.

## Architecture

```
experiment_tracking/
├── __init__.py                # Package exports
├── tracking_config.py         # MLflow server config & client setup
├── log_utils.py              # Logging utilities & decorators
└── model_registry.py         # Model Registry management
```

## Setup

### Local Development
```bash
# MLflow is installed in requirements.txt
pip install -r requirements.txt

# Initialize MLflow (run once)
python -c "from experiment_tracking import init_mlflow; init_mlflow()"
```

### Docker Compose
MLflow server is already configured in `docker-compose.yml`:
```bash
docker-compose up -d mlflow
# Access: http://localhost:5000
```

### Kubernetes
Deploy MLflow on Minikube:
```bash
# Option 1: Deploy all (includes MLflow)
bash infra/k8s/deploy.sh

# Option 2: Deploy only MLflow
bash infra/k8s/deploy-mlflow.sh

# Access via port-forward
kubectl port-forward svc/mlflow-service 5000:5000 -n llmops
# http://localhost:5000
```

## Usage Examples

### 1. Track Training Runs
```python
from experiment_tracking import log_training_run, log_llm_call
import mlflow

# Log LLM calls
log_llm_call(
    model="gpt-4",
    prompt="What is RAG?",
    response="Retrieval-Augmented Generation...",
    tokens_used=256,
    temperature=0.7
)

# Or use decorator
@log_training_run(
    run_name="rag-training-v1",
    params={"model": "gpt-4", "k": 5}
)
def train_model():
    answer = generate_answer(question, context)
    mlflow.log_metric("accuracy", 0.92)
    return answer
```

### 2. Log Predictions
```python
from experiment_tracking import log_prediction

log_prediction(
    question="What is machine learning?",
    answer="Machine learning is...",
    context="Retrieved context: ...",
    latency_ms=125.5,
    model_version="gpt-4-turbo",
    user_feedback="helpful"
)
```

### 3. Log Evaluation Metrics
```python
from experiment_tracking import log_evaluation_metrics

log_evaluation_metrics({
    "rouge_1": 0.85,
    "rouge_2": 0.78,
    "bleu": 0.92,
    "semantic_similarity": 0.89
})
```

### 4. Register & Manage Models
```python
from experiment_tracking import register_model, get_latest_model, transition_model_to_stage

# Register a model
mlflow.start_run()
mlflow.sklearn.log_model(model, "rag-llm")
register_model(
    "runs:/abc123/rag-llm",
    "rag-llm-v1",
    description="RAG LLM for QA",
    tags={"environment": "production"}
)

# Get latest production model
prod_model = get_latest_model("rag-llm-v1", stage="Production")

# Transition to stage
transition_model_to_stage("rag-llm-v1", version=3, stage="Production")
```

## Environment Variables

```bash
# MLflow server URI (default: http://localhost:5000)
export MLFLOW_TRACKING_URI=http://mlflow-service:5000

# Experiment name (default: llmops-rag)
export MLFLOW_EXPERIMENT_NAME=llmops-rag

# Artifacts path (default: ./mlflow_artifacts or /mlflow/artifacts in container)
export MLFLOW_ARTIFACT_PATH=/mlflow/artifacts
```

## Integration Points

### API Gateway
Add to `api_gateway/main.py`:
```python
from experiment_tracking import log_prediction
import time

@app.post("/ask")
def ask(req: AskRequest):
    start = time.time()
    answer = answer_question(req.question, k=req.k)
    latency = (time.time() - start) * 1000
    
    log_prediction(
        question=req.question,
        answer=answer,
        context="...",
        latency_ms=latency
    )
    return {"question": req.question, "answer": answer}
```

### Services
Add to `services/llm_service.py`:
```python
from experiment_tracking import log_llm_call

def generate_answer(question, context, use_demo=False):
    # ... existing code ...
    log_llm_call(
        model="gpt-4",
        prompt=prompt,
        response=answer,
        tokens_used=token_count
    )
    return answer
```

## Dashboard & Monitoring

Once MLflow is running:

1. **Open MLflow UI**: http://localhost:5000 (or http://localhost:5000 via port-forward)
2. **View Experiments**: See all tracked runs and their metrics
3. **Compare Runs**: Side-by-side comparison of different runs
4. **Model Registry**: Register, stage, and deploy models
5. **Artifact Storage**: View logged artifacts, models, and plots

## Best Practices

1. **Set Experiment Name Early**:
   ```python
   from experiment_tracking import init_mlflow
   init_mlflow(experiment_name="my-experiment")
   ```

2. **Use Context Managers**:
   ```python
   with mlflow.start_run():
       mlflow.log_metric("accuracy", 0.95)
   ```

3. **Tag Runs for Organization**:
   ```python
   mlflow.set_tag("environment", "production")
   mlflow.set_tag("team", "ml-engineering")
   ```

4. **Avoid External Calls in Tests**: Ensure MLflow is disabled or mocked in unit tests

## Troubleshooting

### MLflow not connecting
```bash
# Check if MLflow server is running
curl http://localhost:5000/

# Check env vars
echo $MLFLOW_TRACKING_URI

# Restart MLflow
docker-compose restart mlflow
```

### Port conflicts
```bash
# Find process using port 5000
lsof -i :5000

# Use different port
MLFLOW_TRACKING_URI=http://localhost:5001 python app.py
```

## References

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [MLflow Python API](https://mlflow.org/docs/latest/python_api/index.html)
- [Model Registry Guide](https://mlflow.org/docs/latest/model_registry.html)
