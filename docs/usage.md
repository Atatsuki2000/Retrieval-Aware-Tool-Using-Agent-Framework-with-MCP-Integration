# Usage Examples

## Quick Start Examples

### Example 1: Simple Retrieval Query

**Query:** "What library is used for plotting in Python?"

**Expected Flow:**
1. Agent retrieves context from Chroma DB
2. Finds documents mentioning Matplotlib
3. Returns context without tool invocation

**Streamlit Output:**
```
📊 Agent Plan:
Retrieved context mentions Matplotlib as the plotting library.
No tool invocation needed.

📚 Retrieved Context:
- Matplotlib is a popular Python plotting library.
- Python has many data visualization tools.
- NumPy and Pandas work well with Matplotlib.

🔧 Tool Results:
None (information retrieval only)
```

---

### Example 2: Calculator Tool

**Query:** "Calculate 15 * (8 + 2) - 5"

**Expected Flow:**
1. Agent detects keywords: "calculate"
2. Retrieves context (optional)
3. Invokes calculator MCP endpoint
4. Returns numeric result

**Streamlit Output:**
```
📊 Agent Plan:
Detected calculator keywords. Invoking calculator tool.

📚 Retrieved Context:
- Python has a built-in calculator.
- NumExpr evaluates expressions safely.

🔧 Tool Results:
Calculator:
Expression: 15 * (8 + 2) - 5
Result: 145.0
```

**Terminal (Calculator Service):**
```
INFO: 127.0.0.1:xxxxx - "POST /mcp/calculate HTTP/1.1" 200 OK
```

---

### Example 3: Plot Generation

**Query:** "Show me a bar chart"

**Expected Flow:**
1. Agent detects keywords: "chart"
2. Retrieves plotting context
3. Invokes plot-service MCP endpoint
4. Decodes base64 image and displays

**Streamlit Output:**
```
📊 Agent Plan:
Detected plot keywords. Invoking plot tool.

📚 Retrieved Context:
- Matplotlib creates bar charts, histograms, and more.
- Seaborn provides high-level plotting interface.

🔧 Tool Results:
Plot Service:
[Displays bar chart image]
```

---

### Example 4: Multiple Keywords

**Query:** "Calculate the average and plot a histogram"

**Expected Flow:**
1. Agent detects both "calculate" and "plot" keywords
2. Invokes calculator first
3. Invokes plot-service second
4. Returns both results

**Streamlit Output:**
```
📊 Agent Plan:
Detected calculator and plot keywords. Invoking both tools.

📚 Retrieved Context:
- Statistics require calculation and visualization.
- Matplotlib and NumPy work together.

🔧 Tool Results:
Calculator:
Result: 7.5

Plot Service:
[Displays histogram image]
```

---

## API Usage Examples

### Direct MCP Endpoint Calls

#### Calculator Service
```bash
curl -X POST http://127.0.0.1:8001/mcp/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "method": "invoke",
    "params": {
      "expression": "5 + 3 * 2"
    }
  }'
```

**Response:**
```json
{
  "status": "success",
  "result": 11.0
}
```

#### Plot Service
```bash
curl -X POST http://127.0.0.1:8000/mcp/plot \
  -H "Content-Type: application/json" \
  -d '{
    "method": "invoke",
    "params": {
      "tool_name": "plot",
      "payload": {
        "data_reference": "sample data"
      }
    }
  }'
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "type": "image",
    "data": "iVBORw0KGgoAAAANSUhEUgAA..."
  }
}
```

#### PDF Parser
```bash
curl -X POST http://127.0.0.1:8002/mcp/parse \
  -H "Content-Type: application/json" \
  -d '{
    "method": "invoke",
    "params": {
      "pdf_base64": "JVBERi0xLjQKJeLjz9MK..."
    }
  }'
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "pages": [
      {"page": 1, "text": "Page 1 content..."},
      {"page": 2, "text": "Page 2 content..."}
    ],
    "full_text": "Page 1 content... Page 2 content..."
  }
}
```

---

## Python SDK Usage

### Using the Agent Programmatically

```python
from agent.agent import SimpleAgent

# Configure endpoints
endpoints = {
    "calculator": "http://127.0.0.1:8001/mcp/calculate",
    "plot": "http://127.0.0.1:8000/mcp/plot",
    "pdf_parser": "http://127.0.0.1:8002/mcp/parse"
}

# Initialize agent
agent = SimpleAgent(endpoints)

# Execute query
result = agent.plan_and_execute("Calculate 10 * 5")
print(result)
```

**Output:**
```
Plan:
Detected calculator keywords. Invoking calculator tool.

Retrieved Context:
- Python calculator available
- NumExpr for safe evaluation

Tool Results:
Calculator: 50.0
```

---

### Using the Retriever Directly

```python
from agent.retriever import build_index, get_top_k

# Build index
corpus = [
    "Matplotlib creates plots.",
    "Pandas handles data.",
    "NumPy does numerical computing."
]
build_index(corpus, persist_directory="my_index")

# Query
results = get_top_k("Which library handles data?", k=2)
for doc in results:
    print(doc)
```

**Output:**
```
Pandas handles data.
NumPy does numerical computing.
```

---

## Advanced Examples

### Custom Corpus

**Step 1: Prepare your documents**
```python
# my_corpus.txt
Your custom knowledge base here.
Line 1: Information about topic A.
Line 2: Information about topic B.
...
```

**Step 2: Build custom index**
```python
from agent.retriever import build_index

with open("my_corpus.txt") as f:
    corpus = f.readlines()

build_index(corpus, persist_directory="custom_index")
```

**Step 3: Update retriever to use custom index**
```python
# In agent/retriever.py
def get_top_k(query, k=3, persist_directory="custom_index"):
    # ... (rest of code)
```

---

### Adding Custom MCP Tools

**Step 1: Create tool endpoint**
```python
# tools/weather-service/main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class MCPInput(BaseModel):
    method: str
    params: dict

@app.post("/mcp/weather")
async def weather(input: MCPInput):
    location = input.params.get("location")
    # Fetch weather data (mock example)
    result = f"Weather in {location}: Sunny, 72°F"
    return {"status": "success", "result": result}
```

**Step 2: Update agent keyword detection**
```python
# agent/agent.py
def plan_and_execute(self, user_query):
    # ... (existing code)
    
    # Add weather detection
    if any(kw in query_lower for kw in ["weather", "forecast", "temperature"]):
        weather_endpoint = self.endpoints.get("weather")
        if weather_endpoint:
            weather_result = self._post(
                weather_endpoint,
                {"method": "invoke", "params": {"location": "New York"}}
            )
            plan += f"\nWeather: {weather_result}"
```

**Step 3: Update Streamlit UI**
```python
# frontend/app.py
weather_url = st.sidebar.text_input(
    "Weather Service URL",
    os.getenv("WEATHER_URL", "http://127.0.0.1:8003/mcp/weather")
)

endpoints = {
    # ... existing endpoints
    "weather": weather_url
}
```

---

### Error Handling Examples

#### Handling Missing Endpoints

```python
agent = SimpleAgent({
    "calculator": "http://127.0.0.1:8001/mcp/calculate"
    # plot endpoint not provided
})

result = agent.plan_and_execute("Show me a plot")
# Output: "Plot endpoint not configured."
```

#### Handling Service Downtime

```python
# Service at 8001 is not running
agent = SimpleAgent({
    "calculator": "http://127.0.0.1:8001/mcp/calculate"
})

result = agent.plan_and_execute("Calculate 5 + 3")
# Agent retries 3 times with exponential backoff
# After 3 failures: "Error calling calculator: Connection refused"
```

#### Handling Invalid Expressions

```bash
curl -X POST http://127.0.0.1:8001/mcp/calculate \
  -d '{"method": "invoke", "params": {"expression": "import os; os.system(\"rm -rf /\")"}}'
```

**Response:**
```json
{
  "status": "error",
  "error": "Invalid expression. Only mathematical operations allowed."
}
```

---

## Production Usage Patterns

### Rate Limiting

```python
import time
from functools import wraps

def rate_limit(max_calls, time_window):
    calls = []
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            calls[:] = [c for c in calls if c > now - time_window]
            if len(calls) >= max_calls:
                raise Exception("Rate limit exceeded")
            calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Apply to agent
@rate_limit(max_calls=10, time_window=60)
def plan_and_execute(self, user_query):
    # ... (agent logic)
```

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("agent.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def plan_and_execute(self, user_query):
    logger.info(f"Received query: {user_query}")
    # ... (agent logic)
    logger.info(f"Plan executed: {plan}")
```

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_top_k(query, k=3):
    # Caches retrieval results for repeated queries
    # ... (retriever logic)
```

---

## Testing Examples

### Unit Test for Calculator

```python
import pytest
from tools.calculator.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_calculator_basic():
    response = client.post("/mcp/calculate", json={
        "method": "invoke",
        "params": {"expression": "5 + 3"}
    })
    assert response.status_code == 200
    assert response.json()["result"] == 8.0

def test_calculator_order_of_operations():
    response = client.post("/mcp/calculate", json={
        "method": "invoke",
        "params": {"expression": "5 + 3 * 2"}
    })
    assert response.json()["result"] == 11.0
```

---

## Common Pitfalls

### ❌ Don't: Hardcode endpoints
```python
agent = SimpleAgent({
    "calculator": "http://127.0.0.1:8001/mcp/calculate"
})
```

### ✅ Do: Use environment variables
```python
import os
agent = SimpleAgent({
    "calculator": os.getenv("CALCULATOR_URL", "http://127.0.0.1:8001/mcp/calculate")
})
```

---

### ❌ Don't: Ignore errors
```python
result = requests.post(url, json=payload)
return result.json()  # May fail if service is down
```

### ✅ Do: Handle errors gracefully
```python
try:
    result = requests.post(url, json=payload, timeout=5)
    result.raise_for_status()
    return result.json()
except Exception as e:
    logger.error(f"Error: {e}")
    return {"status": "error", "error": str(e)}
```

---

## Performance Tips

1. **Batch Queries**: Send multiple retrieval queries in parallel
2. **Cache Results**: Use `@lru_cache` for repeated queries
3. **Optimize Corpus**: Keep document chunks small (500-1000 chars)
4. **Pre-warm Services**: Keep MCP tools running (avoid cold starts)
5. **Use Async**: FastAPI supports async handlers for better concurrency

---

## Resources

- [Streamlit documentation](https://docs.streamlit.io/)
- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/)
- [LangChain guides](https://python.langchain.com/docs/get_started/introduction)
- [Chroma documentation](https://docs.trychroma.com/)
