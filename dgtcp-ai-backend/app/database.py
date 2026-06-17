from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={"client_encoding": "utf8"}  # <-- Ajoutez cette ligne ici
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dépendance FastAPI — injecte une session DB dans chaque route."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Crée toutes les tables si elles n'existent pas."""
    Base.metadata.create_all(bind=engine)
