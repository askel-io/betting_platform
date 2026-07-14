
from invoke.tasks import task

PYTHON_TARGETS = "line_provider bet_maker tests config"
MIGRATE_ENV = {"PYTHONPATH": "."}


def _run_line_provider_migrations(c) -> None:
    from config.settings import get_settings

    settings = get_settings()
    c.run(
        "alembic -c line_provider/alembic.ini upgrade head",
        env={
            **MIGRATE_ENV,
            "DATABASE_URL": settings.line_provider_database_url,
        },
        pty=False,
    )


def _run_bet_maker_migrations(c) -> None:
    from config.settings import get_settings

    settings = get_settings()
    c.run(
        "alembic -c bet_maker/alembic.ini upgrade head",
        env={
            **MIGRATE_ENV,
            "DATABASE_URL": settings.bet_maker_database_url,
        },
        pty=False,
    )


@task
def migrate_line_provider(c) -> None:
    """Apply Alembic migrations for line-provider."""
    _run_line_provider_migrations(c)


@task
def migrate_bet_maker(c) -> None:
    """Apply Alembic migrations for bet-maker."""
    _run_bet_maker_migrations(c)


@task
def migrate(c, service: str = "all") -> None:
    """Apply Alembic migrations (service: all, line_provider, bet_maker)."""
    if service == "all":
        _run_line_provider_migrations(c)
        _run_bet_maker_migrations(c)
        return

    if service == "line_provider":
        _run_line_provider_migrations(c)
        return

    if service == "bet_maker":
        _run_bet_maker_migrations(c)
        return

    raise ValueError(
        f"Unknown service: {service!r}. Use all, line_provider, or bet_maker."
    )


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
