from app.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.models.device import Device
from app.models.placement import PlacementCreate, RackPlacement
from app.models.rack import Rack
from sqlmodel import Session, select


def get_placements_for_rack(db: Session, rack_id: int) -> list[RackPlacement]:
    statement = select(RackPlacement).where(RackPlacement.rack_id == rack_id)
    return db.exec(statement).all()


def get_placement_by_device(db: Session, device_id: int) -> RackPlacement | None:
    statement = select(RackPlacement).where(RackPlacement.device_id == device_id)
    return db.exec(statement).first()


def get_occupied_units(db: Session, rack_id: int) -> set[int]:
    placements = get_placements_for_rack(db, rack_id)
    occupied = set()
    for p in placements:
        occupied.update(range(p.start_unit, p.end_unit + 1))
    return occupied


def get_current_power(db: Session, rack_id: int) -> int:
    statement = (
        select(Device)
        .join(RackPlacement, RackPlacement.device_id == Device.id)
        .where(RackPlacement.rack_id == rack_id)
    )
    devices = db.exec(statement).all()
    return sum(d.power_w for d in devices)


def place_device(
    db: Session, rack_id: int, placement_data: PlacementCreate
) -> RackPlacement:

    rack = db.get(Rack, rack_id)
    if not rack:
        raise NotFoundError(f"Rack with id {rack_id} not found")

    device = db.get(Device, placement_data.device_id)
    if not device:
        raise NotFoundError(f"Device with id {placement_data.device_id} not found")

    existing_placement = get_placement_by_device(db, placement_data.device_id)
    if existing_placement:
        raise ConflictError(
            f"Device '{device.name}' is already placed in rack {existing_placement.rack_id}"
        )

    start_unit = placement_data.start_unit
    end_unit = start_unit + device.units_required - 1

    if end_unit > rack.total_units:
        raise BusinessRuleError(
            f"Device '{device.name}' requires units {start_unit}-{end_unit}, "
            f"but rack '{rack.name}' only has {rack.total_units} units"
        )

    occupied = get_occupied_units(db, rack_id)
    requested_units = set(range(start_unit, end_unit + 1))
    overlap = occupied & requested_units
    if overlap:
        raise BusinessRuleError(
            f"Units {sorted(overlap)} are already occupied in rack '{rack.name}'"
        )

    current_power = get_current_power(db, rack_id)
    if current_power + device.power_w > rack.max_power_w:
        raise BusinessRuleError(
            f"Adding device '{device.name}' ({device.power_w}W) would exceed rack power capacity. "
            f"Current: {current_power}W, Max: {rack.max_power_w}W, "
            f"Available: {rack.max_power_w - current_power}W"
        )

    placement = RackPlacement(
        rack_id=rack_id,
        device_id=device.id,
        start_unit=start_unit,
        end_unit=end_unit,
    )
    db.add(placement)
    db.commit()
    db.refresh(placement)
    return placement


def remove_device_from_rack(db: Session, rack_id: int, device_id: int) -> None:
    rack = db.get(Rack, rack_id)
    if not rack:
        raise NotFoundError(f"Rack with id {rack_id} not found")

    statement = select(RackPlacement).where(
        RackPlacement.rack_id == rack_id, RackPlacement.device_id == device_id
    )
    placement = db.exec(statement).first()

    if not placement:
        raise NotFoundError(f"Device {device_id} is not placed in rack {rack_id}")

    db.delete(placement)
    db.commit()


def get_rack_devices(db: Session, rack_id: int) -> list[dict]:

    rack = db.get(Rack, rack_id)
    if not rack:
        raise NotFoundError(f"Rack with id {rack_id} not found")

    statement = (
        select(RackPlacement, Device)
        .join(Device, RackPlacement.device_id == Device.id)
        .where(RackPlacement.rack_id == rack_id)
        .order_by(RackPlacement.start_unit)
    )
    results = db.exec(statement).all()

    return [
        {
            "id": placement.id,
            "rack_id": placement.rack_id,
            "device_id": placement.device_id,
            "start_unit": placement.start_unit,
            "end_unit": placement.end_unit,
            "device_name": device.name,
            "device_power_w": device.power_w,
            "device_units_required": device.units_required,
        }
        for placement, device in results
    ]
