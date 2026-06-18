"""
Router Data Collector — Importation de données et analyse IA en masse
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
import io
from datetime import datetime

from app.database import get_db
from app.routers.auth import get_current_user
from app.models.utilisateur import Utilisateur
from app.models.transaction import Transaction, StatutTransaction, TypeTransaction
from app.services.detection import analyser_transaction, creer_anomalie_et_alerte
from app.models.anomalie import Anomalie

router = APIRouter(prefix="/data", tags=["Data Collector"])

@router.post("/import", summary="Importer un fichier CSV de transactions")
async def import_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    if current_user.role == RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="L'administrateur ne peut pas importer de données opérationnelles")

    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Seuls les fichiers CSV sont acceptés")

    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    
    anomalies_count = 0
    
    for _, row in df.iterrows():
        # Création de la transaction
        tx = Transaction(
            reference=str(row['reference']),
            ministere=row['ministere'],
            fournisseur=row['fournisseur'],
            montant=float(row['montant']),
            montant_prevu=float(row.get('montant_prevu', row['montant'])),
            date_transaction=datetime.strptime(row['date_transaction'], '%Y-%m-%d'),
            statut=StatutTransaction.EN_ATTENTE,
            est_anomalie=False
        )
        db.add(tx)
        db.flush()
        
        # Analyse IA immédiate
        anomalie_data = analyser_transaction(tx, db)
        if anomalie_data:
            today_str = tx.date_transaction.strftime("%Y%m%d")
            count_today = db.query(Anomalie).filter(Anomalie.reference.like(f"AN{today_str}-%")).count()
            creer_anomalie_et_alerte(tx, anomalie_data, db, num_seq=count_today + 1)
            anomalies_count += 1
            
    db.commit()
    
    # Ré-entraîner l'IA avec les nouvelles données
    from app.services.detection import entrainer_modele
    entrainer_modele(db)
    
    return {"message": "Importation réussie", "transactions_traitees": len(df), "anomalies_detectees": anomalies_count}
