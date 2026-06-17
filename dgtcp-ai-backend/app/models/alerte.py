from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class NiveauAlerte(str, enum.Enum):
    FAIBLE = "faible"
    MOYEN = "moyen"
    ELEVE = "eleve"
    CRITIQUE = "critique"


class StatutAlerte(str, enum.Enum):
    NON_LUE = "non_lue"
    LUE = "lue"
    TRAITEE = "traitee"
    ARCHIVEE = "archivee"


class Alerte(Base):
    __tablename__ = "alertes"

    id = Column(Integer, primary_key=True, index=True)
    # Liens
    anomalie_id = Column(Integer, ForeignKey("anomalies.id"), nullable=False)
    traitee_par_id = Column(Integer, ForeignKey("utilisateurs.id"))
    # Contenu
    titre = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    niveau = Column(Enum(NiveauAlerte), nullable=False)
    # Contexte affiché dans la sidebar du dashboard
    montant_concerne = Column(Float)
    entite_concernee = Column(String(200))      # Ministère ou fournisseur
    # Statut
    statut = Column(Enum(StatutAlerte), default=StatutAlerte.NON_LUE)
    est_lue = Column(Boolean, default=False)
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    lue_at = Column(DateTime(timezone=True))
    traitee_at = Column(DateTime(timezone=True))

    # Relations
    anomalie = relationship("Anomalie", back_populates="alertes")
    traitee_par_utilisateur = relationship("Utilisateur", back_populates="alertes")
