import re
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from src.config.database import custom_metadata


class BaseModel(DeclarativeBase):
    """
    Base class to be used to create new models
    - __tablename__ attribute is generated from classname ex: 'MyModel' produce 'my_model'
    """

    metadata = custom_metadata

    @declared_attr.directive
    def __tablename__(cls):
        return re.sub("(?<!^)(?=[A-Z])", "_", cls.__name__).lower()

    id: Mapped[int] = mapped_column(primary_key=True)
