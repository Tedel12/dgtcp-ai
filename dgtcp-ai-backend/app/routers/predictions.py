"""
Router Prévisions budgétaires — page Prévisions du dashboard
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
import calendar
from typing import Optional

from app.database import get_db
from app.routers.auth import get_current_user
from app.models.utilisateur import Utilisateur
from app.models.transaction import Transaction

router = APIRouter(prefix="/predictions", tags=["Prévisions budgétaires"])


@router.get("/tresorerie", summary="Prévisions de trésorerie sur 6 mois")
async def previsions_tresorerie(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    now = datetime.utcnow()
    year = now.year

    resultats = []
    for i in range(6):
        month_offset = i
        mois_num = (now.month - 1 + month_offset) % 12 + 1
        annee = year + ((now.month - 1 + month_offset) // 12)
        
        debut = datetime(annee, mois_num, 1)
        _, nb_j = calendar.monthrange(annee, mois_num)
        fin = datetime(annee, mois_num, nb_j, 23, 59, 59)

        depenses_reelles = db.query(func.sum(Transaction.montant)).filter(
            Transaction.date_transaction.between(debut, fin)
        ).scalar() or 0

        # Projection
        est_passe = datetime(annee, mois_num, 1) < datetime(now.year, now.month, 1)
        depenses_prevues = depenses_reelles * 1.05 if est_passe else depenses_reelles * 1.08
        if depenses_reelles == 0: depenses_prevues = 100_000_000 # Default si pas de donnée
        
        recettes_prevues = depenses_prevues * 1.15
        recettes_reelles = depenses_reelles * 1.12 if est_passe else None

        resultats.append({
            "mois": debut.strftime("%B"),
            "mois_num": mois_num,
            "depenses_prevues": round(depenses_prevues, -3),
            "depenses_reelles": round(float(depenses_reelles), -3) if est_passe else None,
            "recettes_prevues": round(recettes_prevues, -3),
            "recettes_reelles": round(float(recettes_reelles), -3) if recettes_reelles else None,
            "solde_previsionnel": round(recettes_prevues - depenses_prevues, -3),
            "ecart_pct": round(
                ((float(depenses_reelles) - depenses_prevues) / depenses_prevues * 100), 1
            ) if est_passe and depenses_prevues > 0 else None,
        })

    solde_actuel = db.query(func.sum(Transaction.montant)).scalar() or 0
    return {
        "solde_actuel_fcfa": round(float(solde_actuel), 2),
        "alerte_liquidite": False,
        "mois_courant": "Mai 2025",
        "previsions": resultats,
    }


@router.get("/risques-budgetaires", summary="Risques budgétaires par ministère")
async def risques_budgetaires(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    """Identifie les ministères avec des dépenses dépassant le budget prévu."""
    results = db.query(
        Transaction.ministere,
        func.sum(Transaction.montant).label("depenses_reelles"),
        func.sum(Transaction.montant_prevu).label("budget_prevu"),
        func.count(Transaction.id).label("nb_transactions"),
    ).filter(
        Transaction.montant_prevu.isnot(None)
    ).group_by(Transaction.ministere).all()

    risques = []
    for r in results:
        if r.budget_prevu and r.budget_prevu > 0:
            ecart = float(r.depenses_reelles) - float(r.budget_prevu)
            taux_execution = round((float(r.depenses_reelles) / float(r.budget_prevu)) * 100, 1)
            risques.append({
                "ministere": r.ministere,
                "depenses_reelles_fcfa": round(float(r.depenses_reelles), 2),
                "budget_prevu_fcfa": round(float(r.budget_prevu), 2),
                "ecart_fcfa": round(ecart, 2),
                "taux_execution_pct": taux_execution,
                "niveau_risque": "eleve" if taux_execution > 110 else "moyen" if taux_execution > 100 else "faible",
                "nb_transactions": r.nb_transactions,
            })

    risques.sort(key=lambda x: x["taux_execution_pct"], reverse=True)
    return risques
