from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import select

from app.api.rest.dependencies import db, filter, user_id
from app.postgresql.models import (
    PinsOrm,
    UsersOrm,
    UsersRecommendationsPinsOrm,
)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/check")
async def check_user_recommendations(user_id: user_id, db: db):
    result = await db.execute(select(UsersOrm).filter_by(id=user_id))
    user = result.scalars().first()

    if (
        user.recommendation_created_at
        and user.recommendation_created_at.date() == datetime.now(timezone.utc).date()
    ):
        return JSONResponse(content={"make_recommendations": False})
    else:
        return JSONResponse(content={"make_recommendations": True})


@router.get("/{update_id}")
async def get_recommendation_pins(update_id: int, user_id: user_id, db: db, filter: filter):
    result = await db.execute(
        select(UsersRecommendationsPinsOrm).where(
            (UsersRecommendationsPinsOrm.user_id == user_id)
            & (UsersRecommendationsPinsOrm.update_id == update_id)
        )
    )

    # Получение результатов
    pins_recommendations = result.scalars().all()

    result_pins = []
    for row in pins_recommendations:
        pin_id = row.pin_id
        pin_db = await db.scalar(select(PinsOrm).where(PinsOrm.id == pin_id))
        result_pins.append(pin_db)

    return result_pins[filter.offset : filter.offset + filter.limit]
