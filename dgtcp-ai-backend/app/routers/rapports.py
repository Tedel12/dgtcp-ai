"""
Router Rapports — Analyse & Rapports (page dédiée du dashboard)
"""
from fastapi import APIRouter, Depends, Query, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime
from typing import Optional
import calendar
import pandas as pd
import io
from app.models.utilisateur import Utilisateur, RoleEnum
from app.models.transaction import Transaction, TypeTransaction
from app.models.anomalie import Anomalie, NiveauRisque
from app.services.pdf_generator import generer_rapport_pdf
from app.routers.dashboard import get_kpi
from app.database import get_db
from app.routers.auth import get_current_user

router = APIRouter(prefix="/rapports", tags=["Analyse & Rapports"])


@router.get("/depenses-par-ministere", summary="Dépenses totales par ministère")
async def depenses_par_ministere(
    annee: int = Query(2025),
    mois: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    if current_user.role == RoleEnum.COMPTABLE:
         raise HTTPException(status_code=403, detail="Accès réservé à la direction et aux auditeurs")
    
    query = db.query(
        Transaction.ministere,
        func.sum(Transaction.montant).label("total"),
        func.count(Transaction.id).label("nombre"),
        func.avg(Transaction.montant).label("moyenne"),
    ).filter(
        func.extract("year", Transaction.date_transaction) == annee
    )

    if mois:
        query = query.filter(func.extract("month", Transaction.date_transaction) == mois)

    results = query.group_by(Transaction.ministere).order_by(desc("total")).all()

    return [
        {
            "ministere": r.ministere,
            "total_fcfa": round(float(r.total), 2),
            "nombre_transactions": r.nombre,
            "moyenne_fcfa": round(float(r.moyenne), 2),
        }
        for r in results
    ]


@router.get("/top-fournisseurs-risque", summary="Top fournisseurs à risque")
async def top_fournisseurs_risque(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    results = (
        db.query(
            Transaction.fournisseur,
            func.count(Transaction.id).label("nb_anomalies"),
            func.sum(Transaction.montant).label("montant_total"),
            func.avg(Transaction.score_risque).label("score_moyen"),
        )
        .filter(Transaction.est_anomalie == True)
        .group_by(Transaction.fournisseur)
        .order_by(desc("score_moyen"))
        .limit(limit)
        .all()
    )

    return [
        {
            "fournisseur": r.fournisseur,
            "nb_anomalies": r.nb_anomalies,
            "montant_total_fcfa": round(float(r.montant_total), 2),
            "score_risque_moyen": round(float(r.score_moyen), 2),
        }
        for r in results
    ]


@router.get("/evolution-mensuelle", summary="Évolution mensuelle des transactions et anomalies")
async def evolution_mensuelle(
    annee: int = Query(default_factory=lambda: datetime.utcnow().year),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    noms_mois = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"]
    resultats = []

    for mois_num in range(1, 13):
        debut = datetime(annee, mois_num, 1)
        _, nb_j = calendar.monthrange(annee, mois_num)
        fin = datetime(annee, mois_num, nb_j, 23, 59, 59)

        total = db.query(func.count(Transaction.id)).filter(
            Transaction.date_transaction.between(debut, fin)
        ).scalar() or 0

        montant = db.query(func.sum(Transaction.montant)).filter(
            Transaction.date_transaction.between(debut, fin)
        ).scalar() or 0

        anomalies = db.query(func.count(Transaction.id)).filter(
            Transaction.date_transaction.between(debut, fin),
            Transaction.est_anomalie == True,
        ).scalar() or 0

        resultats.append({
            "mois": noms_mois[mois_num - 1],
            "mois_num": mois_num,
            "total_transactions": total,
            "montant_total_fcfa": round(float(montant), 2),
            "anomalies": anomalies,
            "taux_anomalie_pct": round((anomalies / total * 100), 2) if total > 0 else 0,
        })

    return resultats


@router.get("/export/transactions", summary="Exporter les transactions (Excel/CSV)")
async def export_transactions(
    format: str = Query("excel", enum=["excel", "csv"]),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    if current_user.role not in [RoleEnum.DIRECTEUR, RoleEnum.COMPTABLE, RoleEnum.CONTROLEUR_FINANCIER, RoleEnum.AUDITEUR]:
        raise HTTPException(status_code=403, detail="Non autorisé à exporter les données")

    # Récupérer toutes les transactions
    txs = db.query(Transaction).all()
    
    data = []
    for t in txs:
        data.append({
            "Référence": t.reference,
            "Ministère": t.ministere,
            "Fournisseur": t.fournisseur,
            "Montant (FCFA)": t.montant,
            "Montant Prévu (FCFA)": t.montant_prevu,
            "Dépassement": (t.montant - t.montant_prevu) if t.montant_prevu else 0,
            "Date": t.date_transaction.strftime("%d/%m/%Y"),
            "Statut": t.statut.value,
            "Score Risque (%)": t.score_risque,
            "Est Anomalie": "Oui" if t.est_anomalie else "Non"
        })
    
    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    if format == "csv":
        df.to_csv(output, index=False, encoding='utf-8-sig')
        media_type = "text/csv"
        filename = f"transactions_dgtcp_{datetime.now().strftime('%Y%m%d')}.csv"
    else:
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Transactions')
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"transactions_dgtcp_{datetime.now().strftime('%Y%m%d')}.xlsx"
    
    output.seek(0)
    return StreamingResponse(
        output, 
        media_type=media_type, 
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/rapport-executif", summary="Générer le rapport PDF Stratégique")
async def rapport_executif(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    if current_user.role not in [RoleEnum.DIRECTEUR, RoleEnum.ADMIN]:
        raise HTTPException(status_code=403, detail="Seule la direction peut générer ce rapport")

    # 1. Récupérer les stats réelles via le router dashboard
    stats = await get_kpi(db=db, current_user=current_user)
    stats_dict = stats.model_dump()

    # 2. Récupérer les 5 anomalies les plus critiques (Score max)
    top_anomalies = (
        db.query(Anomalie)
        .filter(Anomalie.statut == "non_traite")
        .order_by(desc(Anomalie.score_risque))
        .limit(5)
        .all()
    )

    # 3. Générer le PDF
    pdf_buffer = generer_rapport_pdf(stats_dict, top_anomalies)
    
    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=Rapport_Strategique_DGTCP.pdf"}
    )



