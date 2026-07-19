from __future__ import annotations

import pytest

import app.agents.competitor_report.renderer as competitor_renderer


def _sample_report_dataset() -> dict[str, object]:
    return {
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
    dataset["daily_trend"] = [
        {"publish_date": "2026-07-10<日>", "work_count": 1, "total_engagement": 50},
    ]
    dataset["account_contribution"] = [
        {
            "author_name": "官方账号<img src=x>",
            "account_type": "官方号&品牌",
            "is_official": True,
            "work_count": 1,
            "total_engagement": 50,
        },
    ]
    dataset["topic_distribution"] = [
        {"topic": "新能源<script>", "work_count": 1, "total_engagement": 50},
    ]
    dataset["data_notes"] = ["总互动口径含点赞、评论、收藏与分享 <不得省略> & 复核。"]

    html = competitor_renderer.render_competitor_report_html(dataset, _sample_llm_summary())

    chapters = [
        "本期概览",
        "核心发现",
        "Top3 热门作品",
        "账号互动贡献",
        "发布时间与互动走势",
        "原始话题与主题分布",
        "经销商承接效果",
        "数据口径和证据说明",
    ]
    positions = [html.index(f"<h2>{chapter}</h2>") for chapter in chapters]
    assert positions == sorted(positions)
    for expected in (
        "2026-07-10&lt;日&gt;",
        "官方账号&lt;img src=x&gt;",
        "官方号&amp;品牌",
        "新能源&lt;script&gt;",
        "总互动口径含点赞、评论、收藏与分享 &lt;不得省略&gt; &amp; 复核。",
    ):
        assert expected in html
    for unsafe in ("2026-07-10<日>", "官方账号<img src=x>", "新能源<script>", "<不得省略>"):
        assert unsafe not in html


def test_top_work_cards_render_topics_video_link_and_parsed_insight_sections() -> None:
    dataset = _sample_report_dataset()
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

    for group in ("视频基本信息", "视频内容解析", "评论解析"):
        assert f"<h4>{group}</h4>" in html
    assert "<dt>主题</dt><dd>新能源,发布会</dd>" in html
    assert 'href="https://example.test/w-001?x=1&amp;y=2"' in html
    assert ">查看原视频</a>" in html
    expected_sections = {
        "视频介绍": "车型外观采用 &lt;流线设计&gt; &amp; 黑色饰条。",
        "要点总结": "- 空间表现突出<br>- 智能座舱升级",
        "评论情绪": "积极 &amp; 中性",
        "评论关键词": "空间、座舱&lt;script&gt;",
        "典型评论": "“后排很宽敞 &lt;b&gt;认可&lt;/b&gt;”",
        "作者回复": "感谢关注 &amp; 欢迎试驾",
    }
    for label, value in expected_sections.items():
        assert f"<dt>{label}</dt><dd>{value}</dd>" in html
    assert "<流线设计>" not in html
    assert "座舱<script>" not in html
    assert "<b>认可</b>" not in html


def test_top_work_cards_show_none_for_each_missing_topic_link_and_insight_field() -> None:
    dataset = _sample_report_dataset()
    dataset["top_works"][0].update({"topic_tags": "", "video_url": None, "insight_markdown": "无"})

    html = competitor_renderer.render_competitor_report_html(dataset, _sample_llm_summary())

    for label in (
        "主题",
        "视频链接",
        "视频介绍",
        "要点总结",
        "评论情绪",
        "评论关键词",
        "典型评论",
        "作者回复",
    ):
        assert f"<dt>{label}</dt><dd>无</dd>" in html


@pytest.mark.parametrize("video_url", ["javascript:alert(1)", "data:text/html,<script>alert(1)</script>"])
def test_top_work_cards_do_not_create_links_for_unsafe_video_url_schemes(video_url: str) -> None:
    dataset = _sample_report_dataset()
    dataset["top_works"][0]["video_url"] = video_url

    html = competitor_renderer.render_competitor_report_html(dataset, _sample_llm_summary())

    assert "<dt>视频链接</dt><dd>无</dd>" in html
    assert video_url not in html
