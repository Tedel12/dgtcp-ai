"""
DGTCP-AI — Point d'entrée principal
Plateforme intelligente de détection des anomalies financières
Direction Générale du Trésor et de la Comptabilité Publique — Bénin
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import create_tables, SessionLocal
from app.routers import auth, dashboard, transactions, anomalies, alertes, rapports, predictions, users, data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Exécuté au démarrage : crée les tables et lance le seed si la DB est vide."""
    create_tables()

    # Auto-seed si pas de données
    db = SessionLocal()
    try:
        from app.models.transaction import Transaction
        count = db.query(Transaction).count()
        if count == 0:
            print("Base de données vide — lancement du seeding automatique...")
            from app.seed.seeder import run_seed
            run_seed(db)
        else:
            print(f"Base prête — {count} transactions existantes.")
    finally:
        db.close()

    yield
    print("Arrêt du serveur DGTCP-AI.")


# ── Application ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="DGTCP-AI API",
    description=(
        "Plateforme intelligente de détection des anomalies financières "
        "et d'aide à la décision — Direction Générale du Trésor et de la "
        "Comptabilité Publique du Bénin."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS (autorise le frontend React en dev) ──────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
PREFIX = "/api"

app.include_router(auth.router,          prefix=PREFIX)
app.include_router(dashboard.router,     prefix=PREFIX)
app.include_router(transactions.router,  prefix=PREFIX)
app.include_router(anomalies.router,     prefix=PREFIX)
app.include_router(alertes.router,       prefix=PREFIX)
app.include_router(rapports.router,      prefix=PREFIX)
app.include_router(predictions.router,   prefix=PREFIX)
app.include_router(users.router,         prefix=PREFIX)
app.include_router(data.router,          prefix=PREFIX)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
