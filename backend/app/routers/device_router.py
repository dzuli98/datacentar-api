from app.database import get_db
from app.models.device import DeviceCreate, DeviceRead, DeviceUpdate
from app.services import device_service
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.get("/", response_model=list[DeviceRead])
def list_devices(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return device_service.get_devices(db, skip=skip, limit=limit)


@router.get("/{device_id}", response_model=DeviceRead)
def get_device(
    device_id: int,
    db: Session = Depends(get_db),
):
    return device_service.get_device(db, device_id)


@router.post("/", response_model=DeviceRead, status_code=status.HTTP_201_CREATED)
def create_device(
    device: DeviceCreate,
    db: Session = Depends(get_db),
):
    return device_service.create_device(db, device)


@router.put("/{device_id}", response_model=DeviceRead)
def update_device(
    device_id: int,
    device: DeviceUpdate,
    db: Session = Depends(get_db),
):
    return device_service.update_device(db, device_id, device)


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(
    device_id: int,
    db: Session = Depends(get_db),
):
    device_service.delete_device(db, device_id)
