# Contributing Guide

Thank you for your interest in contributing to the Retrieval-Aware Tool-Using Agent Framework! This guide will help you get started.

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- Git
- Basic knowledge of FastAPI, LangChain, and Streamlit

### Setup Development Environment

1. **Fork and Clone**
   ```bash
   git clone https://github.com/Atatsuki2000/Retrieval-Aware-Tool-Using-Agent-Framework-with-MCP-Integration.git
   cd Retrieval-Aware-Tool-Using-Agent-Framework-with-MCP-Integration
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

4. **Run Tests**
   ```bash
   pytest tests/
   ```

## 📋 Development Workflow

### Branching Strategy
- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/your-feature-name`: New features
- `bugfix/issue-number`: Bug fixes

### Creating a New Feature

1. **Create a branch**
   ```bash
   git checkout -b feature/my-new-tool
   ```

2. **Make changes**
   - Write code
   - Add tests
   - Update documentation

3. **Run tests locally**
   ```bash
   pytest tests/ --cov=agent
   flake8 agent/ tools/ tests/
   ```

4. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add new weather tool"
   ```

5. **Push to GitHub**
   ```bash
   git push origin feature/my-new-tool
   ```

6. **Create Pull Request**
   - Go to GitHub
   - Click "New Pull Request"
   - Fill in description
   - Wait for CI checks to pass

## 🔨 Adding New MCP Tools

### Step 1: Create Tool Endpoint

Create a new directory under `tools/`:
```
tools/
  your-tool/
    main.py
    requirements.txt
    test_your_tool.py
```

### Step 2: Implement FastAPI Endpoint

```python
# tools/your-tool/main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class MCPInput(BaseModel):
    method: str
    params: dict

@app.post("/mcp/your-tool")
async def your_tool(input: MCPInput):
    # Your tool logic here
    result = process_input(input.params)
    return {"status": "success", "result": result}
```

### Step 3: Update Agent

```python
# agent/agent.py
def plan_and_execute(self, user_query):
    # Add keyword detection
    if any(kw in query_lower for kw in ["your", "keywords"]):
        tool_endpoint = self.endpoints.get("your_tool")
        # Invoke tool
```

### Step 4: Update Streamlit UI

```python
# frontend/app.py
your_tool_url = st.sidebar.text_input(
    "Your Tool URL",
    os.getenv("YOUR_TOOL_URL", "http://127.0.0.1:8003/mcp/your-tool")
)

endpoints = {
    # ... existing endpoints
    "your_tool": your_tool_url
}
```

### Step 5: Write Tests

```python
# tests/test_your_tool.py
def test_your_tool():
    # Test your tool functionality
    pass
```

## 🧪 Testing Guidelines

### Writing Tests
- Use pytest
- Aim for >80% coverage
- Test edge cases and error handling
- Use descriptive test names

### Test Structure
```python
def test_feature_name():
    # Arrange: Set up test data
    input_data = {...}
    
    # Act: Execute the code
    result = function_under_test(input_data)
    
    # Assert: Verify the output
    assert result == expected_output
```

### Running Tests
```bash
# All tests
pytest tests/

# Specific file
pytest tests/test_agent.py

# With coverage
pytest tests/ --cov=agent --cov-report=html

# Verbose
pytest tests/ -v
```

## 📝 Code Style

### Python Style Guide
- Follow PEP 8
- Use type hints where possible
- Document functions with docstrings
- Maximum line length: 100 characters

### Example
```python
def get_top_k(query: str, k: int = 3) -> list[str]:
    """
    Retrieve top-k documents for a query.
    
    Args:
        query: The search query string
        k: Number of results to return
        
    Returns:
        List of document strings
        
    Raises:
        ValueError: If k < 1
    """
    if k < 1:
        raise ValueError("k must be >= 1")
    # Implementation
```

### Linting
```bash
# Check syntax errors
flake8 agent/ tools/ tests/ --count --select=E9,F63,F7,F82

# Check style
flake8 agent/ tools/ tests/ --max-line-length=100
```

## 📚 Documentation Guidelines

### Update These Files When:
- **README.md**: Adding major features
- **docs/architecture.md**: Changing system design
- **docs/usage.md**: Adding new usage examples
- **docs/deployment.md**: Modifying deployment process

### Docstring Format
```python
def function(param1: str, param2: int) -> bool:
    """
    One-line summary.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When this exception occurs
        
    Example:
        >>> function("test", 5)
        True
    """
```

## 🐛 Reporting Bugs

### Before Reporting
1. Check existing issues
2. Test on latest version
3. Reproduce the bug locally

### Bug Report Template
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Start service '...'
2. Send request '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
 - OS: [e.g. Windows 11]
 - Python version: [e.g. 3.10.5]
 - Package versions: [run `pip list`]

**Additional context**
Any other context about the problem.
```

## 💡 Feature Requests

### Feature Request Template
```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features.

**Additional context**
Any other context or screenshots.
```

## 🔍 Code Review Process

### What We Look For
- ✅ Code follows style guide
- ✅ Tests pass and coverage is maintained
- ✅ Documentation is updated
- ✅ No breaking changes (or clearly documented)
- ✅ Commit messages are clear

### Review Checklist
- [ ] Code compiles and runs
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] CI checks pass

## 🎯 Pull Request Guidelines

### PR Title Format
- `feat: add new calculator function`
- `fix: resolve retriever duplicate issue`
- `docs: update deployment guide`
- `test: add agent error handling tests`
- `refactor: simplify endpoint configuration`

### PR Description Template
```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How has this been tested?

## Checklist
- [ ] My code follows the style guide
- [ ] I have added tests
- [ ] I have updated documentation
- [ ] All tests pass locally
- [ ] I have added an entry to CHANGELOG.md (if applicable)
```

## 🏆 Recognition

Contributors will be:
- Listed in the README.md
- Mentioned in release notes
- Given credit in commit history

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas
- **Email**: For security issues (security@example.com)

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
