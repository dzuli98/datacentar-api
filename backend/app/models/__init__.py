# Models package
# Import all models to register them with SQLModel metadata
from app.models.device import (Device, DeviceBase, DeviceCreate, DeviceRead,
                               DeviceUpdate)
from app.models.distribution import (DeviceInDistribution, DistributionRequest,
                                     DistributionResponse, RackDistribution,
                                     UnplacedDevice)
from app.models.placement import (PlacementCreate, PlacementRead,
                                  PlacementReadWithDevice, RackPlacement)
from app.models.rack import (Rack, RackBase, RackCreate, RackRead,
                             RackReadWithPower, RackUpdate)
from sqlmodel import SQLModel

__all__ = [
    "SQLModel",
    # Device models
    "Device",
    "DeviceBase",
    "DeviceCreate",
    "DeviceUpdate",
    "DeviceRead",
    # Rack models
    "Rack",
    "RackBase",
    "RackCreate",
    "RackUpdate",
    "RackRead",
    "RackReadWithPower",
    # Placement models
    "RackPlacement",
    "PlacementCreate",
    "PlacementRead",
    "PlacementReadWithDevice",
    # Distribution models
    "DistributionRequest",
    "DeviceInDistribution",
    "UnplacedDevice",
    "RackDistribution",
    "DistributionResponse",
]
