from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class StatutTransaction(str, enum.Enum):
    EN_ATTENTE = "en_attente"
    VALIDEE = "validee"
    REJETEE = "rejetee"
    SUSPENDUE = "suspendue"


class TypeTransaction(str, enum.Enum):
    DEPENSE = "depense"
    RECETTE = "recette"
    VIREMENT = "virement"
    REMBOURSEMENT = "remboursement"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(50), unique=True, index=True, nullable=False)
    # Qui paie / qui reçoit
    ministere = Column(String(200), nullable=False)
    fournisseur = Column(String(200), nullable=False)
    code_fournisseur = Column(String(50))
    # Montants en FCFA
    montant = Column(Float, nullable=False)
    montant_prevu = Column(Float)           # Budget initial prévu
    # Classification
    type_transaction = Column(Enum(TypeTransaction), default=TypeTransaction.DEPENSE)
    categorie = Column(String(100))         # Travaux, Fournitures, Services...
    ligne_budgetaire = Column(String(100))
    statut = Column(Enum(StatutTransaction), default=StatutTransaction.EN_ATTENTE)
    # Méta
    description = Column(Text)
    date_transaction = Column(DateTime(timezone=True), nullable=False)
    date_echeance = Column(DateTime(timezone=True))
    # Flags IA
    est_anomalie = Column(Boolean, default=False)
    score_risque = Column(Float, default=0.0)   # 0 à 100
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations
    anomalies = relationship("Anomalie", back_populates="transaction")
