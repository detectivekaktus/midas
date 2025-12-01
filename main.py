from asyncio import run

from src.loggers import load_logging_config
from src.platform.telegram import start_bot


async def main() -> None:
    load_logging_config()
    await start_bot()


if __name__ == "__main__":
    run(main())
