from sqlmodel import Field, SQLModel


class DeviceBase(SQLModel):
    name: str = Field(min_length=1, max_length=255, description="Device name")
    description: str | None = Field(
        default=None, max_length=1000, description="Device description"
    )
    serial_number: str = Field(
        min_length=1,
        max_length=100,
        unique=True,
        index=True,
        description="Serial number",
    )
    units_required: int = Field(ge=1, description="Number of units in rack")
    power_w: int = Field(gt=0, description="Power consumption in Watts")


class Device(DeviceBase, table=True):
    __tablename__ = "devices"
    id: int | None = Field(default=None, primary_key=True)


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    serial_number: str | None = Field(default=None, min_length=1, max_length=100)
    units_required: int | None = Field(default=None, ge=1)
    power_w: int | None = Field(default=None, gt=0)


class DeviceRead(DeviceBase):
    id: int
