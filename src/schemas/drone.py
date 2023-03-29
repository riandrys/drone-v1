from pydantic import BaseModel, validator
from src.models.drone import Status, Models
from src.schemas.load import Load


class DroneBase(BaseModel):
    serial_number: str
    model: Models
    weight_limit: int | None = 500
    battery_capacity: int | None = 100
    state: Status

    @validator("weight_limit")
    def check_weight_limit(cls, v):
        assert 0 < v <= 500
        return v

    @validator("battery_capacity")
    def check_battery_capacity(cls, v):
        assert 0 < v <= 100
        return v


class DroneCreate(DroneBase):
    pass


class Drone(DroneBase):
    id: int

    class Config:
        orm_mode = True


class DroneLoading(Drone):
    loads: list[Load] = []

    class Config:
        orm_mode = True
