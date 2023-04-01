import os
from collections.abc import Sequence
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.database import get_async_session
from src.schemas.load import LoadCreate
from src.config.files import IMG_DIR
from src.schemas.medication import MedicationCreate
from src.models.drone import Drone, Status
from src.models.load import Load, load_medication
from src.models.medication import Medication
from src.schemas.drone import DroneCreate
from src.config.logs import get_logger


async def get_drones(session: AsyncSession) -> Sequence[Drone]:
    query = select(Drone)
    result = await session.scalars(query)

    return result.all()


async def get_medications(session: AsyncSession) -> Sequence[Medication]:
    query = select(Medication)
    result = await session.scalars(query)
    rows = result.all()
    for row in rows:
        if row.image:
            file_location = os.path.abspath(os.path.join(IMG_DIR, row.image))
            row.image = file_location

    return rows


async def get_drone_by_id(session: AsyncSession, drone_id: int) -> Drone | None:
    return await session.get(Drone, drone_id)


async def get_drone_by_serial_number(
    session: AsyncSession, serial_number: str
) -> Drone | None:
    query = select(Drone).where(Drone.serial_number == serial_number)
    result = await session.execute(query)
    row = result.first()
    return row[0] if row else None


async def get_medication_by_id(
    session: AsyncSession, medication_id: int
) -> Medication | None:
    result = await session.get(Medication, medication_id)
    if result and result.image:
        file_location = os.path.abspath(os.path.join(IMG_DIR, result.image))
        result.image = file_location
    return result


async def get_mediaction_by_code(session: AsyncSession, code: str) -> Medication | None:
    query = select(Medication).where(Medication._code == code)
    result = await session.execute(query)
    row = result.first()

    return row[0] if row else None


async def create_drone(session: AsyncSession, drone: DroneCreate) -> Drone:
    db_drone = Drone(**drone.dict())
    session.add(db_drone)
    await session.commit()
    return db_drone


async def create_medication(
    session: AsyncSession, medication: MedicationCreate, image: str | None = None
) -> Medication:
    db_medication = Medication(**medication.dict(), image=image)
    session.add(db_medication)
    await session.commit()
    return db_medication


async def load_drone(
    session: AsyncSession,
    drone_id: int,
    load: LoadCreate,
    medications: list[Medication],
    weight_loaded: int,
):
    load_attributes = load.dict()
    load_attributes.pop("medications")
    db_load = Load(**load_attributes, drone_id=drone_id, weight_loaded=weight_loaded)
    session.add(db_load)
    await session.commit()

    load_medication_values = [
        {"load_id": db_load.id, "medication_id": medication.id}
        for medication in medications
    ]
    await session.execute(insert(load_medication).values(load_medication_values))
    await session.commit()
    await update_drone(session, drone_id, state=Status.LOADED)

    return db_load


async def update_drone(session: AsyncSession, drone_id: int, **kwarg):
    update_query = update(Drone).where(Drone.id == drone_id).values(kwarg)
    await session.execute(update_query)
    await session.commit()


async def get_drone_loads(session: AsyncSession, drone_id: int):
    query = select(Load).where(Load.drone_id == drone_id)
    result = await session.scalars(query)
    return result.all()


async def get_medication_by_load(session: AsyncSession, load_id: int):
    query = select(load_medication.c.medication_id).where(
        load_medication.c.load_id == load_id
    )
    result = await session.scalars(query)
    rows = result.all()

    medications: list[Medication] = [
        await get_medication_by_id(session, medication_id) for medication_id in rows
    ]

    return medications


async def get_available_drones(session: AsyncSession) -> list[Drone]:
    query = select(Drone).where(
        Drone.state == Status.IDLE, Drone.battery_capacity >= 25
    )
    result = await session.scalars(query)
    return result.all()


async def update_and_check_battery():
    # subtract 1% of battery
    async for session in get_async_session():
        logger = get_logger("battery_check")
        query = (
            update(Drone)
            .where(Drone.battery_capacity > 0)
            .values(battery_capacity=Drone.battery_capacity - 1)
            .returning(Drone)
        )
        result = await session.scalars(query)
        await session.commit()
        rows = result.all()
        for row in rows:
            logger.info(
                f"Drone {row.serial_number}, battery capacity: {row.battery_capacity} %"
            )
