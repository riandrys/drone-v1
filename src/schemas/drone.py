from pydantic import BaseModel, Field
from src.schemas.load import Load
from src.models.drone import Status, Models


class DroneBase(BaseModel):
    serial_number: str = Field(min_length=1, max_length=100)
    model: Models
    weight_limit: int | None = Field(gt=0, le=500, default=500)
    battery_capacity: int | None = Field(ge=0, le=100, default=100)
    state: Status


class DroneCreate(DroneBase):
    pass


class Drone(DroneBase):
    id: int

    class Config:
        orm_mode = True


class DroneLoading(Drone):
    load: Load

    class Config:
        orm_mode = True


class DroneLoads(Drone):
    loads: list[Load] = []

    class Config:
        orm_mode = True
