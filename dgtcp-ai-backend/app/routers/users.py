"""
Router Utilisateurs — Gestion des comptes et rôles
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.routers.auth import get_current_user
from app.models.utilisateur import Utilisateur, RoleEnum
from app.schemas.auth import UtilisateurPublic

router = APIRouter(prefix="/users", tags=["Utilisateurs"])

@router.get("", response_model=List[UtilisateurPublic], summary="Liste de tous les utilisateurs")
async def get_users(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    # Seul un admin peut lister les utilisateurs
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    users = db.query(Utilisateur).all()
    return [UtilisateurPublic.model_validate(u) for u in users]

@router.patch("/{user_id}/role", response_model=UtilisateurPublic, summary="Modifier le rôle d'un utilisateur")
async def update_user_role(
    user_id: int,
    role: RoleEnum,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    
    user.role = role
    db.commit()
    db.refresh(user)
    return UtilisateurPublic.model_validate(user)
