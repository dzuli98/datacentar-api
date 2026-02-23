from app.exceptions import ConflictError, NotFoundError
from app.models.device import Device, DeviceCreate, DeviceUpdate
from app.models.placement import RackPlacement
from sqlmodel import Session, select


def get_devices(db: Session, skip: int = 0, limit: int = 100) -> list[Device]:
    statement = select(Device).offset(skip).limit(limit)
    return db.exec(statement).all()


def get_device(db: Session, device_id: int) -> Device:
    device = db.get(Device, device_id)
    if not device:
        raise NotFoundError(f"Device with id {device_id} not found")
    return device


def get_device_by_serial(db: Session, serial_number: str) -> Device | None:
    statement = select(Device).where(Device.serial_number == serial_number)
    return db.exec(statement).first()


def create_device(db: Session, device_data: DeviceCreate) -> Device:
    existing = get_device_by_serial(db, device_data.serial_number)
    if existing:
        raise ConflictError(
            f"Device with serial number '{device_data.serial_number}' already exists"
        )

    device = Device.model_validate(device_data)
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def update_device(db: Session, device_id: int, device_data: DeviceUpdate) -> Device:
    device = get_device(db, device_id)

    if device_data.serial_number and device_data.serial_number != device.serial_number:
        existing = get_device_by_serial(db, device_data.serial_number)
        if existing:
            raise ConflictError(
                f"Device with serial number '{device_data.serial_number}' already exists"
            )

    update_data = device_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(device, key, value)

    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def delete_device(db: Session, device_id: int) -> None:
    device = get_device(db, device_id)

    statement = select(RackPlacement).where(RackPlacement.device_id == device_id)
    placement = db.exec(statement).first()
    if placement:
        db.delete(placement)

    db.delete(device)
    db.commit()
