import logging
from collections.abc import Mapping
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.database import get_async_session
from .services import get_drone_by_id, get_medication_by_id


logging.basicConfig(format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("Drones")
logger.setLevel(logging.DEBUG)


async def valid_drone_id(
    drone_id: int, session: AsyncSession = Depends(get_async_session)
) -> Mapping:
    result = await get_drone_by_id(session, drone_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Don't exist any Drone with id {drone_id}",
        )

    return result


async def valid_medication_id(
    medication_id: int, session: AsyncSession = Depends(get_async_session)
) -> Mapping:
    result = await get_medication_by_id(session, medication_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Don't exist any Medication with id {medication_id}",
        )

    return result
