"""Add user table and seed admin

Revision ID: a3e28e9d0b43
Revises:
Create Date: 2024-10-01 01:55:36.446876

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import orm

from unicon_backend.dependencies import AUTH_PWD_CONTEXT
from unicon_backend.models.user import User

# revision identifiers, used by Alembic.
revision: str = "a3e28e9d0b43"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    session = orm.Session(bind=op.get_bind())
    session.add(User(username="admin", password=AUTH_PWD_CONTEXT.hash("admin")))
    session.commit()
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("user")
    # ### end Alembic commands ###
