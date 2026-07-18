from pathlib import Path

import httpx
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


def test_data_lineage_list_and_detail_api(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)
    monkeypatch.setattr(
        "app.routers.tasks.list_lineage_nodes",
        lambda **kwargs: {"summary": {"node_count": 1}, "nodes": [{"lineage_code": "metric.content_count"}]},
    )
    monkeypatch.setattr(
        "app.routers.tasks.get_lineage_detail",
        lambda lineage_code: {"node": {"lineage_code": lineage_code}, "upstream": [], "downstream": []},
    )

    list_response = client.get("/api/system/data-lineage?business_domain=market")
    detail_response = client.get("/api/system/data-lineage/metric.content_count")

    assert list_response.status_code == 200
    assert list_response.json()["nodes"][0]["lineage_code"] == "metric.content_count"
    assert detail_response.status_code == 200
    assert detail_response.json()["node"]["lineage_code"] == "metric.content_count"


def test_data_lineage_node_and_edge_mutation_api(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)
    monkeypatch.setattr("app.routers.tasks.create_lineage_node", lambda payload: {**payload, "is_system": False})
    monkeypatch.setattr(
        "app.routers.tasks.update_lineage_node",
        lambda lineage_code, payload: {"lineage_code": lineage_code, **payload, "is_system": True},
    )
    monkeypatch.setattr("app.routers.tasks.create_lineage_edge", lambda payload: {"edge_id": 8, **payload})
    monkeypatch.setattr("app.routers.tasks.delete_lineage_edge", lambda edge_id: edge_id == 8)

    node_payload = {
        "lineage_code": "metric.custom",
        "lineage_name": "自定义指标",
        "node_kind": "metric",
        "generation_type": "derived_metric",
        "business_domain": "sales",
    }
    assert client.post("/api/system/data-lineage/nodes", json=node_payload).status_code == 200
    assert client.put(
        "/api/system/data-lineage/nodes/metric.content_count",
        json={"business_definition": "事件内去重内容数"},
    ).status_code == 200
    assert client.post(
        "/api/system/data-lineage/edges",
        json={"upstream_code": "metric.a", "downstream_code": "metric.b", "relation_type": "depends_on"},
    ).json()["edge_id"] == 8
    assert client.delete("/api/system/data-lineage/edges/8").status_code == 200


def test_data_lineage_api_maps_missing_and_validation_errors(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)
    monkeypatch.setattr("app.routers.tasks.get_lineage_detail", lambda lineage_code: None)
    monkeypatch.setattr("app.routers.tasks.create_lineage_node", lambda payload: (_ for _ in ()).throw(ValueError("非法节点")))
    monkeypatch.setattr("app.routers.tasks.delete_lineage_edge", lambda edge_id: False)

    assert client.get("/api/system/data-lineage/missing").status_code == 404
    assert client.post("/api/system/data-lineage/nodes", json={}).status_code == 400
    assert client.delete("/api/system/data-lineage/edges/99").status_code == 404


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
            "comment_quality": {
                "summary": {
                    "labeled_comment_count": 19,
                    "vehicle_related_count": 16,
                    "vehicle_related_rate": 84.2,
                    "positive_rate": 52.6,
                    "negative_rate": 5.3,
                    "mid_high_purchase_signal_count": 4,
                    "mid_high_purchase_signal_rate": 21.1,
                    "top_aspect": "外观",
                    "top_intent": "购买意向",
                },
                "sentiment_distribution": [{"label": "正向", "count": 10, "rate": 52.6}],
                "intent_distribution": [{"label": "购买意向", "count": 6, "rate": 31.6}],
                "aspect_distribution": [{"label": "外观", "count": 7, "rate": 36.8}],
                "purchase_signal_distribution": [{"label": "中", "count": 4, "rate": 21.1}],
            },
            "hot_posts": [{"content_id": "c1", "title": "试驾体验", "total_engagement": 999}],
        }

    monkeypatch.setattr("app.routers.tasks.get_voc_event_market_dashboard", fake_dashboard)

    response = client.get("/api/voc/events/event_001/market-dashboard")

    assert response.status_code == 200
    payload = response.json()
    assert payload["event"]["event_id"] == "event_001"
    assert payload["overview_metrics"]["total_volume"] == 44
    assert payload["comment_quality"]["summary"]["vehicle_related_rate"] == 84.2
    assert payload["comment_quality"]["aspect_distribution"][0]["label"] == "外观"
    assert payload["hot_posts"][0]["title"] == "试驾体验"


def test_voc_event_discussion_point_comments_api_returns_comment_evidence(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)

    def fake_discussion_comments(event_id, aspect, limit=20, offset=0):
        return {
            "aspect": aspect,
            "comments": [
                {
                    "comment_id": "cm1",
                    "content_id": "c1",
                    "source_title": "上市短视频",
                    "comment_author_name": "九月九的酒",
                    "comment_text": "外观确实挺好看",
                    "published_at": "2026-05-18T12:30:00",
                    "interaction_cnt": 8,
                    "comment_sentiment": "正向",
                    "purchase_signal": "中",
                }
            ],
            "total": 1,
            "limit": limit,
            "offset": offset,
        }

    monkeypatch.setattr("app.routers.tasks.get_voc_event_discussion_point_comments", fake_discussion_comments)

    response = client.get("/api/voc/events/event_001/discussion-points/%E5%A4%96%E8%A7%82/comments")

    assert response.status_code == 200
    payload = response.json()
    assert payload["aspect"] == "外观"
    assert payload["comments"][0]["source_title"] == "上市短视频"
    assert payload["comments"][0]["interaction_cnt"] == 8
    assert payload["comments"][0]["purchase_signal"] == "中"


def test_voc_event_product_dashboard_api_returns_focus_story(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)

    def fake_product_dashboard(event_id):
        return {
            "event": {"event_id": event_id, "event_name": "IDT6上市"},
            "product_focus_story": {
                "summary": {
                    "top_aspect": "空间",
                    "aspect_count": 3,
                    "total_mentions": 27,
                    "rule_based_conclusion": "用户讨论最集中在空间。",
                },
                "aspects": [{"aspect": "空间", "comment_count": 12, "positive_rate": 66.7, "negative_rate": 8.3}],
            },
        }

    monkeypatch.setattr("app.routers.tasks.get_voc_event_product_dashboard", fake_product_dashboard)

    response = client.get("/api/voc/events/event_001/product-dashboard")

    assert response.status_code == 200
    payload = response.json()
    assert payload["event"]["event_id"] == "event_001"
    assert payload["product_focus_story"]["summary"]["top_aspect"] == "空间"
    assert payload["product_focus_story"]["aspects"][0]["positive_rate"] == 66.7


def test_voc_event_content_detail_api_supports_comment_sort_and_paging(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)
    captured = {}

    def fake_detail(event_id, content_id, sort="interaction", limit=10, offset=0):
        captured.update({"event_id": event_id, "content_id": content_id, "sort": sort, "limit": limit, "offset": offset})
        return {
            "content": {"content_id": content_id, "event_id": event_id, "title": "top post", "source_url": "https://example.test/post"},
            "comments": [
                {
                    "comment_id": "cm2",
                    "parent_comment_id": "cm1",
                    "parent_comment_author_name": "user a",
                    "comment_author_name": "user b",
                    "comment_text": "reply",
                    "interaction_cnt": 8,
                }
            ],
            "comment_timeline": [
                {"time_bucket": "2026-05-18 10:00:00", "comment_count": 1, "interaction_count": 8},
            ],
            "total": 21,
            "limit": limit,
            "offset": offset,
            "sort": sort,
        }

    monkeypatch.setattr("app.routers.tasks.get_voc_event_content_detail", fake_detail)

    response = client.get("/api/voc/events/event_001/contents/content_001/detail?sort=published_at&limit=5&offset=10")

    assert response.status_code == 200
    payload = response.json()
    assert captured == {"event_id": "event_001", "content_id": "content_001", "sort": "published_at", "limit": 5, "offset": 10}
    assert payload["content"]["source_url"] == "https://example.test/post"
    assert payload["comments"][0]["parent_comment_id"] == "cm1"
    assert payload["comments"][0]["parent_comment_author_name"] == "user a"
    assert payload["comment_timeline"][0]["comment_count"] == 1
    assert payload["total"] == 21


def test_voc_author_detail_api_returns_global_author_story(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)

    def fake_author_detail(author_id):
        return {
            "author": {"author_id": author_id, "author_name": "车圈老张", "is_kol": True},
            "metrics": {"event_count": 2, "content_count": 5, "received_comment_count": 30, "total_engagement": 900},
            "kol_profile": {"kol_main_type": "车型实测测评KOL", "car_focus": "新能源专注"},
            "events": [{"event_id": "event_1", "event_name": "上市发布", "content_count": 3}],
            "contents": [{"content_id": "content_1", "title": "试驾体验", "engagement_total": 500}],
            "comment_quality": {"summary": {"labeled_comment_count": 20, "vehicle_related_rate": 80.0}},
            "sankey": {"nodes": [{"id": "author:author_1", "label": "车圈老张", "layer": 0}], "links": []},
        }

    monkeypatch.setattr("app.routers.tasks.get_voc_author_detail", fake_author_detail)

    response = client.get("/api/voc/authors/author_1/detail")

    assert response.status_code == 200
    payload = response.json()
    assert payload["author"]["author_name"] == "车圈老张"
    assert payload["kol_profile"]["kol_main_type"] == "车型实测测评KOL"
    assert payload["metrics"]["event_count"] == 2
    assert payload["sankey"]["nodes"][0]["layer"] == 0


def test_voc_author_detail_api_returns_404_for_missing_author(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)

    monkeypatch.setattr("app.routers.tasks.get_voc_author_detail", lambda author_id: {"author": {}})

    response = client.get("/api/voc/authors/missing/detail")

    assert response.status_code == 404


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


def test_competitor_work_insight_api_crud_and_missing_work(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)
    saved: dict[str, object] = {}

    def fake_get(work_id: str) -> dict[str, object]:
        if work_id == "missing":
            raise ValueError("Competitor work not found")
        return saved.get(work_id, {"work_id": work_id, "insight_markdown": "", "updated_by": None})  # type: ignore[return-value]

    def fake_save(work_id: str, insight_markdown: str, updated_by: str | None = None) -> dict[str, object]:
        if work_id == "missing":
            raise ValueError("Competitor work not found")
        saved[work_id] = {
            "work_id": work_id,
            "insight_markdown": insight_markdown,
            "updated_by": updated_by,
        }
        return saved[work_id]  # type: ignore[return-value]

    monkeypatch.setattr("app.routers.tasks.get_competitor_work_insight", fake_get)
    monkeypatch.setattr("app.routers.tasks.save_competitor_work_insight", fake_save)

    assert client.get("/api/competitors/works/work_001/insight").json()["insight_markdown"] == ""
    assert client.get("/api/competitors/works/missing/insight").status_code == 404

    markdown = "  解读内容  \n"
    put_response = client.put(
        "/api/competitors/works/work_001/insight",
        json={"insight_markdown": markdown, "updated_by": "tester"},
    )
    assert put_response.status_code == 200
    assert put_response.json()["insight_markdown"] == markdown
    assert put_response.json()["updated_by"] == "tester"
    assert client.get("/api/competitors/works/work_001/insight").json()["insight_markdown"] == markdown

    delete_response = client.delete("/api/competitors/works/work_001/insight")
    assert delete_response.status_code == 200
    assert delete_response.json()["insight_markdown"] == ""
    assert client.put(
        "/api/competitors/works/missing/insight",
        json={"insight_markdown": "内容"},
    ).status_code == 404


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


def test_comment_user_ai_profile_api_runs_profile(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)
    captured = {}

    def fake_run_comment_user_ai_profile(comment_user_id, **kwargs):
        captured["comment_user_id"] = comment_user_id
        captured.update(kwargs)
        return {
            "comment_user_id": comment_user_id,
            "comment_count": 2,
            "profile_batch": kwargs["profile_batch"],
            "prompt_version": kwargs["prompt_version"],
            "db_loaded": {"raw_loaded": 1, "profiles_loaded": 1, "label_scores_loaded": 3},
        }

    monkeypatch.setattr("app.routers.tasks.run_comment_user_ai_profile", fake_run_comment_user_ai_profile)

    response = client.post(
        "/api/profiles/comment-users/comment_user_001/ai-run",
        json={
            "profile_batch": "batch_ai",
            "prompt_version": "comment_user_profile_v1",
            "prompt_file": "画像提示词.txt",
        },
    )

    assert response.status_code == 200
    assert response.json()["comment_count"] == 2
    assert captured["comment_user_id"] == "comment_user_001"
    assert captured["profile_batch"] == "batch_ai"
    assert captured["prompt_version"] == "comment_user_profile_v1"
    assert captured["prompt_path"].name == "画像提示词.txt"


def test_comment_user_ai_profile_api_returns_clear_timeout_error(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)

    def fake_run_comment_user_ai_profile(comment_user_id, **kwargs):
        raise httpx.ReadTimeout("timed out")

    monkeypatch.setattr("app.routers.tasks.run_comment_user_ai_profile", fake_run_comment_user_ai_profile)

    response = client.post(
        "/api/profiles/comment-users/comment_user_001/ai-run",
        json={
            "profile_batch": "batch_ai",
            "prompt_version": "comment_user_profile_v1",
            "prompt_file": "画像提示词.txt",
        },
    )

    assert response.status_code == 504
    assert "AI画像调用超时" in response.json()["detail"]


def test_system_ai_config_api_reads_and_saves_without_returning_secret(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)
    captured = {}

    def fake_get_default_ai_config():
        return {
            "config_name": "default",
            "base_url": "https://llm.example/v1",
            "model_name": "profile-model",
            "timeout_seconds": 60,
            "is_enabled": True,
            "api_key_configured": True,
            "api_key_masked": "sk-****cdef",
        }

    def fake_save_default_ai_config(payload):
        captured.update(payload)
        return {
            "config_name": "default",
            "base_url": payload["base_url"],
            "model_name": payload["model_name"],
            "timeout_seconds": payload["timeout_seconds"],
            "is_enabled": payload["is_enabled"],
            "api_key_configured": True,
            "api_key_masked": "sk-****9876",
        }

    monkeypatch.setattr("app.routers.tasks.get_default_ai_config", fake_get_default_ai_config)
    monkeypatch.setattr("app.routers.tasks.save_default_ai_config", fake_save_default_ai_config)

    read_response = client.get("/api/system/ai-config")
    assert read_response.status_code == 200
    assert read_response.json()["api_key_masked"] == "sk-****cdef"
    assert "api_key" not in read_response.json()

    save_response = client.put(
        "/api/system/ai-config",
        json={
            "base_url": "https://new.example/v1",
            "api_key": "sk-new-secret-9876",
            "model_name": "new-model",
            "timeout_seconds": 90,
            "is_enabled": True,
        },
    )

    assert save_response.status_code == 200
    assert save_response.json()["base_url"] == "https://new.example/v1"
    assert "api_key" not in save_response.json()
    assert captured["api_key"] == "sk-new-secret-9876"
    assert captured["model_name"] == "new-model"


def test_system_prompt_api_lists_and_saves_templates(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)
    captured = {}

    def fake_list_prompt_templates(scene=None):
        captured["scene"] = scene
        return {
            "prompts": [
                {
                    "prompt_id": 1,
                    "prompt_name": "评论用户画像",
                    "prompt_scene": "comment_user_profile",
                    "prompt_version": "comment_user_profile_v1",
                    "prompt_content": "用户ID：{{user_id}}",
                    "is_default": True,
                    "is_enabled": True,
                }
            ]
        }

    def fake_save_prompt_template(payload):
        captured["saved"] = payload
        return {
            "prompt_id": 2,
            "prompt_name": payload["prompt_name"],
            "prompt_scene": payload["prompt_scene"],
            "prompt_version": payload["prompt_version"],
            "prompt_content": payload["prompt_content"],
            "is_default": payload["is_default"],
            "is_enabled": payload["is_enabled"],
        }

    monkeypatch.setattr("app.routers.tasks.list_prompt_templates", fake_list_prompt_templates)
    monkeypatch.setattr("app.routers.tasks.save_prompt_template", fake_save_prompt_template)

    list_response = client.get("/api/system/prompts?scene=comment_user_profile")
    assert list_response.status_code == 200
    assert list_response.json()["prompts"][0]["prompt_version"] == "comment_user_profile_v1"
    assert captured["scene"] == "comment_user_profile"

    save_response = client.post(
        "/api/system/prompts",
        json={
            "prompt_name": "评论用户画像",
            "prompt_scene": "comment_user_profile",
            "prompt_version": "comment_user_profile_v2",
            "prompt_content": "评论列表：{{comments}}",
            "is_default": True,
            "is_enabled": True,
        },
    )

    assert save_response.status_code == 200
    assert save_response.json()["prompt_version"] == "comment_user_profile_v2"
    assert captured["saved"]["prompt_content"] == "评论列表：{{comments}}"



def test_system_emoji_api_lists_and_saves_mappings(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)
    captured = {}

    def fake_list_emoji_mappings(enabled_only=False):
        captured["enabled_only"] = enabled_only
        return {
            "emojis": [
                {
                    "emoji_id": 1,
                    "emoji_code": "[666]",
                    "emoji_type": "emoji",
                    "emoji_value": "??",
                    "display_name": "666",
                    "is_enabled": True,
                }
            ]
        }

    def fake_save_emoji_mapping(payload):
        captured["saved"] = payload
        return {
            "emoji_id": 2,
            "emoji_code": payload["emoji_code"],
            "emoji_type": payload["emoji_type"],
            "emoji_value": payload["emoji_value"],
            "display_name": payload["display_name"],
            "is_enabled": payload["is_enabled"],
        }

    monkeypatch.setattr("app.routers.tasks.list_emoji_mappings", fake_list_emoji_mappings)
    monkeypatch.setattr("app.routers.tasks.save_emoji_mapping", fake_save_emoji_mapping)

    list_response = client.get("/api/system/emojis?enabled_only=true")
    assert list_response.status_code == 200
    assert list_response.json()["emojis"][0]["emoji_code"] == "[666]"
    assert captured["enabled_only"] is True

    save_response = client.post(
        "/api/system/emojis",
        json={
            "emoji_code": "[??]",
            "emoji_type": "emoji",
            "emoji_value": "??",
            "display_name": "??",
            "is_enabled": True,
        },
    )

    assert save_response.status_code == 200
    assert save_response.json()["emoji_value"] == "??"
    assert captured["saved"]["emoji_code"] == "[??]"

def test_comment_user_ai_flow_api_returns_process_nodes(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)

    def fake_build_comment_user_ai_flow():
        return {
            "nodes": [
                {
                    "id": "select_users",
                    "order": 1,
                    "title": "选择用户范围",
                    "desc": "从评论用户资产中选择需要画像的用户。",
                    "function_name": "select_comment_users",
                    "input_tables": ["data_asset.dwd_comment"],
                    "output_tables": ["comment_user_id"],
                    "rules": ["默认使用全库评论"],
                    "metrics": {"comment_user_count": 77},
                    "status": "ready",
                }
            ],
            "summary": {"comment_user_count": 77, "profiled_user_count": 1},
        }

    monkeypatch.setattr("app.routers.tasks.build_comment_user_ai_flow", fake_build_comment_user_ai_flow)

    response = client.get("/api/profiles/comment-users/ai-flow")

    assert response.status_code == 200
    payload = response.json()
    assert payload["nodes"][0]["id"] == "select_users"
    assert payload["nodes"][0]["status"] == "ready"
    assert payload["summary"]["comment_user_count"] == 77


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
    assert run_response.json()["summary"]["dwd_comment"] == 248

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
    assert run_response.json()["summary"]["dwd_comment"] == 248


def test_voc_event_market_dashboard_api_returns_region_and_topic_sections(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)

    def fake_dashboard(event_id):
        return {
            "event": {"event_id": event_id, "event_name": "launch event"},
            "overview_metrics": {},
            "volume_trend": [],
            "channel_distribution": [],
            "kol_type_distribution": [],
            "comment_quality": {},
            "regional_response_story": {
                "summary": {"data_scope": "comment_location_only", "top_location": "Shanghai"},
                "locations": [{"location": "Shanghai", "comment_count": 12}],
                "top_contents": [],
            },
            "topic_spread_story": {
                "summary": {"top_topic": "SmartCabin", "topic_count": 1},
                "topics": [{"topic": "SmartCabin", "comment_count": 9}],
            },
            "hot_posts": [],
        }

    monkeypatch.setattr("app.routers.tasks.get_voc_event_market_dashboard", fake_dashboard)

    response = client.get("/api/voc/events/event_001/market-dashboard")

    assert response.status_code == 200
    payload = response.json()
    assert payload["regional_response_story"]["summary"]["data_scope"] == "comment_location_only"
    assert payload["topic_spread_story"]["summary"]["top_topic"] == "SmartCabin"
