from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

from app.main import create_app


def make_client(tmp_path: Path) -> TestClient:
    return TestClient(create_app(tasks_dir=tmp_path / "tasks"))


def make_client_with_script(tmp_path: Path) -> TestClient:
    script_path = tmp_path / "event_voc_ods_etl.py"
    script_path.write_text("def run_etl():\n    pass\n", encoding="utf-8")
    return TestClient(
        create_app(
            tasks_dir=tmp_path / "tasks",
            script_path=script_path,
            script_backup_dir=tmp_path / "backups",
        )
    )


def test_list_tasks_starts_empty(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.get("/api/tasks")

    assert response.status_code == 200
    assert response.json() == []


def test_home_page_serves_task_management_ui(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.get("/")

    assert response.status_code == 200
    assert "任务管理" in response.text


def test_template_download(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.get("/api/templates/comment_upload_template.xlsx")

    assert response.status_code == 200
    assert response.headers["content-disposition"].startswith("attachment;")


def test_etl_flow_api_enriches_selected_batch(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    task = client.app.state.task_store.create_task(input_files={})
    client.app.state.task_store.update_task(task["batch_id"], summary={"dwd_comment": 19})

    response = client.get(f"/api/etl/flow?batch_id={task['batch_id']}")

    assert response.status_code == 200
    nodes = response.json()["nodes"]
    comment_node = next(node for node in nodes if node["id"] == "standardize_comment")
    assert comment_node["metrics"]["dwd_comment"] == 19


def test_script_api_reads_and_saves_with_backup(tmp_path: Path) -> None:
    client = make_client_with_script(tmp_path)

    read_response = client.get("/api/etl/script")
    assert read_response.status_code == 200
    assert "def run_etl" in read_response.json()["content"]

    save_response = client.put("/api/etl/script", json={"content": "print('new script')\n"})
    assert save_response.status_code == 200
    assert save_response.json()["content"] == "print('new script')\n"
    assert save_response.json()["backups"]


def test_script_test_run_requires_existing_batch(tmp_path: Path) -> None:
    client = make_client_with_script(tmp_path)

    response = client.post("/api/etl/script/test-run", json={"batch_id": "missing"})

    assert response.status_code == 404


def test_asset_api_returns_business_assets(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)

    def fake_list_assets(asset_key, q=None, limit=50, offset=0):
        return {
            "asset": asset_key,
            "label": "事件资产",
            "total": 1,
            "columns": [{"key": "event_name", "label": "事件名称"}],
            "rows": [{"event_name": "上市事件"}],
        }

    monkeypatch.setattr("app.routers.tasks.list_assets", fake_list_assets)

    response = client.get("/api/assets/events?q=上市")

    assert response.status_code == 200
    assert response.json()["columns"][0]["label"] == "事件名称"
    assert response.json()["rows"][0]["event_name"] == "上市事件"


def test_voc_event_api_returns_event_market_overview(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)

    def fake_list_voc_events(q=None, limit=20):
        return {
            "events": [
                {
                    "event_id": "event_001",
                    "event_name": "launch event",
                    "content_cnt": 12,
                    "comment_cnt": 80,
                    "kol_content_cnt": 3,
                }
            ]
        }

    monkeypatch.setattr("app.routers.tasks.list_voc_events", fake_list_voc_events)

    response = client.get("/api/voc/events?q=launch")

    assert response.status_code == 200
    assert response.json()["events"][0]["event_id"] == "event_001"


def test_voc_event_detail_api_returns_kol_and_user_profile_story(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)

    def fake_get_voc_event_detail(event_id):
        return {
            "event_id": event_id,
            "overview": {"event_name": "launch event", "content_cnt": 12, "comment_cnt": 80},
            "top_contents": [{"title": "top post", "engagement_total": 99}],
            "kol_voice": [{"author_name": "kol a", "kol_main_type": "test drive"}],
            "user_profiles": [{"main_label": "price sensitive", "user_cnt": 8}],
            "asset_counts": {"contents": 12, "comments": 80},
        }

    monkeypatch.setattr("app.routers.tasks.get_voc_event_detail", fake_get_voc_event_detail)

    response = client.get("/api/voc/events/event_001")

    assert response.status_code == 200
    payload = response.json()
    assert payload["overview"]["event_name"] == "launch event"
    assert payload["kol_voice"][0]["kol_main_type"] == "test drive"
    assert payload["user_profiles"][0]["main_label"] == "price sensitive"


def test_voc_event_market_dashboard_api_returns_business_sections(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)

    def fake_dashboard(event_id):
        return {
            "event": {"event_id": event_id, "event_name": "IDT6上市"},
            "overview_metrics": {
                "total_volume": 44,
                "content_count": 25,
                "comment_count": 19,
                "kol_count": 2,
                "kol_content_count": 6,
                "total_engagement": 65692,
            },
            "volume_trend": [{"date": "2026-05-14", "content_count": 2, "comment_count": 3, "total_volume": 5}],
            "channel_distribution": [{"channel": "抖音", "content_count": 10, "comment_count": 8, "total_volume": 18}],
            "kol_type_distribution": [{"kol_main_type": "车型实测测评KOL", "kol_count": 2, "content_count": 4, "total_engagement": 1200}],
            "hot_posts": [{"content_id": "c1", "title": "试驾体验", "total_engagement": 999}],
        }

    monkeypatch.setattr("app.routers.tasks.get_voc_event_market_dashboard", fake_dashboard)

    response = client.get("/api/voc/events/event_001/market-dashboard")

    assert response.status_code == 200
    payload = response.json()
    assert payload["event"]["event_id"] == "event_001"
    assert payload["overview_metrics"]["total_volume"] == 44
    assert payload["hot_posts"][0]["title"] == "试驾体验"


def test_competitor_work_api_passes_published_date_filters(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)
    captured = {}

    def fake_list_competitor_works(**kwargs):
        captured.update(kwargs)
        return {
            "asset": "competitor_works",
            "label": "竞品作品库",
            "total": 0,
            "columns": [],
            "rows": [],
        }

    monkeypatch.setattr("app.routers.tasks.list_competitor_works", fake_list_competitor_works)

    response = client.get(
        "/api/competitors/works?q=途观&brand_name=上汽大众&account_type=经销商&start_date=2026-05-01&end_date=2026-05-31"
    )

    assert response.status_code == 200
    assert captured["q"] == "途观"
    assert captured["brand_name"] == "上汽大众"
    assert captured["account_type"] == "经销商"
    assert captured["start_date"] == "2026-05-01"
    assert captured["end_date"] == "2026-05-31"


def test_asset_export_returns_excel_file(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)

    def fake_list_assets(asset_key, q=None, limit=50, offset=0, max_limit=200):
        return {
            "asset": asset_key,
            "label": "事件资产",
            "total": 1,
            "columns": [{"key": "event_name", "label": "事件名称"}],
            "rows": [{"event_name": "上市事件"}],
        }

    monkeypatch.setattr("app.routers.tasks.list_assets", fake_list_assets)

    response = client.get("/api/assets/events/export?q=上市")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    assert "attachment;" in response.headers["content-disposition"]
    assert response.content.startswith(b"PK")


def test_competitor_work_export_passes_current_filters(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)
    captured = {}

    def fake_list_competitor_works(**kwargs):
        captured.update(kwargs)
        return {
            "asset": "competitor_works",
            "label": "竞品作品库",
            "total": 1,
            "columns": [{"key": "title", "label": "标题"}],
            "rows": [{"title": "本周新增"}],
        }

    monkeypatch.setattr("app.routers.tasks.list_competitor_works", fake_list_competitor_works)

    response = client.get(
        "/api/competitors/works/export?q=途观&brand_name=上汽大众&account_type=经销商&start_date=2026-05-01&end_date=2026-05-31"
    )

    assert response.status_code == 200
    assert captured["q"] == "途观"
    assert captured["brand_name"] == "上汽大众"
    assert captured["account_type"] == "经销商"
    assert captured["start_date"] == "2026-05-01"
    assert captured["end_date"] == "2026-05-31"
    assert captured["limit"] > 1000
    assert response.content.startswith(b"PK")


def test_task_table_export_returns_excel_file(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    task = client.app.state.task_store.create_task(input_files={})
    output_dir = client.app.state.task_store.output_dir(task["batch_id"])
    output_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([{"comment_id": "c1", "location": "北京"}]).to_csv(
        output_dir / "dwd_comment.csv",
        index=False,
        encoding="utf-8-sig",
    )

    response = client.get(f"/api/tasks/{task['batch_id']}/tables/dwd_comment/export")

    assert response.status_code == 200
    assert response.content.startswith(b"PK")


def test_kol_sample_export_returns_excel_file(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)

    def fake_export_kol_samples(days=7):
        return pd.DataFrame(
            [
                {
                    "author_id": "author_001",
                    "platform": "抖音",
                    "author_name": "车圈老张",
                    "author_home_url": "https://example.com/u/1",
                    "content_count": 2,
                    "content_text": "近7日发帖文本",
                    "total_engagement": 99,
                }
            ]
        )

    monkeypatch.setattr("app.routers.tasks.export_kol_profile_samples", fake_export_kol_samples)

    response = client.get("/api/profiles/kols/samples/export?days=7")

    assert response.status_code == 200
    assert response.content.startswith(b"PK")


def test_kol_profile_upload_calls_loader(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)
    captured = {}

    def fake_load_kol_profiles(upload_path, source_file_name, database_url=None):
        captured["source_file_name"] = source_file_name
        return {"loaded": 1}

    monkeypatch.setattr("app.routers.tasks.load_kol_profiles", fake_load_kol_profiles)
    upload_path = tmp_path / "kol_profile.xlsx"
    pd.DataFrame(
        [
            {
                "author_id": "author_001",
                "kol_main_type": "车型实测测评KOL",
                "content_tendency": "偏客观实测",
                "car_focus": "燃油车专注",
                "remark": "近7日测评内容占比最高",
                "profile_batch": "prompt_v1",
            }
        ]
    ).to_excel(upload_path, index=False)

    with upload_path.open("rb") as upload_file:
        response = client.post(
            "/api/profiles/kols/upload",
            files={"profile_file": ("kol_profile.xlsx", upload_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )

    assert response.status_code == 200
    assert response.json()["loaded"] == 1
    assert captured["source_file_name"] == "kol_profile.xlsx"


def test_kol_profile_upload_returns_clear_error_for_missing_author_id(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    upload_path = tmp_path / "kol_profile_missing_author_id.xlsx"
    pd.DataFrame([{"kol_main_type": "车型实测测评KOL"}]).to_excel(upload_path, index=False)

    with upload_path.open("rb") as upload_file:
        response = client.post(
            "/api/profiles/kols/upload",
            files={"profile_file": ("kol_profile_missing_author_id.xlsx", upload_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )

    assert response.status_code == 400
    assert "author_id" in response.json()["detail"]


def test_comment_user_sample_export_returns_excel_file(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)

    def fake_export_comment_user_samples():
        return pd.DataFrame(
            [
                {
                    "comment_user_id": "comment_user_001",
                    "platform": "douyin",
                    "comment_author_name": "driver_a",
                    "location": "beijing",
                    "comment_id": "comment_001",
                    "event_name": "launch event",
                    "content_title": "new car",
                    "content_author_name": "official account",
                    "source_url": "https://example.com/post/1",
                    "comment_text": "price is important",
                    "published_at": "2026-05-01 10:00:00",
                    "like_cnt": 3,
                    "reply_cnt": 1,
                }
            ]
        )

    monkeypatch.setattr("app.routers.tasks.export_comment_user_profile_samples", fake_export_comment_user_samples)

    response = client.get("/api/profiles/comment-users/samples/export")

    assert response.status_code == 200
    assert response.content.startswith(b"PK")


def test_comment_user_profile_upload_calls_loader(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)
    captured = {}

    def fake_load_comment_user_profiles(upload_path, source_file_name, database_url=None):
        captured["source_file_name"] = source_file_name
        return {"raw_loaded": 1, "profiles_loaded": 1, "label_scores_loaded": 1}

    monkeypatch.setattr("app.routers.tasks.load_comment_user_profiles", fake_load_comment_user_profiles)
    upload_path = tmp_path / "comment_user_profile.xlsx"
    pd.DataFrame(
        [
            {
                "comment_user_id": "comment_user_001",
                "profile_batch": "prompt_v1",
                "prompt_version": "v1",
                "llm_result_json": '{"total_comments": 1, "valid_comments": 1, "comment_evidence_results": []}',
            }
        ]
    ).to_excel(upload_path, index=False)

    with upload_path.open("rb") as upload_file:
        response = client.post(
            "/api/profiles/comment-users/upload",
            files={"profile_file": ("comment_user_profile.xlsx", upload_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )

    assert response.status_code == 200
    assert response.json()["profiles_loaded"] == 1
    assert captured["source_file_name"] == "comment_user_profile.xlsx"


def test_comment_user_profile_api_returns_profiles(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)
    captured = {}

    def fake_list_comment_user_profiles(q=None, profile_batch=None, limit=50, offset=0):
        captured.update({"q": q, "profile_batch": profile_batch, "limit": limit, "offset": offset})
        return {
            "asset": "comment_user_profiles",
            "label": "comment user profiles",
            "total": 1,
            "columns": [{"key": "main_label", "label": "main label"}],
            "rows": [{"main_label": "price_sensitive"}],
        }

    monkeypatch.setattr("app.routers.tasks.list_comment_user_profiles", fake_list_comment_user_profiles)

    response = client.get("/api/profiles/comment-users?q=price&profile_batch=prompt_v1&limit=10&offset=20")

    assert response.status_code == 200
    assert response.json()["rows"][0]["main_label"] == "price_sensitive"
    assert captured == {"q": "price", "profile_batch": "prompt_v1", "limit": 10, "offset": 20}


def test_upload_run_and_preview_tables(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)
    monkeypatch.setattr(
        "app.services.etl_runner.load_etl_outputs",
        lambda output_dir, batch_id, database_url: {"dwd_comment": 19},
    )
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


def test_upload_accepts_csv_files(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)
    monkeypatch.setattr(
        "app.services.etl_runner.load_etl_outputs",
        lambda output_dir, batch_id, database_url: {"dwd_comment": 19},
    )
    sample_input = Path("samples/event_voc_etl_sample/input")
    csv_input = tmp_path / "csv_input"
    csv_input.mkdir()
    for name in ["event_upload", "content_upload", "comment_upload"]:
        dataframe = pd.read_excel(sample_input / f"{name}.xlsx")
        dataframe.to_csv(csv_input / f"{name}.csv", index=False, encoding="utf-8-sig")

    with (
        (csv_input / "event_upload.csv").open("rb") as event_file,
        (csv_input / "content_upload.csv").open("rb") as content_file,
        (csv_input / "comment_upload.csv").open("rb") as comment_file,
    ):
        upload_response = client.post(
            "/api/tasks/upload",
            files={
                "event_file": ("event_upload.csv", event_file, "text/csv"),
                "content_file": ("content_upload.csv", content_file, "text/csv"),
                "comment_file": ("comment_upload.csv", comment_file, "text/csv"),
            },
        )

    batch_id = upload_response.json()["batch_id"]
    run_response = client.post(f"/api/tasks/{batch_id}/run")

    assert run_response.status_code == 200
    assert run_response.json()["status"] == "success"
    assert run_response.json()["summary"]["dwd_comment"] == 19
