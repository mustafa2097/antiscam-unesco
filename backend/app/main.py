from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.database import SessionLocal, init_db
from app.rate_limit import limiter
from app.routers import auth, datasets, opportunities, recommend, scan
from app.services.seed import ensure_seed_opportunities, ensure_seed_user


@asynccontextmanager
async def lifespan(_: FastAPI):
    from app import models  # noqa: F401

    await init_db()
    async with SessionLocal() as db:
        await ensure_seed_user(db)
        await ensure_seed_opportunities(db)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    origins = [o.strip() for o in settings.frontend_origin.split(",") if o.strip()]
    application = FastAPI(
        title=settings.app_name,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["http://localhost:5000"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With"],
        expose_headers=[],
        max_age=600,
    )

    application.include_router(auth.router)
    application.include_router(scan.router)
    application.include_router(datasets.router)
    application.include_router(opportunities.router)
    application.include_router(recommend.router)

    @application.get("/health")
    @limiter.limit("60/minute")
    async def health(request: Request) -> dict[str, object]:
        from app.ml.predictor import MODEL_PATH, load_model

        model = load_model()
        metrics: dict[str, object] = {}
        metrics_path = MODEL_PATH.with_name("metrics.json")
        if metrics_path.exists():
            try:
                import json

                metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            except Exception:
                metrics = {}
        return {
            "status": "ok",
            "model_loaded": model is not None,
            "model_trained_on": metrics.get("trained_on"),
            "model_roc_auc": metrics.get("roc_auc"),
            "model_rows": metrics.get("rows"),
        }

    return application


app = create_app()
