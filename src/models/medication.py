import re
from sqlalchemy import (
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, validates, relationship
from src.models.base_model import BaseModel
from src.models.load import Load, load_medication


class Medication(BaseModel):
    name: Mapped[str] = mapped_column(String)
    weight: Mapped[int] = mapped_column(Integer)
    _code: Mapped[str] = mapped_column("code", String)
    image: Mapped[str] = mapped_column(String, nullable=True)

    loads: Mapped[list[Load]] = relationship(
        secondary=load_medication, back_populates="medications"
    )

    @validates("name")
    def validate_name(self, key, name):
        pattern = "^[A-Za-z0-9_-]*$"
        if not re.match(pattern, name):
            raise ValueError("name field allows only letters, numbers, '-', '_'")
        return name

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, code):
        pattern = r"^[A-Z_\d]+$"
        if not re.match(pattern, code):
            raise ValueError(
                "code field allows only upper case letters, underscore and numbers"
            )
        self._code = code
