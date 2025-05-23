import asyncio
from datetime import datetime

import fastapi
from sqlalchemy import cast, func, select
from sqlalchemy.dialects.postgresql import JSONB

from rg_app.api.dependencies.auth import UserInfoRequired
from rg_app.api.dependencies.db import AsyncSession
from rg_app.common.msg.base_model import BaseModel
from rg_app.db import Activity, Region

router = fastapi.APIRouter(tags=["regions"], prefix="/regions")


class UnlockedRegion(BaseModel):
    region_id: str


class UnlockedRegionDetail(UnlockedRegion):
    last_visited: datetime | None = None
    first_visited: datetime | None = None
    last_activity_id: str | None = None
    visited_count: int


@router.get("/unlocked")
async def unlocked(session: AsyncSession, user_info: UserInfoRequired) -> list[UnlockedRegion]:
    """
    Get all the regions that the user has unlocked
    """

    element = func.jsonb_array_elements(Activity.visited_regions).alias("element")

    query = (
        select(
            element.column.label("element"),
        )
        .select_from(Activity, element)
        .where(Activity.user_id == user_info.user_id)
        .group_by(element.column)
    )

    result = await session.execute(query)
    return [UnlockedRegion(region_id=row.element) for row in result]


@router.get("/unlocked/{region_id}")
async def unlocked_detail(region_id: str, session: AsyncSession, user_info: UserInfoRequired) -> UnlockedRegionDetail:
    """
    Get the details of a specific region that the user has unlocked
    """

    query_region_exists = select(Region.id, Region.type).where(Region.id == region_id)

    result_region_exists = (await session.execute(query_region_exists)).one_or_none()
    if result_region_exists is None:
        raise fastapi.HTTPException(status_code=404, detail="Region not found")
    else:
        region_type = result_region_exists.type

    if region_type == "GMI":
        cont_where_clause = Activity.visited_regions.contains(cast(region_id, JSONB))
    else:
        cont_where_clause = Activity.visited_regions_additional.contains(cast(region_id, JSONB))

    query_stats = select(
        func.min(Activity.start).label("first_visited"),
        func.max(Activity.start).label("last_visited"),
        func.count(Activity.id).label("visited_count"),
    ).where(
        Activity.user_id == user_info.user_id,
        cont_where_clause,
    )

    query_last_activity_id = (
        select(Activity.id)
        .where(
            Activity.user_id == user_info.user_id,
            cont_where_clause,
        )
        .order_by(Activity.start.desc())
        .limit(1)
    )
    aw_stats = session.execute(query_stats)
    aw_last_activity_id = session.execute(query_last_activity_id)

    result_stats, result_last_activity_id = await asyncio.gather(aw_stats, aw_last_activity_id)

    row_stats = result_stats.fetchone()
    scalar_last_activity_id = result_last_activity_id.scalar_one_or_none()

    if row_stats is None or row_stats.first_visited is None:
        return UnlockedRegionDetail(region_id=region_id, visited_count=0)
    else:
        la_id = str(scalar_last_activity_id) if scalar_last_activity_id is not None else None
        return UnlockedRegionDetail(
            region_id=region_id,
            last_visited=row_stats.last_visited,
            first_visited=row_stats.first_visited,
            visited_count=row_stats.visited_count,
            last_activity_id=la_id,
        )
