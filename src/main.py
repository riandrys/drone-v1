from collections.abc import Mapping
from uuid import uuid4
import aiofiles
from fastapi import Depends, FastAPI, Form, HTTPException, status, UploadFile
from fastapi.staticfiles import StaticFiles
from src.models.drone import Status

from src.schemas.load import Load, LoadCreate

from .dependencies import (
    drone_has_been_loaded,
    drones_avaliable,
    valid_drone_id,
    valid_medication_id,
    drone_is_avaliable,
    drone_can_carry_load,
)
from .services import (
    get_drones,
    get_drone_by_serial_number as get_by_serial_number,
    create_drone,
    create_medication,
    get_medication_by_code,
    get_medication_by_load,
    get_medications,
    load_drone,
    update_and_check_battery,
    update_drone,
)
from src.schemas.drone import Drone, DroneCreate, DroneLoading, DroneLoads
from src.schemas.medication import MedicationCreate, Medication
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.database import get_async_session
import os
from src.config.files import STATIC_FILES_DIR, IMG_DIR
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.config.base_config import base_settings


app = FastAPI()


scheduler = AsyncIOScheduler()


async def check_battery():
    await update_and_check_battery()


@app.on_event("startup")
async def start_background_task():
    interval = base_settings.check_battery_interval
    scheduler.add_job(check_battery, "interval", minutes=interval, id="check_battery")
    scheduler.start()


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


@app.get("/medications/{medication_id}", response_model=Medication)
async def get_medication(medication: Mapping = Depends(valid_medication_id)):
    return medication


@app.post("/medications/", response_model=Medication)
async def create_new_medication(
    name: str = Form(regex="^[A-Za-z0-9_-]*$"),
    weight: int = Form(gt=0),
    code: str = Form(regex=r"^[A-Z_\d]+$"),
    image: UploadFile | None = None,
    session: AsyncSession = Depends(get_async_session),
):
    db_medication = await get_medication_by_code(session, code=code)
    if db_medication:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Code already registered"
        )
    medication = MedicationCreate(name=name, code=code, weight=weight)
    if image:
        if image.content_type not in ["image/png", "image/jpeg"]:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Only .jpeg or .png files allowed",
            )

        _, ext = os.path.splitext(image.filename)
        content = await image.read()

        filename = f"{uuid4().hex}{ext}"
        async with aiofiles.open(os.path.join(IMG_DIR, filename), mode="wb") as f:
            await f.write(content)
        result = await create_medication(session, medication, filename)
        file_location = os.path.abspath(os.path.join(IMG_DIR, filename))
        result.image = file_location
    else:
        result = await create_medication(session, medication)
    return result


@app.post("/drones/{drone_id}/loading/", response_model=DroneLoading)
async def loading_drone(
    load: LoadCreate,
    drone: Mapping = Depends(drone_is_avaliable),
    session: AsyncSession = Depends(get_async_session),
):
    await update_drone(session, drone.id, state=Status.LOADING)
    can_be_carry = await drone_can_carry_load(drone, load.medications, session)
    if len(can_be_carry.get("medications")):
        result = await load_drone(
            session,
            drone.id,
            load,
            can_be_carry.get("medications"),
            can_be_carry.get("weight_loaded"),
        )
    else:
        await update_drone(session, drone.id, state=Status.IDLE)
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Neither medication could be loaded.",
        )

    drone_ = drone.__dict__
    drone_.pop("_sa_instance_state")
    load_ = result.__dict__
    load_.pop("_sa_instance_state")
    load_schema = Load(**load_, medications=can_be_carry.get("medications"))

    respose = DroneLoading(**drone_, load=load_schema)
    return respose


@app.get("/drones/{drone_id}/loaded/", response_model=DroneLoads)
async def loads_by_drone_id(
    drone: dict[str, Mapping] = Depends(drone_has_been_loaded),
    session: AsyncSession = Depends(get_async_session),
):
    drone_ = drone.get("drone").__dict__
    drone_.pop("_sa_instance_state")
    if drone.get("loads"):
        drone_loads = []
        for load in drone.get("loads"):
            medications = await get_medication_by_load(session, load.id)
            load_ = load.__dict__
            load_.pop("_sa_instance_state")
            load_schema = Load(**load_, medications=medications)
            drone_loads.append(load_schema)

        respose = DroneLoads(**drone_, loads=drone_loads)
    else:
        respose = DroneLoads(**drone_, loads=[])
    return respose


@app.get("/drones/available/", response_model=list[Drone])
async def get_available_drones(drones: list[Drone] = Depends(drones_avaliable)):
    return drones
