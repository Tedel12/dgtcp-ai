"""
Seeder DGTCP-AI
Génère ~12 458 transactions réalistes + anomalies injectées
avec des données contextualisées au Bénin (montants FCFA, ministères, fournisseurs locaux).
"""
import random
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.models.utilisateur import Utilisateur, RoleEnum
from app.models.transaction import Transaction, StatutTransaction, TypeTransaction
from app.models.anomalie import Anomalie, TypeAnomalie, NiveauRisque, StatutAnomalie
from app.models.alerte import Alerte, NiveauAlerte, StatutAlerte

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Données de référence béninoises ──────────────────────────────────────────

MINISTERES = [
    "Ministère de l'Économie et des Finances",
    "Ministère de la Santé",
    "Ministère de l'Éducation Nationale",
    "Ministère des Travaux Publics et des Transports",
    "Ministère de l'Agriculture",
    "Ministère de l'Intérieur et de la Sécurité Publique",
    "Ministère de l'Énergie",
    "Ministère de l'Équipement et des Infrastructures",
    "Direction Générale des Impôts",
    "Direction Générale des Douanes",
    "Ministère du Numérique et de la Digitalisation",
    "Ministère de la Justice",
]

FOURNISSEURS_NORMAUX = [
    ("SOBEBRA SA", "F001", 730),
    ("BÉNIN TÉLÉCOM SA", "F002", 1095),
    ("SODECO", "F003", 900),
    ("SBEE (Société Béninoise d'Énergie Électrique)", "F004", 1460),
    ("SONEB", "F005", 1200),
    ("GIZ BÉNIN", "F006", 800),
    ("PAPETERIE BÉNIN SARL", "F007", 650),
    ("SETAB CONSTRUCTION", "F008", 540),
    ("PHARMACIE CENTRALE DU BÉNIN", "F009", 720),
    ("CIMBENIN SA", "F010", 480),
    ("NESTLE BÉNIN", "F011", 390),
    ("MTN BÉNIN", "F012", 1100),
    ("MOOV AFRICA BÉNIN", "F013", 980),
    ("CANAL+ BÉNIN", "F014", 420),
    ("TOTAL ENERGIES BÉNIN", "F015", 870),
    ("AFRICA BUREAU", "F016", 560),
    ("BUREAU VERITAS BÉNIN", "F017", 700),
    ("CABINET AUDIT & CONSEIL", "F018", 450),
    ("IMPRIMERIE NATIONALE", "F019", 610),
    ("BTP AFRIQUE SARL", "F020", 490),
]

# Fournisseurs suspects — récents, peu connus
FOURNISSEURS_SUSPECTS = [
    ("ETS GLOBAL SERVICES", "S001", 15),       # 15 jours seulement
    ("RAPID SOLUTIONS BJ", "S002", 22),
    ("INFRA TECH BÉNIN", "S003", 45),
    ("MULTISERVICES PLUS", "S004", 8),
    ("DELTA CONSTRUCT", "S005", 60),
]

CATEGORIES = [
    "Fournitures de bureau",
    "Travaux de construction",
    "Services informatiques",
    "Équipements médicaux",
    "Carburant et lubrifiants",
    "Prestations intellectuelles",
    "Formation et renforcement de capacités",
    "Entretien et maintenance",
    "Acquisition de véhicules",
    "Frais de mission",
]

LIGNES_BUDGETAIRES = [
    "21-01 Salaires et traitements",
    "21-02 Indemnités et avantages",
    "22-01 Fournitures courantes",
    "22-02 Services",
    "23-01 Transferts courants",
    "31-01 Bâtiments et ouvrages",
    "31-02 Équipements et matériels",
    "32-01 Infrastructures routières",
]

# ── Montants réalistes par catégorie (FCFA) ──────────────────────────────────

PLAGES_MONTANTS = {
    "Fournitures de bureau":              (500_000,    15_000_000),
    "Travaux de construction":            (5_000_000,  800_000_000),
    "Services informatiques":             (2_000_000,  120_000_000),
    "Équipements médicaux":               (3_000_000,  250_000_000),
    "Carburant et lubrifiants":           (1_000_000,  50_000_000),
    "Prestations intellectuelles":        (2_000_000,  80_000_000),
    "Formation et renforcement de capacités": (1_000_000, 30_000_000),
    "Entretien et maintenance":           (500_000,    25_000_000),
    "Acquisition de véhicules":           (8_000_000,  180_000_000),
    "Frais de mission":                   (200_000,    5_000_000),
}


def _random_date_mois_courant(annee: int = 2025, mois: int = 5) -> datetime:
    """Date aléatoire dans mai 2025 (mois de la maquette)."""
    import calendar
    _, nb_jours = calendar.monthrange(annee, mois)
    jour = random.randint(1, nb_jours)
    heure = random.randint(7, 17)
    minute = random.randint(0, 59)
    return datetime(annee, mois, jour, heure, minute)


def _random_date_historique() -> datetime:
    """Date dans les 12 derniers mois."""
    jours_arriere = random.randint(1, 365)
    return datetime(2025, 5, 31) - timedelta(days=jours_arriere)


def generer_reference_transaction(index: int) -> str:
    return f"TXN-2025-{index:06d}"


# ── Seed utilisateurs ─────────────────────────────────────────────────────────

def seed_utilisateurs(db: Session) -> List[Utilisateur]:
    utilisateurs_data = [
        {
            "nom": "AGOSSOU", "prenom": "Comptable Principal",
            "email": "admin@dgtcp.bj",
            "password": "Admin@2025",
            "role": RoleEnum.ADMIN,
            "poste": "Administrateur Système",
        },
        {
            "nom": "HOUNKPE", "prenom": "Jean-Baptiste",
            "email": "jb.hounkpe@dgtcp.bj",
            "password": "Comptable@2025",
            "role": RoleEnum.COMPTABLE,
            "poste": "Comptable Principal",
        },
        {
            "nom": "DOSSOU", "prenom": "Mariette",
            "email": "m.dossou@dgtcp.bj",
            "password": "Auditeur@2025",
            "role": RoleEnum.AUDITEUR,
            "poste": "Auditeur Interne Senior",
        },
        {
            "nom": "ZANNOU", "prenom": "Romuald",
            "email": "r.zannou@dgtcp.bj",
            "password": "Directeur@2025",
            "role": RoleEnum.DIRECTEUR,
            "poste": "Directeur Général Adjoint",
        },
        {
            "nom": "KODJO", "prenom": "Hervé",
            "email": "h.kodjo@dgtcp.bj",
            "password": "Analyste@2025",
            "role": RoleEnum.ANALYSTE_FINANCIER,
            "poste": "Analyste Risques Financiers",
        },
        {
            "nom": "TOSSOU", "prenom": "Bernice",
            "email": "b.tossou@dgtcp.bj",
            "password": "Controleur@2025",
            "role": RoleEnum.CONTROLEUR_FINANCIER,
            "poste": "Contrôleur Budgétaire",
        },
    ]

    created = []
    for data in utilisateurs_data:
        existing = db.query(Utilisateur).filter(Utilisateur.email == data["email"]).first()
        if not existing:
            u = Utilisateur(
                nom=data["nom"],
                prenom=data["prenom"],
                email=data["email"],
                hashed_password=pwd_context.hash(data["password"]),
                role=data["role"],
                poste=data["poste"],
            )
            db.add(u)
            created.append(u)

    db.commit()
    print(f" {len(created)} utilisateurs créés.")
    return created


# ── Seed transactions normales ────────────────────────────────────────────────

def seed_transactions_normales(db: Session, count: int = 12200) -> List[Transaction]:
    transactions = []
    for i in range(1, count + 1):
        fournisseur_nom, fournisseur_code, _ = random.choice(FOURNISSEURS_NORMAUX)
        categorie = random.choice(CATEGORIES)
        ministere = random.choice(MINISTERES)
        plage = PLAGES_MONTANTS.get(categorie, (1_000_000, 50_000_000))
        montant = round(random.uniform(*plage), -3)  # Arrondi à millier

        # Majorité mois courant, reste historique
        if i <= int(count * 0.08):   # 8% = mois courant
            date_tx = _random_date_mois_courant()
        else:
            date_tx = _random_date_historique()

        statut_choices = [
            StatutTransaction.VALIDEE,
            StatutTransaction.VALIDEE,
            StatutTransaction.VALIDEE,
            StatutTransaction.EN_ATTENTE,
        ]

        t = Transaction(
            reference=generer_reference_transaction(i),
            ministere=ministere,
            fournisseur=fournisseur_nom,
            code_fournisseur=fournisseur_code,
            montant=montant,
            montant_prevu=round(montant * random.uniform(0.9, 1.1), -3),
            type_transaction=TypeTransaction.DEPENSE,
            categorie=categorie,
            ligne_budgetaire=random.choice(LIGNES_BUDGETAIRES),
            statut=random.choice(statut_choices),
            description=f"Paiement {categorie.lower()} — {fournisseur_nom}",
            date_transaction=date_tx,
            est_anomalie=False,
            score_risque=round(random.uniform(0, 30), 2),
        )
        transactions.append(t)

    db.bulk_save_objects(transactions)
    db.commit()
    print(f"✅ {count} transactions normales créées.")
    return transactions


# ── Seed anomalies injectées ──────────────────────────────────────────────────

def seed_anomalies(db: Session) -> None:
    """
    Injecte 243 anomalies réalistes dans la base :
    - 40% Montant inhabituel
    - 25% Paiement double
    - 15% Fournisseur suspect
    - 10% Fractionnement
    - 10% Autres
    """
    anomalies_config = [
        # (type, nb, niveau_risque, score_min, score_max, montant_min, montant_max)
        (TypeAnomalie.TROP_PERCU, 45, NiveauRisque.CRITIQUE, 90, 99, 50_000_000, 500_000_000),
        (TypeAnomalie.MONTANT_INHABITUEL, 85, NiveauRisque.ELEVE, 75, 95, 800_000_000, 2_000_000_000),
        (TypeAnomalie.PAIEMENT_DOUBLE, 50, NiveauRisque.ELEVE, 70, 90, 300_000_000, 900_000_000),
        (TypeAnomalie.FOURNISSEUR_SUSPECT, 30, NiveauRisque.ELEVE, 72, 92, 100_000_000, 600_000_000),
        (TypeAnomalie.FRACTIONNEMENT, 20, NiveauRisque.MOYEN, 40, 65, 20_000_000, 150_000_000),
        (TypeAnomalie.COMPORTEMENTAL, 10, NiveauRisque.MOYEN, 45, 70, 200_000_000, 800_000_000),
        (TypeAnomalie.AUTRE, 3, NiveauRisque.FAIBLE, 15, 39, 5_000_000, 80_000_000),
    ]

    # Récupère les derniers IDs de transactions
    last_tx = db.query(Transaction).order_by(Transaction.id.desc()).limit(500).all()
    if not last_tx:
        print("⚠️  Pas de transactions pour injecter les anomalies.")
        return

    seq = 1
    descriptions = {
        TypeAnomalie.MONTANT_INHABITUEL: "Montant très supérieur à la moyenne habituelle pour ce ministère.",
        TypeAnomalie.PAIEMENT_DOUBLE: "Paiement similaire déjà effectué — doublon détecté dans les 7 derniers jours.",
        TypeAnomalie.FOURNISSEUR_SUSPECT: "Fournisseur récemment créé avec un montant inhabituellement élevé.",
        TypeAnomalie.FRACTIONNEMENT: "Plusieurs transactions liées détectées — fractionnement de marché possible.",
        TypeAnomalie.COMPORTEMENTAL: "Dépenses mensuelles du ministère anormalement élevées vs historique.",
        TypeAnomalie.AUTRE: "Transaction présentant plusieurs indicateurs de risque mineurs.",
    }

    recommandations = {
        TypeAnomalie.MONTANT_INHABITUEL: "Suspendre le paiement et soumettre à vérification complémentaire.",
        TypeAnomalie.PAIEMENT_DOUBLE: "Suspendre le paiement et vérifier si une transaction identique a déjà été effectuée.",
        TypeAnomalie.FOURNISSEUR_SUSPECT: "Effectuer une vérification d'identité complète du fournisseur avant paiement.",
        TypeAnomalie.FRACTIONNEMENT: "Regrouper les transactions et soumettre à la commission des marchés publics.",
        TypeAnomalie.COMPORTEMENTAL: "Analyser les dépenses du ministère et demander une justification budgétaire.",
        TypeAnomalie.AUTRE: "Demander une vérification documentaire complémentaire.",
    }

    # Niveaux alertes
    niveau_map = {
        NiveauRisque.FAIBLE: NiveauAlerte.FAIBLE,
        NiveauRisque.MOYEN: NiveauAlerte.MOYEN,
        NiveauRisque.ELEVE: NiveauAlerte.ELEVE,
        NiveauRisque.CRITIQUE: NiveauAlerte.CRITIQUE,
    }

    titres_alertes = {
        TypeAnomalie.MONTANT_INHABITUEL: "Montant inhabituel détecté",
        TypeAnomalie.PAIEMENT_DOUBLE: "Paiement en double possible",
        TypeAnomalie.FOURNISSEUR_SUSPECT: "Fournisseur suspect",
        TypeAnomalie.TROP_PERCU: "Trop perçu critique",
        TypeAnomalie.FRACTIONNEMENT: "Fractionnement détecté",
        TypeAnomalie.COMPORTEMENTAL: "Dérive comportementale",
        TypeAnomalie.AUTRE: "Transaction inhabituelle",
    }

    statuts_anomalie = [
        StatutAnomalie.NON_TRAITE,
        StatutAnomalie.NON_TRAITE,
        StatutAnomalie.EN_COURS,
        StatutAnomalie.TRAITE,
    ]

    statuts_alerte = [
        StatutAlerte.NON_LUE,
        StatutAlerte.NON_LUE,
        StatutAlerte.LUE,
        StatutAlerte.TRAITEE,
    ]

    tx_pool = list(last_tx)
    random.shuffle(tx_pool)
    tx_iter = iter(tx_pool * 10)  # Répéter pour avoir assez

    for type_an, nb, niveau, score_min, score_max, mont_min, mont_max in anomalies_config:
        for _ in range(nb):
            try:
                tx = next(tx_iter)
            except StopIteration:
                break

            score = round(random.uniform(score_min, score_max), 2)
            montant = round(random.uniform(mont_min, mont_max), -3)

            # Si c'est un trop perçu, on s'assure que montant > montant_prevu
            if type_an == TypeAnomalie.TROP_PERCU:
                tx.montant_prevu = round(montant * 0.5, -3)  # Perçoit 2x plus
                tx.montant = montant
            
            date_str = tx.date_transaction.strftime("%Y%m%d")
            reference = f"AN{date_str}-{seq:03d}"

            # Choisir fournisseur suspect si applicable
            if type_an == TypeAnomalie.FOURNISSEUR_SUSPECT:
                fournisseur_susp = random.choice(FOURNISSEURS_SUSPECTS)
                entite = fournisseur_susp[0]
            else:
                entite = tx.fournisseur

            statut_an = random.choice(statuts_anomalie)
            statut_al = StatutAlerte.NON_LUE if statut_an == StatutAnomalie.NON_TRAITE else StatutAlerte.LUE

            desc = descriptions.get(type_an, "Anomalie détectée.")
            reco = (
                "Suspendre le paiement et soumettre à vérification complémentaire."
                if niveau == NiveauRisque.ELEVE
                else "Demander une vérification documentaire."
            )

            anomalie = Anomalie(
                reference=reference,
                transaction_id=tx.id,
                type_anomalie=type_an,
                niveau_risque=niveau,
                score_risque=score,
                description=desc,
                recommandation=reco,
                details_techniques=f"Score: {score} | Montant: {montant:,.0f} FCFA | Ministère: {tx.ministere}",
                statut=statut_an,
                detected_at=tx.date_transaction + timedelta(seconds=random.randint(10, 60)),
            )
            db.add(anomalie)
            db.flush()

            # Mise à jour transaction
            tx.est_anomalie = True
            tx.score_risque = score

            alerte = Alerte(
                anomalie_id=anomalie.id,
                titre=titres_alertes.get(type_an, "Anomalie"),
                message=desc,
                niveau=niveau_map[niveau],
                montant_concerne=montant,
                entite_concernee=entite,
                statut=statut_al,
                est_lue=(statut_al != StatutAlerte.NON_LUE),
            )
            db.add(alerte)
            seq += 1

    db.commit()
    print(f"✅ {seq - 1} anomalies + alertes créées.")


# ── Point d'entrée ────────────────────────────────────────────────────────────

def run_seed(db: Session) -> None:
    print("🌱 Démarrage du seeding DGTCP-AI...")
    seed_utilisateurs(db)
    seed_transactions_normales(db, count=12200)
    seed_anomalies(db)
    print("🎉 Seeding terminé avec succès !")

