from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.transaction import StatutTransaction, TypeTransaction


class TransactionBase(BaseModel):
    reference: str
    ministere: str
    fournisseur: str
    code_fournisseur: Optional[str] = None
    montant: float
    montant_prevu: Optional[float] = None
    type_transaction: TypeTransaction = TypeTransaction.DEPENSE
    categorie: Optional[str] = None
    ligne_budgetaire: Optional[str] = None
    description: Optional[str] = None
    date_transaction: datetime
    date_echeance: Optional[datetime] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionOut(TransactionBase):
    id: int
    statut: StatutTransaction
    est_anomalie: bool
    score_risque: float
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionListResponse(BaseModel):
    total: int
    page: int
    limit: int
    transactions: List[TransactionOut]


class TransactionFilters(BaseModel):
    ministere: Optional[str] = None
    type_transaction: Optional[TypeTransaction] = None
    statut: Optional[StatutTransaction] = None
    est_anomalie: Optional[bool] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    montant_min: Optional[float] = None
    montant_max: Optional[float] = None
