from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from unicon_backend.models.links import UserRole

if TYPE_CHECKING:
    from .organisation import Role


class UserORM(SQLModel, table=True):
    __tablename__ = "user"

    id: int = Field(primary_key=True)
    username: str
    password: str

    roles: list["Role"] = Relationship(back_populates="users", link_model=UserRole)
