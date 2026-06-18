from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.routers.auth import get_current_user
from app.models.transaction import Transaction
from app.models.anomalie import Anomalie
from app.models.utilisateur import Utilisateur, RoleEnum

router = APIRouter(prefix="/search", tags=["Recherche"])

class SearchResult(BaseModel):
    type: str # 'transaction' | 'anomalie'
    id: int
    title: str
    subtitle: str
    metadata: Optional[dict] = None

@router.get("", response_model=List[dict], summary="Recherche globale")
async def global_search(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    if current_user.role == RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="L'administrateur ne peut pas effectuer de recherches opérationnelles")
    
    """
    Recherche dans les transactions (référence, fournisseur) 
    et anomalies (référence, description).
    """
    results = []

    # 1. Recherche dans les transactions
    txs = db.query(Transaction).filter(
        or_(
            Transaction.reference.ilike(f"%{q}%"),
            Transaction.fournisseur.ilike(f"%{q}%"),
            Transaction.ministere.ilike(f"%{q}%")
        )
    ).limit(5).all()

    for t in txs:
        results.append({
            "type": "transaction",
            "id": t.id,
            "title": f"Transaction {t.reference}",
            "subtitle": f"{t.fournisseur} - {t.montant:,.0f} FCFA",
            "url": f"/transactions/{t.id}"
        })

    # 2. Recherche dans les anomalies
    anomalies = db.query(Anomalie).filter(
        or_(
            Anomalie.reference.ilike(f"%{q}%"),
            Anomalie.description.ilike(f"%{q}%")
        )
    ).limit(5).all()

    for a in anomalies:
        results.append({
            "type": "anomalie",
            "id": a.id,
            "title": f"Anomalie {a.reference}",
            "subtitle": a.type_anomalie,
            "url": f"/anomalies/{a.id}"
        })

    return results
