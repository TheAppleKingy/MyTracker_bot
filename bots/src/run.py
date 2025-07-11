from bot import start
import asyncio
import os
import hupper


def run():
    asyncio.run(start())


if os.getenv('AUTO_RELOAD'):
    hupper.start_reloader('run.run')


if __name__ == "__main__":
    run()
