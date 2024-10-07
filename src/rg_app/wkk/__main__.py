import asyncio

import click

from .app import main as app_main
from .config import Config


async def gthr(to_gather):
    await asyncio.gather(*to_gather)


@click.command(help="Run the WKK service")
@click.option("-c", "--config", "config_path", type=click.Path(exists=True), help="Config file path", required=True)
def run(config_path: str):
    config = Config.from_file(config_path)
    asyncio.run(app_main(config))


def main():
    run()


if __name__ == "__main__":
    main()