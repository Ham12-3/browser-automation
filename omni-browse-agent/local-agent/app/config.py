from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "OmniBrowse Agent"
    host: str = "127.0.0.1"
    port: int = 8765
    api_token: str | None = None
    database_url: str = "sqlite:///./omnibrowse.db"
    screenshot_dir: Path = Path("./data/screenshots")
    allowed_extension_ids: list[str] = Field(default_factory=list)
    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost", "http://127.0.0.1"])
    safe_domains_allowlist: list[str] = Field(default_factory=list)
    blocked_domains: list[str] = Field(default_factory=list)
    default_control_mode: str = "auto"
    max_actions_per_task: int = 20
    action_delay_seconds: float = 0.35
    approval_timeout_seconds: int = 300
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "llama3.1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="OMNI_",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.screenshot_dir.mkdir(parents=True, exist_ok=True)
    return settings

