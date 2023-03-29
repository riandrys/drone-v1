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

    drone: Mapped["Drone"] = relationship(back_populates="loads")  # noqa: F821

    medications: Mapped[list["Medication"]] = relationship(  # noqa: F821
        secondary=load_medication, back_populates="loads"
    )
