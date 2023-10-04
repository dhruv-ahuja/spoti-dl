import asyncio

from spotidl.cli import controller


async def cli():
    await controller()


if __name__ == "__main__":
    asyncio.run(cli())
