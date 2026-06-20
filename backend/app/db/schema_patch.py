from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.config import settings


async def apply_schema_patches(conn: AsyncConnection) -> None:
    """Add columns introduced after initial deploy (create_all does not alter tables)."""
    if settings.is_postgres:
        await conn.execute(text("ALTER TABLE npcs ADD COLUMN IF NOT EXISTS known_name VARCHAR(120)"))
        await conn.execute(text("ALTER TABLE npcs ADD COLUMN IF NOT EXISTS met_location VARCHAR(200)"))
        return

    def _patch_sqlite(sync_conn) -> None:
        rows = sync_conn.execute(text("PRAGMA table_info(npcs)")).fetchall()
        cols = {row[1] for row in rows}
        if "known_name" not in cols:
            sync_conn.execute(text("ALTER TABLE npcs ADD COLUMN known_name VARCHAR(120)"))
        if "met_location" not in cols:
            sync_conn.execute(text("ALTER TABLE npcs ADD COLUMN met_location VARCHAR(200)"))

    await conn.run_sync(_patch_sqlite)
