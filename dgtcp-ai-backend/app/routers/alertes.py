"""
Router Alertes — sidebar du dashboard + gestion des notifications
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional

from app.database import get_db
from app.routers.auth import get_current_user
from app.models.utilisateur import Utilisateur
from app.models.alerte import Alerte, NiveauAlerte, StatutAlerte
from app.schemas.alerte import AlerteOut, AlerteUpdate, AlerteListResponse
from app.services.alertes import (
    get_alertes_recentes, compter_alertes_non_lues,
    marquer_comme_lue, marquer_toutes_lues,
)

router = APIRouter(prefix="/alertes", tags=["Alertes"])


@router.get("", response_model=AlerteListResponse, summary="Liste des alertes")
async def list_alertes(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    niveau: Optional[NiveauAlerte] = Query(None),
    statut: Optional[StatutAlerte] = Query(None),
    non_lues_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    if current_user.role == RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="L'administrateur n'a pas accès au flux d'alertes opérationnelles")
    
    query = db.query(Alerte)

    if niveau:
        query = query.filter(Alerte.niveau == niveau)
    if statut:
        query = query.filter(Alerte.statut == statut)
    if non_lues_only:
        query = query.filter(Alerte.est_lue == False)

    query = query.order_by(desc(Alerte.created_at))
    total = query.count()
    non_lues = compter_alertes_non_lues(db)
    items = query.offset((page - 1) * limit).limit(limit).all()

    return AlerteListResponse(total=total, non_lues=non_lues, alertes=items)


@router.get("/recentes", summary="Alertes récentes pour la sidebar du dashboard")
async def get_recentes(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    """Retourne les N alertes les plus récentes + le count non lues (badge cloche)."""
    alertes = get_alertes_recentes(db, limit=limit)
    non_lues = compter_alertes_non_lues(db)
    return {
        "non_lues": non_lues,
        "alertes": [AlerteOut.model_validate(a) for a in alertes],
    }


@router.patch("/{alerte_id}/lire", response_model=AlerteOut, summary="Marquer une alerte comme lue")
async def lire_alerte(
    alerte_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    alerte = marquer_comme_lue(alerte_id, db)
    if not alerte:
        raise HTTPException(status_code=404, detail="Alerte introuvable")
    return alerte


@router.post("/lire-toutes", summary="Marquer toutes les alertes comme lues")
async def lire_toutes(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    count = marquer_toutes_lues(db)
    return {"message": f"{count} alerte(s) marquée(s) comme lues"}


@router.patch("/{alerte_id}", response_model=AlerteOut, summary="Mettre à jour le statut d'une alerte")
async def update_alerte(
    alerte_id: int,
    data: AlerteUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    alerte = db.query(Alerte).filter(Alerte.id == alerte_id).first()
    if not alerte:
        raise HTTPException(status_code=404, detail="Alerte introuvable")

    if data.statut is not None:
        alerte.statut = data.statut
    if data.est_lue is not None:
        alerte.est_lue = data.est_lue

    db.commit()
    db.refresh(alerte)
    return alerte
