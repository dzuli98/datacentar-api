from sqlmodel import Field, SQLModel


class RackPlacement(SQLModel, table=True):
    __tablename__ = "rack_placements"

    id: int | None = Field(default=None, primary_key=True)
    rack_id: int = Field(foreign_key="racks.id", index=True)
    device_id: int = Field(foreign_key="devices.id", unique=True, index=True)
    start_unit: int = Field(ge=1, description="Starting unit in rack")
    end_unit: int = Field(ge=1, description="Ending unit in rack")


class PlacementCreate(SQLModel):
    device_id: int = Field(description="Device id")
    start_unit: int = Field(ge=1, description="Starting unit in rack")


class PlacementRead(SQLModel):
    id: int
    rack_id: int
    device_id: int
    start_unit: int
    end_unit: int


class PlacementReadWithDevice(PlacementRead):
    device_name: str
    device_power_w: int
    device_units_required: int
