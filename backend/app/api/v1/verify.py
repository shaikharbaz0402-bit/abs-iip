from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.report import VerificationResponse
from app.services.reporting import verify_report_token

router = APIRouter(prefix="/verify", tags=["verify"])


@router.get("/{token}", response_model=VerificationResponse)
def verify(token: str, db: Session = Depends(get_db)) -> VerificationResponse:
    return VerificationResponse(**verify_report_token(db, token))
