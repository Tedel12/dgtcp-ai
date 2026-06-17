from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class TypeAnomalie(str, enum.Enum):
    MONTANT_INHABITUEL = "montant_inhabituel"
    PAIEMENT_DOUBLE = "paiement_double"
    FOURNISSEUR_SUSPECT = "fournisseur_suspect"
    TROP_PERCU = "trop_percu"
    FRACTIONNEMENT = "fractionnement"
    COMPORTEMENTAL = "comportemental"
    AUTRE = "autre"


class NiveauRisque(str, enum.Enum):
    FAIBLE = "faible"
    MOYEN = "moyen"
    ELEVE = "eleve"
    CRITIQUE = "critique"


class StatutAnomalie(str, enum.Enum):
    NON_TRAITE = "non_traite"
    EN_COURS = "en_cours"
    TRAITE = "traite"
    FAUX_POSITIF = "faux_positif"


class Anomalie(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(50), unique=True, index=True, nullable=False)
    # Lien avec la transaction
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    # Classification
    type_anomalie = Column(Enum(TypeAnomalie), nullable=False)
    niveau_risque = Column(Enum(NiveauRisque), nullable=False)
    score_risque = Column(Float, nullable=False)     # 0 à 100
    # Description
    description = Column(Text, nullable=False)
    details_techniques = Column(Text)                # Raisons IA détaillées
    # Recommandation automatique du système
    recommandation = Column(Text)
    # Traitement
    statut = Column(Enum(StatutAnomalie), default=StatutAnomalie.NON_TRAITE)
    traitee_par = Column(Integer, ForeignKey("utilisateurs.id"))
    note_traitement = Column(Text)
    date_traitement = Column(DateTime(timezone=True))
    # Timestamps
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations
    transaction = relationship("Transaction", back_populates="anomalies")
    alertes = relationship("Alerte", back_populates="anomalie")
