from __future__ import annotations

import json
import re

import pandas as pd
import pytest

import app.agents.competitor_report.renderer as competitor_renderer


def test_topic_account_network_uses_engagement_for_nodes_and_work_count_for_links() -> None:
    from app.agents.competitor_report.skill_generator import build_topic_account_network

    frame = pd.DataFrame(
        [
            {"作者": "品牌官方", "账号类型": "官方号", "是否官方号": "是", "话题标签": "#智能座舱", "总互动量": 100, "标题": "作品一"},
            {"作者": "品牌官方", "账号类型": "官方号", "是否官方号": "是", "话题标签": "#智能座舱", "总互动量": 80, "标题": "作品二"},
            {"作者": "门店A", "账号类型": "经销商", "是否官方号": "否", "话题标签": "#智能座舱 #空间", "总互动量": 40, "标题": "作品三"},
        ]
    )

    result = build_topic_account_network(frame)

    topic = next(item for item in result["topics"] if item["name"] == "智能座舱")
    official = next(item for item in result["accounts"] if item["name"] == "品牌官方")
    official_link = next(
        item
        for item in result["links"]
        if item["topic"] == "智能座舱" and item["account"] == "品牌官方"
    )
    assert topic["interaction_count"] == 220
    assert official["interaction_count"] == 180
    assert official["account_type"] == "official"
    assert official_link["work_count"] == 2
    assert official_link["interaction_count"] == 180


def test_topic_account_network_is_bounded_and_empty_without_original_tags() -> None:
    from app.agents.competitor_report.skill_generator import build_topic_account_network

    rows = []
    for topic_index in range(7):
        for account_index in range(25):
            rows.append(
                {
                    "作者": f"账号{account_index}",
                    "账号类型": "其他",
                    "是否官方号": "否",
                    "话题标签": f"#话题{topic_index}",
                    "总互动量": (topic_index + 1) * (account_index + 1),
                    "标题": "测试作品",
                }
            )

    result = build_topic_account_network(pd.DataFrame(rows))
    empty = build_topic_account_network(
        pd.DataFrame([{"作者": "无标签账号", "话题标签": "", "总互动量": 10, "标题": "无标签"}])
    )

    assert len(result["topics"]) == 5
    assert len(result["accounts"]) == 20
    assert empty["topics"] == []
    assert empty["accounts"] == []
    assert empty["links"] == []
    assert "暂无" in empty["message"]


def _sample_report_dataset() -> dict[str, object]:
    dataset = {
        "brand_name": "比亚迪&汽车",
        "start_date": "2026-07-01",
        "end_date": "2026-07-18",
        "overview": {
            "work_count": 1,
            "account_count": 1,
            "total_engagement": 50,
            "average_engagement": 50,
        },
        "daily_trend": [{"publish_date": "2026-07-10", "work_count": 1, "total_engagement": 50}],
        "account_contribution": [
            {
                "author_name": "官方账号",
                "account_type": "官方号",
                "is_official": True,
                "work_count": 1,
                "total_engagement": 50,
            }
        ],
        "topic_distribution": [{"topic": "新能源", "work_count": 1, "total_engagement": 50}],
        "top_works": [
            {
                "work_id": "w-001",
                "title": "车型亮点",
                "author_name": "官方账号",
                "brand_name": "比亚迪&汽车",
                "account_type": "官方号",
                "is_official": True,
                "published_at": "2026-07-10T10:00:00",
                "topic_tags": "新能源,发布会",
                "video_url": "https://example.test/w-001?x=1&y=2",
                "interaction_like_cnt": 30,
                "comment_cnt": 10,
                "favorite_cnt": 5,
                "share_cnt": 5,
                "total_engagement": 50,
                "insight_markdown": "无",
            }
        ],
        "data_notes": ["总互动量为互动点赞数、评论数、收藏数与分享数之和。"],
    }
    dataset["records"] = dataset["top_works"]
    return dataset


def _sample_llm_summary() -> dict[str, object]:
    return {
        "executive_summary": ["w-001 以 50 次互动排名第一。"],
        "top_work_findings": [{"work_id": "w-001", "why_it_matters": "互动量 50，排名第一。"}],
        "account_summary": "官方账号贡献 50 次互动。",
        "rhythm_summary": "7 月 10 日互动达到 50。",
        "dealer_summary": "经销商证据不足。",
    }


def test_fixed_html_renderer_consumes_all_dataset_sections_in_chapter_order() -> None:
    dataset = _sample_report_dataset()
    dataset["top_works"][0]["published_at"] = "2026-07-10<日>"
    dataset["top_works"][0]["author_name"] = "官方账号<img src=x>"
    dataset["top_works"][0]["account_type"] = "官方号&品牌"
    dataset["top_works"][0]["topic_tags"] = "#新能源<script>"
    dataset["data_notes"] = ["总互动口径含点赞、评论、收藏与分享 <不得省略> & 复核。"]

    html = competitor_renderer.render_competitor_report_html(dataset, _sample_llm_summary())

    chapters = [
        "核心发现",
        "Top3 热门作品",
        "账号互动贡献",
        "发布时间与互动走势",
        "上周该品牌相关热门话题",
        "话题传播网络",
        "官方发起 → 经销商承接 桑基图",
    ]
    positions = [html.index(f"<h2>{chapter}</h2>") for chapter in chapters]
    assert positions == sorted(positions)
    for expected in (
        "2026-07-10&lt;日&gt;",
        "官方账号&lt;img src=x&gt;",
        "新能源&lt;script&gt;",
        "总互动口径含点赞、评论、收藏与分享 &lt;不得省略&gt; &amp; 复核。",
    ):
        assert expected in html
    for unsafe in ("2026-07-10<日>", "官方账号<img src=x>", "新能源<script>", "<不得省略>"):
        assert unsafe not in html


def test_top_work_cards_render_topics_video_link_and_parsed_insight_sections() -> None:
    dataset = _sample_report_dataset()
    dataset["top_works"][0]["topic_tags"] = "#新能源 #发布会"
    dataset["top_works"][0]["insight_markdown"] = """\
## 视频介绍
车型外观采用 <流线设计> & 黑色饰条。
### 要点总结
- 空间表现突出
- 智能座舱升级
## 评论情绪
积极 & 中性
## 评论关键词
空间、座舱<script>
## 典型评论
“后排很宽敞 <b>认可</b>”
## 作者回复
感谢关注 & 欢迎试驾
"""

    html = competitor_renderer.render_competitor_report_html(dataset, _sample_llm_summary())

    for group in ("视频与评论洞察补充", "视频内容要点", "时间线摘要"):
        assert f"<h3>{group}</h3>" in html
    assert "<strong>原始话题：</strong>#新能源 #发布会" in html
    assert 'href="https://example.test/w-001?x=1&amp;y=2"' in html
    for value in (
        "车型外观采用 &lt;流线设计&gt; &amp; 黑色饰条。",
        "空间表现突出",
        "智能座舱升级",
        "积极 &amp; 中性",
        "“后排很宽敞 &lt;b&gt;认可&lt;/b&gt;”",
        "感谢关注 &amp; 欢迎试驾",
    ):
        assert value in html
    assert "<流线设计>" not in html
    assert "<b>认可</b>" not in html


def test_top_work_cards_keep_final_skill_missing_data_copy() -> None:
    dataset = _sample_report_dataset()
    dataset["top_works"][0].update({"topic_tags": "", "video_url": None, "insight_markdown": "无"})

    html = competitor_renderer.render_competitor_report_html(dataset, _sample_llm_summary())

    assert "<strong>原始话题：</strong>暂无原始话题" in html
    assert "视频与评论洞察补充" in html
    for label in ("视频介绍", "要点总结", "评论情绪", "评论关键词", "典型评论", "作者回复"):
        assert f"<dt>{label}</dt><dd>无</dd>" in html


@pytest.mark.parametrize("video_url", ["javascript:alert(1)", "data:text/html,<script>alert(1)</script>"])
def test_top_work_cards_do_not_create_links_for_unsafe_video_url_schemes(video_url: str) -> None:
    dataset = _sample_report_dataset()
    dataset["top_works"][0]["video_url"] = video_url

    html = competitor_renderer.render_competitor_report_html(dataset, _sample_llm_summary())

    assert video_url not in html


def test_renderer_uses_complete_mckinsey_report_and_local_echarts() -> None:
    rendered = competitor_renderer.render_competitor_report_html(
        _sample_report_dataset(),
        _sample_llm_summary(),
    )

    required_fragments = [
        "McKinsey Consulting",
        "Top3 热门作品",
        'id="authorChart"',
        'id="trendChart"',
        'id="topicChart"',
        'id="sankeyChart"',
        "账号互动贡献",
        "话题传播网络",
        "官方发起 → 经销商承接 桑基图",
    ]
    for fragment in required_fragments:
        assert fragment in rendered
    assert "cdn.jsdelivr.net" not in rendered
    assert "echarts.init" in rendered


def test_competitor_report_uses_big_force_and_consolidates_repeated_sections() -> None:
    rendered = competitor_renderer.render_competitor_report_html(
        _sample_report_dataset(),
        _sample_llm_summary(),
    )

    assert "renderTopicForceGraph" in rendered
    assert "FORCE GRAPH · TOPIC ACCOUNT NETWORK" in rendered
    assert "type: 'graph'" in rendered
    assert "layout: 'force'" in rendered
    assert "renderMode: 'richText'" in rendered
    assert "话题分类分布" not in rendered
    assert "<h2>重点经销商承接效果</h2>" not in rendered
    assert "最强承接账号" in rendered
    assert "覆盖话题最多账号" in rendered
    assert "低效承接账号" in rendered
    assert "cdn.jsdelivr.net" not in rendered


def test_competitor_report_uses_lieflat_tick_rows_for_author_contribution() -> None:
    rendered = competitor_renderer.render_competitor_report_html(
        _sample_report_dataset(),
        _sample_llm_summary(),
    )

    assert '<svg id="authorChart"' in rendered
    assert "TICK ROWS" in rendered
    assert "相对贡献刻度" in rendered
    assert "renderAuthorTickRows" in rendered
    assert "echarts.init(document.getElementById('authorChart'))" not in rendered


def test_competitor_report_uses_interactive_big_threads_for_dealer_paths() -> None:
    rendered = competitor_renderer.render_competitor_report_html(
        _sample_report_dataset(),
        _sample_llm_summary(),
    )

    assert '<svg id="sankeyChart"' in rendered
    assert "BIG THREADS" in rendered
    assert 'id="threadStatus"' in rendered
    assert "renderBigThreads" in rendered
    assert "thread-route" in rendered
    assert "PINNED" in rendered
    assert "echarts.init(document.getElementById('sankeyChart'))" not in rendered
    assert "type: 'sankey'" not in rendered


def _extract_parity_payload(rendered: str) -> dict[str, object]:
    kpis = dict(
        re.findall(
            r'<div class="label">([^<]+)</div><div class="value">([^<]+)</div>',
            rendered,
        )
    )
    work_ids = re.findall(r'<article class="hot-card" data-work-id="([^"]+)"', rendered)
    report_data_match = re.search(r"const reportData = (\{.+?\});", rendered)
    assert report_data_match is not None
    return {
        "kpis": kpis,
        "work_ids": work_ids,
        "report_data": json.loads(report_data_match.group(1)),
    }


def test_database_records_and_excel_rows_have_identical_report_payload(tmp_path) -> None:
    from app.agents.competitor_report.skill_generator import (
        build_html,
        generate_html_from_records,
        prepare_top_hot_df,
        prepare_works_df,
        summarize_hot_topics,
    )

    records = [
        {
            "work_id": "w-001",
            "title": "智能新车发布会",
            "author_name": "A&B 官方账号",
            "brand_name": "比亚迪",
            "account_type": "官方号",
            "is_official": True,
            "published_at": "2026-07-10T10:00:00",
            "topic_tags": "#智能 #发布会",
            "video_url": "https://example.test/w-001",
            "interaction_like_cnt": 30,
            "comment_cnt": 10,
            "favorite_cnt": 5,
            "share_cnt": 5,
        },
        {
            "work_id": "w-002",
            "title": "门店智能试驾",
            "author_name": "华东经销商",
            "brand_name": "比亚迪",
            "account_type": "经销商",
            "is_official": False,
            "published_at": "2026-07-11T10:00:00",
            "topic_tags": "#智能 #发布会",
            "video_url": "https://example.test/w-002",
            "interaction_like_cnt": 20,
            "comment_cnt": 5,
            "favorite_cnt": 3,
            "share_cnt": 2,
        },
        {
            "work_id": "w-003",
            "title": "家庭空间体验",
            "author_name": "用户账号",
            "brand_name": "比亚迪",
            "account_type": "用户",
            "is_official": False,
            "published_at": "2026-07-12T10:00:00",
            "topic_tags": "#家庭",
            "video_url": "https://example.test/w-003",
            "interaction_like_cnt": 10,
            "comment_cnt": 5,
            "favorite_cnt": 3,
            "share_cnt": 2,
        },
        {
            "work_id": "w-004",
            "title": "服务保障",
            "author_name": "服务账号",
            "brand_name": "比亚迪",
            "account_type": "服务号",
            "is_official": False,
            "published_at": "2026-07-13T10:00:00",
            "topic_tags": "#服务",
            "video_url": "https://example.test/w-004",
            "interaction_like_cnt": 1,
            "comment_cnt": 1,
            "favorite_cnt": 1,
            "share_cnt": 1,
        },
    ]
    excel_rows = pd.DataFrame(
        [
            {
                "作品ID": row["work_id"],
                "标题": row["title"],
                "作者": row["author_name"],
                "品牌": row["brand_name"],
                "账号类型": row["account_type"],
                "是否官方号": "是" if row["is_official"] else "否",
                "发布时间": row["published_at"],
                "话题标签": row["topic_tags"],
                "视频链接": row["video_url"],
                "互动点赞数": row["interaction_like_cnt"],
                "评论数": row["comment_cnt"],
                "收藏数": row["favorite_cnt"],
                "分享数": row["share_cnt"],
            }
            for row in records
        ]
    )
    excel_path = tmp_path / "works.xlsx"
    excel_rows.to_excel(excel_path, index=False)

    works_df = prepare_works_df(excel_path)
    top_df = prepare_top_hot_df(works_df)
    excel_html = build_html(
        "比亚迪",
        works_df,
        top_df,
        pd.DataFrame(),
        summarize_hot_topics(works_df),
        excel_path.name,
        style_key="mckinsey",
    )
    records_html = generate_html_from_records(
        records,
        brand_name="比亚迪",
        output_name=excel_path.name,
        video_insights_by_work_id={},
    )

    assert _extract_parity_payload(records_html) == _extract_parity_payload(excel_html)
    assert _extract_parity_payload(records_html)["report_data"]["author_labels"][0] == "A&B 官方账号"


def test_dataframe_html_and_embedded_json_escape_injection_at_output_sinks() -> None:
    from app.agents.competitor_report.skill_generator import (
        build_html,
        prepare_top_hot_df,
        summarize_hot_topics,
    )

    marker = '</script><script id="xss">alert(1)</script>\u2028\u2029'
    works_df = pd.DataFrame(
        [
            {
                "作品ID": "w-xss",
                "标题": marker,
                "作者": marker,
                "品牌": "安全测试",
                "账号类型": "官方号",
                "是否官方号": "是",
                "发布时间": marker,
                "发布日": "2026-07-10",
                "话题标签": f"#{marker}",
                "主题分类": marker,
                "视频链接": 'javascript:alert(1)',
                "封面图路径": '" onerror="alert(1)',
                "互动点赞数": 1,
                "评论数": 1,
                "收藏数": 1,
                "分享数": 1,
                "总互动量": 4,
            }
        ]
    )

    rendered = build_html(
        "安全测试",
        works_df,
        prepare_top_hot_df(works_df),
        pd.DataFrame([{"标题": marker, "评论": marker, "昵称": marker}]),
        summarize_hot_topics(works_df),
        "xss.xlsx",
    )

    assert '<script id="xss">' not in rendered
    assert '&lt;/script&gt;&lt;script id=&quot;xss&quot;&gt;' in rendered
    assert '" onerror="alert(1)' not in rendered
    assert "javascript:alert(1)" not in rendered
    report_data_match = re.search(r"const reportData = (\{.+?\});", rendered)
    assert report_data_match is not None
    serialized = report_data_match.group(1)
    assert "</script" not in serialized.lower()
    assert "<" not in serialized
    assert "\u2028" not in serialized
    assert "\u2029" not in serialized
    assert "\\u2028" in serialized
    assert "\\u2029" in serialized
    assert json.loads(serialized)["author_labels"] == [marker]


def test_excel_total_engagement_is_recomputed_from_four_components(tmp_path) -> None:
    from app.agents.competitor_report.skill_generator import prepare_top_hot_df, prepare_works_df

    row = {
        "作品ID": "w-001",
        "标题": "指标校验",
        "作者": "账号",
        "品牌": "比亚迪",
        "发布时间": "2026-07-10",
        "互动点赞数": 1,
        "评论数": 1,
        "收藏数": 1,
        "分享数": 1,
        "总互动量": 999,
    }
    works_path = tmp_path / "works.xlsx"
    top_path = tmp_path / "top.xlsx"
    pd.DataFrame([row]).to_excel(works_path, index=False)
    pd.DataFrame([row]).to_excel(top_path, index=False)

    works_df = prepare_works_df(works_path)
    top_df = prepare_top_hot_df(works_df, top_hot_path=top_path)

    assert works_df.loc[0, "总互动量"] == 4
    assert top_df.loc[0, "总互动量"] == 4


def test_top3_ties_are_stable_by_work_id_regardless_of_input_order() -> None:
    from app.agents.competitor_report.skill_generator import generate_html_from_records

    records = [
        {
            "work_id": f"w-{index}",
            "title": "同分作品",
            "author_name": "同一账号",
            "brand_name": "比亚迪",
            "account_type": "媒体",
            "is_official": False,
            "published_at": "2026-07-10T10:00:00",
            "topic_tags": "#同分",
            "video_url": f"https://example.test/w-{index}",
            "interaction_like_cnt": 1,
            "comment_cnt": 1,
            "favorite_cnt": 1,
            "share_cnt": 1,
        }
        for index in (4, 3, 2, 1)
    ]

    forward = generate_html_from_records(
        records,
        brand_name="比亚迪",
        output_name="records",
        video_insights_by_work_id={},
    )
    reverse = generate_html_from_records(
        list(reversed(records)),
        brand_name="比亚迪",
        output_name="records",
        video_insights_by_work_id={},
    )

    assert _extract_parity_payload(forward)["work_ids"] == ["w-1", "w-2", "w-3"]
    assert _extract_parity_payload(reverse)["work_ids"] == ["w-1", "w-2", "w-3"]


def test_renderer_uses_full_scope_records_instead_of_top3_for_kpis_and_charts() -> None:
    dataset = _sample_report_dataset()
    records = []
    for index in range(1, 6):
        records.append(
            {
                **dataset["top_works"][0],
                "work_id": f"w-{index:03d}",
                "title": f"作品 {index}",
                "author_name": f"账号 {index}",
                "interaction_like_cnt": 10,
                "comment_cnt": 0,
                "favorite_cnt": 0,
                "share_cnt": 0,
                "total_engagement": 10,
            }
        )
    dataset["records"] = records
    dataset["top_works"] = records[:3]
    dataset["overview"] = {
        "work_count": 5,
        "account_count": 5,
        "total_engagement": 50,
        "average_engagement": 10,
    }

    rendered = competitor_renderer.render_competitor_report_html(dataset, _sample_llm_summary())
    payload = _extract_parity_payload(rendered)

    assert payload["kpis"]["本周新增作品"] == "5"
    assert payload["kpis"]["总互动量"] == "50"
    assert len(payload["report_data"]["author_labels"]) == 5
    assert payload["work_ids"] == ["w-001", "w-002", "w-003"]


def test_renderer_rejects_partial_top3_when_full_scope_records_are_missing() -> None:
    dataset = _sample_report_dataset()
    dataset.pop("records")
    dataset["overview"]["work_count"] = 10

    with pytest.raises(ValueError, match="full-scope"):
        competitor_renderer.render_competitor_report_html(dataset, _sample_llm_summary())


def test_renderer_rejects_explicit_empty_full_records_for_positive_overview(monkeypatch) -> None:
    dataset = _sample_report_dataset()
    monkeypatch.setattr(
        competitor_renderer,
        "generate_html_from_records",
        lambda *args, **kwargs: pytest.fail("empty full records must not reach generator"),
    )

    with pytest.raises(ValueError, match="full-scope"):
        competitor_renderer.render_competitor_report_html(
            dataset,
            _sample_llm_summary(),
            records=[],
        )


def test_compatibility_summary_is_visible_in_matching_mckinsey_modules() -> None:
    summary = {
        "executive_summary": ["EXEC-VISIBLE"],
        "top_work_findings": [{"work_id": "w-001", "why_it_matters": "TOP-VISIBLE"}],
        "account_summary": "ACCOUNT-VISIBLE",
        "rhythm_summary": "RHYTHM-VISIBLE",
        "dealer_summary": "DEALER-VISIBLE",
    }

    rendered = competitor_renderer.render_competitor_report_html(_sample_report_dataset(), summary)

    for marker in (
        "EXEC-VISIBLE",
        "TOP-VISIBLE",
        "ACCOUNT-VISIBLE",
        "RHYTHM-VISIBLE",
        "DEALER-VISIBLE",
    ):
        assert marker in rendered
    assert "aria-hidden" not in rendered
    assert "sr-only" not in rendered


def test_top_work_selection_reason_is_styled_inside_hot_body() -> None:
    rendered = competitor_renderer.render_competitor_report_html(
        _sample_report_dataset(),
        _sample_llm_summary(),
    )

    card = re.search(
        r'<article class="hot-card" data-work-id="w-001">(.*?)</article>',
        rendered,
        flags=re.DOTALL,
    )
    assert card is not None
    card_html = card.group(1)
    selection_position = card_html.index('<p class="selection-reason">')
    assert selection_position < card_html.rfind('</div>')
    assert re.search(r'\.selection-reason\s*\{[^}]+\}', rendered)
