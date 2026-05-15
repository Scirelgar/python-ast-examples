import ast
from pprint import pformat

from ast_exercises import (
    DataMovement,
    Fact,
    exercise_1_parse_source,
    exercise_2_collect_function_names,
    exercise_3_collect_function_args,
    exercise_4_count_returns,
    exercise_5_collect_simple_calls,
    exercise_6_collect_dotted_calls,
    exercise_7_detect_write_candidates,
    exercise_8_detect_read_candidates,
    exercise_9_detect_routes,
    exercise_10_collect_function_scoped_calls,
    exercise_11_extract_facts,
    exercise_12_infer_movements,
    get_call_name,
)


# ============================================================
# Test feedback helpers
# ============================================================


def assert_equal(actual, expected, context: str, hint: str | None = None):
    """
    Assert equality with a readable debugging message.

    Pytest already provides diffs for failed equality assertions,
    but this helper adds exercise-specific context and hints.
    """
    message = (
        f"\n{context}\n\nExpected:\n{pformat(expected)}\n\nActual:\n{pformat(actual)}"
    )

    if hint:
        message += f"\n\nHint:\n{hint}"

    assert actual == expected, message


def assert_is_instance(actual, expected_type, context: str, hint: str | None = None):
    message = (
        f"\n{context}\n\n"
        f"Expected instance of:\n{expected_type}\n\n"
        f"Actual type:\n{type(actual)}\n\n"
        f"Actual value:\n{pformat(actual)}"
    )

    if hint:
        message += f"\n\nHint:\n{hint}"

    assert isinstance(actual, expected_type), message


# ============================================================
# Shared helper tests
# ============================================================


class TestGetCallName:
    def test_simple_name(self):
        node = ast.parse("save(user)").body[0].value.func

        actual = get_call_name(node)
        expected = "save"

        assert_equal(
            actual=actual,
            expected=expected,
            context="get_call_name should return the identifier for a simple ast.Name call.",
            hint="For ast.Name nodes, return node.id.",
        )

    def test_dotted_name(self):
        node = ast.parse("db.session.add(user)").body[0].value.func

        actual = get_call_name(node)
        expected = "db.session.add"

        assert_equal(
            actual=actual,
            expected=expected,
            context="get_call_name should resolve dotted ast.Attribute calls recursively.",
            hint="For ast.Attribute, resolve node.value first, then append '.' + node.attr.",
        )

    def test_chained_call(self):
        node = (
            ast.parse("db.session.query(User).filter_by(id=1).first()")
            .body[0]
            .value.func
        )

        actual = get_call_name(node)
        expected = "db.session.query.filter_by.first"

        assert_equal(
            actual=actual,
            expected=expected,
            context="get_call_name should resolve chained calls into a readable dotted name.",
            hint=(
                "A chained call may contain ast.Call inside ast.Attribute.value. "
                "For ast.Call nodes, resolve node.func."
            ),
        )


# ============================================================
# Exercise 1
# ============================================================


class TestExercise1:
    def test_parse_source_returns_module(self):
        source = "x = 1 + 2"

        tree = exercise_1_parse_source(source)

        assert_is_instance(
            actual=tree,
            expected_type=ast.Module,
            context="Exercise 1 should return the AST root produced by ast.parse.",
            hint="Use ast.parse(source).",
        )

        assert_is_instance(
            actual=tree.body[0],
            expected_type=ast.Assign,
            context="Exercise 1 should preserve the assignment statement in the parsed AST.",
            hint="Do not return ast.dump(...); return the AST object itself.",
        )


# ============================================================
# Exercise 2
# ============================================================


class TestExercise2:
    def test_collect_function_names(self):
        source = """
def add(x, y):
    return x + y

def subtract(x, y):
    return x - y
"""

        actual = exercise_2_collect_function_names(source)
        expected = ["add", "subtract"]

        assert_equal(
            actual=actual,
            expected=expected,
            context="Exercise 2 should collect function names in source order.",
            hint="Implement visit_FunctionDef and append node.name.",
        )

    def test_collect_function_names_ignores_classes(self):
        source = """
class User:
    pass

def create_user():
    pass
"""

        actual = exercise_2_collect_function_names(source)
        expected = ["create_user"]

        assert_equal(
            actual=actual,
            expected=expected,
            context="Exercise 2 should collect function names, not class names.",
            hint="Only visit FunctionDef nodes. ClassDef nodes should not be added.",
        )


# ============================================================
# Exercise 3
# ============================================================


class TestExercise3:
    def test_collect_function_args(self):
        source = """
def create_user(name, email, age):
    return {"name": name, "email": email, "age": age}
"""

        actual = exercise_3_collect_function_args(source)
        expected = {"create_user": ["name", "email", "age"]}

        assert_equal(
            actual=actual,
            expected=expected,
            context="Exercise 3 should map each function to its positional argument names.",
            hint="Use [arg.arg for arg in node.args.args].",
        )

    def test_collect_args_for_multiple_functions(self):
        source = """
def a():
    pass

def b(x, y):
    pass
"""

        actual = exercise_3_collect_function_args(source)
        expected = {
            "a": [],
            "b": ["x", "y"],
        }

        assert_equal(
            actual=actual,
            expected=expected,
            context="Exercise 3 should handle functions with zero or many positional arguments.",
            hint="An empty argument list should produce an empty list, not None.",
        )


# ============================================================
# Exercise 4
# ============================================================


class TestExercise4:
    def test_count_returns_per_function(self):
        source = """
def classify(x):
    if x > 0:
        return "positive"
    if x < 0:
        return "negative"
    return "zero"
"""

        actual = exercise_4_count_returns(source)
        expected = {"classify": 3}

        assert_equal(
            actual=actual,
            expected=expected,
            context="Exercise 4 should count all return statements inside a function, including nested ones.",
            hint="Call self.generic_visit(node) inside visit_FunctionDef so nested Return nodes are visited.",
        )

    def test_count_returns_multiple_functions(self):
        source = """
def a():
    return 1

def b(x):
    if x:
        return 2
    return 3
"""

        actual = exercise_4_count_returns(source)
        expected = {
            "a": 1,
            "b": 2,
        }

        assert_equal(
            actual=actual,
            expected=expected,
            context="Exercise 4 should count returns separately for each function.",
            hint="Track current_function when entering a function and restore the previous value afterward.",
        )


# ============================================================
# Exercise 5
# ============================================================


class TestExercise5:
    def test_collect_simple_calls(self):
        source = """
def process(user):
    save(user)
    notify(user)
    print("done")
"""

        actual = exercise_5_collect_simple_calls(source)
        expected = ["save", "notify", "print"]

        assert_equal(
            actual=actual,
            expected=expected,
            context="Exercise 5 should collect calls whose callee is a simple ast.Name.",
            hint="For save(user), node.func is ast.Name and node.func.id is 'save'.",
        )

    def test_ignores_dotted_calls(self):
        source = """
def process(user):
    db.session.add(user)
    save(user)
"""

        actual = exercise_5_collect_simple_calls(source)
        expected = ["save"]

        assert_equal(
            actual=actual,
            expected=expected,
            context="Exercise 5 should ignore dotted calls such as db.session.add(...).",
            hint="Only append calls when isinstance(node.func, ast.Name).",
        )


# ============================================================
# Exercise 6
# ============================================================


class TestExercise6:
    def test_collect_dotted_calls(self):
        source = """
def create_user(user):
    db.session.add(user)
    db.session.commit()
    requests.post("https://example.com", json=user)
"""

        actual = exercise_6_collect_dotted_calls(source)
        expected = [
            "db.session.add",
            "db.session.commit",
            "requests.post",
        ]

        assert_equal(
            actual=actual,
            expected=expected,
            context="Exercise 6 should collect readable names for dotted calls.",
            hint="Visit Call nodes and append get_call_name(node.func).",
        )

    def test_collect_nested_chained_calls(self):
        source = """
def get_user():
    return db.session.query(User).filter_by(id=1).first()
"""

        actual = exercise_6_collect_dotted_calls(source)
        expected = [
            "db.session.query.filter_by.first",
            "db.session.query.filter_by",
            "db.session.query",
        ]

        assert_equal(
            actual=actual,
            expected=expected,
            context="Exercise 6 should collect every call in a chained call expression.",
            hint=(
                "A chain like query(...).filter_by(...).first() contains three ast.Call nodes. "
                "generic_visit(node) must be called after recording the current call."
            ),
        )


# ============================================================
# Exercise 7
# ============================================================


class TestExercise7:
    def test_detect_database_write_candidates(self):
        source = """
def create_user(user):
    db.session.add(user)
    db.session.commit()
    return user

def delete_user(user):
    db.session.delete(user)
    db.session.commit()
"""

        actual = exercise_7_detect_write_candidates(source)
        expected = [
            {"call": "db.session.add", "line": 3},
            {"call": "db.session.delete", "line": 8},
        ]

        assert_equal(
            actual=actual,
            expected=expected,
            context="Exercise 7 should detect only known database write candidate calls.",
            hint=(
                "Detect db.session.add, db.session.delete, and db.session.merge. "
                "Use node.lineno for the line number."
            ),
        )

    def test_commit_is_not_counted_as_write_candidate(self):
        source = """
def create_user(user):
    db.session.commit()
"""

        actual = exercise_7_detect_write_candidates(source)
        expected = []

        assert_equal(
            actual=actual,
            expected=expected,
            context="Exercise 7 should not count db.session.commit as a write candidate.",
            hint="Commit confirms a transaction, but this exercise only treats add/delete/merge as write candidates.",
        )


# ============================================================
# Exercise 8
# ============================================================


class TestExercise8:
    def test_detect_database_read_candidates(self):
        source = """
def get_user(user_id):
    return db.session.query(User).filter_by(id=user_id).first()

def list_users():
    return User.query.all()
"""

        actual = exercise_8_detect_read_candidates(source)
        expected = [
            ("db.session.query", 3),
            ("User.query.all", 6),
        ]

        assert_equal(
            actual=actual,
            expected=expected,
            context="Exercise 8 should detect known database read candidate calls.",
            hint=(
                "Use get_call_name(node.func). "
                "Because generic_visit is called, db.session.query(...) inside the chain should also be visited."
            ),
        )


# ============================================================
# Exercise 9
# ============================================================


class TestExercise9:
    def test_detect_fastapi_style_routes(self):
        source = """
@app.get("/users")
def list_users():
    return []

@app.post("/users")
def create_user(user: UserIn):
    return user
"""

        actual = exercise_9_detect_routes(source)
        expected = [
            {
                "method": "app.get",
                "path": "/users",
                "function": "list_users",
                "line": 3,
            },
            {
                "method": "app.post",
                "path": "/users",
                "function": "create_user",
                "line": 7,
            },
        ]

        assert_equal(
            actual=actual,
            expected=expected,
            context="Exercise 9 should detect FastAPI-style route decorators.",
            hint=(
                "Inspect node.decorator_list in visit_FunctionDef. "
                "For @app.get('/users'), the decorator is an ast.Call."
            ),
        )

    def test_detect_router_routes(self):
        source = """
@router.get("/orders")
def list_orders():
    return []
"""

        actual = exercise_9_detect_routes(source)
        expected = [
            {
                "method": "router.get",
                "path": "/orders",
                "function": "list_orders",
                "line": 3,
            },
        ]

        assert_equal(
            actual=actual,
            expected=expected,
            context="Exercise 9 should also detect router.get and router.post decorators.",
            hint="The accepted decorator names include app.get, app.post, router.get, and router.post.",
        )


# ============================================================
# Exercise 10
# ============================================================


class TestExercise10:
    def test_collect_function_scoped_calls(self):
        source = """
def create_user(user):
    validate(user)
    save(user)
    return user

def send_email(user):
    email_client.send(user.email)
"""

        actual = exercise_10_collect_function_scoped_calls(source)
        expected = [
            {"function": "create_user", "call": "validate", "line": 3},
            {"function": "create_user", "call": "save", "line": 4},
            {"function": "send_email", "call": "email_client.send", "line": 8},
        ]

        assert_equal(
            actual=actual,
            expected=expected,
            context="Exercise 10 should collect calls together with the function where they appear.",
            hint=(
                "Set current_function when entering visit_FunctionDef, "
                "then restore the previous value after generic_visit."
            ),
        )


# ============================================================
# Exercise 11
# ============================================================


class TestExercise11:
    def test_extract_neutral_facts(self):
        source = """
@app.post("/users")
def create_user(user):
    db.session.add(user)
    return user
"""

        actual = exercise_11_extract_facts(source)
        expected = [
            Fact(
                kind="route_candidate",
                name="app.post",
                function="create_user",
                line=3,
            ),
            Fact(
                kind="write_candidate",
                name="db.session.add",
                function="create_user",
                line=4,
            ),
            Fact(
                kind="exit_candidate",
                name="return",
                function="create_user",
                line=5,
            ),
        ]

        assert_equal(
            actual=actual,
            expected=expected,
            context="Exercise 11 should extract neutral source-code facts.",
            hint=(
                "Do not infer Entry/Write/Exit here. "
                "Return Fact objects with route_candidate, write_candidate, and exit_candidate."
            ),
        )

    def test_extract_facts_does_not_infer_movements(self):
        source = """
@app.get("/users")
def list_users():
    return []
"""

        actual = exercise_11_extract_facts(source)

        assert all(isinstance(item, Fact) for item in actual), (
            "\nExercise 11 should return only Fact objects.\n\n"
            f"Actual result:\n{pformat(actual)}\n\n"
            "Hint:\n"
            "This exercise is the extraction phase only. "
            "DataMovement objects belong to Exercise 12."
        )

        assert not any(isinstance(item, DataMovement) for item in actual), (
            "\nExercise 11 should not return DataMovement objects.\n\n"
            f"Actual result:\n{pformat(actual)}\n\n"
            "Hint:\n"
            "Do not convert route_candidate to Entry yet. "
            "That inference happens in Exercise 12."
        )


# ============================================================
# Exercise 12
# ============================================================


class TestExercise12:
    def test_infer_simple_cosmic_movements(self):
        facts = [
            Fact(
                kind="route_candidate",
                name="app.post",
                function="create_user",
                line=3,
            ),
            Fact(
                kind="write_candidate",
                name="db.session.add",
                function="create_user",
                line=4,
            ),
            Fact(
                kind="exit_candidate",
                name="return",
                function="create_user",
                line=5,
            ),
        ]

        actual = exercise_12_infer_movements(facts)
        expected = [
            DataMovement(
                kind="Entry",
                function="create_user",
                line=3,
                rationale="Route handler suggests data entering from a functional user",
            ),
            DataMovement(
                kind="Write",
                function="create_user",
                line=4,
                rationale="Persistence mutation suggests writing to storage",
            ),
            DataMovement(
                kind="Exit",
                function="create_user",
                line=5,
                rationale="Return statement suggests data leaving the process",
            ),
        ]

        assert_equal(
            actual=actual,
            expected=expected,
            context="Exercise 12 should infer simple COSMIC-like data movements from facts.",
            hint=(
                "Map route_candidate to Entry, write_candidate to Write, "
                "and exit_candidate to Exit."
            ),
        )

    def test_unknown_fact_kinds_are_ignored(self):
        facts = [
            Fact(
                kind="unknown_candidate",
                name="something",
                function="do_something",
                line=10,
            )
        ]

        actual = exercise_12_infer_movements(facts)
        expected = []

        assert_equal(
            actual=actual,
            expected=expected,
            context="Exercise 12 should ignore unknown fact kinds.",
            hint="Only route_candidate, write_candidate, and exit_candidate should produce DataMovement objects.",
        )
