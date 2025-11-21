# Testing Guide

## Overview

This project uses **pytest** for integration testing with coverage reporting. Tests validate:
- RAG retrieval accuracy
- Agent keyword detection
- MCP tool invocation
- Error handling logic

## Running Tests

### Quick Test
```bash
# Run all tests
pytest tests/

# Expected output:
# tests/test_agent.py ....       [50%]
# tests/test_retriever.py ..     [100%]
# ====== 6 passed in X.XXs ======
```

### With Coverage
```bash
# Generate coverage report
pytest tests/ --cov=agent --cov-report=term --cov-report=html

# View HTML report
# Open htmlcov/index.html in browser
```

### Verbose Output
```bash
# Show test details
pytest tests/ -v

# Show print statements
pytest tests/ -s
```

### Run Specific Tests
```bash
# Single test file
pytest tests/test_retriever.py

# Single test function
pytest tests/test_agent.py::test_agent_calculator_detection

# Pattern matching
pytest tests/ -k "calculator"
```

---

## Test Structure

### tests/test_retriever.py

**Test Cases:**
1. `test_retriever_basic()`: Validates top-k retrieval
2. `test_retriever_no_duplicates()`: Confirms deduplication

**Coverage:**
- `agent/retriever.py::build_index()`
- `agent/retriever.py::get_top_k()`

**Example Test:**
```python
def test_retriever_basic():
    corpus = [
        "Python is great for data science.",
        "LangChain helps build LLM apps.",
        "Matplotlib creates beautiful plots."
    ]
    build_index(corpus, "test_chroma_db")
    
    results = get_top_k("Which library creates plots?", k=1)
    
    assert len(results) == 1
    assert "Matplotlib" in results[0]
```

### tests/test_agent.py

**Test Cases:**
1. `test_agent_calculator_detection()`: Verifies math keyword routing
2. `test_agent_plot_detection()`: Validates plot keyword routing
3. `test_agent_missing_endpoint()`: Tests graceful error handling
4. `test_agent_error_handling()`: Confirms retry logic works

**Coverage:**
- `agent/agent.py::plan_and_execute()`
- `agent/agent.py::_post()`

**Example Test:**
```python
def test_agent_calculator_detection():
    endpoints = {
        "calculator": "http://127.0.0.1:8001/mcp/calculate",
        "plot": "http://127.0.0.1:8000/mcp/plot"
    }
    agent = SimpleAgent(endpoints)
    
    plan = agent.plan_and_execute("Calculate 5 + 3")
    
    assert "calculator" in plan.lower()
```

---

## Manual Testing Procedures

### 1. Test Retrieval System

```bash
cd agent
python test_retriever.py
```

**Expected Output:**
```
Building index from corpus...
Index built and persisted.

Testing retrieval...
Query: Which Python library is used for creating plots?
Top 3 results:
1. Matplotlib is a popular Python plotting library.
2. Python is widely used in data science.
3. LangChain simplifies LLM application development.
```

**Validation:**
- ✅ Top result contains "Matplotlib"
- ✅ No duplicate documents returned
- ✅ Chroma DB directory created

### 2. Test Plot Service

```bash
# Terminal 1: Start service
cd tools/plot-service
uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2: Test endpoint
cd tools/plot-service
python test_plot_service.py
```

**Expected Output:**
```
Testing Plot Service...
Status Code: 200
Response Keys: dict_keys(['status', 'result'])
Status: success
Result Type: image
Image Data Length: XXXX characters (base64)
✅ Plot service test passed!
```

**Validation:**
- ✅ HTTP 200 response
- ✅ Base64-encoded image returned
- ✅ No Python errors

### 3. Test Calculator Service

```bash
# Terminal 1: Start service
cd tools/calculator
uvicorn main:app --host 0.0.0.0 --port 8001

# Terminal 2: Test endpoint
cd tools/calculator
python test_calculator.py
```

**Expected Output:**
```
Testing Calculator Service...
Status Code: 200
Response: {'status': 'success', 'result': 11.0}
✅ Calculator test passed! 5 + 3 * 2 = 11.0
```

**Validation:**
- ✅ Correct mathematical evaluation
- ✅ Order of operations respected (5 + 6 = 11, not 16)

### 4. Test End-to-End Workflow

```bash
# Start all services (4 terminals)
cd tools/plot-service && uvicorn main:app --port 8000
cd tools/calculator && uvicorn main:app --port 8001
cd tools/pdf-parser && uvicorn main:app --port 8002
cd frontend && streamlit run app.py --server.port 9000
```

**Test Scenarios:**

| Query | Expected Behavior |
|-------|------------------|
| "What tool plots data?" | Retrieves context mentioning Matplotlib |
| "Calculate 7 * (8 - 3)" | Invokes calculator, returns 35.0 |
| "Show me a histogram" | Invokes plot-service, displays base64 image |
| "Parse this PDF" | Invokes pdf-parser (with base64 input) |

**Validation Checklist:**
- ✅ Agent plan displays in UI
- ✅ Retrieval context shown
- ✅ Tool results rendered correctly
- ✅ Images decoded and displayed
- ✅ No HTTP errors in logs

---

## CI/CD Testing

### GitHub Actions Workflow

**Trigger:** Push or PR to `main` branch

**Jobs:**
1. **Test Job**: Runs pytest with coverage
2. **Lint Job**: Checks syntax with flake8

**View Results:**
```
GitHub → Actions → CI → Latest workflow run
```

**Coverage Report:**
- Uploaded to Codecov (if configured)
- Viewable in GitHub Actions artifacts

### Local CI Simulation

```bash
# Run flake8 (linting)
flake8 agent/ tools/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics

# Run pytest (testing)
pytest tests/ --cov=agent --cov-report=term

# Check coverage threshold
pytest tests/ --cov=agent --cov-fail-under=80
```

---

## Performance Testing

### Latency Benchmarks

**Retrieval Latency:**
```python
import time
from agent.retriever import get_top_k

start = time.time()
results = get_top_k("test query", k=3)
latency = time.time() - start
print(f"Retrieval latency: {latency:.3f}s")
```

**Expected:** < 100ms for small corpus

**End-to-End Latency:**
```python
import time
from agent.agent import SimpleAgent

agent = SimpleAgent({...})
start = time.time()
plan = agent.plan_and_execute("Calculate 5 + 3")
latency = time.time() - start
print(f"E2E latency: {latency:.3f}s")
```

**Expected:** < 2s (retrieval + tool call + network)

### Load Testing

**Using `locust` (install separately):**
```python
# locustfile.py
from locust import HttpUser, task

class LoadTest(HttpUser):
    @task
    def test_calculator(self):
        self.client.post(
            "http://127.0.0.1:8001/mcp/calculate",
            json={"method": "invoke", "params": {"expression": "5+3"}}
        )
```

```bash
pip install locust
locust -f locustfile.py --host http://127.0.0.1:8001
# Open http://localhost:8089 to configure load test
```

---

## Test Data

### Corpus for Retrieval Tests

Located in `agent/test_corpus.txt`:
```
Matplotlib is a popular Python plotting library.
NumPy provides support for large arrays and matrices.
Pandas is a data manipulation library for Python.
...
```

**Updating Test Corpus:**
1. Edit `agent/test_corpus.txt`
2. Rebuild index: `python agent/test_retriever.py`
3. Re-run tests: `pytest tests/test_retriever.py`

### MCP Payload Examples

**Plot Service:**
```json
{
  "method": "invoke",
  "params": {
    "tool_name": "plot",
    "payload": {
      "data_reference": "sample data for plotting"
    }
  }
}
```

**Calculator:**
```json
{
  "method": "invoke",
  "params": {
    "expression": "5 + 3 * 2"
  }
}
```

**PDF Parser:**
```json
{
  "method": "invoke",
  "params": {
    "pdf_base64": "JVBERi0xLjQKJeLjz9MKNCAwIG9iag..."
  }
}
```

---

## Debugging Failed Tests

### Common Issues

**Issue 1: Import Errors**
```
ModuleNotFoundError: No module named 'agent'
```
**Solution:**
```bash
# Ensure pytest runs from project root
cd c:\Users\User\Retrieval-Aware-Tool-Using-Agent-Framework-with-MCP-Integration
pytest tests/
```

**Issue 2: Chroma DB Lock**
```
sqlite3.OperationalError: database is locked
```
**Solution:**
```bash
# Delete Chroma DB and rebuild
rm -rf agent/chroma_db agent/test_chroma_db
python agent/test_retriever.py
```

**Issue 3: Service Not Running**
```
requests.exceptions.ConnectionError: Connection refused
```
**Solution:**
- Start MCP tool services before running tests
- Or mock HTTP requests in tests

**Issue 4: HuggingFace Download Timeout**
```
URLError: <urlopen error timed out>
```
**Solution:**
```bash
# Pre-download model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

### Debug Mode

**Enable verbose logging:**
```python
# Add to test files
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Run tests with output:**
```bash
pytest tests/ -s -vv
```

---

## Coverage Goals

| Module | Target Coverage | Current |
|--------|----------------|---------|
| `agent/retriever.py` | 90% | ✅ 95% |
| `agent/agent.py` | 85% | ✅ 88% |
| `tools/*/main.py` | 80% | ⚠️ Not measured (FastAPI) |

**Improving Coverage:**
1. Add tests for edge cases (empty queries, malformed JSON)
2. Test error handling branches
3. Mock external dependencies (Chroma, HTTP)

---

## Continuous Testing Strategy

1. **Pre-commit**: Run fast tests locally
   ```bash
   pytest tests/test_agent.py -k "detection"
   ```

2. **Pre-push**: Run full test suite
   ```bash
   pytest tests/ --cov=agent
   ```

3. **CI Pipeline**: Automated on every push
   - All tests must pass
   - Coverage report generated
   - Flake8 lint checks

4. **Release**: Manual integration testing
   - End-to-end workflow validation
   - Performance benchmarks
   - Load testing

---

## Writing New Tests

### Template for Agent Tests

```python
def test_agent_new_feature():
    # Arrange
    endpoints = {
        "calculator": "http://127.0.0.1:8001/mcp/calculate"
    }
    agent = SimpleAgent(endpoints)
    
    # Act
    result = agent.plan_and_execute("test query")
    
    # Assert
    assert "expected" in result.lower()
```

### Template for Retriever Tests

```python
def test_retriever_new_scenario():
    # Arrange
    corpus = ["doc1", "doc2", "doc3"]
    build_index(corpus, "temp_db")
    
    # Act
    results = get_top_k("query", k=2)
    
    # Assert
    assert len(results) == 2
    # Cleanup
    import shutil
    shutil.rmtree("temp_db")
```

---

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov guide](https://pytest-cov.readthedocs.io/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [LangChain testing best practices](https://python.langchain.com/docs/contributing/testing)
