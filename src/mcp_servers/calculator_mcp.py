#!/usr/bin/env python3
"""
Calculator MCP Server
Supports basic arithmetic operations, mathematical functions, and constants.
The server exposes a 'calculate' tool that can evaluate mathematical expressions.
"""

import ast
import operator
import math
import logging
from typing import Any
from fastmcp import FastMCP

calculator_mcp = FastMCP("Calculator MCP")


def evaluate(expression: str) -> str:
    """
    Safely evaluate a mathematical expression using AST parsing.

    Args:
        expression: Mathematical expression as a string

    Returns:
        String representation of the result

    Raises:
        ValueError: If the expression contains unsupported operations
        ZeroDivisionError: If division by zero occurs
        OverflowError: If the result is too large
    """
    # Define allowed operators
    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }

    # Define allowed mathematical functions and constants
    allowed_names = {
        k: getattr(math, k)
        for k in dir(math)
        if not k.startswith("__") and callable(getattr(math, k))
    }

    # Add mathematical constants
    allowed_names.update({
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
        "inf": math.inf,
        "nan": math.nan,
    })

    def eval_expr(node: ast.AST) -> Any:
        """Recursively evaluate AST nodes."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            if node.id in allowed_names:
                return allowed_names[node.id]
            raise ValueError(f"Unknown identifier: {node.id}")
        elif isinstance(node, ast.BinOp):
            left = eval_expr(node.left)
            right = eval_expr(node.right)
            if type(node.op) in allowed_operators:
                try:
                    return allowed_operators[type(node.op)](left, right)
                except ZeroDivisionError:
                    raise ZeroDivisionError("Division by zero")
                except OverflowError:
                    raise OverflowError("Result too large")
            else:
                raise ValueError(f"Unsupported binary operator: {type(node.op)}")
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -eval_expr(node.operand)
        elif isinstance(node, ast.Call):
            func = eval_expr(node.func)
            args = [eval_expr(arg) for arg in node.args]
            try:
                return func(*args)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Function call error: {e}")
        else:
            raise ValueError(f"Unsupported operation: {ast.dump(node)}")

    try:
        # Normalize expression symbols
        expression = expression.replace('^', '**').replace('×', '*').replace('÷', '/')
        # Parse the expression
        parsed_expr = ast.parse(expression, mode='eval')
        # print(ast.dump(parsed_expr, indent=4))
        # Evaluate the expression
        result = eval_expr(parsed_expr.body)
        # Handle special cases
        if math.isnan(result):
            return "NaN"
        elif math.isinf(result):
            return "Infinity" if result > 0 else "-Infinity"
        # Format the result
        if isinstance(result, float) and result.is_integer():
            return str(int(result))
        elif isinstance(result, float):
            # Round to avoid floating point precision issues
            return str(round(result, 8))
        else:
            return str(result)

    except SyntaxError as e:
        raise ValueError(f"Invalid expression syntax: {e}")
    except Exception as e:
        raise ValueError(f"Evaluation error: {e}")


@calculator_mcp.tool()
def calculate(expression: str) -> str:
    """
    Calculate the result of a mathematical expression.
    Supports:
    - Basic arithmetic: +, -, *, /, //, %, **
    - Mathematical functions: sin, cos, tan, log, sqrt, abs, etc.
    - Mathematical constants: pi, e, tau
    - Parentheses for grouping
    :param expression: expression: The mathematical expression to evaluate (e.g., "2 + 3 * 4", "sin(pi/2)", "sqrt(16)")
    Send the input as {'expression': 'expression_value'}
    :return: The calculated result as a string
    """
    try:
        result = evaluate(expression)
        return result
    except Exception as e:
        return (f"Error happened during calculate call: {e}"
                f"Check the error and if possible, try again.")


@calculator_mcp.tool()
def list_functions() -> str:
    """
    List all available mathematical functions and constants.

    Returns:
        A formatted string listing all available functions and constants
    """
    functions = []
    constants = []

    for name in dir(math):
        if not name.startswith("__"):
            attr = getattr(math, name)
            if callable(attr):
                functions.append(name)
            else:
                constants.append(name)

    # Add our custom constants
    constants.extend(["pi", "e", "tau"])

    result = "Available Mathematical Functions:\n"
    result += ", ".join(sorted(functions))
    result += "\n\nAvailable Constants:\n"
    result += ", ".join(sorted(constants))
    result += "\n\nOperators: +, -, *, /, //, %, ** (or ^)"

    return result


if __name__ == "__main__":
    calculator_mcp.run(transport="stdio")
    # print(calculate("sqrt((5-1)^2 + (3-0)^2)"))