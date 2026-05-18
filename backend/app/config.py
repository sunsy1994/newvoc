from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
UPLOAD_DIR = STORAGE_DIR / "uploads"
JOB_STORE_PATH = STORAGE_DIR / "import_jobs.json"
CALC_RUN_STORE_PATH = STORAGE_DIR / "calc_task_runs.json"
CALC_LOG_DIR = STORAGE_DIR / "logs"


class Settings(BaseSettings):
    app_name: str = "AutoVOC Data Import API"
    api_prefix: str = "/api"
    database_url: str | None = None
    template_dir: str = str((BASE_DIR.parent / "app" / "public" / "data-import-templates").resolve())
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

STORAGE_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CALC_LOG_DIR.mkdir(parents=True, exist_ok=True)
