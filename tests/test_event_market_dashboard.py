from app.services import event_voc_insights


def test_market_dashboard_payload_uses_real_sections(monkeypatch) -> None:
    def fake_overview(conn, event_id):
        return {
            "event_id": event_id,
            "event_name": "IDT6上市",
            "brand_name": "一汽大众",
            "model_name": "ID.AURA T6",
            "event_type": "新品上市",
            "event_status": "进行中",
            "start_time": "2026-05-14T00:00:00",
            "end_time": "2026-05-20T00:00:00",
            "content_cnt": 25,
            "comment_cnt": 19,
            "kol_content_cnt": 6,
            "total_engagement": 65692,
        }

    monkeypatch.setattr(event_voc_insights, "fetch_event_overview", fake_overview)
    monkeypatch.setattr(
        event_voc_insights,
        "fetch_event_volume_trend",
        lambda conn, event_id: [{"date": "2026-05-14", "content_count": 2, "comment_count": 3, "total_volume": 5}],
    )
    monkeypatch.setattr(
        event_voc_insights,
        "fetch_event_channel_distribution",
        lambda conn, event_id: [{"channel": "抖音", "content_count": 10, "comment_count": 8, "total_volume": 18}],
    )
    monkeypatch.setattr(
        event_voc_insights,
        "fetch_event_kol_type_distribution",
        lambda conn, event_id: [{"kol_main_type": "车型实测测评KOL", "kol_count": 2, "content_count": 4, "total_engagement": 1200}],
    )
    monkeypatch.setattr(
        event_voc_insights,
        "fetch_event_hot_posts",
        lambda conn, event_id: [{"content_id": "c1", "title": "试驾体验", "total_engagement": 999}],
    )
    monkeypatch.setattr(
        event_voc_insights,
        "fetch_latest_comment_user_profiles",
        lambda conn, event_id: [{"main_label": "价格敏感"}, {"main_label": "价格敏感"}, {"main_label": "空间关注"}],
    )

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(event_voc_insights.psycopg, "connect", lambda *args, **kwargs: FakeConnection())

    payload = event_voc_insights.get_voc_event_market_dashboard("event_001")

    assert payload["event"]["event_id"] == "event_001"
    assert payload["overview_metrics"] == {
        "total_volume": 44,
        "content_count": 25,
        "comment_count": 19,
        "kol_count": 2,
        "kol_content_count": 6,
        "total_engagement": 65692,
    }
    assert payload["volume_trend"][0]["total_volume"] == 5
    assert payload["channel_distribution"][0]["channel"] == "抖音"
    assert payload["kol_type_distribution"][0]["kol_main_type"] == "车型实测测评KOL"
    assert payload["user_profile_distribution"][0] == {"main_label": "价格敏感", "user_cnt": 2}
    assert payload["hot_posts"][0]["title"] == "试驾体验"
