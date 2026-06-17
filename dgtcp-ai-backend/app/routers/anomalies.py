"""
Router Anomalies — liste, détail, mise à jour du statut, stats
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func
from typing import Optional

from app.database import get_db
from app.routers.auth import get_current_user
from app.models.utilisateur import Utilisateur
from app.models.anomalie import Anomalie, TypeAnomalie, NiveauRisque, StatutAnomalie
from app.models.transaction import Transaction
from app.schemas.anomalie import AnomalieOut, AnomalieUpdate, AnomalieListResponse
from datetime import datetime

router = APIRouter(prefix="/anomalies", tags=["Anomalies"])


def _enrichir(anomalie: Anomalie) -> dict:
    """Ajoute les données de la transaction à l'anomalie pour le frontend."""
    d = {c.name: getattr(anomalie, c.name) for c in anomalie.__table__.columns}
    if anomalie.transaction:
        d["montant"] = anomalie.transaction.montant
        d["ministere"] = anomalie.transaction.ministere
        d["fournisseur"] = anomalie.transaction.fournisseur
        d["reference_transaction"] = anomalie.transaction.reference
    return d


@router.get("", response_model=AnomalieListResponse, summary="Liste des anomalies avec filtres")
async def list_anomalies(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    type_anomalie: Optional[TypeAnomalie] = Query(None),
    niveau_risque: Optional[NiveauRisque] = Query(None),
    statut: Optional[StatutAnomalie] = Query(None),
    ministere: Optional[str] = Query(None),
    date_debut: Optional[datetime] = Query(None),
    date_fin: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    query = db.query(Anomalie).options(joinedload(Anomalie.transaction))

    if type_anomalie:
        query = query.filter(Anomalie.type_anomalie == type_anomalie)
    if niveau_risque:
        query = query.filter(Anomalie.niveau_risque == niveau_risque)
    if statut:
        query = query.filter(Anomalie.statut == statut)
    if ministere:
        query = query.join(Transaction).filter(Transaction.ministere.ilike(f"%{ministere}%"))
    if date_debut:
        query = query.filter(Anomalie.detected_at >= date_debut)
    if date_fin:
        query = query.filter(Anomalie.detected_at <= date_fin)

    query = query.order_by(desc(Anomalie.detected_at))
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()

    anomalies_enrichies = [AnomalieOut(**_enrichir(a)) for a in items]

    return AnomalieListResponse(total=total, page=page, limit=limit, anomalies=anomalies_enrichies)


@router.get("/stats", summary="Statistiques globales des anomalies")
async def get_stats_anomalies(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    """Résumé utilisé dans la page Détection d'anomalies."""
    par_type = (
        db.query(Anomalie.type_anomalie, func.count(Anomalie.id))
        .group_by(Anomalie.type_anomalie)
        .all()
    )
    par_niveau = (
        db.query(Anomalie.niveau_risque, func.count(Anomalie.id))
        .group_by(Anomalie.niveau_risque)
        .all()
    )
    par_statut = (
        db.query(Anomalie.statut, func.count(Anomalie.id))
        .group_by(Anomalie.statut)
        .all()
    )
    score_moyen = db.query(func.avg(Anomalie.score_risque)).scalar() or 0

    return {
        "total": db.query(func.count(Anomalie.id)).scalar(),
        "score_moyen": round(float(score_moyen), 2),
        "par_type": {t.value: c for t, c in par_type},
        "par_niveau": {n.value: c for n, c in par_niveau},
        "par_statut": {s.value: c for s, c in par_statut},
    }


@router.get("/{anomalie_id}", response_model=AnomalieOut, summary="Détail d'une anomalie")
async def get_anomalie(
    anomalie_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    anomalie = (
        db.query(Anomalie)
        .options(joinedload(Anomalie.transaction))
        .filter(Anomalie.id == anomalie_id)
        .first()
    )
    if not anomalie:
        raise HTTPException(status_code=404, detail="Anomalie introuvable")
    return AnomalieOut(**_enrichir(anomalie))


@router.patch("/{anomalie_id}", response_model=AnomalieOut, summary="Mettre à jour le statut d'une anomalie")
async def update_anomalie(
    anomalie_id: int,
    data: AnomalieUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    anomalie = (
        db.query(Anomalie)
        .options(joinedload(Anomalie.transaction))
        .filter(Anomalie.id == anomalie_id)
        .first()
    )
    if not anomalie:
        raise HTTPException(status_code=404, detail="Anomalie introuvable")

    anomalie.statut = data.statut
    if data.note_traitement:
        anomalie.note_traitement = data.note_traitement
    anomalie.traitee_par = current_user.id
    anomalie.date_traitement = datetime.utcnow()

    db.commit()
    db.refresh(anomalie)
    return AnomalieOut(**_enrichir(anomalie))
