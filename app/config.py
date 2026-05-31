from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = PROJECT_ROOT / "runtime"
TASKS_DIR = RUNTIME_DIR / "tasks"
TEMPLATE_DIR = PROJECT_ROOT / "templates" / "event-voc"
