"""Initial migration - create all tables

Revision ID: 001_initial
Revises:
Create Date: 2026-02-19

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create devices table
    op.create_table(
        "devices",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column(
            "description", sqlmodel.sql.sqltypes.AutoString(length=1000), nullable=True
        ),
        sa.Column(
            "serial_number",
            sqlmodel.sql.sqltypes.AutoString(length=100),
            nullable=False,
        ),
        sa.Column("units_required", sa.Integer(), nullable=False),
        sa.Column("power_w", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_devices_serial_number"), "devices", ["serial_number"], unique=True
    )

    # Create racks table
    op.create_table(
        "racks",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column(
            "description", sqlmodel.sql.sqltypes.AutoString(length=1000), nullable=True
        ),
        sa.Column(
            "serial_number",
            sqlmodel.sql.sqltypes.AutoString(length=100),
            nullable=False,
        ),
        sa.Column("total_units", sa.Integer(), nullable=False),
        sa.Column("max_power_w", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_racks_serial_number"), "racks", ["serial_number"], unique=True
    )

    # Create rack_placements table
    op.create_table(
        "rack_placements",
        sa.Column("rack_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("start_unit", sa.Integer(), nullable=False),
        sa.Column("end_unit", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["devices.id"],
        ),
        sa.ForeignKeyConstraint(
            ["rack_id"],
            ["racks.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_rack_placements_device_id"),
        "rack_placements",
        ["device_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_rack_placements_rack_id"), "rack_placements", ["rack_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_rack_placements_rack_id"), table_name="rack_placements")
    op.drop_index(op.f("ix_rack_placements_device_id"), table_name="rack_placements")
    op.drop_table("rack_placements")
    op.drop_index(op.f("ix_racks_serial_number"), table_name="racks")
    op.drop_table("racks")
    op.drop_index(op.f("ix_devices_serial_number"), table_name="devices")
    op.drop_table("devices")
