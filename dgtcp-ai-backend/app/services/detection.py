"""
Moteur de détection des anomalies — DGTCP-AI
Combine :
  1. Isolation Forest (ML non supervisé) pour détecter les outliers
  2. Règles métier explicites (doublons, fractionnement, fournisseur suspect)
  3. Détection comportementale (dérive vs historique du ministère)
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.transaction import Transaction
from app.models.anomalie import Anomalie, TypeAnomalie, NiveauRisque, StatutAnomalie
from app.models.alerte import Alerte, NiveauAlerte, StatutAlerte
from app.services.scoring import calculer_score_risque, niveau_depuis_score, recommandation_auto
from app.config import settings


# ── Isolation Forest singleton ────────────────────────────────────────────────

_model: Optional[IsolationForest] = None
_scaler: Optional[StandardScaler] = None


def _get_features(transactions: List[Transaction], moyennes_ministeres: Dict[str, float]) -> np.ndarray:
    """Extrait les features numériques pour Isolation Forest."""
    rows = []
    for t in transactions:
        moy = moyennes_ministeres.get(t.ministere, t.montant)
        ratio = t.montant / moy if moy > 0 else 1.0
        rows.append([
            t.montant,
            ratio,
            t.date_transaction.hour if hasattr(t.date_transaction, "hour") else 12,
            t.date_transaction.weekday() if hasattr(t.date_transaction, "weekday") else 0,
        ])
    return np.array(rows, dtype=float)


def entrainer_modele(db: Session) -> None:
    """Entraîne Isolation Forest sur toutes les transactions existantes."""
    global _model, _scaler

    transactions = db.query(Transaction).all()
    if len(transactions) < 50:
        return  # Pas assez de données

    moyennes = _calculer_moyennes_ministeres(db)
    X = _get_features(transactions, moyennes)

    _scaler = StandardScaler()
    X_scaled = _scaler.fit_transform(X)

    _model = IsolationForest(
        n_estimators=200,
        contamination=0.05,   # On s'attend à ~5% d'anomalies
        random_state=42,
        n_jobs=-1,
    )
    _model.fit(X_scaled)


def _calculer_moyennes_ministeres(db: Session) -> Dict[str, float]:
    """Calcule la moyenne des montants par ministère."""
    result = (
        db.query(Transaction.ministere, func.avg(Transaction.montant))
        .group_by(Transaction.ministere)
        .all()
    )
    return {ministere: float(avg) for ministere, avg in result}


# ── Règles métier ─────────────────────────────────────────────────────────────

def _detecter_doublon(transaction: Transaction, db: Session) -> bool:
    """Détecte si une transaction identique existe déjà (même fournisseur, même montant, fenêtre 7j)."""
    fenetre = transaction.date_transaction - timedelta(days=7)
    doublon = (
        db.query(Transaction)
        .filter(
            Transaction.fournisseur == transaction.fournisseur,
            Transaction.montant == transaction.montant,
            Transaction.date_transaction >= fenetre,
            Transaction.id != transaction.id,
        )
        .first()
    )
    return doublon is not None


def _detecter_fractionnement(transaction: Transaction, db: Session) -> bool:
    """
    Détecte le fractionnement de marché :
    même fournisseur + plusieurs transactions proches dans les 30 derniers jours
    dont le total dépasse 50M FCFA.
    """
    SEUIL_FRACTIONNEMENT = 50_000_000  # 50M FCFA
    fenetre = transaction.date_transaction - timedelta(days=30)

    transactions_liees = (
        db.query(Transaction)
        .filter(
            Transaction.fournisseur == transaction.fournisseur,
            Transaction.ministere == transaction.ministere,
            Transaction.date_transaction >= fenetre,
            Transaction.id != transaction.id,
        )
        .all()
    )

    if not transactions_liees:
        return False

    total = sum(t.montant for t in transactions_liees) + transaction.montant
    return len(transactions_liees) >= 2 and total > SEUIL_FRACTIONNEMENT


def _detecter_fournisseur_suspect(fournisseur_age_jours: int, montant: float) -> bool:
    """Fournisseur récent (< 90j) avec un gros montant (> 100M FCFA)."""
    return fournisseur_age_jours < 90 and montant > 100_000_000


def _detecter_comportemental(
    transaction: Transaction,
    moyenne_ministere: float,
) -> bool:
    """Dérive comportementale : montant > 3x la moyenne du ministère."""
    if moyenne_ministere <= 0:
        return False
    return transaction.montant > 3 * moyenne_ministere


# ── Point d'entrée principal ──────────────────────────────────────────────────

def analyser_transaction(
    transaction: Transaction,
    db: Session,
    fournisseur_age_jours: int = 365,
) -> Optional[Dict]:
    """
    Analyse une transaction et retourne un dict décrivant l'anomalie détectée,
    ou None si la transaction est normale.
    """
    moyennes = _calculer_moyennes_ministeres(db)
    moyenne_ministere = moyennes.get(transaction.ministere, transaction.montant)

    # Règles métier
    est_doublon = _detecter_doublon(transaction, db)
    est_fractionnement = _detecter_fractionnement(transaction, db)
    est_fournisseur_suspect = _detecter_fournisseur_suspect(fournisseur_age_jours, transaction.montant)
    est_comportemental = _detecter_comportemental(transaction, moyenne_ministere)

    # Score IA (si modèle entraîné)
    score_if = None
    if _model is not None and _scaler is not None:
        X = _get_features([transaction], moyennes)
        X_scaled = _scaler.transform(X)
        score_if = float(_model.score_samples(X_scaled)[0])

    # Score global
    score = calculer_score_risque(
        montant=transaction.montant,
        montant_moyen_ministere=moyenne_ministere,
        fournisseur_age_jours=fournisseur_age_jours,
        est_doublon=est_doublon,
        est_fractionnement=est_fractionnement,
        score_isolation_forest=score_if,
    )

    niveau = niveau_depuis_score(score)

    # Déterminer le type d'anomalie principal
    if est_doublon:
        type_anomalie = TypeAnomalie.PAIEMENT_DOUBLE
        description = f"Paiement similaire déjà effectué pour {transaction.fournisseur} — montant identique détecté dans les 7 derniers jours."
    elif est_fractionnement:
        type_anomalie = TypeAnomalie.FRACTIONNEMENT
        description = f"Plusieurs transactions liées détectées pour {transaction.fournisseur} ce mois-ci. Total cumulé potentiellement au-dessus du seuil réglementaire."
    elif est_fournisseur_suspect:
        type_anomalie = TypeAnomalie.FOURNISSEUR_SUSPECT
        description = f"Fournisseur nouveau avec un montant élevé ({transaction.montant:,.0f} FCFA). Enregistrement récent (< 90 jours)."
    elif est_comportemental:
        type_anomalie = TypeAnomalie.COMPORTEMENTAL
        description = f"Montant ({transaction.montant:,.0f} FCFA) très supérieur à la moyenne habituelle de {transaction.ministere} ({moyenne_ministere:,.0f} FCFA)."
    elif score >= settings.SEUIL_SCORE_RISQUE_MOYEN:
        type_anomalie = TypeAnomalie.MONTANT_INHABITUEL
        description = f"Montant inhabituel pour ce type de transaction ({transaction.montant:,.0f} FCFA)."
    else:
        return None  # Transaction normale

    recommandation = recommandation_auto(niveau, type_anomalie.value, transaction.montant)

    return {
        "type_anomalie": type_anomalie,
        "niveau_risque": NiveauRisque(niveau),
        "score_risque": score,
        "description": description,
        "recommandation": recommandation,
        "details_techniques": (
            f"Score IF: {score_if:.4f} | " if score_if is not None else "Score IF: N/A | "
            f"Doublon: {est_doublon} | "
            f"Fractionnement: {est_fractionnement} | "
            f"Fournisseur suspect: {est_fournisseur_suspect} | "
            f"Comportemental: {est_comportemental} | "
            f"Ratio/moyenne: {transaction.montant/moyenne_ministere:.2f}x"
        ) if moyenne_ministere > 0 else "Première transaction de ce ministère.",
    }


def creer_anomalie_et_alerte(
    transaction: Transaction,
    anomalie_data: Dict,
    db: Session,
    num_seq: int,
) -> Tuple[Anomalie, Alerte]:
    """Persiste l'anomalie et génère l'alerte associée."""
    # Générer une référence unique
    date_str = transaction.date_transaction.strftime("%Y%m%d")
    reference = f"AN{date_str}-{num_seq:03d}"

    anomalie = Anomalie(
        reference=reference,
        transaction_id=transaction.id,
        type_anomalie=anomalie_data["type_anomalie"],
        niveau_risque=anomalie_data["niveau_risque"],
        score_risque=anomalie_data["score_risque"],
        description=anomalie_data["description"],
        recommandation=anomalie_data["recommandation"],
        details_techniques=anomalie_data["details_techniques"],
        statut=StatutAnomalie.NON_TRAITE,
    )
    db.add(anomalie)
    db.flush()  # Pour avoir l'ID

    # Titre de l'alerte selon le type
    titres = {
        TypeAnomalie.MONTANT_INHABITUEL: "Montant inhabituel détecté",
        TypeAnomalie.PAIEMENT_DOUBLE: "Paiement en double possible",
        TypeAnomalie.FOURNISSEUR_SUSPECT: "Fournisseur suspect",
        TypeAnomalie.TROP_PERCU: "Trop perçu critique",
        TypeAnomalie.FRACTIONNEMENT: "Fractionnement détecté",
        TypeAnomalie.COMPORTEMENTAL: "Dérive comportementale",
        TypeAnomalie.AUTRE: "Anomalie détectée",
    }

    niveaux_alerte = {
        NiveauRisque.FAIBLE: NiveauAlerte.FAIBLE,
        NiveauRisque.MOYEN: NiveauAlerte.MOYEN,
        NiveauRisque.ELEVE: NiveauAlerte.ELEVE,
        NiveauRisque.CRITIQUE: NiveauAlerte.CRITIQUE,
    }

    alerte = Alerte(
        anomalie_id=anomalie.id,
        titre=titres.get(anomalie_data["type_anomalie"], "Anomalie détectée"),
        message=anomalie_data["description"],
        niveau=niveaux_alerte[anomalie_data["niveau_risque"]],
        montant_concerne=transaction.montant,
        entite_concernee=transaction.fournisseur,
        statut=StatutAlerte.NON_LUE,
        est_lue=False,
    )
    db.add(alerte)

    # Marquer la transaction
    transaction.est_anomalie = True
    transaction.score_risque = anomalie_data["score_risque"]

    return anomalie, alerte
