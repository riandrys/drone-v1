from datetime import datetime
from pydantic import BaseModel

from src.schemas.medication import Medication


class LoadBase(BaseModel):
    origin: str | None = None
    destination: str | None = None
    create: datetime = datetime.utcnow()
    drone_id: int


class LoadCreate(LoadBase):
    pass


class Load(LoadBase):
    id: int
    medications: list[Medication]

    class Config:
        orm_mode = True
