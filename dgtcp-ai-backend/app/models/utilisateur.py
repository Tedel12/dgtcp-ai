from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    COMPTABLE = "comptable"
    AUDITEUR = "auditeur"
    DIRECTEUR = "directeur"
    ANALYSTE_FINANCIER = "analyste_financier"
    CONTROLEUR_FINANCIER = "controleur_financier"


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.COMPTABLE, nullable=False)
    poste = Column(String(150))
    avatar_url = Column(String(255))
    est_actif = Column(Boolean, default=True)
    derniere_connexion = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    alertes = relationship("Alerte", back_populates="traitee_par_utilisateur")

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"
