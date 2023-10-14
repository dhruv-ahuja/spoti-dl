import asyncio

from spotidl.cli import controller


def main():
    event_loop = asyncio.get_event_loop()
    task = event_loop.create_task(controller())
    event_loop.run_until_complete(task)


if __name__ == "__main__":
    main()
