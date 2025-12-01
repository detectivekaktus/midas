from asyncio import run

from src.platform.telegram import start_bot


async def main() -> None:
    await start_bot()


if __name__ == "__main__":
    run(main())
