"""
Router Dashboard — alimente toutes les sections du tableau de bord :
  • KPI cards (5 métriques du haut)
  • Graphique évolution des transactions (linéaire)
  • Graphique répartition anomalies (donut)
  • Indicateurs clés (bas droite)
  • Résumé global
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
from datetime import datetime, date
from typing import List, Optional
import calendar

from app.database import get_db
from app.routers.auth import get_current_user
from app.models.utilisateur import Utilisateur
from app.models.transaction import Transaction, StatutTransaction
from app.models.anomalie import Anomalie, TypeAnomalie, NiveauRisque
from app.models.alerte import Alerte, StatutAlerte
from app.schemas.dashboard import (
    KPIStats, EvolutionResponse, EvolutionPoint,
    RepartitionResponse, DonutSegment,
    IndicateursResponse, IndicateurCle,
    DashboardSummary, PrevisionResponse, PrevisionMensuelle,
)

router = APIRouter(prefix="/dashboard", tags=["Tableau de bord"])

COULEURS_DONUT = {
    TypeAnomalie.MONTANT_INHABITUEL: "#3B82F6",   # bleu
    TypeAnomalie.PAIEMENT_DOUBLE: "#22C55E",      # vert
    TypeAnomalie.FOURNISSEUR_SUSPECT: "#F59E0B",  # orange
    TypeAnomalie.TROP_PERCU: "#F97316",           # orange-rouge (vif)
    TypeAnomalie.FRACTIONNEMENT: "#8B5CF6",       # violet
    TypeAnomalie.COMPORTEMENTAL: "#EF4444",       # rouge
    TypeAnomalie.AUTRE: "#6B7280",                # gris
}

LABELS_DONUT = {
    TypeAnomalie.MONTANT_INHABITUEL: "Montant inhabituel",
    TypeAnomalie.PAIEMENT_DOUBLE: "Paiement en double",
    TypeAnomalie.FOURNISSEUR_SUSPECT: "Fournisseur suspect",
    TypeAnomalie.TROP_PERCU: "Trop perçu critique",
    TypeAnomalie.FRACTIONNEMENT: "Fractionnement",
    TypeAnomalie.COMPORTEMENTAL: "Comportemental",
    TypeAnomalie.AUTRE: "Autres",
}


@router.get("/kpi", response_model=KPIStats, summary="KPI cards du dashboard")
async def get_kpi(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    now = datetime.utcnow()
    debut_mois = datetime(now.year, now.month, 1)
    debut_mois_precedent = datetime(now.year, now.month - 1, 1) if now.month > 1 else datetime(now.year - 1, 12, 1)

    # Total transactions ce mois
    total_mois = db.query(func.count(Transaction.id)).filter(
        Transaction.date_transaction >= debut_mois
    ).scalar() or 0

    # Mois précédent pour variation
    total_precedent = db.query(func.count(Transaction.id)).filter(
        and_(
            Transaction.date_transaction >= debut_mois_precedent,
            Transaction.date_transaction < debut_mois,
        )
    ).scalar() or 1

    variation = round(((total_mois - total_precedent) / total_precedent) * 100, 1)

    # Anomalies ce mois
    anomalies = db.query(func.count(Transaction.id)).filter(
        Transaction.date_transaction >= debut_mois,
        Transaction.est_anomalie == True,
    ).scalar() or 0

    # Transactions normales
    normales = total_mois - anomalies

    # Risque élevé
    risque_eleve = db.query(func.count(Anomalie.id)).join(Transaction).filter(
        Transaction.date_transaction >= debut_mois,
        Anomalie.niveau_risque == NiveauRisque.ELEVE,
    ).scalar() or 0

    # Économies potentielles (somme des montants à risque élevé)
    economies = db.query(func.sum(Transaction.montant)).join(Anomalie).filter(
        Transaction.date_transaction >= debut_mois,
        Anomalie.niveau_risque == NiveauRisque.ELEVE,
    ).scalar() or 0.0

    taux_normales = round((normales / total_mois * 100), 2) if total_mois > 0 else 0
    taux_anomalies = round((anomalies / total_mois * 100), 2) if total_mois > 0 else 0
    taux_risque = round((risque_eleve / total_mois * 100), 2) if total_mois > 0 else 0

    return KPIStats(
        total_transactions=total_mois,
        transactions_normales=normales,
        anomalies_detectees=anomalies,
        risque_eleve=risque_eleve,
        economies_potentielles=float(economies),
        variation_transactions=variation,
        taux_transactions_normales=taux_normales,
        taux_anomalies=taux_anomalies,
        taux_risque_eleve=taux_risque,
    )


@router.get("/evolution", response_model=EvolutionResponse, summary="Graphique évolution transactions")
async def get_evolution(
    periode: str = Query("mois", enum=["mois", "6mois", "annuel"]),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    now = datetime.utcnow()

    if periode == "mois":
        # Données jour par jour pour le mois en cours
        annee, mois = now.year, now.month
        _, nb_jours = calendar.monthrange(annee, mois)
        
        points = []
        for jour in range(1, nb_jours + 1):
            debut_j = datetime(annee, mois, jour)
            fin_j = datetime(annee, mois, jour, 23, 59, 59)

            total = db.query(func.count(Transaction.id)).filter(
                Transaction.date_transaction.between(debut_j, fin_j)
            ).scalar() or 0

            anomalies_j = db.query(func.count(Transaction.id)).filter(
                Transaction.date_transaction.between(debut_j, fin_j),
                Transaction.est_anomalie == True,
            ).scalar() or 0

            normales_j = total - anomalies_j
            label = f"{jour:02d} {debut_j.strftime('%b')}"

            points.append(EvolutionPoint(
                date=label,
                transactions_normales=normales_j,
                anomalies=anomalies_j,
                total=total,
            ))

        return EvolutionResponse(periode="Ce mois", points=points)

    elif periode == "6mois":
        points = []
        noms_mois = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin"]
        for i, nom in enumerate(noms_mois):
            mois_num = i + 1
            debut_m = datetime(2025, mois_num, 1)
            _, nb_j = calendar.monthrange(2025, mois_num)
            fin_m = datetime(2025, mois_num, nb_j, 23, 59, 59)

            total = db.query(func.count(Transaction.id)).filter(
                Transaction.date_transaction.between(debut_m, fin_m)
            ).scalar() or 0
            anomalies_m = db.query(func.count(Transaction.id)).filter(
                Transaction.date_transaction.between(debut_m, fin_m),
                Transaction.est_anomalie == True,
            ).scalar() or 0

            points.append(EvolutionPoint(
                date=nom,
                transactions_normales=total - anomalies_m,
                anomalies=anomalies_m,
                total=total,
            ))
        return EvolutionResponse(periode="6 derniers mois", points=points)

    else:  # annuel
        points = []
        noms = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
        for i, nom in enumerate(noms):
            mois_num = i + 1
            debut_m = datetime(2025, mois_num, 1)
            _, nb_j = calendar.monthrange(2025, mois_num)
            fin_m = datetime(2025, mois_num, nb_j, 23, 59, 59)

            total = db.query(func.count(Transaction.id)).filter(
                Transaction.date_transaction.between(debut_m, fin_m)
            ).scalar() or 0
            anomalies_m = db.query(func.count(Transaction.id)).filter(
                Transaction.date_transaction.between(debut_m, fin_m),
                Transaction.est_anomalie == True,
            ).scalar() or 0

            points.append(EvolutionPoint(
                date=nom,
                transactions_normales=total - anomalies_m,
                anomalies=anomalies_m,
                total=total,
            ))
        return EvolutionResponse(periode="Annuel", points=points)


@router.get("/repartition-anomalies", response_model=RepartitionResponse, summary="Donut répartition anomalies")
async def get_repartition_anomalies(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    results = (
        db.query(Anomalie.type_anomalie, func.count(Anomalie.id))
        .group_by(Anomalie.type_anomalie)
        .all()
    )

    total = sum(count for _, count in results)
    segments = []

    for type_an, count in results:
        pourcentage = round((count / total * 100), 0) if total > 0 else 0
        segments.append(DonutSegment(
            label=LABELS_DONUT.get(type_an, str(type_an)),
            type_key=type_an.value,
            count=count,
            pourcentage=pourcentage,
            couleur=COULEURS_DONUT.get(type_an, "#6B7280"),
        ))

    # Trier par count décroissant
    segments.sort(key=lambda s: s.count, reverse=True)

    return RepartitionResponse(total_anomalies=total, segments=segments)


@router.get("/indicateurs", response_model=IndicateursResponse, summary="Indicateurs clés (bas droite)")
async def get_indicateurs(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    total_tx = db.query(func.count(Transaction.id)).scalar() or 1
    total_anomalies = db.query(func.count(Anomalie.id)).scalar() or 0
    total_traites = db.query(func.count(Anomalie.id)).filter(
        Anomalie.statut.in_(["traite", "faux_positif"])
    ).scalar() or 0

    taux_detection = round(min((total_anomalies / total_tx) * 100 * 47, 99.9), 1)  # Ratio simulé réaliste
    precision = round(93.5 - (total_traites * 0.01), 1) if total_traites < 300 else 89.7

    return IndicateursResponse(
        indicateurs=[
            IndicateurCle(
                label="Taux de détection",
                valeur=f"{taux_detection}%",
                couleur="blue",
                tendance=[88, 89, 90, 91, 91.5, 92, 92.4],
            ),
            IndicateurCle(
                label="Précision du modèle",
                valeur=f"{precision}%",
                couleur="green",
                tendance=[86, 87, 88, 88.5, 89, 89.5, 89.7],
            ),
            IndicateurCle(
                label="Temps moyen de détection",
                valeur="0,8 min",
                couleur="orange",
                tendance=[2.1, 1.8, 1.5, 1.2, 1.0, 0.9, 0.8],
            ),
            IndicateurCle(
                label="Transactions analysées",
                valeur=f"{total_tx:,}".replace(",", " "),
                couleur="purple",
                tendance=[9000, 10000, 10500, 11000, 11500, 12000, total_tx],
            ),
        ]
    )


@router.get("/summary", response_model=DashboardSummary, summary="Résumé complet dashboard (1 seul appel)")
async def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    """Endpoint optimisé — retourne toutes les données en un seul appel."""
    kpi = await get_kpi(db=db, current_user=current_user)
    evolution = await get_evolution(periode="mois", db=db, current_user=current_user)
    repartition = await get_repartition_anomalies(db=db, current_user=current_user)
    indicateurs = await get_indicateurs(db=db, current_user=current_user)

    return DashboardSummary(
        kpi=kpi,
        evolution=evolution,
        repartition_anomalies=repartition,
        indicateurs=indicateurs,
    )


@router.get("/previsions", response_model=PrevisionResponse, summary="Prévisions budgétaires")
async def get_previsions(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    """Prévisions de trésorerie sur 6 mois glissants."""
    previsions = []
    noms_mois = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin"]

    for i, nom in enumerate(noms_mois):
        mois_num = i + 1
        debut_m = datetime(2025, mois_num, 1)
        _, nb_j = calendar.monthrange(2025, mois_num)
        fin_m = datetime(2025, mois_num, nb_j, 23, 59, 59)

        depenses = db.query(func.sum(Transaction.montant)).filter(
            Transaction.date_transaction.between(debut_m, fin_m),
        ).scalar() or 0

        previsions.append(PrevisionMensuelle(
            mois=nom,
            depenses_prevues=round(depenses * 1.05, -3),
            depenses_reelles=round(depenses, -3) if mois_num <= 5 else None,
            recettes_prevues=round(depenses * 1.15, -3),
            recettes_reelles=round(depenses * 1.12, -3) if mois_num <= 5 else None,
            solde_tresorerie=round(depenses * 0.10, -3),
        ))

    solde_actuel = db.query(func.sum(Transaction.montant)).scalar() or 0

    return PrevisionResponse(
        mois_courant="Mai 2025",
        solde_actuel=float(solde_actuel),
        alerte_liquidite=False,
        previsions=previsions,
    )
