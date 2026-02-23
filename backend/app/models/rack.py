from sqlmodel import Field, SQLModel


class RackBase(SQLModel):
    name: str = Field(min_length=1, max_length=255, description="Rack name")
    description: str | None = Field(
        default=None, max_length=1000, description="Rack description"
    )
    serial_number: str = Field(
        min_length=1,
        max_length=100,
        unique=True,
        index=True,
        description="Serial number (unique)",
    )
    total_units: int = Field(gt=0, description="Total number of units (e.g., 42U, 48U)")
    max_power_w: int = Field(
        ge=5000, description="Maximum declared power consumption in Watts (min 5000W)"
    )


class Rack(RackBase, table=True):
    __tablename__ = "racks"

    id: int | None = Field(default=None, primary_key=True)


class RackCreate(RackBase):
    pass


class RackUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    serial_number: str | None = Field(default=None, min_length=1, max_length=100)
    total_units: int | None = Field(default=None, gt=0)
    max_power_w: int | None = Field(default=None, ge=5000)


class RackRead(RackBase):
    id: int


class RackReadWithPower(RackRead):
    current_power_w: int = Field(
        default=0, description="Current total power consumption of devices in rack"
    )
    used_units: int = Field(default=0, description="Number of used units")
    available_units: int = Field(default=0, description="Number of available units")
    power_utilization_percent: float = Field(
        default=0.0, description="Power utilization percentage"
    )
