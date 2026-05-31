from app.services.etl_flow import build_flow_nodes


def test_build_flow_nodes_returns_transparent_etl_steps() -> None:
    nodes = build_flow_nodes()

    assert nodes[0]["id"] == "upload"
    assert nodes[0]["title"] == "原始上传文件"
    assert any(node["function_name"] == "standardize_comments" for node in nodes)
    assert nodes[-1]["id"] == "postgres_load"


def test_build_flow_nodes_enriches_counts_from_summary() -> None:
    nodes = build_flow_nodes(
        {
            "ods_event_upload": 1,
            "ods_content_upload": 25,
            "dwd_comment": 19,
            "ads_event_overview": 1,
        }
    )

    ods_node = next(node for node in nodes if node["id"] == "ods")
    comment_node = next(node for node in nodes if node["id"] == "standardize_comment")

    assert ods_node["metrics"]["ods_event_upload"] == 1
    assert ods_node["metrics"]["ods_content_upload"] == 25
    assert comment_node["metrics"]["dwd_comment"] == 19
