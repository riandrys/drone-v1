from pydantic import BaseModel, Field, constr


class MedicationBase(BaseModel):
    name: constr(regex="^[A-Za-z0-9_-]*$", strip_whitespace=True)  # noqa: F722
    weight: int = Field(gt=0)
    code: constr(regex=r"^[A-Z_\d]+$", strip_whitespace=True)  # noqa: F722


class MedicationCreate(MedicationBase):
    pass


class Medication(MedicationBase):
    id: int
    image: str | None = None

    class Config:
        orm_mode = True


class MedicationLoad(Medication):
    loads: list["Load"] = []  # noqa

    class Config:
        orm_mode = True
