import logging
import os
from collections.abc import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.files import IMG_DIR
from src.schemas.medication import MedicationCreate
from src.models.drone import Drone
from src.models.medication import Medication
from src.schemas.drone import Drone as DroneCreate


logging.basicConfig(format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("Drones")
logger.setLevel(logging.DEBUG)


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
