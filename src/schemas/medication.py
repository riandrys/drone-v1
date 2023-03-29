import re
from pydantic import BaseModel, FilePath, validator


class MedicationBase(BaseModel):
    name: str
    weight: int
    code: str

    @validator("name")
    def check_name(cls, v):
        pattern = "^[A-Za-z0-9_-]*$"
        assert re.match(pattern, v)
        return v

    @validator("code")
    def check_code(cls, v):
        pattern = r"^[A-Z_\d]+$"
        assert re.match(pattern, v)
        return v


class MedicationCreate(MedicationBase):
    image: bytes | None = None


class Medication(MedicationBase):
    id: int
    image: FilePath | None = None

    class Config:
        orm_mode = True


class MedicationLoad(Medication):
    loads: list["Load"] = []  # noqa

    class Config:
        orm_mode = True
