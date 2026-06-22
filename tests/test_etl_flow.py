import pandas as pd

from app.services.etl_flow import build_flow_nodes
from etl.event_voc_ods_etl import standardize_comments


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


def test_standardize_comments_preserves_comment_label_json() -> None:
    ods_comment = pd.DataFrame(
        [
            {
                "content_id": "CONTENT-001",
                "content_source_url": "https://example.com/post",
                "platform": "抖音",
                "comment_author_name": "user_a",
                "comment_text": "这个价格很香",
                "published_at": "2026-06-01 10:00:00",
                "like_cnt": 3,
                "reply_cnt": 1,
                "comment_label_json": '{"is_vehicle_related":"是","comment_sentiment":"正向"}',
            }
        ]
    )
    dwd_content = pd.DataFrame(
        [
            {
                "content_id": "CONTENT-001",
                "platform": "抖音",
                "source_url": "https://example.com/post",
            }
        ]
    )

    dwd_comment, rejected_comment = standardize_comments(ods_comment, dwd_content, "batch_001")

    assert rejected_comment.empty
    assert dwd_comment.loc[0, "comment_label_json"] == '{"is_vehicle_related":"是","comment_sentiment":"正向"}'
