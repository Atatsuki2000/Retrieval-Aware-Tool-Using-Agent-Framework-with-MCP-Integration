from fastapi import FastAPI
from pydantic import BaseModel
import ast
import operator
import traceback

app = FastAPI()

class MCPInput(BaseModel):
    mcp_version: str
    tool: str
    input: dict
    metadata: dict = {}

# Safe math operations
SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}

def safe_eval(expr_str):
    """Safely evaluate a mathematical expression using AST"""
    def eval_node(node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            op = SAFE_OPS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operation: {type(node.op).__name__}")
            return op(eval_node(node.left), eval_node(node.right))
        elif isinstance(node, ast.UnaryOp):
            op = SAFE_OPS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operation: {type(node.op).__name__}")
            return op(eval_node(node.operand))
        else:
            raise ValueError(f"Unsupported expression: {type(node).__name__}")

    tree = ast.parse(expr_str, mode='eval')
    return eval_node(tree.body)

@app.post("/mcp/calculate")
def calculate_endpoint(req: MCPInput):
    """
    Safely evaluate mathematical expressions.
    Example input: {"expression": "2 + 2 * 3"}
    """
    try:
        expression = req.input.get('expression', '')
        if not expression:
            return {
                "status": "error",
                "result": {"error": "No expression provided"},
                "logs": ["error: missing expression"]
            }

        # Use safe AST-based evaluation
        result = safe_eval(expression)

        return {
            "status": "success",
            "result": {
                "expression": expression,
                "value": float(result),
                "type": "numeric"
            },
            "logs": [f"evaluated: {expression} = {result}"]
        }
    except Exception as e:
        return {
            "status": "error",
            "result": {
                "error": str(e),
                "traceback": traceback.format_exc()
            },
            "logs": [f"error: {str(e)}"]
        }

@app.get("/health")
def health_check():
    return {"status": "healthy", "tool": "calculator"}
