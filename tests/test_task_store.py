from pathlib import Path

from app.services.task_store import TaskStore


def test_create_task_writes_metadata(tmp_path: Path) -> None:
    store = TaskStore(tmp_path)

    task = store.create_task(
        input_files={
            "event_upload": "event_upload.xlsx",
            "content_upload": "content_upload.xlsx",
            "comment_upload": "comment_upload.xlsx",
        }
    )

    assert task["status"] == "uploaded"
    assert task["batch_id"].startswith("batch_")
    assert task["input_files"]["event_upload"] == "event_upload.xlsx"
    assert (tmp_path / task["batch_id"] / "task.json").exists()


def test_update_task_status_and_summary(tmp_path: Path) -> None:
    store = TaskStore(tmp_path)
    task = store.create_task(input_files={"event_upload": "event_upload.xlsx"})

    updated = store.update_task(
        task["batch_id"],
        status="success",
        summary={"dwd_comment": 19, "rejected_comment": 0},
        error_message=None,
    )

    assert updated["status"] == "success"
    assert updated["summary"]["dwd_comment"] == 19
    assert updated["error_message"] is None
    assert store.get_task(task["batch_id"])["status"] == "success"


def test_list_tasks_returns_newest_first(tmp_path: Path) -> None:
    store = TaskStore(tmp_path)
    first = store.create_task(input_files={"event_upload": "first.xlsx"})
    second = store.create_task(input_files={"event_upload": "second.xlsx"})

    tasks = store.list_tasks()

    assert [task["batch_id"] for task in tasks] == [second["batch_id"], first["batch_id"]]
