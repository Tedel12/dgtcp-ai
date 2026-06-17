from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.anomalie import TypeAnomalie, NiveauRisque, StatutAnomalie


class AnomalieOut(BaseModel):
    id: int
    reference: str
    transaction_id: int
    type_anomalie: TypeAnomalie
    niveau_risque: NiveauRisque
    score_risque: float
    description: str
    details_techniques: Optional[str] = None
    recommandation: Optional[str] = None
    statut: StatutAnomalie
    detected_at: datetime
    # Données de la transaction embarquées
    montant: Optional[float] = None
    ministere: Optional[str] = None
    fournisseur: Optional[str] = None
    reference_transaction: Optional[str] = None

    model_config = {"from_attributes": True}


class AnomalieUpdate(BaseModel):
    statut: StatutAnomalie
    note_traitement: Optional[str] = None


class AnomalieListResponse(BaseModel):
    total: int
    page: int
    limit: int
    anomalies: List[AnomalieOut]


class RepartitionAnomalie(BaseModel):
    """Pour le graphique donut du dashboard."""
    type_anomalie: str
    label: str
    count: int
    pourcentage: float
