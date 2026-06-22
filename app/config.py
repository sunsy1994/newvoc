from pathlib import Path
import os


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = PROJECT_ROOT / "runtime"
TASKS_DIR = RUNTIME_DIR / "tasks"
SCRIPT_BACKUP_DIR = RUNTIME_DIR / "script_backups"
TEMPLATE_DIR = PROJECT_ROOT / "templates" / "event-voc"
ETL_SCRIPT_PATH = PROJECT_ROOT / "etl" / "event_voc_ods_etl.py"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:123456@127.0.0.1:5432/postgres")
SCHEMA_SQL_PATH = PROJECT_ROOT / "schema" / "data_access_schema.sql"
PROFILE_AI_BASE_URL = os.getenv("PROFILE_AI_BASE_URL", "")
PROFILE_AI_API_KEY = os.getenv("PROFILE_AI_API_KEY", "")
PROFILE_AI_MODEL = os.getenv("PROFILE_AI_MODEL", "")
PROFILE_AI_TIMEOUT_SECONDS = int(os.getenv("PROFILE_AI_TIMEOUT_SECONDS", "60"))
