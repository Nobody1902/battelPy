import ast
import operator

# Allowed operators
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.floordiv,  # Enforce integer division
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    # Bitwise ops
    ast.BitAnd: operator.and_,
    ast.BitOr: operator.or_,
    ast.BitXor: operator.xor,
    ast.LShift: operator.lshift,
    ast.RShift: operator.rshift,
    # Unary ops
    ast.Invert: operator.invert,
    ast.UAdd: operator.pos,
}


def replace_vars(expr, variables):
    for var, val in variables.items():
        expr = expr.replace(var, str(val))
    return expr


def eval_expr(expr):
    tree = ast.parse(expr, mode="eval")
    result = _eval_ast(tree.body)

    if not isinstance(result, int):
        raise ValueError("Expression must evaluate to an integer.")
    if result < 0:
        raise ValueError("Negative values are not allowed (unsigned only).")
    return result


def _eval_ast(node):
    if isinstance(node, ast.BinOp):
        left = _eval_ast(node.left)
        right = _eval_ast(node.right)
        op_type = type(node.op)
        if op_type not in OPERATORS:
            raise ValueError(f"Unsupported operator: {op_type}")
        return OPERATORS[op_type](left, right)

    elif isinstance(node, ast.UnaryOp):
        operand = _eval_ast(node.operand)
        op_type = type(node.op)
        if op_type not in OPERATORS:
            raise ValueError(f"Unsupported unary operator: {op_type}")
        return OPERATORS[op_type](operand)

    elif isinstance(node, ast.Constant):  # Python 3.8+
        if isinstance(node.value, int):
            return node.value
        raise ValueError("Only integer constants are allowed.")

    else:
        raise ValueError(f"Unsupported expression element: {ast.dump(node)}")
