from pydantic_settings import BaseSettings, SettingsConfigDict

_PROFILE_DEFAULTS = {
    "sqlite-dev": "sqlite+aiosqlite:///./wfrp_solo.db",
    "postgres": "postgresql+asyncpg://wfrp:wfrp@localhost:5432/wfrp_solo",
    "supabase": "",
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_profile: str = "sqlite-dev"  # sqlite-dev | postgres | supabase
    database_url: str = ""
    llm_provider: str = "deepseek"  # mock | anthropic | deepseek
    anthropic_api_key: str = ""
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    llm_model: str = "deepseek-chat"
    cloudflare_account_id: str = ""
    cloudflare_api_token: str = ""
    cloudflare_ai_model: str = "@cf/black-forest-labs/flux-1-schnell"
    api_base_url: str = "http://localhost:8000"
    cors_origins: str = "http://localhost:3000"
    session_turn_history_limit: int = 20
    semantic_memory_limit: int = 8

    @property
    def resolved_database_url(self) -> str:
        custom = self.database_url.strip()
        if custom and "://" in custom:
            return custom
        url = _PROFILE_DEFAULTS.get(self.database_profile, "")
        if not url:
            raise ValueError(
                f"Perfil '{self.database_profile}' exige DATABASE_URL explícita "
                "(ex.: URL do Supabase)."
            )
        return url

    @property
    def is_postgres(self) -> bool:
        return self.resolved_database_url.startswith("postgresql")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
