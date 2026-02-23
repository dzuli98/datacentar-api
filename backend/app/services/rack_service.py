from app.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.models.placement import RackPlacement
from app.models.rack import Rack, RackCreate, RackUpdate
from sqlmodel import Session, select


def get_racks(db: Session, skip: int = 0, limit: int = 100) -> list[Rack]:
    statement = select(Rack).offset(skip).limit(limit)
    return db.exec(statement).all()


def get_rack(db: Session, rack_id: int) -> Rack:
    rack = db.get(Rack, rack_id)
    if not rack:
        raise NotFoundError(f"Rack with id {rack_id} not found")
    return rack


def get_rack_by_serial(db: Session, serial_number: str) -> Rack | None:
    statement = select(Rack).where(Rack.serial_number == serial_number)
    return db.exec(statement).first()


def create_rack(db: Session, rack_data: RackCreate) -> Rack:
    existing = get_rack_by_serial(db, rack_data.serial_number)
    if existing:
        raise ConflictError(
            f"Rack with serial number '{rack_data.serial_number}' already exists"
        )

    rack = Rack.model_validate(rack_data)
    db.add(rack)
    db.commit()
    db.refresh(rack)
    return rack


def update_rack(db: Session, rack_id: int, rack_data: RackUpdate) -> Rack:
    rack = get_rack(db, rack_id)

    if rack_data.serial_number and rack_data.serial_number != rack.serial_number:
        existing = get_rack_by_serial(db, rack_data.serial_number)
        if existing:
            raise ConflictError(
                f"Rack with serial number '{rack_data.serial_number}' already exists"
            )

    update_data = rack_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(rack, key, value)

    db.add(rack)
    db.commit()
    db.refresh(rack)
    return rack


def delete_rack(db: Session, rack_id: int, force: bool = False) -> None:
    rack = get_rack(db, rack_id)

    statement = select(RackPlacement).where(RackPlacement.rack_id == rack_id)
    placements = db.exec(statement).all()

    if placements:
        if not force:
            device_count = len(placements)
            raise BusinessRuleError(
                f"Cannot delete rack '{rack.name}' - it contains {device_count} device(s). "
                f"Remove devices first or use force=true to delete anyway."
            )
        for placement in placements:
            db.delete(placement)

    db.delete(rack)
    db.commit()


def calculate_rack_stats(db: Session, rack: Rack) -> dict:
    from app.models.device import Device
    from app.models.placement import RackPlacement

    statement = (
        select(Device)
        .join(RackPlacement, RackPlacement.device_id == Device.id)
        .where(RackPlacement.rack_id == rack.id)
    )
    devices = db.exec(statement).all()

    current_power_w = sum(d.power_w for d in devices)
    used_units = sum(d.units_required for d in devices)

    return {
        "current_power_w": current_power_w,
        "used_units": used_units,
        "available_units": rack.total_units - used_units,
        "power_utilization_percent": (
            round((current_power_w / rack.max_power_w) * 100, 2)
            if rack.max_power_w > 0
            else 0.0
        ),
    }
