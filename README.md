# Python AST examples

This repo contains examples and exercises for working with the built-in `ast` module in Python. The `ast` module provides a way to interact with Python code as an Abstract Syntax Tree (AST), allowing you to analyze and manipulate Python code programmatically.

Grading works with `uv` and `pytest`. The tests are located in the `tests/` directory.

## Première configuration

> [!IMPORTANT]
> Ce template est prévu pour `uv`. Utilisez `uv sync` pour installer les dépendances et `uv run` pour exécuter les commandes du projet.

### Configuration avec [`uv`](https://docs.astral.sh/uv/)

<details>
<summary>Instructions pour uv</summary>

#### 1) Installer les dépendances

```bash
uv sync --group dev
```

#### 2) Exécuter les tests

```bash
uv run pytest tests/
```

#### 3) Lancer les hooks qualité

```bash
uv tool install pre-commit
uvx pre-commit install
uvx pre-commit run --all-files
```

