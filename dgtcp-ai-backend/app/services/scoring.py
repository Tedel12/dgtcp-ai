"""
Service de scoring de risque.
Calcule un score entre 0 et 100 pour chaque transaction
en combinant règles métier + signal IA (Isolation Forest).
"""
import numpy as np
from typing import Optional
from app.config import settings


def calculer_score_risque(
    montant: float,
    montant_moyen_ministere: float,
    fournisseur_age_jours: int,
    est_doublon: bool,
    est_fractionnement: bool,
    score_isolation_forest: Optional[float] = None,  # -1 à 0 (plus négatif = + anormal)
) -> float:
    """
    Retourne un score de risque entre 0.0 et 100.0.
    Chaque règle contribue à un score partiel pondéré.
    """
    score = 0.0

    # ── Règle 1 : Montant anormalement élevé ────────────────────────────────
    # Si le montant dépasse 3x la moyenne du ministère → suspect
    if montant_moyen_ministere > 0:
        ratio = montant / montant_moyen_ministere
        if ratio > 5:
            score += 35
        elif ratio > 3:
            score += 25
        elif ratio > 2:
            score += 15
        elif ratio > 1.5:
            score += 8

    # ── Règle 2 : Montant absolu très élevé ─────────────────────────────────
    if montant >= 1_000_000_000:          # ≥ 1 milliard FCFA
        score += 20
    elif montant >= settings.SEUIL_MONTANT_ELEVE:   # ≥ 500M FCFA
        score += 12
    elif montant >= 100_000_000:          # ≥ 100M FCFA
        score += 5

    # ── Règle 3 : Nouveau fournisseur ───────────────────────────────────────
    if fournisseur_age_jours < 30:
        score += 25
    elif fournisseur_age_jours < 90:
        score += 15
    elif fournisseur_age_jours < 180:
        score += 8

    # ── Règle 4 : Paiement en double ────────────────────────────────────────
    if est_doublon:
        score += 30

    # ── Règle 5 : Fractionnement de marché ──────────────────────────────────
    if est_fractionnement:
        score += 25

    # ── Signal IA (Isolation Forest) ────────────────────────────────────────
    # score_isolation_forest est dans [-0.5, 0] : plus négatif = plus anormal
    if score_isolation_forest is not None:
        anomaly_contribution = abs(score_isolation_forest) * 30  # max ~15 pts
        score += min(anomaly_contribution, 20)

    # Clamp entre 0 et 100
    return round(min(max(score, 0.0), 100.0), 2)


def niveau_depuis_score(score: float) -> str:
    """Retourne le niveau de risque textuel depuis un score."""
    if score >= settings.SEUIL_SCORE_RISQUE_ELEVE:
        return "eleve"
    elif score >= settings.SEUIL_SCORE_RISQUE_MOYEN:
        return "moyen"
    else:
        return "faible"


def recommandation_auto(
    niveau_risque: str,
    type_anomalie: str,
    montant: float,
) -> str:
    """Génère une recommandation textuelle automatique."""
    if niveau_risque == "eleve":
        if type_anomalie == "paiement_double":
            return (
                "Suspendre immédiatement le paiement et vérifier si une transaction "
                "identique a déjà été effectuée. Contacter le service ordonnateur."
            )
        elif type_anomalie == "fournisseur_suspect":
            return (
                "Effectuer une vérification d'identité complète du fournisseur "
                "(RCCM, IFU, références bancaires). Suspendre le paiement jusqu'à validation."
            )
        elif type_anomalie == "fractionnement":
            return (
                "Regrouper les transactions liées et soumettre à la commission des marchés publics "
                "si le total dépasse le seuil réglementaire."
            )
        elif type_anomalie == "trop_percu":
            return (
                "ALERTE CRITIQUE : Le montant dépasse le budget prévu. Bloquer immédiatement le paiement "
                "et vérifier le contrat original. Risque de fuite de capitaux ou fraude."
            )
        else:
            return (
                f"Risque élevé détecté sur une transaction de {montant:,.0f} FCFA. "
                "Suspendre le paiement et soumettre à une vérification complémentaire par l'auditeur interne."
            )
    elif niveau_risque == "moyen":
        return (
            "Demander une vérification documentaire complémentaire (bon de commande, "
            "facture pro-forma, attestation de service fait) avant validation."
        )
    else:
        return (
            "Transaction à surveiller. Valider les pièces justificatives "
            "selon la procédure standard."
        )
