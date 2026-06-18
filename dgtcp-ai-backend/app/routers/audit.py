from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.database import get_db
from app.routers.auth import get_current_user
from app.models.utilisateur import Utilisateur, RoleEnum
from app.models.audit import AuditLog
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/audit", tags=["Audit & Journal"])

class AuditLogOut(BaseModel):
    id: int
    action: str
    entite: Optional[str]
    details: Optional[dict]
    ip_address: Optional[str]
    created_at: datetime
    utilisateur_nom: str

    class Config:
        from_attributes = True

@router.get("/logs")
async def get_audit_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    # Seuls Directeur et Auditeur peuvent voir les logs
    if current_user.role not in [RoleEnum.DIRECTEUR, RoleEnum.AUDITEUR]:
        return {"detail": "Accès non autorisé"}
    
    logs = db.query(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit).all()
    
    return [
        {
            "id": log.id,
            "action": log.action,
            "entite": log.entite,
            "details": log.details,
            "ip_address": log.ip_address,
            "created_at": log.created_at,
            "utilisateur_nom": f"{log.utilisateur.prenom} {log.utilisateur.nom}" if log.utilisateur else "Système"
        } for log in logs
    ]
