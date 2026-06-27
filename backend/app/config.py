import os
import warnings

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///./wfrp_solo.db"
    llm_provider: str = "deepseek"  # mock | anthropic | deepseek
    anthropic_api_key: str = ""
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    llm_model: str = "deepseek-chat"
    openrouter_api_key: str = ""
    openrouter_image_model: str = "black-forest-labs/flux.2-klein-4b"
    api_base_url: str = "http://localhost:8000"
    cors_origins: str = "http://localhost:3000"
    session_turn_history_limit: int = 20
    semantic_memory_limit: int = 8
    jwt_secret: str = "change-me-in-production-use-long-random-string"
    jwt_expire_days: int = 7
    email_provider: str = "mock"  # mock | smtp
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@wfrpsolo.local"
    smtp_use_tls: bool = True
    enable_custom_chargen: bool = False
    app_env: str = "development"  # development | production
    auth_mode: str = "fixed_admin"  # fixed_admin | multi_user
    admin_password: str = ""  # ADMIN_PASSWORD — required when fixed_admin

    @property
    def effective_app_env(self) -> str:
        env = self.app_env.strip().lower()
        if env in ("development", "production"):
            return env
        return "development"

    @property
    def is_production(self) -> bool:
        return self.effective_app_env == "production"

    @property
    def is_fixed_admin(self) -> bool:
        return self.auth_mode.strip().lower() != "multi_user"

    @property
    def is_multi_user(self) -> bool:
        return self.auth_mode.strip().lower() == "multi_user"

    def validate_startup_config(self) -> None:
        if self.is_fixed_admin and len(self.admin_password) < 8:
            raise RuntimeError(
                "ADMIN_PASSWORD is required (min 8 chars) when AUTH_MODE=fixed_admin"
            )
        if not self.is_production:
            return
        if self.jwt_secret.startswith("change-me"):
            raise RuntimeError(
                "JWT_SECRET must be set to a secure value when APP_ENV=production"
            )
        if self.is_multi_user and self.email_provider != "smtp":
            raise RuntimeError("EMAIL_PROVIDER must be smtp when AUTH_MODE=multi_user in production")

    @property
    def resolved_database_url(self) -> str:
        url = self.database_url.strip() or "sqlite+aiosqlite:///./wfrp_solo.db"
        if not url.startswith("sqlite"):
            raise ValueError(
                "Only SQLite is supported. DATABASE_URL must start with sqlite+aiosqlite://"
            )
        return url

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()

if os.environ.get("DATABASE_PROFILE"):
    warnings.warn(
        "DATABASE_PROFILE is deprecated and ignored; use DATABASE_URL instead.",
        DeprecationWarning,
        stacklevel=1,
    )
