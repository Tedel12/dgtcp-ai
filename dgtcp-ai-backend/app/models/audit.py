from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    action = Column(String(100), nullable=False)  # ex: "LOGIN", "VALIDATION_ANOMALIE"
    entite = Column(String(50))  # ex: "ANOMALIE", "UTILISATEUR"
    entite_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(45))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relation
    utilisateur = relationship("Utilisateur")
