import datetime
from httpx import AsyncClient
import pytest
from fastapi import status
from src.schemas.drone import DroneCreate
from src.models.drone import Models, Status
from src.services import create_drone, get_available_drones, get_drones, get_medications
from sqlalchemy.ext.asyncio import AsyncSession
from tests.utils.utils import generate_random_alphanum, random_number
from tests.utils.seed_db import seed_db


@pytest.mark.asyncio
async def test_create_drone(client: AsyncClient) -> None:
    data = {
        "serial_number": generate_random_alphanum(15),
        "model": Models.CRUISERWEIGHT.value,
        "battery_capacity": random_number(),
        "weight_limit": random_number(500),
        "state": Status.IDLE.value,
    }

    resp = await client.post(
        "/drones/",
        json=data,
    )
    resp_json = resp.json()
    assert resp.status_code == status.HTTP_200_OK
    assert "id" in resp_json
    assert resp_json["model"] == data["model"]
    assert resp_json["battery_capacity"] == data["battery_capacity"]


@pytest.mark.asyncio
async def test_get_drone(client: AsyncClient, session: AsyncSession) -> None:
    drone = DroneCreate(
        serial_number=generate_random_alphanum(10),
        model=Models.LIGHTWEIGHT,
        weight_limit=random_number(500),
        battery_capacity=random_number(),
        state=Status.IDLE,
    )
    await create_drone(session, drone)
    resp = await client.get(
        "/drones/1",
    )
    resp_json = resp.json()
    assert resp.status_code == status.HTTP_200_OK
    assert "id" in resp_json
    assert resp_json["model"] == drone.model.value
    assert resp_json["battery_capacity"] == drone.battery_capacity


@pytest.mark.asyncio
async def test_get_drone_incorrect_id(client: AsyncClient) -> None:
    resp = await client.get(
        "/drones/5",
    )
    resp_json = resp.json()
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp_json["detail"] == "Don't exist any Drone with id 5"


@pytest.mark.asyncio
async def test_get_list_drone(client: AsyncClient, session: AsyncSession) -> None:
    for i in range(3):
        drone = DroneCreate(
            serial_number=generate_random_alphanum(10 + i),
            model=Models.LIGHTWEIGHT,
            weight_limit=random_number(500),
            battery_capacity=random_number(),
            state=Status.IDLE,
        )
        await create_drone(session, drone)
    drones = await get_drones(session)
    resp = await client.get(
        "/drones/",
    )
    resp_json = resp.json()
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp_json) == len(drones)


@pytest.mark.asyncio
async def test_get_available_drones(client: AsyncClient, session: AsyncSession) -> None:
    for i in range(3):
        drone = DroneCreate(
            serial_number=generate_random_alphanum(10 + i),
            model=Models.LIGHTWEIGHT,
            weight_limit=random_number(500),
            battery_capacity=random_number(30, 100),
            state=Status.IDLE,
        )
        await create_drone(session, drone)

    drone_loaded = DroneCreate(
        serial_number=generate_random_alphanum(8),
        model=Models.LIGHTWEIGHT,
        weight_limit=random_number(500),
        battery_capacity=random_number(),
        state=Status.LOADED,
    )
    await create_drone(session, drone_loaded)
    drone_with_out_battery = DroneCreate(
        serial_number=generate_random_alphanum(8),
        model=Models.LIGHTWEIGHT,
        weight_limit=random_number(500),
        battery_capacity=random_number(20),
        state=Status.IDLE,
    )
    await create_drone(session, drone_with_out_battery)
    resp = await client.get(
        "/drones/available/",
    )
    resp_json = resp.json()

    drones = await get_drones(session)
    assert len(drones) == 5
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp_json) == 3


@pytest.mark.asyncio
async def test_loading_drone(client: AsyncClient, session: AsyncSession) -> None:
    await seed_db()
    available_drones = await get_available_drones(session)

    drone = available_drones[0]
    medications = await get_medications(session)

    data = {
        "origin": "La habana",
        "destination": "Playa",
        "create": str(datetime.datetime.now()),
        "medications": [m.id for m in medications],
    }

    resp = await client.post(
        f"/drones/{drone.id}/loading/",
        json=data,
    )
    assert resp.status_code == status.HTTP_200_OK
    contect = resp.json()
    assert contect["serial_number"] == drone.serial_number
    assert contect["state"] == Status.LOADED.value
    assert len(contect["load"]["medications"]) == len(medications)


@pytest.mark.asyncio
async def test_loading_drone_with_overweight(
    client: AsyncClient, session: AsyncSession
) -> None:
    await seed_db()
    available_drones = await get_available_drones(session)

    drone = available_drones[2]
    medications = await get_medications(session)
    load_medication = medications[0]

    data = {
        "origin": "La habana",
        "destination": "Playa",
        "create": str(datetime.datetime.now()),
        "medications": [load_medication.id],
    }

    resp = await client.post(
        f"/drones/{drone.id}/loading/",
        json=data,
    )
    contect = resp.json()
    assert resp.status_code == status.HTTP_406_NOT_ACCEPTABLE
    assert contect["detail"] == "Neither medication could be loaded."
