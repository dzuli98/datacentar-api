from sqlmodel import Field, SQLModel


class DistributionRequest(SQLModel):

    device_ids: list[int] = Field(description="List of device ids to distribute")
    rack_ids: list[int] = Field(description="List of rack ids")


class DeviceInDistribution(SQLModel):

    id: int
    name: str
    power_w: int
    units_required: int


class UnplacedDevice(SQLModel):

    device_id: int
    device_name: str
    power_w: int
    units_required: int
    reason: str


class RackDistribution(SQLModel):

    rack_id: int
    rack_name: str
    total_units: int
    max_power_w: int
    devices: list[DeviceInDistribution] = []
    used_units: int = 0
    total_power_w: int = 0
    utilization_percent: float = 0.0


class DistributionResponse(SQLModel):

    distribution: list[RackDistribution]
    unplaced_devices: list[UnplacedDevice]
    summary: dict = Field(default_factory=dict)
