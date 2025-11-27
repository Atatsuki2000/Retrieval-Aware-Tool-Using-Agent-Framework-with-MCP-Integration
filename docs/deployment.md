# Deployment Guide

## Local Development Deployment

### Prerequisites
- Python 3.10+
- Git
- 4 GB RAM minimum
- 2 GB disk space

### Step-by-Step Setup

#### 1. Environment Setup
```bash
# Clone repository
git clone https://github.com/Atatsuki2000/Retrieval-Aware-Tool-Using-Agent-Framework-with-MCP-Integration.git
cd Retrieval-Aware-Tool-Using-Agent-Framework-with-MCP-Integration

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Windows CMD
.venv\Scripts\activate.bat
# Linux/Mac
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Build Vector Database
```bash
cd agent
python test_retriever.py
# This will download HuggingFace model (~90MB) and build Chroma index
```

#### 3. Start MCP Tool Services

**Terminal 1 - Plot Service:**
```bash
cd tools/plot-service
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - Calculator Service:**
```bash
cd tools/calculator
uvicorn main:app --host 0.0.0.0 --port 8001
```

**Terminal 3 - PDF Parser Service:**
```bash
cd tools/pdf-parser
uvicorn main:app --host 0.0.0.0 --port 8002
```

#### 4. Launch Frontend
**Terminal 4 - Streamlit UI:**
```bash
cd frontend
streamlit run app.py --server.port 9000
```

#### 5. Access Application
Open browser: `http://localhost:9000`

---

## Google Cloud Run Deployment (Optional)

Deploy all MCP tools to Google Cloud Run using the automated deployment script.

### Prerequisites
- Google Cloud Platform account
- gcloud CLI installed ([installation guide](https://cloud.google.com/sdk/docs/install))

### Quick Start (Automated Deployment)

**Step 1: Authenticate with Google Cloud**
```bash
# Login to Google Cloud
gcloud auth login

# Set your project ID
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

**Step 2: Deploy All Services**
```bash
# Run the automated deployment script
bash deploy-cloud-run.sh
```

The script will:
- Deploy plot-service, calculator, and pdf-parser to Cloud Run
- Configure each service with 512Mi memory, 1 CPU, 60s timeout
- Set up auto-scaling (0-10 instances)
- Output service URLs for configuration

**Step 3: Update Agent Configuration**

The script outputs environment variables. Add to your `.env` file:
```bash
PLOT_SERVICE_URL=https://plot-service-xxx.run.app/mcp/plot
CALCULATOR_URL=https://calculator-xxx.run.app/mcp/calculate
PDF_PARSER_URL=https://pdf-parser-xxx.run.app/mcp/parse
```

Or configure in Streamlit sidebar.

---

### Manual Deployment (Advanced)

If you prefer manual control over the deployment process:

#### Step 1: Review Dockerfiles

**tools/plot-service/Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**tools/plot-service/requirements.txt:**
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
matplotlib==3.10.7
pydantic==2.5.3
```

**tools/calculator/Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**tools/calculator/requirements.txt:**
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
numexpr==2.10.2
pydantic==2.5.3
```

**tools/pdf-parser/Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**tools/pdf-parser/requirements.txt:**
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
pypdf==5.1.0
pydantic==2.5.3
```

#### Step 2: Deploy Each Service Manually

```bash
# Set project ID and region
export PROJECT_ID=your-gcp-project-id
export REGION=us-central1

# Authenticate
gcloud auth login
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com

# Deploy plot-service
cd tools/plot-service
gcloud run deploy plot-service \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60 \
  --max-instances 10 \
  --min-instances 0

# Deploy calculator
cd ../calculator
gcloud run deploy calculator \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60 \
  --max-instances 10 \
  --min-instances 0

# Deploy pdf-parser
cd ../pdf-parser
gcloud run deploy pdf-parser \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60 \
  --max-instances 10 \
  --min-instances 0
```

#### Step 3: Get Service URLs

```bash
# Get deployed URLs
gcloud run services describe plot-service --region $REGION --format 'value(status.url)'
gcloud run services describe calculator --region $REGION --format 'value(status.url)'
gcloud run services describe pdf-parser --region $REGION --format 'value(status.url)'
```

---

## CI/CD with GitHub Actions

The project includes automated workflows in `.github/workflows/ci.yml`:

### Triggers
- Push to `main` branch
- Pull requests to `main`

### Jobs
1. **Test Job**: Runs pytest with coverage
2. **Lint Job**: Checks code style with flake8

### Manual Deployment Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches:
      - main

env:
  PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  REGION: us-central1

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Cloud SDK
      uses: google-github-actions/setup-gcloud@v1
      with:
        service_account_key: ${{ secrets.GCP_SA_KEY }}
        project_id: ${{ secrets.GCP_PROJECT_ID }}
    
    - name: Build and Deploy Plot Service
      run: |
        cd tools/plot-service
        gcloud builds submit --tag gcr.io/$PROJECT_ID/plot-service
        gcloud run deploy plot-service \
          --image gcr.io/$PROJECT_ID/plot-service \
          --platform managed \
          --region $REGION \
          --allow-unauthenticated
    
    - name: Build and Deploy Calculator
      run: |
        cd tools/calculator
        gcloud builds submit --tag gcr.io/$PROJECT_ID/calculator
        gcloud run deploy calculator \
          --image gcr.io/$PROJECT_ID/calculator \
          --platform managed \
          --region $REGION \
          --allow-unauthenticated
    
    - name: Build and Deploy PDF Parser
      run: |
        cd tools/pdf-parser
        gcloud builds submit --tag gcr.io/$PROJECT_ID/pdf-parser
        gcloud run deploy pdf-parser \
          --image gcr.io/$PROJECT_ID/pdf-parser \
          --platform managed \
          --region $REGION \
          --allow-unauthenticated
```

### Required GitHub Secrets
- `GCP_PROJECT_ID`: Your GCP project ID
- `GCP_SA_KEY`: Service account JSON key with Cloud Run Admin permissions

---

## Monitoring & Logging

### Local Development
- **Streamlit logs**: Terminal 4 output
- **Tool logs**: Terminals 1-3 output
- **Agent logs**: Add `logging` module to `agent.py`

### Cloud Run
```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=plot-service" --limit 50

# Monitor metrics
gcloud monitoring dashboards list
```

---

## Troubleshooting

### Issue: Port already in use
**Solution:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Issue: HuggingFace model download fails
**Solution:**
```bash
# Manually download model
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
```

### Issue: Chroma DB persistence error
**Solution:**
Delete existing Chroma directory and rebuild:
```bash
rm -rf agent/chroma_db
python agent/test_retriever.py
```

### Issue: Cloud Run cold start latency
**Solution:**
Enable minimum instances:
```bash
gcloud run services update plot-service \
  --min-instances 1 \
  --region $REGION
```

---

## Cost Estimation (Cloud Run)

| Service | Requests/day | Monthly Cost (estimate) |
|---------|-------------|------------------------|
| plot-service | 1,000 | $0.50 |
| calculator | 1,000 | $0.50 |
| pdf-parser | 1,000 | $0.50 |
| **Total** | | **~$1.50/month** |

*Based on 1M free requests/month and minimal CPU/memory usage*

---

## Security Best Practices

1. **Authentication**: Add API key validation for production
2. **Rate Limiting**: Implement per-user quotas
3. **HTTPS**: Use TLS certificates (automatic on Cloud Run)
4. **Input Validation**: Already implemented in MCP endpoints
5. **Secret Management**: Use Google Secret Manager for credentials

---

## Scaling Considerations

### Horizontal Scaling
- Cloud Run auto-scales based on traffic
- Configure max instances:
```bash
gcloud run services update plot-service --max-instances 10
```

### Vertical Scaling
- Increase memory/CPU:
```bash
gcloud run services update plot-service --memory 2Gi --cpu 2
```

### Database Scaling
- For large corpora, consider Pinecone or Weaviate
- Chroma supports distributed deployment
