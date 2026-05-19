import ast
from dataclasses import dataclass
from typing import Any
import pprint as pp


@dataclass
class Fact:
    kind: str
    name: str
    function: str | None
    line: int


@dataclass
class DataMovement:
    kind: str
    function: str
    line: int
    rationale: str


# ============================================================
# Shared helper
# ============================================================


def get_call_name(node: ast.AST) -> str:
    """
    Return a readable name for a call expression.

    Examples:
        save(...)              -> "save"
        db.session.add(...)    -> "db.session.add"
        User.query.all(...)    -> "User.query.all"

    This helper is intentionally used by several exercises.
    """
    # TODO:
    # - If node is ast.Name, return its identifier.
    # - If node is ast.Attribute, recursively resolve its owner.
    # - If node is ast.Call, resolve the called function.
    # - Otherwise, return "<unknown>".

    if isinstance(node, ast.Name):
        return node.id

    elif isinstance(node, ast.Attribute):
        return ".".join([get_call_name(node.value), node.attr])

    elif isinstance(node, ast.Call):
        return get_call_name(node.func)

    else:
        return "<unknown>"


# ============================================================
# Exercise 1
# Parse Python source into an AST.
# ============================================================


def exercise_1_parse_source(source: str) -> ast.AST:
    """
    Parse a Python source string and return the AST root node.
    """
    # DONE: use ast.parse(...)
    return ast.parse(source)


# ============================================================
# Exercise 2
# Collect all function names.
# ============================================================


def exercise_2_collect_function_names(source: str) -> list[str]:
    """
    Return the names of all functions defined in the source code.

    Example:
        def add(...): ...
        def subtract(...): ...

    Expected:
        ["add", "subtract"]
    """

    # DONE:
    # - Define a NodeVisitor.
    # - Implement visit_FunctionDef.
    # - Collect node.name.
    # - Return the collected names.
    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.names: list[str] = []

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self.names.append(node.name)

    tree = ast.parse(source)
    v = Visitor()
    v.visit(tree)
    return v.names


# ============================================================
# Exercise 3
# Collect function arguments.
# ============================================================


def exercise_3_collect_function_args(source: str) -> dict[str, list[str]]:
    """
    Return a mapping from function name to its positional argument names.

    Example:
        def create_user(name, email): ...

    Expected:
        {"create_user": ["name", "email"]}
    """
    # DONE:
    # - Visit FunctionDef nodes.
    # - Read node.args.args.
    # - Each argument node has an .arg attribute.
    tree = ast.parse(source)

    class FuncVisitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.func_args: dict = {}

        def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
            pp.pp(node)
            pp.pp(node.args)
            pp.pp(node.args.args)
            self.func_args[node.name] = [arg.arg for arg in node.args.args]

    fv = FuncVisitor()
    fv.visit(tree)
    return fv.func_args


# ============================================================
# Exercise 4
# Count return statements per function.
# ============================================================


def exercise_4_count_returns(source: str) -> dict[str, int]:
    """
    Return a mapping from function name to the number of return statements
    inside that function.

    Nested returns inside if/else blocks should count.
    """
    # DONE:
    # - Track the current function.
    # - Initialize its return count when entering a FunctionDef.
    # - Increment the count in visit_Return.
    # - Restore the previous function when leaving a function.
    tree = ast.parse(source)

    class ReturnVisitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.map = {}
            self.current_func = ""

        def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
            prev = self.current_func
            self.current_func = node.name
            self.map[self.current_func] = 0
            pp.pp(self.map)
            self.generic_visit(node)
            self.current_func = prev

        def visit_Return(self, node: ast.Return) -> Any:
            pp.pp(node)
            self.map[self.current_func] += 1

    rv = ReturnVisitor()
    rv.visit(tree)

    return rv.map


# ============================================================
# Exercise 5
# Collect simple function calls.
# ============================================================


def exercise_5_collect_simple_calls(source: str) -> list[str]:
    """
    Collect calls where the called function is a simple name.

    Example:
        save(user)
        print("done")

    Expected:
        ["save", "print"]

    Dotted calls such as db.session.add(...) should be ignored here.
    """
    # DONE:
    # - Visit Call nodes.
    # - Only collect calls where node.func is ast.Name.
    tree = ast.parse(source)

    class NameVisitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.names = []

        def visit_Call(self, node: ast.Call) -> Any:
            if isinstance(node.func, ast.Name):
                self.names.append(node.func.id)

    nv = NameVisitor()
    nv.visit(tree)
    return nv.names


# ============================================================
# Exercise 6
# Collect dotted call names.
# ============================================================


def exercise_6_collect_dotted_calls(source: str) -> list[str]:
    """
    Collect readable names for all function calls, including dotted calls.

    Example:
        db.session.add(user)
        requests.post(url)

    Expected:
        ["db.session.add", "requests.post"]
    """
    # DONE:
    # - Visit Call nodes.
    # - Use get_call_name(node.func).
    tree = ast.parse(source)

    class CallVisitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.calls = []

        def visit_Call(self, node: ast.Call) -> Any:
            self.calls.append(get_call_name(node))
            self.generic_visit(node)

    cv = CallVisitor()
    cv.visit(tree)

    return cv.calls


# ============================================================
# Exercise 7
# Detect database write candidates.
# ============================================================


def exercise_7_detect_write_candidates(source: str) -> list[dict]:
    """
    Detect calls that look like database write operations.

    Write candidates:
        db.session.add(...)
        db.session.delete(...)
        db.session.merge(...)

    Return dictionaries with:
        {
            "call": call_name,
            "line": line_number,
        }
    """
    # TODO:
    # - Visit Call nodes.
    # - Use get_call_name(node.func).
    # - If the call is in the write-call set, record it.
    raise NotImplementedError


# ============================================================
# Exercise 8
# Detect database read candidates.
# ============================================================


def exercise_8_detect_read_candidates(source: str) -> list[tuple[str, int]]:
    """
    Detect calls that look like database read operations.

    Read candidates:
        db.session.query(...)
        User.query.all(...)

    Return tuples:
        (call_name, line_number)
    """
    # TODO:
    # - Visit Call nodes.
    # - Use get_call_name(node.func).
    # - Detect known read-call patterns.
    raise NotImplementedError


# ============================================================
# Exercise 9
# Detect FastAPI-style route decorators.
# ============================================================


def exercise_9_detect_routes(source: str) -> list[dict]:
    """
    Detect route handlers decorated with FastAPI-style decorators.

    Supported decorators:
        @app.get(...)
        @app.post(...)
        @router.get(...)
        @router.post(...)

    Return dictionaries with:
        {
            "method": decorator_name,
            "path": route_path,
            "function": function_name,
            "line": line_number,
        }
    """
    # TODO:
    # - Visit FunctionDef nodes.
    # - Inspect node.decorator_list.
    # - Detect ast.Call decorators.
    # - Resolve decorator.func with get_call_name.
    # - Extract the first string argument as the route path.
    raise NotImplementedError


# ============================================================
# Exercise 10
# Track current function while collecting calls.
# ============================================================


def exercise_10_collect_function_scoped_calls(source: str) -> list[dict]:
    """
    Collect all function calls and identify the function in which each call appears.

    Return dictionaries with:
        {
            "function": current_function_name,
            "call": call_name,
            "line": line_number,
        }
    """
    # TODO:
    # - Track the current function.
    # - Visit Call nodes.
    # - Record the current function, call name, and line.
    raise NotImplementedError


# ============================================================
# Exercise 11
# Extract neutral facts instead of direct COSMIC counts.
# ============================================================


def exercise_11_extract_facts(source: str) -> list[Fact]:
    """
    Extract neutral source-code facts.

    Required facts:
        - route_candidate for @app.get and @app.post
        - write_candidate for db.session.add(...)
        - exit_candidate for return statements

    Do not infer COSMIC movements here.
    Only collect source-level evidence.
    """
    # TODO:
    # - Track the current function.
    # - Detect route decorators on FunctionDef.
    # - Detect db.session.add(...) calls.
    # - Detect Return nodes.
    # - Return a list of Fact objects.
    raise NotImplementedError


# ============================================================
# Exercise 12
# Infer simple COSMIC-like data movements from facts.
# ============================================================


def exercise_12_infer_movements(facts: list[Fact]) -> list[DataMovement]:
    """
    Convert neutral facts into simple COSMIC-like movement candidates.

    Mapping:
        route_candidate -> Entry
        write_candidate -> Write
        exit_candidate  -> Exit

    This is intentionally simplified.
    """
    # TODO:
    # - Iterate through facts.
    # - Convert each known fact kind into a DataMovement.
    # - Preserve function and line information.
    raise NotImplementedError
