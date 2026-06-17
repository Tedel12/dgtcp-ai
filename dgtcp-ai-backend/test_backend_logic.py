
import sys
import os
from datetime import datetime

# Ajout du chemin pour importer l'app
sys.path.append(os.getcwd())

from app.models.transaction import Transaction, TypeTransaction
from app.models.anomalie import TypeAnomalie, NiveauRisque
from app.models.utilisateur import RoleEnum
from app.services.detection import _detecter_trop_percu, analyser_transaction
from app.services.scoring import calculer_score_risque
from sqlalchemy.orm import Session
from app.database import SessionLocal

def test_roles_exist():
    print("Test : Vérification des nouveaux rôles...")
    assert "analyste_financier" in [r.value for r in RoleEnum]
    assert "controleur_financier" in [r.value for r in RoleEnum]
    print(" Rôles validés.")

def test_detection_trop_percu():
    print("Test : Détection logique du Trop Perçu...")
    
    # Cas 1 : Normal
    t1 = Transaction(montant=50000, montant_prevu=50000)
    assert _detecter_trop_percu(t1) is False
    
    # Cas 2 : Trop perçu (100k au lieu de 50k)
    t2 = Transaction(montant=100000, montant_prevu=50000)
    assert _detecter_trop_percu(t2) is True
    print("Logique de détection validée.")

def test_scoring_trop_percu():
    print("Test : Scoring du risque pour Trop Perçu...")
    
    # Sans trop perçu
    score_normal = calculer_score_risque(
        montant=50000, 
        montant_moyen_ministere=50000, 
        fournisseur_age_jours=365, 
        est_doublon=False, 
        est_fractionnement=False,
        est_trop_percu=False
    )
    
    # Avec trop perçu
    score_risque = calculer_score_risque(
        montant=50000, 
        montant_moyen_ministere=50000, 
        fournisseur_age_jours=365, 
        est_doublon=False, 
        est_fractionnement=False,
        est_trop_percu=True
    )
    
    print(f"   Score normal: {score_normal} | Score Trop Perçu: {score_risque}")
    assert score_risque > score_normal
    assert score_risque >= 45 # Le bonus qu'on a ajouté
    print("Scoring du risque validé.")

def run_all_tests():
    try:
        test_roles_exist()
        test_detection_trop_percu()
        test_scoring_trop_percu()
        print("\n TOUT LE BACKEND LOGIQUE EST VALIDE !")
    except AssertionError as e:
        print(f"\n ÉCHEC DU TEST : {e}")
    except Exception as e:
        print(f"\n ERREUR INATTENDUE : {e}")

if __name__ == "__main__":
    run_all_tests()
