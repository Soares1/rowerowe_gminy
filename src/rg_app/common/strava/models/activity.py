from datetime import datetime
from decimal import Decimal
from typing import Any, TypeVar

from pydantic import AliasChoices, Field

from .base import BaseStravaModel


class ActivityMap(BaseStravaModel):
    id: str | None = None
    polyline: str | None = None
    summary_polyline: str | None = None


class AthleteReference(BaseStravaModel):
    id: int


class ActivityPartial(BaseStravaModel):
    id: int
    athlete: AthleteReference
    sport_type: str = Field(validation_alias=AliasChoices("sport_type", "type"))
    name: str
    moving_time: int
    elapsed_time: int
    total_elevation_gain: Decimal | None = None
    map: ActivityMap | None = None
    start_date: datetime
    manual: bool
    trainer: bool
    distance: Decimal | None = None
    elev_high: Decimal | None = None
    elev_low: Decimal | None = None
    gear_id: str | None = None
    original_data: dict[str, Any] | None = None
    description: str | None = None  # Only for detailed activity


class ActivityPatch(BaseStravaModel):
    description: str | None = None


T = TypeVar("T")


class ActivityStreamData[T](BaseStravaModel):
    data: list[T]
    series_type: str
    original_size: int
    resolution: str


class ActivityStreamSet(BaseStravaModel):
    latlng: ActivityStreamData[tuple[float, float]]
    altitude: ActivityStreamData[float]
    time: ActivityStreamData[int]
