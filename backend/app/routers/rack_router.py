from app.database import get_db
from app.models.rack import RackCreate, RackRead, RackReadWithPower, RackUpdate
from app.services import rack_service
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

router = APIRouter(prefix="/racks", tags=["Racks"])


@router.get("/", response_model=list[RackRead])
def list_racks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return rack_service.get_racks(db, skip=skip, limit=limit)


@router.get("/{rack_id}", response_model=RackReadWithPower)
def get_rack(
    rack_id: int,
    db: Session = Depends(get_db),
):
    rack = rack_service.get_rack(db, rack_id)
    stats = rack_service.calculate_rack_stats(db, rack)

    return RackReadWithPower(
        **rack.model_dump(),
        **stats,
    )


@router.post("/", response_model=RackRead, status_code=status.HTTP_201_CREATED)
def create_rack(
    rack: RackCreate,
    db: Session = Depends(get_db),
):
    return rack_service.create_rack(db, rack)


@router.put("/{rack_id}", response_model=RackRead)
def update_rack(
    rack_id: int,
    rack: RackUpdate,
    db: Session = Depends(get_db),
):
    return rack_service.update_rack(db, rack_id, rack)


@router.delete("/{rack_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rack(
    rack_id: int,
    force: bool = False,
    db: Session = Depends(get_db),
):
    rack_service.delete_rack(db, rack_id, force=force)
