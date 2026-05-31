from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app


def make_client(tmp_path: Path) -> TestClient:
    return TestClient(create_app(tasks_dir=tmp_path / "tasks"))


def test_list_tasks_starts_empty(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.get("/api/tasks")

    assert response.status_code == 200
    assert response.json() == []


def test_template_download(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.get("/api/templates/comment_upload_template.xlsx")

    assert response.status_code == 200
    assert response.headers["content-disposition"].startswith("attachment;")


def test_upload_run_and_preview_tables(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    sample_input = Path("samples/event_voc_etl_sample/input")

    with (
        (sample_input / "event_upload.xlsx").open("rb") as event_file,
        (sample_input / "content_upload.xlsx").open("rb") as content_file,
        (sample_input / "comment_upload.xlsx").open("rb") as comment_file,
    ):
        upload_response = client.post(
            "/api/tasks/upload",
            files={
                "event_file": ("event_upload.xlsx", event_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
                "content_file": ("content_upload.xlsx", content_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
                "comment_file": ("comment_upload.xlsx", comment_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            },
        )

    assert upload_response.status_code == 200
    batch_id = upload_response.json()["batch_id"]
    assert upload_response.json()["status"] == "uploaded"

    run_response = client.post(f"/api/tasks/{batch_id}/run")
    assert run_response.status_code == 200
    assert run_response.json()["status"] == "success"
    assert run_response.json()["summary"]["dwd_comment"] == 19

    tables_response = client.get(f"/api/tasks/{batch_id}/tables")
    assert tables_response.status_code == 200
    assert "dwd_comment" in tables_response.json()["tables"]

    table_response = client.get(f"/api/tasks/{batch_id}/tables/dwd_comment?limit=5")
    assert table_response.status_code == 200
    payload = table_response.json()
    assert "location" in payload["columns"]
    assert len(payload["rows"]) == 5
