from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection


async def apply_schema_patches(conn: AsyncConnection) -> None:
    """Add columns introduced after initial deploy (create_all does not alter tables)."""

    def _patch_sqlite(sync_conn) -> None:
        rows = sync_conn.execute(text("PRAGMA table_info(npcs)")).fetchall()
        cols = {row[1] for row in rows}
        if "known_name" not in cols:
            sync_conn.execute(text("ALTER TABLE npcs ADD COLUMN known_name VARCHAR(120)"))
        if "met_location" not in cols:
            sync_conn.execute(text("ALTER TABLE npcs ADD COLUMN met_location VARCHAR(200)"))

        session_rows = sync_conn.execute(text("PRAGMA table_info(game_sessions)")).fetchall()
        session_cols = {row[1] for row in session_rows}
        if "images_enabled" not in session_cols:
            sync_conn.execute(
                text("ALTER TABLE game_sessions ADD COLUMN images_enabled BOOLEAN NOT NULL DEFAULT 0")
            )

        char_rows = sync_conn.execute(text("PRAGMA table_info(player_characters)")).fetchall()
        char_cols = {row[1] for row in char_rows}
        if "user_id" not in char_cols:
            sync_conn.execute(text("ALTER TABLE player_characters ADD COLUMN user_id CHAR(32)"))
        if "is_starter" not in char_cols:
            sync_conn.execute(
                text("ALTER TABLE player_characters ADD COLUMN is_starter BOOLEAN NOT NULL DEFAULT 0")
            )
        if "progression_source_session_id" not in char_cols:
            sync_conn.execute(
                text("ALTER TABLE player_characters ADD COLUMN progression_source_session_id CHAR(32)")
            )
        if "progression_refund_budget" not in char_cols:
            sync_conn.execute(
                text(
                    "ALTER TABLE player_characters ADD COLUMN progression_refund_budget "
                    "INTEGER NOT NULL DEFAULT 0"
                )
            )
        if "progression_purchases" not in char_cols:
            sync_conn.execute(
                text(
                    "ALTER TABLE player_characters ADD COLUMN progression_purchases "
                    "JSON NOT NULL DEFAULT '[]'"
                )
            )

    await conn.run_sync(_patch_sqlite)
