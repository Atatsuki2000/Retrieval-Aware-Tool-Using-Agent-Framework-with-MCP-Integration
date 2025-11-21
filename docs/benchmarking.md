# Performance Benchmarking Guide

## 📊 Overview

The `benchmark.py` script provides comprehensive performance evaluation for the RAG+MCP Agent Framework, measuring:

- **Retrieval Precision@k**: Accuracy of relevant document retrieval
- **Latency Breakdown**: Time spent in retrieval, LLM processing, and tool invocation
- **Tool Selection Accuracy**: Correctness of agent's tool choice
- **Tool Success Rate**: Percentage of successful MCP calls
- **Mode Comparison**: Performance across keyword, local LLM, and OpenAI modes

---

## 🚀 Quick Start

### Prerequisites

1. **Start MCP Services** (required for tool benchmarks):
   ```powershell
   .\start_services.ps1
   ```

2. **Ensure Dependencies Installed**:
   ```bash
   pip install -r requirements.txt
   ```

### Run All Benchmarks

```bash
python benchmark.py --mode all --save
```

This will:
- Test retrieval precision and latency
- Compare all agent modes (keyword, local LLM, OpenAI*)
- Save results to `benchmark_results.json`

*OpenAI mode requires API key (optional)

---

## 📋 Usage Examples

### Test Only Retrieval
```bash
python benchmark.py --mode retrieval
```

Measures:
- Precision@5 for document retrieval
- Average retrieval latency
- Standard deviation of latency

### Test Specific Agent Mode
```bash
# Keyword-based mode
python benchmark.py --mode agent --agent-mode keyword

# Local LLM mode (TinyLlama)
python benchmark.py --mode agent --agent-mode local

# OpenAI mode (requires API key)
python benchmark.py --mode agent --agent-mode openai --openai-api-key sk-...
```

### Compare All Modes
```bash
python benchmark.py --mode comparison --save
```

Generates side-by-side comparison:
- Tool selection accuracy (%)
- Tool success rate (%)
- End-to-end latency (ms)

---

## 📊 Metrics Explained

### Retrieval Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Precision@k** | Ratio of relevant docs in top-k results | >0.60 |
| **Avg Latency** | Time to retrieve k documents | <100ms |
| **Std Latency** | Consistency of retrieval time | <50ms |

### Agent Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Tool Selection Accuracy** | % of correct tool choices | >85% |
| **Tool Success Rate** | % of successful MCP calls | >90% |
| **End-to-End Latency** | Total query processing time | <2000ms |

### Mode-Specific Expected Performance

| Mode | Accuracy | Latency | Cost |
|------|----------|---------|------|
| **Keyword** | 85-90% | ~50ms | $0 |
| **Local LLM** | 90-95% | ~500ms | $0 |
| **OpenAI** | 95-98% | ~800ms | ~$0.0004/query |

---

## 🧪 Test Queries

The benchmark uses 10 predefined test queries covering:

### Calculation Queries (5)
- "Calculate 25 * 17 + 89" → calculator
- "What is 100 divided by 4?" → calculator
- "Compute 2^10" → calculator
- "What is the square root of 144?" → calculator
- "Calculate (5 + 3) * (10 - 2)" → calculator

### Visualization Queries (5)
- "Show me a bar chart of sales data" → plot
- "Generate a scatter plot" → plot
- "Create a histogram visualization" → plot
- "Draw a line graph" → plot
- "Plot random data" → plot

### Retrieval Queries (3)
- "machine learning algorithms"
- "data visualization techniques"
- "python programming"

---

## 📈 Sample Output

```
🔍 Checking MCP Services...
  ✅ plot: http://127.0.0.1:8000/mcp/plot
  ✅ calculator: http://127.0.0.1:8001/mcp/calculate
  ✅ pdf: http://127.0.0.1:8002/mcp/parse

📊 Benchmarking Retrieval (k=5)...
  ✓ 'machine learning algorithms...' - Precision: 0.80, Latency: 45.2ms
  ✓ 'data visualization techniques...' - Precision: 1.00, Latency: 38.7ms
  ✓ 'python programming...' - Precision: 0.60, Latency: 42.1ms

🤖 Benchmarking Agent (Local LLM)...

  Testing: 'Calculate 25 * 17 + 89'
    Expected tool: calculator
    ✓ Tool selection: calculator (correct)
    ✓ Tool execution: success (156.3ms)
    ⏱️  End-to-end: 612.5ms

============================================================
📊 BENCHMARK SUMMARY
============================================================

🔍 Retrieval Performance:
  • Average Precision@k: 80.00%
  • Average Latency: 42.0ms (±3.2ms)
  • Queries Tested: 3

🤖 Agent Mode Comparison:

  Tool Selection Accuracy:
    • Keyword-based: 85.0%
    • Local LLM: 92.0%
    • OpenAI GPT-3.5: 96.0%

  Tool Success Rate:
    • Keyword-based: 90.0%
    • Local LLM: 95.0%
    • OpenAI GPT-3.5: 98.0%

  Average End-to-End Latency:
    • Keyword-based: 234.5ms (±45.2ms)
    • Local LLM: 567.8ms (±89.3ms)
    • OpenAI GPT-3.5: 823.1ms (±102.4ms)

============================================================

💾 Results saved to: benchmark_results.json

✅ Benchmark complete!
```

---

## 📁 Output Files

### benchmark_results.json

JSON structure:
```json
{
  "retrieval": {
    "queries_tested": 3,
    "avg_precision": 0.8,
    "avg_latency_ms": 42.0,
    "std_latency_ms": 3.2,
    "precision_at_k": [0.8, 1.0, 0.6],
    "latencies_ms": [45.2, 38.7, 42.1]
  },
  "comparison": {
    "keyword": {
      "mode": "keyword",
      "tool_selection_accuracy": 85.0,
      "tool_success_rate": 90.0,
      "avg_end_to_end_ms": 234.5,
      "errors": []
    },
    "local_llm": {
      "mode": "local",
      "tool_selection_accuracy": 92.0,
      "tool_success_rate": 95.0,
      "avg_end_to_end_ms": 567.8,
      "errors": []
    }
  }
}
```

---

## 🔧 Customization

### Add Custom Test Queries

Edit `TEST_QUERIES` in `benchmark.py`:

```python
TEST_QUERIES = [
    {
        "query": "Your custom query here",
        "expected_tool": "calculator",  # or "plot", "pdf"
        "ground_truth": 42,  # Expected result (optional)
        "category": "custom"
    },
    # ... more queries
]
```

### Adjust Retrieval Test

Modify `RETRIEVAL_QUERIES` to match your document corpus:

```python
RETRIEVAL_QUERIES = [
    {
        "query": "domain-specific query",
        "relevant_docs": ["term1", "term2", "term3"]  # Keywords in relevant docs
    }
]
```

### Change Precision@k Value

```bash
# Test with k=10 instead of default k=5
python benchmark.py --mode retrieval
# (Edit k parameter in benchmark_retrieval() method)
```

---

## 🐛 Troubleshooting

### Services Not Running
```
⚠️  Warning: No MCP services are running!
   Start services with: .\start_services.ps1
```
**Solution**: Run `.\start_services.ps1` in a separate terminal

### Local LLM Not Loading
```
⚠️ transformers not installed. Install with: pip install transformers torch
Falling back to keyword mode
```
**Solution**: `pip install transformers torch accelerate`

### OpenAI API Error
```
Error: OpenAI API key not valid
```
**Solution**: Check your API key with `--openai-api-key sk-...`

### Low Retrieval Precision
```
Average Precision@k: 30.00%
```
**Solution**: 
1. Check if vector DB is properly initialized
2. Verify test queries match your corpus
3. Adjust `RETRIEVAL_QUERIES` relevant terms

---

## 📊 Interpreting Results

### Good Performance Indicators
- ✅ Retrieval precision >60%
- ✅ Tool selection accuracy >85%
- ✅ Tool success rate >90%
- ✅ End-to-end latency <2000ms

### Performance Issues
- ⚠️ Retrieval precision <50% → Check vector DB quality
- ⚠️ Tool selection accuracy <80% → Review keyword/LLM logic
- ⚠️ High latency (>3000ms) → Check service response times
- ⚠️ Low success rate (<80%) → Debug MCP service errors

### Cost Analysis
```
Local LLM Mode (Recommended):
- Accuracy: 90-95%
- Cost per query: $0
- Total cost for 1000 queries: $0

OpenAI Mode:
- Accuracy: 95-98%
- Cost per query: ~$0.0004
- Total cost for 1000 queries: ~$0.40
```

---

## 🎯 Next Steps

After running benchmarks:

1. **Analyze Results**: Review `benchmark_results.json`
2. **Identify Bottlenecks**: Check latency breakdown
3. **Optimize**: 
   - Tune retrieval parameters
   - Adjust LLM prompts
   - Cache frequent queries
4. **Generate Report**: Use results for documentation/presentation
5. **Track Over Time**: Re-run after changes to measure improvements

---

## 📚 Related Documentation

- [Local LLM Setup Guide](docs/local-llm-setup.md)
- [Testing Guide](docs/testing.md)
- [Architecture Documentation](docs/architecture.md)

---

## 💡 Tips

1. **Run Multiple Times**: Average results over 3-5 runs for consistency
2. **Cold Start**: First run may be slower (model loading)
3. **Service Warmup**: Run a test query before benchmarking
4. **Compare Baseline**: Save initial results before optimizations
5. **Monitor Resources**: Check CPU/memory during LLM benchmarks

---

*Generated for RAG+MCP Agent Framework Project*
