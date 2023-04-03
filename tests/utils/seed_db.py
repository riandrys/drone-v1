import asyncio
from sqlalchemy import insert
from src.models.medication import Medication
from src.config.database import get_async_session
from src.models.drone import Status, Models, Drone
from .utils import generate_random_alphanum, random_upper_string, random_number
from src.config.database import custom_metadata, async_engine


drones = [
    {
        "serial_number": generate_random_alphanum(10),
        "model": Models.LIGHTWEIGHT.value,
        "weight_limit": 500,
        "battery_capacity": random_number(30, 100),
        "state": Status.IDLE,
    },
    {
        "serial_number": generate_random_alphanum(9),
        "model": Models.HEAVYWEIGHT.value,
        "weight_limit": 300,
        "battery_capacity": random_number(30, 100),
        "state": Status.IDLE,
    },
    {
        "serial_number": generate_random_alphanum(15),
        "model": Models.HEAVYWEIGHT.value,
        "weight_limit": 35,
        "battery_capacity": random_number(30, 100),
        "state": Status.IDLE,
    },
    {
        "serial_number": generate_random_alphanum(11),
        "model": Models.HEAVYWEIGHT.value,
        "weight_limit": random_number(500),
        "battery_capacity": random_number(50),
        "state": Status.LOADED,
    },
    {
        "serial_number": generate_random_alphanum(12),
        "model": Models.HEAVYWEIGHT.value,
        "weight_limit": random_number(500),
        "battery_capacity": random_number(50),
        "state": Status.LOADED,
    },
]

medications = [
    {
        "code": random_upper_string(10),
        "name": generate_random_alphanum(10),
        "weight": 50,
    },
    {
        "code": random_upper_string(9),
        "name": generate_random_alphanum(10),
        "weight": 20,
    },
    {
        "code": random_upper_string(11),
        "name": generate_random_alphanum(10),
        "weight": 30,
    },
    {
        "code": random_upper_string(8),
        "name": generate_random_alphanum(10),
        "weight": 100,
    },
    {
        "code": random_upper_string(7),
        "name": generate_random_alphanum(10),
        "weight": 15,
    },
]


async def seed_db():
    async for session in get_async_session():
        async with async_engine.begin() as conn:
            await conn.run_sync(custom_metadata.create_all)
        await session.execute(insert(Drone).values(drones))
        await session.execute(insert(Medication).values(medications))
        await session.commit()


loop = asyncio.get_event_loop()
loop.run_until_complete(seed_db())
