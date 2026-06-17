# DGTCP-AI — Backend FastAPI

> Plateforme intelligente de détection des anomalies financières  
> Direction Générale du Trésor et de la Comptabilité Publique — Bénin

---

## Stack technique

| Composant | Technologie |
|---|---|
| Framework API | FastAPI + Uvicorn |
| ORM | SQLAlchemy 2.0 |
| Base de données | PostgreSQL |
| IA / ML | Scikit-learn (Isolation Forest) |
| Auth | JWT (python-jose) + bcrypt |
| Données simulées | Faker + seed custom |

---

## Prérequis

- Python 3.10 ou 3.11
- PostgreSQL 14+
- pip

---

## Installation pas à pas

### 1. Cloner / extraire le projet

```bash
cd dgtcp-ai-backend
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Créer la base de données PostgreSQL

```sql
-- Dans psql ou pgAdmin
CREATE DATABASE dgtcp_ai;
```

### 5. Configurer les variables d'environnement

Le fichier `.env` est déjà présent avec les valeurs par défaut.  
Modifiez si nécessaire :

```env
DATABASE_URL=postgresql://postgres:VOTRE_MOT_DE_PASSE@localhost:5432/dgtcp_ai
SECRET_KEY=changez_cette_clé_en_production
```

### 6. Démarrer le serveur

```bash
uvicorn main:app --reload --port 8000
```

Au **premier démarrage**, le serveur :
1. Crée toutes les tables automatiquement
2. Lance le seeding (~12 458 transactions + 243 anomalies + alertes + 4 utilisateurs)

Cela prend environ **30 à 60 secondes**.

---

## Accès

| URL | Description |
|---|---|
| http://localhost:8000 | Health check |
| http://localhost:8000/docs | Documentation Swagger interactive |
| http://localhost:8000/redoc | Documentation ReDoc |

---

## Comptes de test

| Email | Mot de passe | Rôle |
|---|---|---|
| admin@dgtcp.bj | Admin@2025 | Administrateur |
| jb.hounkpe@dgtcp.bj | Comptable@2025 | Comptable Principal |
| m.dossou@dgtcp.bj | Auditeur@2025 | Auditeur Interne |
| r.zannou@dgtcp.bj | Directeur@2025 | Directeur Général Adjoint |

---

## Endpoints principaux

### Auth
| Méthode | Route | Description |
|---|---|---|
| POST | /api/auth/login | Connexion → retourne JWT |
| GET | /api/auth/me | Utilisateur connecté |

### Dashboard
| Méthode | Route | Description |
|---|---|---|
| GET | /api/dashboard/summary | Toutes les stats en 1 appel |
| GET | /api/dashboard/kpi | 5 KPI cards |
| GET | /api/dashboard/evolution?periode=mois | Graphique linéaire |
| GET | /api/dashboard/repartition-anomalies | Graphique donut |
| GET | /api/dashboard/indicateurs | Indicateurs clés |
| GET | /api/dashboard/previsions | Prévisions budgétaires |

### Transactions
| Méthode | Route | Description |
|---|---|---|
| GET | /api/transactions | Liste paginée + filtres |
| GET | /api/transactions/{id} | Détail |
| POST | /api/transactions | Créer + analyse IA auto |
| PATCH | /api/transactions/{id}/statut | Changer statut |

### Anomalies
| Méthode | Route | Description |
|---|---|---|
| GET | /api/anomalies | Liste paginée + filtres |
| GET | /api/anomalies/stats | Stats globales |
| GET | /api/anomalies/{id} | Détail avec recommandation |
| PATCH | /api/anomalies/{id} | Traiter une anomalie |

### Alertes
| Méthode | Route | Description |
|---|---|---|
| GET | /api/alertes/recentes | Sidebar dashboard (badge cloche) |
| GET | /api/alertes | Liste complète |
| PATCH | /api/alertes/{id}/lire | Marquer comme lue |
| POST | /api/alertes/lire-toutes | Tout marquer comme lu |

### Rapports & Prévisions
| Méthode | Route | Description |
|---|---|---|
| GET | /api/rapports/depenses-par-ministere | Dépenses par ministère |
| GET | /api/rapports/top-fournisseurs-risque | Fournisseurs à risque |
| GET | /api/rapports/evolution-mensuelle | Évolution mensuelle |
| GET | /api/predictions/tresorerie | Prévisions 6 mois |
| GET | /api/predictions/risques-budgetaires | Risques par ministère |

---

## Architecture des fichiers

```
dgtcp-ai-backend/
├── main.py                    # Point d'entrée FastAPI + lifespan
├── requirements.txt
├── .env
└── app/
    ├── config.py              # Settings (pydantic-settings)
    ├── database.py            # SQLAlchemy engine + session
    ├── models/
    │   ├── utilisateur.py     # Modèle User + RoleEnum
    │   ├── transaction.py     # Modèle Transaction
    │   ├── anomalie.py        # Modèle Anomalie + TypeAnomalie
    │   └── alerte.py          # Modèle Alerte
    ├── schemas/
    │   ├── auth.py            # Pydantic Login/Token
    │   ├── transaction.py     # Schémas Transaction
    │   ├── anomalie.py        # Schémas Anomalie
    │   ├── alerte.py          # Schémas Alerte
    │   └── dashboard.py       # KPI, Evolution, Donut, Indicateurs
    ├── routers/
    │   ├── auth.py            # Login, /me, logout
    │   ├── dashboard.py       # KPI, graphiques, summary
    │   ├── transactions.py    # CRUD transactions
    │   ├── anomalies.py       # Anomalies + stats
    │   ├── alertes.py         # Alertes + notifications
    │   ├── rapports.py        # Analyse & rapports
    │   └── predictions.py     # Prévisions budgétaires
    ├── services/
    │   ├── detection.py       # Moteur IA (Isolation Forest + règles métier)
    │   ├── scoring.py         # Score de risque 0-100%
    │   └── alertes.py         # Gestion alertes
    └── seed/
        └── seeder.py          # ~12 500 transactions simulées réalistes
```

---

## Connecter le frontend React

Dans votre frontend, configurez :

```js
// src/api/config.js
export const API_URL = "http://localhost:8000/api";
```

Exemple de login :
```js
const res = await fetch(`${API_URL}/auth/login`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ email: "admin@dgtcp.bj", password: "Admin@2025" }),
});
const { access_token } = await res.json();
// Stocker le token et l'envoyer dans chaque requête :
// headers: { Authorization: `Bearer ${access_token}` }
```
