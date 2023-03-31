from datetime import datetime
from pydantic import BaseModel

from src.schemas.medication import Medication


class LoadBase(BaseModel):
    origin: str | None = None
    destination: str | None = None
    create: datetime = datetime.utcnow()


class LoadCreate(LoadBase):
    medications: list[int]


class Load(LoadBase):
    id: int
    drone_id: int
    weight_loaded: int
    medications: list[Medication]

    class Config:
        orm_mode = True
