from pathlib import Path
import os


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = PROJECT_ROOT / "runtime"
TASKS_DIR = RUNTIME_DIR / "tasks"
TEMPLATE_DIR = PROJECT_ROOT / "templates" / "event-voc"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:123456@127.0.0.1:5432/postgres")
SCHEMA_SQL_PATH = PROJECT_ROOT / "schema" / "data_access_schema.sql"
