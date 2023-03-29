import enum
from sqlalchemy import (
    CheckConstraint,
    Enum,
    Integer,
    String,
)
from sqlalchemy.orm import relationship, Mapped, validates, mapped_column
from src.models.base_model import BaseModel
from src.models.load import Load


class Status(enum.Enum):
    IDLE = "IDLE"
    LOADING = "LOADING"
    LOADED = "LOADED"
    DELIVERING = "DELIVERING"
    DELIVERED = "DELIVERED"
    RETURNING = "RETURNING"


class Models(enum.Enum):
    LIGHTWEIGHT = "LIGHTWEIGHT"
    MIDDLEWEIGHT = "MIDDLEWEIGHT"
    CRUISERWEIGHT = "CRUISERWEIGHT"
    HEAVYWEIGHT = "HEAVYWEIGHT"


class Drone(BaseModel):
    serial_number: Mapped[str] = mapped_column(String(100), unique=True)
    model: Mapped[Models] = mapped_column(Enum(Models), nullable=False)
    weight_limit: Mapped[int] = mapped_column(
        Integer, CheckConstraint("weight_limit<=500"), default=500
    )
    battery_capacity: Mapped[int] = mapped_column(
        Integer, CheckConstraint("battery_capacity<=100"), default=100
    )
    state: Mapped[Status] = mapped_column(Enum(Status), nullable=False)

    loads: Mapped[list[Load]] = relationship(back_populates="drone")

    @validates("weight_limit")
    def validate_weight_limit(self, key, weight_limit):
        if 0 > weight_limit > 500:
            raise ValueError("weight limit value must be between 0-500")
        return weight_limit

    @validates("battery_capacity")
    def validate_battery_capacity(self, key, battery_capacity):
        if 0 > battery_capacity > 100:
            raise ValueError("battery capacity value must be between 0-100")
        return battery_capacity
