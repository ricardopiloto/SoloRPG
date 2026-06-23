import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.auth_routes import router as auth_router
from app.api.routes import router
from app.config import settings
from app.db.database import async_session, engine
from app.db.models import Base
from app.db.schema_patch import apply_schema_patches
from app.services.admin_user import ensure_admin_user

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.validate_startup_config()
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await apply_schema_patches(conn)
    except Exception as exc:
        raise RuntimeError(f"Falha ao conectar ao banco SQLite: {exc}") from exc

    if settings.is_fixed_admin:
        async with async_session() as db:
            await ensure_admin_user(db)

    yield
    await engine.dispose()


app = FastAPI(title="WFRP Solo API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(router, prefix="/api")


@app.get("/health")
async def health():
    database_ok = False
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        database_ok = True
    except Exception:
        pass
    return {
        "status": "ok" if database_ok else "degraded",
        "database_ok": database_ok,
        "app_env": settings.effective_app_env,
        "llm_provider": settings.llm_provider,
    }
