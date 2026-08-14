# Deploy free (from any device)

This stack runs online for **$0** using free tiers:

| Layer | Free service | Notes |
|-------|--------------|-------|
| Postgres | [Neon](https://neon.tech) | Create DB `antiscam`, copy connection string |
| API | [Render](https://render.com) free Web Service | Uses `backend/Dockerfile` + `render.yaml` |
| Frontend | [Cloudflare Pages](https://pages.cloudflare.com) or [Netlify](https://netlify.com) | Static Vite build |

## 1) Database (Neon)

1. Create a free Neon project.
2. Create database `antiscam`.
3. Copy the connection string and convert it for async SQLAlchemy:

```
postgresql+asyncpg://USER:PASSWORD@HOST/antiscam?ssl=require
```

> Neon often gives `postgresql://...`. Replace the scheme with `postgresql+asyncpg://`.

## 2) Train / refresh the ML model (optional, Kaggle)

1. Open a Kaggle notebook.
2. Add a fake-job dataset (e.g. *Real or Fake Job Posting Prediction*).
3. Run `ml/kaggle/train_scam_detector_kaggle.py`.
4. Download `scam_tfidf_logreg.joblib` into `backend/app/ml/artifacts/`.
5. Commit and redeploy the API.

Local training (seed corpus, no Kaggle needed):

```bash
cd backend
python -m pip install -r requirements.txt
python -m app.ml.train
```

## 3) Backend (Render)

1. Push this repo to GitHub.
2. On Render: **New → Blueprint** (uses `render.yaml`) or **Web Service** from `backend/`.
3. Set env vars:

```
DATABASE_URL=postgresql+asyncpg://...@.../antiscam?ssl=require
JWT_SECRET=<long random secret 32+ chars>
FRONTEND_ORIGIN=https://YOUR-FRONTEND.pages.dev
COOKIE_SECURE=true
```

4. Deploy. Health check: `https://YOUR-API.onrender.com/health`
5. API docs: `https://YOUR-API.onrender.com/docs`

Free Render dynos sleep after idle; first request may take ~30–60s.

## 4) Frontend (Cloudflare Pages)

1. Build command: `npm install && npm run build` (root = `frontend`)
2. Output directory: `dist`
3. Environment variable:

```
VITE_API_BASE_URL=https://YOUR-API.onrender.com
```

4. After deploy, copy the Pages URL into Render `FRONTEND_ORIGIN` (comma-separated if you have several).

## 5) Local check before going live

```bash
# terminal 1 — Postgres must be reachable
cd backend
python -m uvicorn app.main:app --reload --port 8000

# terminal 2
cd frontend
npm run dev
```

Open http://localhost:5000

## What the online app does

1. User pastes a suspicious job post.
2. API scores scam risk (ML + rule indicators).
3. Detects job field (developer, nurse, …).
4. Suggests **courses** and **verified jobs** in the same field.
5. Directory lists seeded verified opportunities from Postgres.
