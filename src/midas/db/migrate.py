# This file is meant to be ran with poetry via `poetry run migrate`
# however it still provides the entry point at the bottom.
from alembic import command
from alembic.config import Config


def main() -> None:
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "heads")


if __name__ == "__main__":
    main()
