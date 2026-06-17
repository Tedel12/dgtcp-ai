"""
Router Transactions — CRUD + filtres + analyse IA à la volée
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, and_, or_
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.routers.auth import get_current_user
from app.models.utilisateur import Utilisateur
from app.models.transaction import Transaction, StatutTransaction, TypeTransaction
from app.models.anomalie import Anomalie
from app.schemas.transaction import (
    TransactionOut, TransactionCreate, TransactionListResponse,
)
from app.services.detection import analyser_transaction, creer_anomalie_et_alerte

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=TransactionListResponse, summary="Liste des transactions avec filtres")
async def list_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    ministere: Optional[str] = Query(None),
    fournisseur: Optional[str] = Query(None),
    type_transaction: Optional[TypeTransaction] = Query(None),
    statut: Optional[StatutTransaction] = Query(None),
    est_anomalie: Optional[bool] = Query(None),
    score_min: Optional[float] = Query(None),
    date_debut: Optional[datetime] = Query(None),
    date_fin: Optional[datetime] = Query(None),
    montant_min: Optional[float] = Query(None),
    montant_max: Optional[float] = Query(None),
    tri: str = Query("date_desc", enum=["date_desc", "date_asc", "montant_desc", "montant_asc", "score_desc"]),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    query = db.query(Transaction)

    # ── Filtres ──────────────────────────────────────────────────────────────
    if ministere:
        query = query.filter(Transaction.ministere.ilike(f"%{ministere}%"))
    if fournisseur:
        query = query.filter(Transaction.fournisseur.ilike(f"%{fournisseur}%"))
    if type_transaction:
        query = query.filter(Transaction.type_transaction == type_transaction)
    if statut:
        query = query.filter(Transaction.statut == statut)
    if est_anomalie is not None:
        query = query.filter(Transaction.est_anomalie == est_anomalie)
    if score_min is not None:
        query = query.filter(Transaction.score_risque >= score_min)
    if date_debut:
        query = query.filter(Transaction.date_transaction >= date_debut)
    if date_fin:
        query = query.filter(Transaction.date_transaction <= date_fin)
    if montant_min is not None:
        query = query.filter(Transaction.montant >= montant_min)
    if montant_max is not None:
        query = query.filter(Transaction.montant <= montant_max)

    # ── Tri ──────────────────────────────────────────────────────────────────
    ordre = {
        "date_desc":    desc(Transaction.date_transaction),
        "date_asc":     asc(Transaction.date_transaction),
        "montant_desc": desc(Transaction.montant),
        "montant_asc":  asc(Transaction.montant),
        "score_desc":   desc(Transaction.score_risque),
    }
    query = query.order_by(ordre.get(tri, desc(Transaction.date_transaction)))

    total = query.count()
    transactions = query.offset((page - 1) * limit).limit(limit).all()

    return TransactionListResponse(
        total=total,
        page=page,
        limit=limit,
        transactions=transactions,
    )


@router.get("/{transaction_id}", response_model=TransactionOut, summary="Détail d'une transaction")
async def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction introuvable")
    return tx


@router.post("", response_model=TransactionOut, status_code=201, summary="Créer une transaction + analyse IA automatique")
async def create_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    """
    Crée la transaction et la soumet immédiatement au moteur de détection.
    Si une anomalie est détectée, une alerte est générée automatiquement.
    """
    # Vérifier unicité de la référence
    existing = db.query(Transaction).filter(Transaction.reference == data.reference).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Référence {data.reference} déjà existante")

    tx = Transaction(**data.model_dump())
    db.add(tx)
    db.commit()
    db.refresh(tx)

    # ── Analyse IA immédiate ──────────────────────────────────────────────
    anomalie_data = analyser_transaction(tx, db)
    if anomalie_data:
        # Compter les anomalies du jour pour la séquence
        today_str = tx.date_transaction.strftime("%Y%m%d")
        count_today = db.query(Anomalie).filter(
            Anomalie.reference.like(f"AN{today_str}-%")
        ).count()

        creer_anomalie_et_alerte(tx, anomalie_data, db, num_seq=count_today + 1)
        db.commit()
        db.refresh(tx)

    return tx


@router.patch("/{transaction_id}/statut", response_model=TransactionOut, summary="Changer le statut d'une transaction")
async def update_statut_transaction(
    transaction_id: int,
    statut: StatutTransaction,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction introuvable")
    tx.statut = statut
    db.commit()
    db.refresh(tx)
    return tx


@router.get("/{transaction_id}/anomalies", summary="Anomalies liées à une transaction")
async def get_anomalies_de_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction introuvable")
    return tx.anomalies
