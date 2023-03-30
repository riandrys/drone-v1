from collections.abc import Mapping
from uuid import uuid4
import aiofiles
from fastapi import Depends, FastAPI, HTTPException, status, UploadFile
from fastapi.staticfiles import StaticFiles

from .dependencies import valid_drone_id, valid_medication_id
from .services import (
    get_drones,
    get_drone_by_serial_number as get_by_serial_number,
    create_drone,
    create_medication,
    get_mediaction_by_code,
    get_medications,
)
from src.schemas.drone import Drone, DroneCreate
from src.schemas.medication import MedicationCreate, Medication
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.database import get_async_session
import os
from src.config.files import STATIC_FILES_DIR, IMG_DIR


app = FastAPI()


app.mount(STATIC_FILES_DIR, StaticFiles(directory="static"), name="static")


@app.get("/drones/", response_model=list[Drone])
async def list_drones(session: AsyncSession = Depends(get_async_session)):
    result = await get_drones(session)
    return result


@app.get("/drones/{drone_id}", response_model=Drone)
async def get_drone(drone: Mapping = Depends(valid_drone_id)):
    return drone


@app.post("/drones/", response_model=Drone)
async def create_new_drone(
    drone: DroneCreate, session: AsyncSession = Depends(get_async_session)
):
    db_drone = await get_by_serial_number(session, serial_number=drone.serial_number)
    if db_drone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Serial number already registered",
        )
    return await create_drone(session, drone)


@app.get("/medications/", response_model=list[Medication])
async def list_medications(session: AsyncSession = Depends(get_async_session)):
    result = await get_medications(session)
    return result


@app.get("/medications/{mediaction_id}", response_model=Medication)
async def get_medication(medication: Mapping = Depends(valid_medication_id)):
    return medication


@app.post("/medications/", response_model=Medication)
async def create_new_medication(
    medication: MedicationCreate = Depends(),
    file: UploadFile | None = None,
    session: AsyncSession = Depends(get_async_session),
):
    db_medication = await get_mediaction_by_code(session, code=medication.code)
    if db_medication:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Code already registered"
        )

    if file:
        if file.content_type not in ["image/png", "image/jpeg"]:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Only .jpeg or .png files allowed",
            )

        _, ext = os.path.splitext(file.filename)
        content = await file.read()

        filename = f"{uuid4().hex}{ext}"
        async with aiofiles.open(os.path.join(IMG_DIR, filename), mode="wb") as f:
            await f.write(content)
        result = await create_medication(session, medication, filename)
        file_location = os.path.abspath(os.path.join(IMG_DIR, filename))
        result.image = file_location
    else:
        result = await create_medication(session, medication)
    return result
