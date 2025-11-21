---
mode: agent
---
Reply to me and write comments in English.
# Retrieval-Aware Tool-Using Agent Framework with MCP Integration
### Project Plan (Prompt Context)

> SYSTEM NOTE: Use this project plan as background context when generating, improving, or executing RAG-MCP Agent code.

This file provides the complete project plan context for the RAG + MCP + Agent system. 
Load this prompt as background knowledge for reasoning, task planning, and implementation guidance.


Retrieval-Aware Tool-Using Agent Framework with MCP
 Integration — Detailed Project Plan
 
Executive Summary: This document is a comprehensive, developer-ready project plan to build a Retrieval-Augmented
Generation (RAG) + Model Context Protocol (MCP) + Agent system. The system ingests user queries, retrieves
relevant documents using a vector store, reasons using an LLM-driven agent, and autonomously invokes
MCP-compatible tool endpoints hosted on Google Cloud Run. It is designed to be resume- and portfolio-ready once
completed, with clear deliverables, code snippets, deployment scripts, testing plans, and metrics for evaluation.
1. Goals and Success Criteria
1
Build an end-to-end system that demonstrates RAG + MCP + Agent tightly integrated.
2
Produce at least three MCP tool endpoints (plot-service, pdf-parser, calculator) deployed to Google Cloud Run.
3
Create a demonstrable UI (Streamlit) showing retrieval hits, agent plan, MCP calls, and final results.
4
Produce documentation, a 2–3 minute demo video, and measurable metrics (precision@k, latency, tool success
rate).
5
Deliver a GitHub repository with CI/CD and clear README so recruiters can reproduce the demo.
2. System Architecture (Detailed)
High-level components and responsibilities: - Frontend (Streamlit): Accepts user queries and displays retrieval results,
agent planning trace, tool calls, and final artifacts. - Agent Orchestrator (LangGraph): Orchestrates retrieval, planning,
decision-making, and tool invocation. Uses LLMs for planning and natural language generation. - Retriever
(LangChain): Embeddings + vector store (Chroma or FAISS) that returns top-k document chunks for a query. - MCP
Tool Services (FastAPI): Stateless HTTP endpoints that accept a standardized MCP JSON schema and return
structured results (artifact URL/base64, summary, logs). - Storage & Secrets: Chroma (local) for vectors in dev;
Firestore or Cloud Storage for production persistence; Secret Manager for API keys. - LLM Backend: OpenAI (GPT-4 /
GPT-4o) or Vertex AI. Embeddings via OpenAI or a local embedding model during prototyping. - CI/CD & Hosting:
GitHub Actions to build images and deploy to Google Cloud Run. Artifact Registry / GCR for container images.
Architecture Diagram (textual):
[User UI (Streamlit / CLI)]
        ↓
[Agent Orchestrator (LangGraph)]
   ↓                ↓             ↓
[RAG Retriever]  [LLM Reasoner]  [MCP Tool Caller]
   ↓               ↓                ↑
[Vector DB]     [LLM API]     [Cloud Run Tool Services]
3. Technology Stack (concrete)
1
Language: Python 3.10+
2
Agent: LangGraph (or CrewAI/AutoGen)
3
RAG: LangChain (+ LlamaIndex optional)
4
Vector DB: Chroma (dev) / FAISS / Pinecone (prod)
5
Embeddings: OpenAI Embeddings (or local alternatives)
6
LLM: OpenAI GPT-4 / Vertex AI models

7
MCP Tool Framework: FastAPI + Uvicorn, containerized with Docker
8
Cloud: Google Cloud Run, Secret Manager, Cloud Build / Artifact Registry, Firestore (optional)
9
Frontend: Streamlit (demo) or FastAPI + simple frontend
10
CI: GitHub Actions
4. Milestones & Timeline (6-week plan, detailed tasks)
Week 0 (Setup, 1–2 days) — Create GitHub repo, GCP project, enable APIs (Cloud Run, Cloud Build), configure
gcloud, create service account, store initial secrets in Secret Manager.
Week 1 (RAG prototype) — Install LangChain, Chroma, OpenAI SDK. Create small corpus (5–20 docs). Implement
text-splitting, embeddings ingestion, and get_top_k(query) function. Write unit tests for retrieval correctness. Save
embeddings to local Chroma DB.
Week 2 (Agent orchestration) — Integrate LangGraph. Implement simple agent loop: receive query, call retriever,
compose context, call LLM to create plan. Log planning steps. Add simple rule-based tool-detection heuristic to plan for
plotting or analysis.
Week 3 (MCP tool design & deploy 1) — Design MCP JSON schema; implement plot-service (FastAPI) with plotting
logic using matplotlib; containerize with Docker; deploy to Cloud Run; set up public/authorized endpoint and test with
curl.
Week 4 (Agent → MCP integration) — Implement HTTP client in agent to build MCP payloads and parse responses.
Add robust error handling and retries. Update agent planning step to call plot-service when plan requires visualization.
Add Streamlit UI endpoints for invoking agent.
Week 5 (More tools & CI/CD) — Implement pdf-parser (use pdfplumber or PyMuPDF) and calculator (safe eval or
numexpr) as MCP tools. Create GitHub Actions workflow to build and deploy tool images to Artifact Registry & Cloud
Run on push. Add integration tests using pytest.
Week 6 (Polish & deliverables) — Create README, architecture diagrams, demo.mp4, and results document. Run
benchmarks (latency, retrieval precision@k). Final cleanup and prepare résumé bullet points.
5. MCP JSON Schema (standardized request/response)
Example MCP Request (Plot Service):
{
  "mcp_version": "1.0",
  "tool": "plot-service",
  "input": {
    "instructions": "Plot a histogram of the numeric column 'value' grouped by 'category'",
    "data_reference": {
       "type": "inline",
       "payload": {
         "columns": ["category", "value"],
         "rows": [["A", 10], ["B", 3], ["A", 2]]
       }
    },
    "options": {"bins": 10, "title": "Value by Category"}
  },
  "metadata": {"request_id": "abc123", "agent_id":"research_agent_v1"}
}
Example MCP Response:
{
  "status": "success",
  "result": {
    "artifact_type": "image/png",
    "artifact_url": "https://.../plot.png",

    "summary": "Histogram with 10 bins",
    "artifact_base64": "<base64...>"  // optional for inline transport
  },
  "logs": ["parsed input","generated histogram"],
  "metadata": {"tool_time_ms": 154}
}
6. Code Snippets (key components)
6.1 Retriever (LangChain + Chroma)
# retriever.py
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import os
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
emb = OpenAIEmbeddings(openai_api_key=OPENAI_KEY)
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
def build_index(texts, persist_directory="db/chroma"):
    docs = []
    for text in texts:
        splits = splitter.split_text(text)
        docs.extend([Document(page_content=s) for s in splits])
    vectordb = Chroma.from_documents(docs, embedding=emb, collection_name="my_index", persist_directory=persist_directory)
    vectordb.persist()
    return vectordb
def get_top_k(query, k=5, persist_directory="db/chroma"):
    vectordb = Chroma(collection_name="my_index", persist_directory=persist_directory, embedding_function=emb)
    docs = vectordb.similarity_search(query, k=k)
    return docs
6.2 Agent Orchestrator (LangGraph pseudo)
# agent.py (pseudo)
from langgraph import Agent
from retriever import get_top_k
import requests, os, json
PLOT_SERVICE_URL = os.getenv("PLOT_SERVICE_URL")
class MyAgent(Agent):
    def __init__(self, llm):
        super().__init__()
        self.llm = llm
    def plan_and_execute(self, user_query):
        docs = get_top_k(user_query, k=5)
        context = "\n\n".join([d.page_content for d in docs])
        prompt = f"User: {user_query}\nContext: {context}\nProduce a plan. If a visualization is needed, say 'CALL_PLOT'."
        plan = self.llm.generate(prompt)
        if "CALL_PLOT" in plan:
            payload = {
                "mcp_version": "1.0",
                "tool": "plot-service",
                "input": {"instructions":"Plot the requested chart","data_reference":{"type":"inline","payload":...}},
                "metadata": {"request_id":"req-123","agent_id":"agent-v1"}
            }
            r = requests.post(PLOT_SERVICE_URL, json=payload, timeout=30)
            return {"plan": plan, "tool_result": r.json()}
        return {"plan": plan, "tool_result": None}

6.3 MCP Tool Example — Plot Service (FastAPI)
# main.py (plot-service)
from fastapi import FastAPI
from pydantic import BaseModel
import matplotlib.pyplot as plt
import io, base64
app = FastAPI()
class MCPInput(BaseModel):
    mcp_version: str
    tool: str
    input: dict
    metadata: dict = {}
@app.post("/mcp/plot")
def plot_endpoint(req: MCPInput):
    rows = req.input.get('data_reference', {}).get('payload', {}).get('rows', [])
    categories = [r[0] for r in rows]
    values = [r[1] for r in rows]
    plt.figure(figsize=(6,4))
    plt.bar(categories, values)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight'); buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode('utf-8')
    return {"status":"success", "result": {"artifact_type":"image/png", "artifact_base64": b64}, "logs": ["plotted"]}
7. Deployment & Cloud Run Commands
Dockerfile (example):
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
Build & deploy (gcloud):
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud builds submit --tag gcr.io/$PROJECT_ID/plot-service:latest
gcloud run deploy plot-service --image gcr.io/$PROJECT_ID/plot-service:latest --platform managed --region us-central1 --allow-unauthenticated
Notes: Use Secret Manager to store API keys. Use Workload Identity for secure Cloud Run access to secrets.
8. CI/CD (GitHub Actions) - Outline
- On push to main: - Build Docker images for each tool. - Push images to Artifact Registry (or GCR). - Deploy to Cloud
Run using gcloud CLI with a service account. - Run integration tests against deployed endpoints.
9. Testing Plan & Metrics
Unit Tests:
- Retriever: verify top-k contains known relevant documents for canned queries.
- Tools: ensure endpoints return valid MCP response structure for sample inputs.
Integration Tests:
- Agent end-to-end: query -> retrieval -> plan -> tool call -> final output validation.
Performance Metrics:
- Retrieval precision@k (manually labeled or synthetic dataset).
- Latency: retrieval time, LLM response time, tool invocation time, end-to-end time.
- Tool success rate (percentage of successful MCP responses).

- Cost per demo (estimate OpenAI tokens + Cloud Run execution time).
Logging and Observability:
- Log MCP request_id, timing, and status to Cloud Run logs.
- Tag logs with agent_id and request_id for traceability.
10. Security, Secrets & Best Practices
- Keep API keys in Secret Manager. Do not hardcode secrets in source. - Use IAM roles and Workload Identity to grant
Cloud Run access to secrets. - Validate inputs on MCP tools to prevent code injection (avoid eval on untrusted input). -
Limit Cloud Run concurrency and CPU/memory to control cost and DoS risk. - Use HTTPS and require authentication
for non-demo deployments. - Sanitize and truncate LLM outputs when necessary before using them to call tools.
11. Cost Estimate (rough)
- Development (local): free aside from OpenAI API usage. - Cloud Run: billed per CPU-second and memory-second;
low for occasional demo invocations (estimate <$10 month at demo scale). - OpenAI API: main cost driver; use smaller
models during dev and limit tokens. - Misc: Cloud Build / Artifact Registry costs minimal for occasional builds.
Recommendation: run agent locally during development; deploy only tools to Cloud Run until demo stage.
12. Deliverables & Repository Structure
1
agent/ - orchestrator, agent code, retriever
2
tools/plot-service/, tools/pdf-parser/, tools/calculator/ - each with Dockerfile and FastAPI app
3
frontend/ - Streamlit demo
4
infra/ - deployment scripts, gcloud commands, optional Terraform
5
ci/ - GitHub Actions workflows
6
docs/ - MCP schema, diagrams, README, demo script
7
demo.mp4 - 2–3 minute demo recording
8
results.pdf - short report with metrics and reflections
13. Demo Script (narration + steps)
1. Start Streamlit UI. Enter the query: "Show distribution of sample measurement values and summarize outliers using retrieved studies."
2. Show retrieval hits (titles + snippets) returned by retriever.get_top_k.
3. Display the agent's plan (LLM output): e.g., "I will extract numeric tables from doc X, compute stats, plot histogram, and summarize."
4. Agent calls MCP pdf-parser -> extracts table -> stores rows in memory / vector store (optional).
5. Agent calls MCP plot-service with inline payload -> receives base64 PNG and summary.
6. Streamlit displays plot (decoded), summary text, and agent reasoning trace with MCP request_id and timings.
7. Conclude with a short slide showing metrics (latency, retrieval precision) and architecture diagram.
14. README Structure and Résumé Lines
README should include: - Project title and one-line summary. - Architecture diagram and component descriptions. -
Quickstart: local run commands, environment variables, how to build vector DB. - Deployment: gcloud commands and
CI notes. - Demo: link to demo.mp4 and example queries. - Tests: how to run unit and integration tests. Suggested
Résumé lines: - Built a retrieval-augmented autonomous agent framework that selects and invokes MCP-compatible
cloud tools to execute data workflows; implemented with LangChain, LangGraph, FastAPI, and Google Cloud Run. -
Deployed containerized MCP tool endpoints with CI/CD to Google Cloud Run and measured system metrics including
retrieval precision and end-to-end latency.

15. Risks, Mitigations & Extensions
Risks and mitigations:
- LLM hallucinations: mitigate using retrieval grounding, require source citations, and post-verify results from tools.
- Cost: use smaller models in dev; throttle requests; cache retrievals and results.
- Complexity: build MVP with one tool first; keep MCP schema minimal.
- Data privacy: avoid sending PII to third-party APIs; redact sensitive fields.
Extensions (future work):
- Add persistent memory across sessions via Firestore and MCP memory packets.
- Multi-agent collaboration via MCP: each agent exposes its knowledge packets and queries others.
- Replace OpenAI with Vertex AI or self-hosted models to control cost and latency.
16. Immediate Next Steps (today)
1
Create GitHub repo and project skeleton
2
Install Python environment and required packages (langchain, chromadb, openai, fastapi, uvicorn, streamlit,
requests)
3
Prepare a small corpus (5–20 docs) for prototyping retrieval
4
Implement retriever.py and verify top-k results locally
5
Scaffold plot-service FastAPI and run locally with uvicorn
6
Acquire OpenAI API key and store in local .env or Secret Manager for cloud
17. Contact & Attribution
Prepared for: Edwin Wilson Prepared by: Project Plan Assistant (ChatGPT) This document is intended to be a
developer-facing blueprint. If you want, I can also scaffold the starter repository (file tree, requirements.txt, Dockerfile,
initial scripts) and generate Cloud Run deploy workflows. Tell me which scaffold you want next and I'll create files you
can download.