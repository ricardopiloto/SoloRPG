import logging
from contextlib import asynccontextmanager
from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.routes import router
from app.config import settings
from app.db.database import engine
from app.db.models import Base
from app.db.schema_patch import apply_schema_patches

logger = logging.getLogger(__name__)


def _postgres_host_port() -> tuple[str, str]:
    parsed = urlparse(settings.resolved_database_url.replace("+asyncpg", ""))
    return parsed.hostname or "localhost", str(parsed.port or 5432)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            if settings.is_postgres:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            await conn.run_sync(Base.metadata.create_all)
            await apply_schema_patches(conn)
    except Exception as exc:
        if settings.is_postgres:
            host, port = _postgres_host_port()
            logger.error(
                "PostgreSQL inacessível em %s:%s.\n"
                "Opções: (1) docker/podman compose up -d  "
                "(2) DATABASE_PROFILE=sqlite-dev  (3) URL Supabase em DATABASE_URL\n"
                "Diagnóstico: ss -tlnp | grep %s | podman compose ps | systemctl status postgresql",
                host,
                port,
                port,
            )
        raise RuntimeError(
            f"Falha ao conectar ao banco (perfil: {settings.database_profile}): {exc}"
        ) from exc
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
        "database_profile": settings.database_profile,
        "database_ok": database_ok,
        "llm_provider": settings.llm_provider,
    }
