from app.database import get_db
from app.models.placement import (PlacementCreate, PlacementRead,
                                  PlacementReadWithDevice)
from app.services import placement_service
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

router = APIRouter(prefix="/racks", tags=["Rack Placements"])


@router.get("/{rack_id}/devices", response_model=list[PlacementReadWithDevice])
def list_rack_devices(
    rack_id: int,
    db: Session = Depends(get_db),
):
    return placement_service.get_rack_devices(db, rack_id)


@router.post(
    "/{rack_id}/devices",
    response_model=PlacementRead,
    status_code=status.HTTP_201_CREATED,
)
def place_device(
    rack_id: int,
    placement: PlacementCreate,
    db: Session = Depends(get_db),
):
    return placement_service.place_device(db, rack_id, placement)


@router.delete("/{rack_id}/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_device(
    rack_id: int,
    device_id: int,
    db: Session = Depends(get_db),
):
    placement_service.remove_device_from_rack(db, rack_id, device_id)
