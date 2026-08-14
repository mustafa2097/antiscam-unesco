# Anti-Scam Job Platform (UNESCO Hackathon)

## Stack
- Frontend: React + Vite + Tailwind + i18next (EN/AR)
- Backend: FastAPI + SQLAlchemy (async) + PostgreSQL
- ML: TF-IDF + LogisticRegression scam detector (Kaggle-retrainable)
- Auth: OAuth2 password flow, JWT in HttpOnly cookies

## What it does
1. Scan job text / link / file for scam risk
2. Detect the job field (developer, nurse, marketing, …)
3. Recommend safer **courses** and **jobs** in the same field
4. List verified opportunities from Postgres

## Quick start (local)

1. Copy env templates:
   - `.env.example` → `.env` (set `JWT_SECRET`)
   - `frontend/.env.example` → `frontend/.env` (optional)

2. Start PostgreSQL, then API:
```bash
docker compose up -d db
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy ..\.env .env
python -m app.ml.train
uvicorn app.main:app --reload --port 8000
```

3. Frontend:
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5000

## Train on Kaggle
See `ml/kaggle/train_scam_detector_kaggle.py` and drop the exported
`scam_tfidf_logreg.joblib` into `backend/app/ml/artifacts/`.

## Deploy free (online)
Follow **[DEPLOY.md](./DEPLOY.md)** — Neon (DB) + Render (API) + Cloudflare Pages (frontend).

## API highlights
- `POST /api/scan/text|link|image` → risk score + role + recommendations
- `GET /api/recommend?role=developer` → courses & jobs for a field
- `GET /api/opportunities` → verified directory
- `GET /docs` → interactive API docs
