from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base_model import BaseModel

if TYPE_CHECKING:
    from src.models.medication import Medication
    from src.models.drone import Drone


load_medication = Table(
    "load_medication",
    BaseModel.metadata,
    Column("load_id", ForeignKey("load.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "medication_id",
        ForeignKey("medication.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Load(BaseModel):
    origin: Mapped[str] = mapped_column(String(100), nullable=True)
    destination: Mapped[str] = mapped_column(String(100), nullable=True)
    create: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow())
    drone_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("drone.id", ondelete="CASCADE")
    )
    weight_loaded: Mapped[int] = mapped_column(Integer, nullable=True)

    drone: Mapped[Drone] = relationship("Drone", back_populates="loads")  # noqa: F821

    medications: Mapped[list[Medication]] = relationship(
        "Medication", secondary=load_medication, back_populates="loads"
    )
