import asyncio
import sys
from contextlib import asynccontextmanager
from logging import Logger
from urllib.parse import urljoin

import httpx
from fastapi import FastAPI

from .config import Config

STRAVA_SUB_URL = "https://www.strava.com/api/v3/push_subscriptions"


def lifespan_factory(config: Config, sleep: int = 5, logger: Logger | None = None):
    @asynccontextmanager
    async def register_sub_hook(app: FastAPI):
        asyncio.create_task(register_sub(config, sleep, logger))
        yield

    return register_sub_hook


async def register_sub(config: Config, sleep: int = 5, logger: Logger | None = None):
    await asyncio.sleep(sleep)
    async with httpx.AsyncClient() as client:
        current_subs = await client.get(
            STRAVA_SUB_URL,
            params={"client_id": config.strava.client_id, "client_secret": config.strava.get_client_secret()},
        )
        current_subs.raise_for_status()
        sub_list = current_subs.json()

        callback_url = urljoin(config.self_url, "/".join(["webhook", config.get_verify_token()]))
        callback_present = False

        if sub_list:
            for sub in sub_list:
                if sub["callback_url"] != callback_url:
                    sub_id = sub["id"]
                    await client.delete(urljoin(STRAVA_SUB_URL, str(sub_id)))
                else:
                    callback_present = True
        if callback_present:
            if logger:
                logger.info("Webhook already registered")
            return
        sub = {
            "client_id": config.strava.client_id,
            "client_secret": config.strava.get_client_secret(),
            "callback_url": callback_url,
            "verify_token": config.get_verify_token(),
        }
        new_sub = await client.post(STRAVA_SUB_URL, data=sub)
        if new_sub.is_success:
            if logger:
                logger.info("Webhook registered!")
        else:
            if logger:
                logger.error("Failed to register webhook")
                logger.error(new_sub.text)
                logger.error("I am dead 😱")
            sys.exit(1)
