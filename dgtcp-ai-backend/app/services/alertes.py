"""Service de gestion et requêtes des alertes."""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from datetime import datetime

from app.models.alerte import Alerte, StatutAlerte


def get_alertes_recentes(db: Session, limit: int = 5) -> List[Alerte]:
    """Retourne les alertes les plus récentes non archivées (sidebar dashboard)."""
    return (
        db.query(Alerte)
        .filter(Alerte.statut != StatutAlerte.ARCHIVEE)
        .order_by(desc(Alerte.created_at))
        .limit(limit)
        .all()
    )


def compter_alertes_non_lues(db: Session) -> int:
    return db.query(Alerte).filter(Alerte.est_lue == False).count()


def marquer_comme_lue(alerte_id: int, db: Session) -> Alerte:
    alerte = db.query(Alerte).filter(Alerte.id == alerte_id).first()
    if alerte:
        alerte.est_lue = True
        alerte.lue_at = datetime.utcnow()
        if alerte.statut == StatutAlerte.NON_LUE:
            alerte.statut = StatutAlerte.LUE
        db.commit()
        db.refresh(alerte)
    return alerte


def marquer_toutes_lues(db: Session) -> int:
    count = (
        db.query(Alerte)
        .filter(Alerte.est_lue == False)
        .update({"est_lue": True, "lue_at": datetime.utcnow(), "statut": StatutAlerte.LUE})
    )
    db.commit()
    return count
