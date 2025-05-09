import logging
import typing as ty

from nats.js import JetStreamContext
from nats.js.api import (
    AckPolicy,
    ConsumerConfig,
    DeliverPolicy,
    ExternalStream,
    KeyValueConfig,
    StorageType,
    StreamConfig,
    StreamSource,
)
from nats.js.errors import BadRequestError

from .cloud import STREAM_INCOMING_WHA
from .utils import add_or_update_stream, make_durable

NAME_INCOMING_WHA_MIRROR = STREAM_INCOMING_WHA.name


def mk_stream_incoming_wha_mirror(cloud_domain: str) -> StreamConfig:
    cfg = StreamConfig(
        name=str(NAME_INCOMING_WHA_MIRROR),
        description="Strava incoming webhooks - cloud replication",
        mirror=StreamSource(
            name=ty.cast(str, STREAM_INCOMING_WHA.name),
            external=ExternalStream(api=f"$JS.{cloud_domain}.API", deliver="_MIRRORS.CLOUD"),
        ),
        max_bytes=2 * (1024**3),  # 2GB
    )
    return cfg


CONSUMER_WKK = make_durable(
    ConsumerConfig(
        "wkk",
        description="Process incoming activities",
        ack_policy=AckPolicy.EXPLICIT,
        deliver_policy=DeliverPolicy.NEW,
        filter_subject="rg.incoming.wha.activity.*.*",
    )
)

CONSUMER_ACTIVITIES = make_durable(
    ConsumerConfig(
        "activities",
        description="Process incoming activities",
        ack_policy=AckPolicy.EXPLICIT,
        deliver_policy=DeliverPolicy.NEW,
        filter_subject="rg.incoming.wha.activity.*.*",
    )
)

CONSUMER_REVOCATIONS = make_durable(
    ConsumerConfig(
        "revocations",
        description="Process incoming revocations",
        ack_policy=AckPolicy.EXPLICIT,
        deliver_policy=DeliverPolicy.NEW,
        filter_subject="rg.incoming.wha.athlete.*.*",
    )
)

KV_WKK_AUTH = KeyValueConfig(
    bucket="wkk-auth",
    description="WKK Auth info",
    storage=StorageType.FILE,
    max_bytes=20 * (1024**2),  # 20MB
)

KV_RATE_LIMITS = KeyValueConfig(
    bucket="rate-limits",
    description="Strava rate limits",
    storage=StorageType.FILE,
    max_bytes=10 * (1024**1),  # 10kB
)

# rg.internal.cmd.activity.{type}.{athlete_id}.{activity_id?}
# type: "create", "update", "delete", "backlog"
# activity_id token does not exist in backlog
STREAM_ACTIVITY_CMD = StreamConfig(
    name="activity-cmd",
    description="Activity commands",
    subjects=["rg.internal.cmd.activity.>"],
    max_bytes=1 * (1024**3),  # 1GB
)

CONSUMER_ACTIVITY_CMD_STD = make_durable(
    ConsumerConfig(
        "std",
        description="Process standard activitiy commands",
        ack_policy=AckPolicy.EXPLICIT,
        deliver_policy=DeliverPolicy.NEW,
        ack_wait=60,
        filter_subjects=[
            "rg.internal.cmd.activity.create.>",
            "rg.internal.cmd.activity.update.>",
            "rg.internal.cmd.activity.delete.>",
        ],
        max_ack_pending=20,
    )
)

CONSUMER_ACTIVITY_CMD_BACKLOG = make_durable(
    ConsumerConfig(
        "backlog",
        description="Process standard activitiy commands",
        ack_policy=AckPolicy.EXPLICIT,
        deliver_policy=DeliverPolicy.NEW,
        ack_wait=120,
        filter_subjects=[
            "rg.internal.cmd.activity.backlog.>",
        ],
        max_ack_pending=20,
    )
)


# rg.internal.ride.{type}.{athlete_id}.{ride_id}
# type: "fresh", "delete", "refresh", "backlog", "update"
STREAM_INTERNAL_RIDE = StreamConfig(
    name="internal-ride",
    description="Internal rides",
    subjects=["rg.internal.ride.*.*.*"],
    max_bytes=2 * (1024**3),  # 2GB
)


async def setup(js: JetStreamContext, cloud_domain: str = "ngs", dev: bool = False):
    jsm = js._jsm
    if dev:
        wha_mirror_stream = mk_stream_incoming_wha_mirror(cloud_domain)
    else:
        wha_mirror_stream = STREAM_INCOMING_WHA
    try:
        await add_or_update_stream(jsm, wha_mirror_stream)
    except BadRequestError as e:
        logging.warning("Could not update or create stream: %s", e)
    await jsm.add_consumer(ty.cast(str, wha_mirror_stream.name), CONSUMER_WKK)
    await jsm.add_consumer(ty.cast(str, wha_mirror_stream.name), CONSUMER_ACTIVITIES)
    await jsm.add_consumer(ty.cast(str, wha_mirror_stream.name), CONSUMER_REVOCATIONS)

    await add_or_update_stream(jsm, STREAM_ACTIVITY_CMD)
    await jsm.add_consumer(ty.cast(str, STREAM_ACTIVITY_CMD.name), CONSUMER_ACTIVITY_CMD_STD)
    await jsm.add_consumer(ty.cast(str, STREAM_ACTIVITY_CMD.name), CONSUMER_ACTIVITY_CMD_BACKLOG)

    await js.create_key_value(KV_WKK_AUTH)
    await js.create_key_value(KV_RATE_LIMITS)
