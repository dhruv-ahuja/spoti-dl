import asyncio

from spotidl.cli import controller


async def cli():
    await controller()


asyncio.run(cli())
