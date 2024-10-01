from sqlalchemy import create_engine

from unicon_backend.constants import DATABASE_URL
from unicon_backend.models.base import Base
from unicon_backend.models.contest import *  # noqa: F403
from unicon_backend.models.user import User

__all__ = ["User", "Base"]

engine = create_engine(DATABASE_URL, echo=True)
