import os
import aiofiles
from httpx import AsyncClient
import pytest
from fastapi import status
from src.config.files import BASEDIR
from src.schemas.medication import MedicationCreate
from src.services import create_medication, get_medications
from sqlalchemy.ext.asyncio import AsyncSession
from tests.utils.utils import (
    generate_random_alphanum,
    random_number,
    random_upper_string,
)


@pytest.mark.asyncio
async def test_create_medication(client: AsyncClient) -> None:
    async with aiofiles.open(
        os.path.join(BASEDIR, "tests/api/images/Aspirin.jpeg"), mode="rb"
    ) as f:
        image = await f.read()
    data = {
        "name": generate_random_alphanum(15),
        "weight": random_number(50),
        "code": random_upper_string(5),
    }

    resp = await client.post(
        "/medications/", data=data, files={"image": ("filename.png", image)}
    )
    resp_json = resp.json()
    assert resp.status_code == status.HTTP_200_OK
    assert "id" in resp_json


@pytest.mark.asyncio
async def test_create_medication_with_out_image(client: AsyncClient) -> None:
    data = {
        "name": generate_random_alphanum(15),
        "weight": random_number(50),
        "code": random_upper_string(5),
    }

    resp = await client.post(
        "/medications/",
        data=data,
    )
    resp_json = resp.json()
    assert resp.status_code == status.HTTP_200_OK
    assert "id" in resp_json


@pytest.mark.asyncio
async def test_get_medication(client: AsyncClient, session: AsyncSession) -> None:
    medication = MedicationCreate(
        name=generate_random_alphanum(10),
        weight=random_number(100),
        code=random_upper_string(10),
    )
    await create_medication(session, medication)
    resp = await client.get(
        "/medications/1",
    )
    resp_json = resp.json()
    assert resp.status_code == status.HTTP_200_OK
    assert "id" in resp_json
    assert resp_json["code"] == medication.code


@pytest.mark.asyncio
async def test_get_medication_incorrect_id(client: AsyncClient) -> None:
    resp = await client.get(
        "/medications/3",
    )
    resp_json = resp.json()
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp_json["detail"] == "Don't exist any Medication with id 3"


@pytest.mark.asyncio
async def test_get_list_medications(client: AsyncClient, session: AsyncSession) -> None:
    for i in range(3):
        medication = MedicationCreate(
            name=generate_random_alphanum(10),
            weight=random_number(100),
            code=random_upper_string(10),
        )
        await create_medication(session, medication)
    medications = await get_medications(session)
    resp = await client.get(
        "/medications/",
    )
    resp_json = resp.json()
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp_json) == len(medications)
