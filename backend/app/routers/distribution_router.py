from app.database import get_db
from app.models.distribution import DistributionRequest, DistributionResponse
from app.services import distribution_service
from fastapi import APIRouter, Depends
from sqlmodel import Session

router = APIRouter(prefix="/distribution", tags=["Distribution"])


@router.post("/calculate", response_model=DistributionResponse)
def calculate_distribution(
    request: DistributionRequest,
    db: Session = Depends(get_db),
):
    return distribution_service.calculate_distribution(db, request)
