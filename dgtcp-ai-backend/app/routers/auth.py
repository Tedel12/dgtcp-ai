from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

from app.database import get_db
from app.models.utilisateur import Utilisateur, RoleEnum
from app.schemas.auth import Token, UtilisateurPublic, LoginRequest, SignupRequest
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentification"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Utilisateur:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(Utilisateur).filter(Utilisateur.id == int(user_id)).first()
    if user is None or not user.est_actif:
        raise credentials_exception

    # Mettre à jour la dernière connexion
    user.derniere_connexion = datetime.utcnow()
    db.commit()
    return user


@router.post("/login", response_model=Token, summary="Connexion utilisateur")
async def login(form_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Utilisateur).filter(Utilisateur.email == form_data.email).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )
    if not user.est_actif:
        raise HTTPException(status_code=403, detail="Compte désactivé")

    token = create_access_token(data={"sub": str(user.id)})
    return Token(
        access_token=token,
        token_type="bearer",
        utilisateur=UtilisateurPublic.model_validate(user),
    )


@router.post("/signup", response_model=Token, summary="Inscription utilisateur")
async def signup(data: SignupRequest, db: Session = Depends(get_db)):
    # Vérifier si l'utilisateur existe
    existing = db.query(Utilisateur).filter(Utilisateur.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un compte avec cet email existe déjà"
        )
    
    # Créer le nouvel utilisateur
    # Par défaut, un nouvel utilisateur est Analyste Financier
    new_user = Utilisateur(
        nom=data.nom,
        prenom=data.prenom,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        role=RoleEnum.ANALYSTE_FINANCIER,
        poste=data.poste,
        est_actif=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Générer le token directement après l'inscription
    token = create_access_token(data={"sub": str(new_user.id)})
    return Token(
        access_token=token,
        token_type="bearer",
        utilisateur=UtilisateurPublic.model_validate(new_user),
    )


@router.get("/me", response_model=UtilisateurPublic, summary="Utilisateur connecté")
async def get_me(current_user: Utilisateur = Depends(get_current_user)):
    return current_user


from pydantic import BaseModel

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

@router.patch("/password", summary="Changer le mot de passe")
async def change_password(
    data: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Mot de passe actuel incorrect")
    
    current_user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Mot de passe mis à jour avec succès"}
