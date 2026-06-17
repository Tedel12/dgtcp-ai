from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.utilisateur import RoleEnum


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    password: str
    poste: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    utilisateur: "UtilisateurPublic"


class UtilisateurPublic(BaseModel):
    id: int
    nom: str
    prenom: str
    email: str
    role: RoleEnum
    poste: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}


Token.model_rebuild()
