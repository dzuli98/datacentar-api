from app.exceptions import NotFoundError
from app.models.device import Device
from app.models.distribution import (DeviceInDistribution, DistributionRequest,
                                     DistributionResponse, RackDistribution,
                                     UnplacedDevice)
from app.models.rack import Rack
from sqlmodel import Session


def calculate_distribution(
    db: Session, request: DistributionRequest
) -> DistributionResponse:
    """
    Algorithm for balanced distribution of devices across racks.

    1. Sort devices in descending order by powerW (largest first)
    2. For each device:
         - Find the rack with the lowest current utilization
         - Check if the device fits (units + power)
         - If it fits → assign it; if not → try the next one
         - If it doesn't fit anywhere → unplacedDevices
    """

    # 1. Create list of Device objects from device_ids
    devices: list[Device] = []
    for device_id in request.device_ids:
        device = db.get(Device, device_id)
        if not device:
            raise NotFoundError(f"Device with id {device_id} not found")
        devices.append(device)

    # 2. Create list of Rack objects from rack_ids
    racks: list[Rack] = []
    for rack_id in request.rack_ids:
        rack = db.get(Rack, rack_id)
        if not rack:
            raise NotFoundError(f"Rack with id {rack_id} not found")
        racks.append(rack)

    # 3. Sort devices by powerW descending
    devices_sorted = sorted(devices, key=lambda d: d.power_w, reverse=True)

    # 4. Initialize distribution state for each rack
    rack_state: dict[int, RackDistribution] = {}
    for rack in racks:
        rack_state[rack.id] = RackDistribution(
            rack_id=rack.id,
            rack_name=rack.name,
            total_units=rack.total_units,
            max_power_w=rack.max_power_w,
            devices=[],
            used_units=0,
            total_power_w=0,
            utilization_percent=0.0,
        )

    unplaced: list[UnplacedDevice] = []

    # 5. Place devices one by one
    for device in devices_sorted:
        placed = False

        # Sort racks by current utilization (ascending)
        sorted_racks = sorted(rack_state.values(), key=lambda r: r.utilization_percent)

        for rack_dist in sorted_racks:
            # Check units
            if rack_dist.used_units + device.units_required > rack_dist.total_units:
                continue

            # Check power
            if rack_dist.total_power_w + device.power_w > rack_dist.max_power_w:
                continue

            # Place device in this rack
            rack_dist.devices.append(
                DeviceInDistribution(
                    id=device.id,
                    name=device.name,
                    power_w=device.power_w,
                    units_required=device.units_required,
                )
            )
            rack_dist.used_units += device.units_required
            rack_dist.total_power_w += device.power_w
            rack_dist.utilization_percent = (
                round((rack_dist.total_power_w / rack_dist.max_power_w) * 100, 2)
                if rack_dist.max_power_w > 0
                else 0.0
            )

            placed = True
            break

        if not placed:
            # Determine reason for unplaced device
            reason = _determine_unplaced_reason(device, list(rack_state.values()))
            unplaced.append(
                UnplacedDevice(
                    device_id=device.id,
                    device_name=device.name,
                    power_w=device.power_w,
                    units_required=device.units_required,
                    reason=reason,
                )
            )

    # 6. Create summary statistics
    distribution = list(rack_state.values())
    total_devices = len(devices)
    placed_devices = total_devices - len(unplaced)

    utilizations = [r.utilization_percent for r in distribution if r.devices]
    avg_utilization = (
        round(sum(utilizations) / len(utilizations), 2) if utilizations else 0.0
    )
    max_utilization = max(utilizations) if utilizations else 0.0
    min_utilization = min(utilizations) if utilizations else 0.0

    summary = {
        "total_devices": total_devices,
        "placed_devices": placed_devices,
        "unplaced_devices": len(unplaced),
        "total_racks": len(racks),
        "average_utilization_percent": avg_utilization,
        "max_utilization_percent": max_utilization,
        "min_utilization_percent": min_utilization,
        "utilization_spread": round(max_utilization - min_utilization, 2),
    }

    return DistributionResponse(
        distribution=distribution,
        unplaced_devices=unplaced,
        summary=summary,
    )


def _determine_unplaced_reason(device: Device, racks: list[RackDistribution]) -> str:
    if not racks:
        return "No racks available"

    has_units = any(
        r.total_units - r.used_units >= device.units_required for r in racks
    )

    has_power = any(r.max_power_w - r.total_power_w >= device.power_w for r in racks)

    if not has_units and not has_power:
        return "No rack has enough units or power capacity"
    elif not has_units:
        return f"No rack has {device.units_required} free units"
    elif not has_power:
        return f"No rack has {device.power_w}W available power"
    else:
        return "No rack has both enough units and power capacity"
