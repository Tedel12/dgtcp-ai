from pydantic import BaseModel
from typing import List, Optional
from datetime import date


# ── KPI Cards ────────────────────────────────────────────────────────────────

class KPIStats(BaseModel):
    """5 cartes KPI du haut du dashboard."""
    total_transactions: int
    transactions_normales: int
    anomalies_detectees: int
    risque_eleve: int
    economies_potentielles: float          # FCFA
    variation_transactions: float          # % vs mois précédent
    taux_transactions_normales: float      # %
    taux_anomalies: float                  # %
    taux_risque_eleve: float               # %


# ── Graphique évolution transactions ─────────────────────────────────────────

class EvolutionPoint(BaseModel):
    """Un point sur le graphique linéaire."""
    date: str                              # "01 Mai", "06 Mai"...
    transactions_normales: int
    anomalies: int
    total: int


class EvolutionResponse(BaseModel):
    periode: str                           # "Ce mois", "6 mois", "Annuel"
    points: List[EvolutionPoint]


# ── Graphique donut répartition anomalies ────────────────────────────────────

class DonutSegment(BaseModel):
    label: str                             # "Montant inhabituel"
    type_key: str                          # clé interne
    count: int
    pourcentage: float
    couleur: str                           # hex color pour le frontend


class RepartitionResponse(BaseModel):
    total_anomalies: int
    segments: List[DonutSegment]


# ── Indicateurs clés (bas droite) ────────────────────────────────────────────

class IndicateurCle(BaseModel):
    label: str
    valeur: str                            # "92,4%", "89,7%", "0,8 min"
    couleur: str                           # "blue", "green", "orange", "purple"
    tendance: List[float]                  # sparkline data


class IndicateursResponse(BaseModel):
    indicateurs: List[IndicateurCle]


# ── Prévisions budgétaires ────────────────────────────────────────────────────

class PrevisionMensuelle(BaseModel):
    mois: str
    depenses_prevues: float
    depenses_reelles: Optional[float] = None
    recettes_prevues: float
    recettes_reelles: Optional[float] = None
    solde_tresorerie: float


class PrevisionResponse(BaseModel):
    mois_courant: str
    solde_actuel: float
    alerte_liquidite: bool
    previsions: List[PrevisionMensuelle]


# ── Résumé global dashboard ───────────────────────────────────────────────────

class DashboardSummary(BaseModel):
    kpi: KPIStats
    evolution: EvolutionResponse
    repartition_anomalies: RepartitionResponse
    indicateurs: IndicateursResponse
