from collections.abc import Mapping
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.drone import Drone
from src.config.database import get_async_session
from .services import get_drone_by_id, get_medication_by_id, get_drone_loads
from src.models.drone import Status
from src.config.logs import get_logger


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


async def drone_is_avaliable(
    drone: Mapping = Depends(valid_drone_id),
    session: AsyncSession = Depends(get_async_session),
) -> Mapping:
    if drone.state != Status.IDLE:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail=f"The drone's state must be IDLE and it's {drone.state.value}",
        )
    elif drone.battery_capacity < 25:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="The drone's battery level is below 25 percent",
        )
    return drone


async def drone_has_been_loaded(
    drone: Mapping = Depends(valid_drone_id),
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, Mapping]:
    drone_loads = await get_drone_loads(session, drone.id)
    if drone_loads:
        return {"drone": drone, "loads": drone_loads}
    return {"drone": drone, "loads": []}


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


async def drone_can_carry_load(
    drone: Drone,
    medications: list[int],
    session: AsyncSession = Depends(get_async_session),
) -> list[int] | None:
    logger = get_logger()
    medications_can_carry = []
    total_weight = 0
    for medication_id in medications:
        # skip incorrect medication ids
        try:
            medication = await valid_medication_id(medication_id, session)
        except HTTPException as e:
            logger.exception(e)
        else:
            total_weight += medication.weight
            if total_weight <= drone.weight_limit:
                medications_can_carry.append(medication)
                logger.info("Pruebaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
            else:
                # in case another medication can be loaded
                total_weight -= medication.weight
                logger.debug(
                    f"{medication.name} medication can't be load in drone {drone.serial_number} because its weight exceeds the drone's weight limit"
                )
    return {"weight_loaded": total_weight, "medications": medications_can_carry}
