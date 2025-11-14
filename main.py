from asyncio import run
from logging import INFO, basicConfig
from sys import stdout

from src.platform.telegram import start_bot


async def main() -> None:
    basicConfig(level=INFO, stream=stdout)
    await start_bot()


if __name__ == "__main__":
    run(main())
