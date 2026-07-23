import ast
import operator
import re
import cmath
import math
from typing import Union




def is_overflow(result):
    if isinstance(result, complex):
        return math.isinf(result.real) or math.isinf(result.imag)
    elif isinstance(result, float):
        return math.isinf(result)
    elif isinstance(result, int):
        return result.bit_length() > 14300  # at most 4300 decimal digits
    else:
        return False

MAX_LIMIT = 10**4300  # A large number to check for overflow in exponentiation


def _print_limited(label: str, result) -> None:
    if is_overflow(result):
        print("Error: Overflow.")
    else:
        print(label, result)




def _read_number(prompt: str) -> Union[int, float]:
    """Read a number (int or float) from the user, reprompting on invalid input."""
    while True:
        value = input(prompt).strip()
        try:
            f = float(value)
            if f.is_integer():
                return int(f)
            else:
                return f
        except ValueError:
            print("Please enter a valid number.")




def _confirm(prompt: str) -> bool:
    """Ask the user for a yes/no confirmation."""
    while True:
        answer = input(prompt).strip().lower()
        if answer in {"yes", "y"}:
            return True
        if answer in {"no", "n"}:
            return False
        print("Please answer 'yes' or 'no'.")




def _cube_root(x: float) -> float:
    # math.cbrt is only available on Python 3.11+; use a compatible fallback.
    return math.copysign(abs(x) ** (1.0 / 3.0), x)


ALLOW_NAMES = {
    **{name: getattr(math, name) for name in dir(math) if not name.startswith("__")},
    "abs": abs,
    "round": round,
    "sqrt": math.sqrt,
    "cbrt": lambda x: math.copysign(abs(x) ** (1.0 / 3.0), x),
}

ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}


def _replace_percentage(expr: str) -> str:
    # Replace 50% with (50/100) and 2.5% with (2.5/100)
    return re.sub(r"(?P<num>\d*\.?\d+)\s*%", r"(\g<num>/100)", expr)


def _evaluate_node(node):
    if isinstance(node, ast.Expression):
        return _evaluate_node(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float, complex)):
            return node.value
        raise ValueError("Unsupported constant")
    if hasattr(ast, 'Num') and isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.BinOp):
        left = _evaluate_node(node.left)
        right = _evaluate_node(node.right)
        op_type = type(node.op)
        if op_type in ALLOWED_OPERATORS:
            return ALLOWED_OPERATORS[op_type](left, right)
        raise ValueError("Unsupported operator")
    if isinstance(node, ast.UnaryOp):
        operand = _evaluate_node(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
        raise ValueError("Unsupported unary operator")
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id in ALLOW_NAMES:
            args = [_evaluate_node(arg) for arg in node.args]
            return ALLOW_NAMES[node.func.id](*args)
        raise ValueError("Unsupported function")
    if isinstance(node, ast.Name):
        if node.id in ALLOW_NAMES:
            return ALLOW_NAMES[node.id]
        raise ValueError("Unsupported name")
    raise ValueError("Invalid expression")


def evaluate_expression(expr: str):
    expr = expr.strip().replace("×", "*").replace("÷", "/").replace("^", "**")
    expr = _replace_percentage(expr)
    expr_ast = ast.parse(expr, mode="eval")
    return _evaluate_node(expr_ast)


def main() -> None:
    while True:
        raw = input("Enter expression/equation (or 'exit'): ").strip()
        if raw.lower() == "exit":
            return
        if not raw:
            continue

        try:
            if "=" in raw:
                sides = [s.strip() for s in raw.split("=")]
                if len(sides) != 2 or not sides[0] or not sides[1]:
                    print("Invalid equation format. Example: 2+2=4")
                    continue
                left = evaluate_expression(sides[0])
                right = evaluate_expression(sides[1])
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    equal = math.isclose(left, right, rel_tol=1e-9, abs_tol=1e-12)
                else:
                    equal = left == right
                print(f"Equation: {sides[0]} = {sides[1]} -> {equal}")
                print(f" LHS = {left}, RHS = {right}")
            else:
                result = evaluate_expression(raw)
                print(f"Result: {result}")
        except Exception as exc:
            print("Error:", exc)
            continue


if __name__ == "__main__":
    main()
