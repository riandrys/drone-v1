import datetime
from fastapi import HTTPException
import pytest
from src.schemas.drone import DroneCreate
from src.schemas.load import LoadCreate
from src.dependencies import (
    drone_can_carry_load,
    drone_has_been_loaded,
    drone_is_avaliable,
)
from src.models.drone import Models, Status
from src.services import (
    create_drone,
    get_available_drones,
    get_medications,
    load_drone,
)
from sqlalchemy.ext.asyncio import AsyncSession
from tests.utils.utils import generate_random_alphanum
from tests.utils.seed_db import seed_db


@pytest.mark.asyncio
async def test_drone_has_been_loaded(session: AsyncSession) -> None:
    await seed_db()
    available_drones = await get_available_drones(session)
    drones_sroted = sorted(available_drones, key=lambda x: x.weight_limit, reverse=True)

    drone = drones_sroted[0]
    medications = await get_medications(session)
    medication_ids = [m.id for m in medications]
    can_be_carry = await drone_can_carry_load(drone, medication_ids, session)
    load = LoadCreate(
        origin="Playa",
        destination="Habana",
        create=str(datetime.datetime.now()),
        medications=medication_ids,
    )

    await load_drone(
        session,
        drone.id,
        load,
        can_be_carry.get("medications"),
        can_be_carry.get("weight_loaded"),
    )

    drone_loaded = await drone_has_been_loaded(drone, session)
    assert len(drone_loaded["loads"])

    drone_unloaded = await drone_has_been_loaded(drones_sroted[1], session)
    assert not len(drone_unloaded["loads"])


@pytest.mark.asyncio
async def test_drone_is_avaliable(session: AsyncSession) -> None:
    drone1 = DroneCreate(
        serial_number=generate_random_alphanum(10),
        model=Models.CRUISERWEIGHT,
        weight_limit=50,
        battery_capacity=50,
        state=Status.IDLE,
    )
    drone1_db = await create_drone(session, drone1)

    drone2 = DroneCreate(
        serial_number=generate_random_alphanum(11),
        model=Models.CRUISERWEIGHT,
        weight_limit=50,
        battery_capacity=20,
        state=Status.IDLE,
    )
    drone2_db = await create_drone(session, drone2)

    drone3 = DroneCreate(
        serial_number=generate_random_alphanum(10),
        model=Models.CRUISERWEIGHT,
        weight_limit=50,
        battery_capacity=50,
        state=Status.RETURNING,
    )
    drone3_db = await create_drone(session, drone3)

    drone1_available = await drone_is_avaliable(drone1_db, session)
    assert drone1_available.id == drone1_db.id

    with pytest.raises(HTTPException) as e_info:
        await drone_is_avaliable(drone2_db, session)

    assert (
        e_info._excinfo[1].__dict__["detail"]
        == "The drone's battery level is below 25 percent"
    )
    assert e_info._excinfo[1].__dict__["status_code"] == 405

    with pytest.raises(HTTPException) as e:
        await drone_is_avaliable(drone3_db, session)

    assert e._excinfo[1].__dict__["status_code"] == 405
    assert "The drone's state must be IDLE and it's" in e._excinfo[1].__dict__["detail"]
