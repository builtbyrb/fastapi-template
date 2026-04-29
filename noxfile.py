from typing import Self

import nox
from pydantic_settings import BaseSettings, SettingsConfigDict


class CLIArgs(
    BaseSettings,
):
    model_config = SettingsConfigDict(extra="ignore")
    ruff: bool = False
    pyright: bool = False

    @classmethod
    def parse(cls, posargs: list[str]) -> Self:
        posarg_dict: dict[str, bool] = {}

        for posarg_name in posargs:
            posarg_dict[posarg_name] = True

        return cls(**posarg_dict)


@nox.session
def fmt(session: nox.Session) -> None:
    session.run("uv", "run", "ruff", "format", ".")
    session.log("✅ Ruff formatting completed successfully.")


@nox.session
def lint(session: nox.Session) -> None:
    args = CLIArgs.parse(session.posargs)

    if args.ruff:
        session.run("uv", "run", "ruff", "check", ".", "--fix")
    if args.pyright:
        session.run("uv", "run", "pyright")


@nox.session
def test(session: nox.Session) -> None:
    session.run("uv", "run", "alembic", "upgrade", "head")
    session.run("uv", "run", "pytest")


@nox.session
def dev(session: nox.Session) -> None:
    session.run("uv", "run", "alembic", "upgrade", "head")
    session.run(
        "uv",
        "run",
        "fastapi",
        "dev",
        "src/app/main.py",
    )
