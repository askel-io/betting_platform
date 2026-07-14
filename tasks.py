
from invoke.tasks import task

PYTHON_TARGETS = "line_provider bet_maker tests"


@task
def isort(c, check: bool = False) -> None:
    """Sort imports with isort."""
    flag = " --check-only --diff" if check else ""
    c.run(f"isort {PYTHON_TARGETS}{flag}", pty=False)


@task
def black(c, check: bool = False) -> None:
    """Format code with black."""
    flag = " --check --diff" if check else ""
    c.run(f"black {PYTHON_TARGETS}{flag}", pty=False)


@task
def lint(c, fix: bool = False) -> None:
    """Run ruff linter."""
    flag = " --fix" if fix else ""
    c.run(f"ruff check {PYTHON_TARGETS}{flag}", pty=False)


@task
def format(c) -> None:
    """Run isort and black."""
    isort(c)
    black(c)


@task
def check(c) -> None:
    """Run isort, black, and ruff in check mode."""
    isort(c, check=True)
    black(c, check=True)
    lint(c)


@task
def test(c, verbose: bool = True) -> None:
    """Run all tests with pytest and print coverage summary."""
    flag = "-v" if verbose else ""
    c.run(
        f"pytest {flag} --cov --cov-report=term-missing:skip-covered".strip(),
        pty=False,
        env={"PYTHONPATH": "."},
    )


@task(default=True)
def all(c) -> None:
    """Format code and run linter."""
    format(c)
    lint(c)
