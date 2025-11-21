# System Architecture

## High-Level Overview

```
┌────────────────────────────────────────────────────────────────┐
│                       User Interface Layer                      │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              Streamlit Frontend (Port 9000)             │   │
│  │  - Query Input                                          │   │
│  │  - Endpoint Configuration                               │   │
│  │  - Result Visualization                                 │   │
│  └────────────────────────────────────────────────────────┘   │
└───────────────────────────┬────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                      Agent Orchestration Layer                  │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │                   SimpleAgent                           │   │
│  │  - plan_and_execute(query)                             │   │
│  │  - Rule-based tool selection                           │   │
│  │  - Retry logic with exponential backoff                │   │
│  └────────────────────────────────────────────────────────┘   │
└───────┬────────────────────────────────────┬───────────────────┘
        │                                    │
        ▼                                    ▼
┌───────────────────┐              ┌──────────────────────────┐
│  Retrieval Layer  │              │   MCP Tools Layer        │
│                   │              │                          │
│ ┌───────────────┐ │              │  ┌─────────────────┐   │
│ │   Retriever   │ │              │  │  plot-service   │   │
│ │               │ │              │  │  (Port 8000)    │   │
│ │ - get_top_k() │ │              │  │  - Bar charts   │   │
│ │               │ │              │  │  - Base64 PNG   │   │
│ └───────┬───────┘ │              │  └─────────────────┘   │
│         │         │              │                          │
│         ▼         │              │  ┌─────────────────┐   │
│ ┌───────────────┐ │              │  │  calculator     │   │
│ │  Chroma DB    │ │              │  │  (Port 8001)    │   │
│ │               │ │              │  │  - numexpr eval │   │
│ │ - Vector      │ │              │  │  - Safe math    │   │
│ │   Store       │ │              │  └─────────────────┘   │
│ │               │ │              │                          │
│ │ - HuggingFace │ │              │  ┌─────────────────┐   │
│ │   Embeddings  │ │              │  │  pdf-parser     │   │
│ └───────────────┘ │              │  │  (Port 8002)    │   │
│                   │              │  │  - pypdf extract│   │
└───────────────────┘              │  │  - Base64 input │   │
                                   │  └─────────────────┘   │
                                   └──────────────────────────┘
```

## Data Flow Sequence

### 1. Query Processing Flow

```
User → Streamlit UI → Agent.plan_and_execute()
                            ↓
                    [Step 1: Retrieval]
                    retriever.get_top_k(query, k=3)
                            ↓
                    Chroma DB similarity search
                            ↓
                    Return top 3 documents (deduplicated)
                            ↓
                    [Step 2: Tool Selection]
                    Keyword detection:
                    - "calculate|compute|math" → calculator
                    - "plot|chart|histogram" → plot-service
                            ↓
                    [Step 3: Tool Invocation]
                    HTTP POST to MCP endpoint
                            ↓
                    Retry logic (3 attempts, 1s delay)
                            ↓
                    Parse MCP response
                            ↓
                    Return to UI for visualization
```

### 2. MCP Request/Response Format

#### Request Schema
```json
{
  "method": "invoke",
  "params": {
    "tool_name": "plot",
    "payload": {
      "data_reference": "..."
    }
  }
}
```

#### Response Schema
```json
{
  "status": "success",
  "result": {
    "type": "image",
    "data": "base64_encoded_string"
  }
}
```

## Agent Decision Tree

```
User Query
    ↓
Retriever.get_top_k(query, k=3)
    ↓
Extract context
    ↓
Keyword Detection?
    ├── "calculate/compute/math"
    │   ↓
    │   POST to calculator
    │   ↓
    │   Return numeric result
    │
    ├── "plot/chart/histogram"
    │   ↓
    │   POST to plot-service
    │   ↓
    │   Return base64 image
    │
    └── No keywords
        ↓
        Return retrieval context only
```

## Error Handling Flow

```
Tool Invocation
    ↓
Try HTTP POST
    ├── Success → Return result
    │
    ├── ConnectionError/Timeout
    │   ↓
    │   Retry (attempt 1/3)
    │   ↓
    │   Wait 1s × attempt
    │   ↓
    │   Retry (attempt 2/3)
    │   ↓
    │   Wait 2s
    │   ↓
    │   Retry (attempt 3/3)
    │   ↓
    │   Return error message
    │
    └── HTTPError (4xx/5xx)
        ↓
        Return error immediately
        (no retry)
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Streamlit | Interactive UI |
| Agent | Python | Orchestration logic |
| Retrieval | LangChain + Chroma | RAG system |
| Embeddings | HuggingFace | Free vector embeddings |
| MCP Tools | FastAPI | REST endpoints |
| Visualization | Matplotlib | Plot generation |
| Math Eval | numexpr | Safe calculator |
| PDF Parse | pypdf | Text extraction |
| Testing | pytest | Integration tests |
| CI/CD | GitHub Actions | Automated workflows |

## Deployment Options

### Local Development
- All services run on localhost
- High ports (8000+) to avoid Windows permission issues

### Production (Google Cloud Run)
```
Frontend → Cloud Run Service (Streamlit)
            ↓
Agent → Cloud Run Services (3× MCP Tools)
            ↓
        Container Registry (Docker images)
```

## Security Considerations

1. **No Hardcoded Credentials**: Environment variables only
2. **Input Validation**: All MCP endpoints validate payloads
3. **Safe Evaluation**: numexpr prevents arbitrary code execution
4. **Rate Limiting**: Recommended for production deployments
5. **HTTPS**: Use TLS for all external communications
