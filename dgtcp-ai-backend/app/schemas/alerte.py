from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.alerte import NiveauAlerte, StatutAlerte


class AlerteOut(BaseModel):
    id: int
    anomalie_id: int
    titre: str
    message: str
    niveau: NiveauAlerte
    montant_concerne: Optional[float] = None
    entite_concernee: Optional[str] = None
    statut: StatutAlerte
    est_lue: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AlerteUpdate(BaseModel):
    statut: Optional[StatutAlerte] = None
    est_lue: Optional[bool] = None


class AlerteListResponse(BaseModel):
    total: int
    non_lues: int
    alertes: List[AlerteOut]
