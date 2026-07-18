from pathlib import Path
from shutil import copytree

from app.services.etl_runner import EtlRunner
from app.services.task_store import TaskStore


def test_run_task_updates_summary_after_success(tmp_path: Path, monkeypatch) -> None:
    store = TaskStore(tmp_path / "tasks")
    task = store.create_task(
        input_files={
            "event_upload": "event_upload.xlsx",
            "content_upload": "content_upload.xlsx",
            "comment_upload": "comment_upload.xlsx",
        }
    )
    sample_input = Path("samples/event_voc_etl_sample/input")
    copytree(sample_input, store.input_dir(task["batch_id"]), dirs_exist_ok=True)
    monkeypatch.setattr(
        "app.services.etl_runner.load_etl_outputs",
        lambda output_dir, batch_id, database_url: {"dwd_comment": 19},
    )

    result = EtlRunner(store).run_task(task["batch_id"])

    assert result["status"] == "success"
    assert result["summary"]["dwd_event"] == 1
    assert result["summary"]["dwd_content"] == 25
    assert result["summary"]["dwd_comment"] == 248
    assert result["summary"]["rejected_comment"] == 0
    assert result["db_loaded"]["dwd_comment"] == 19
    assert (store.output_dir(task["batch_id"]) / "etl_summary.json").exists()


def test_run_task_records_failure_message(tmp_path: Path) -> None:
    store = TaskStore(tmp_path / "tasks")
    task = store.create_task(input_files={})

    result = EtlRunner(store).run_task(task["batch_id"])

    assert result["status"] == "failed"
    assert result["error_message"]
