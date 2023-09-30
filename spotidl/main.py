from spotidl.cli import controller

# from spotidl.spotify import get_track_details, wrapper
import asyncio


async def cli():
    print("awaiting...")
    v = await controller()


if __name__ == "__main__":
    asyncio.run(cli())
