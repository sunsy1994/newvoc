import json
import re
import subprocess
from functools import lru_cache
from pathlib import Path


def test_root_route_redirects_to_auto_voc_home() -> None:
    root_page = Path("frontend/src/app/page.tsx").read_text(encoding="utf-8")

    assert 'redirect("/auto-voc")' in root_page
    assert 'redirect("/voc/events/market")' not in root_page


def test_next_frontend_uses_app_router_src_tailwind_and_typed_navigation() -> None:
    root = Path("frontend")

    assert (root / "package.json").exists()
    assert (root / "next.config.mjs").exists()
    assert (root / "tailwind.config.ts").exists()
    assert (root / "src/app/layout.tsx").exists()
    assert (root / "src/app/page.tsx").exists()
    assert (root / "src/app/voc/events/market/page.tsx").exists()
    assert (root / "src/app/globals.css").exists()

    navigation = (root / "src/config/navigation.ts").read_text(encoding="utf-8")
    assert "export const navigation" in navigation
    assert "VOC看事件" in navigation
    assert "市场看板" in navigation
    assert "raw" not in navigation.lower()

    primary_nav = (root / "src/components/sidebar/PrimaryNav.tsx").read_text(encoding="utf-8")
    secondary_nav = (root / "src/components/sidebar/SecondaryNav.tsx").read_text(encoding="utf-8")
    sidebar = (root / "src/components/sidebar/Sidebar.tsx").read_text(encoding="utf-8")
    nav_item = (root / "src/components/sidebar/NavItem.tsx").read_text(encoding="utf-8")

    assert "usePathname" in primary_nav
    assert "usePathname" in secondary_nav
    assert "grid-cols-[124px_1fr]" in sidebar
    assert "bg-[var(--sys-icon-fill)] text-white" in nav_item
    assert "bg-[var(--sys-card)] text-[var(--sys-ink)]" in nav_item


def test_frontend_navigation_components_are_small_and_data_driven() -> None:
    root = Path("frontend")
    for relative_path in [
        "src/components/layout/AppShell.tsx",
        "src/components/sidebar/Sidebar.tsx",
        "src/components/sidebar/PrimaryNav.tsx",
        "src/components/sidebar/SecondaryNav.tsx",
        "src/components/sidebar/NavItem.tsx",
    ]:
        text = (root / relative_path).read_text(encoding="utf-8")
        assert len(text.splitlines()) <= 90

    primary_nav = (root / "src/components/sidebar/PrimaryNav.tsx").read_text(encoding="utf-8")
    assert "navigation.map" in primary_nav
    assert "VOC看事件" not in primary_nav


def test_next_frontend_proxies_backend_api_and_has_pages_for_navigation_links() -> None:
    root = Path("frontend")
    next_config = (root / "next.config.mjs").read_text(encoding="utf-8")
    navigation = (root / "src/config/navigation.ts").read_text(encoding="utf-8")

    assert "rewrites" in next_config
    assert "http://127.0.0.1:8000/api/:path*" in next_config

    expected_pages = [
        "src/app/voc/events/product/page.tsx",
        "src/app/voc/events/content/page.tsx",
        "src/app/voc/events/kol-users/page.tsx",
        "src/app/tasks/flow/page.tsx",
        "src/app/tasks/ai-profile-flow/page.tsx",
        "src/app/tasks/scripts/page.tsx",
        "src/app/assets/contents/page.tsx",
        "src/app/assets/comments/page.tsx",
        "src/app/assets/authors/page.tsx",
        "src/app/assets/kols/page.tsx",
        "src/app/assets/comment-users/page.tsx",
        "src/app/assets/reports/page.tsx",
        "src/app/competitors/accounts/page.tsx",
        "src/app/competitors/works/page.tsx",
        "src/app/profiles/kols/page.tsx",
        "src/app/profiles/comment-users/page.tsx",
        "src/app/system/parameters/page.tsx",
        "src/app/system/prompts/page.tsx",
        "src/app/system/emojis/page.tsx",
        "src/app/system/agent-error-questions/page.tsx",
        "src/app/system/data-lineage/page.tsx",
    ]
    for page in expected_pages:
        assert (root / page).exists()

    assert "apiBaseUrl" in navigation
    assert "serverApiBaseUrl" in navigation
    assert "http://127.0.0.1:8000/api" in navigation
    assert "市场看板" in navigation
    assert "/voc/events/product" in navigation
    assert "/assets/comment-users" in navigation
    assert "/assets/reports" in navigation
    assert "/system/parameters" in navigation
    assert "/system/prompts" in navigation
    assert "/system/emojis" in navigation
    assert "/system/agent-error-questions" in navigation
    assert "/system/data-lineage" in navigation
    assert "/tasks/ai-profile-flow" in navigation
    assert "传播内容" not in navigation
    assert "KOL与用户" not in navigation

    market_page = (root / "src/app/voc/events/market/page.tsx").read_text(encoding="utf-8")
    assert "serverApiBaseUrl" in market_page
    assert "/market-dashboard" in market_page


def test_system_management_pages_use_real_api_components() -> None:
    root = Path("frontend")
    globals_css = (root / "src/app/globals.css").read_text(encoding="utf-8")
    navigation = (root / "src/config/navigation.ts").read_text(encoding="utf-8")
    parameter_page = (root / "src/app/system/parameters/page.tsx").read_text(encoding="utf-8")
    prompt_page = (root / "src/app/system/prompts/page.tsx").read_text(encoding="utf-8")
    emoji_page = (root / "src/app/system/emojis/page.tsx").read_text(encoding="utf-8")
    error_page = (root / "src/app/system/agent-error-questions/page.tsx").read_text(encoding="utf-8")
    lineage_page = (root / "src/app/system/data-lineage/page.tsx").read_text(encoding="utf-8")
    component = (root / "src/components/system/SystemSettingsPage.tsx").read_text(encoding="utf-8")
    emoji_component = (root / "src/components/system/EmojiDictionaryPage.tsx").read_text(encoding="utf-8")
    error_component = (root / "src/components/system/AgentErrorQuestionPage.tsx").read_text(encoding="utf-8")
    lineage_component = (root / "src/components/system/DataLineagePage.tsx").read_text(encoding="utf-8")

    assert "系统管理" in navigation
    assert "参数维护" in navigation
    assert "提示词维护" in navigation
    assert "表情包维护" in navigation
    assert "异常问题记录" in navigation
    assert "数据血缘维护" in navigation
    assert "SystemSettingsPage" in parameter_page
    assert "SystemSettingsPage" in prompt_page
    assert "EmojiDictionaryPage" in emoji_page
    assert "AgentErrorQuestionPage" in error_page
    assert "DataLineagePage" in lineage_page
    assert "/system/agent-error-questions" in error_component
    assert "异常问题记录" in error_component
    assert "/system/data-lineage" in lineage_component
    assert "upstream" in lineage_component
    assert "downstream" in lineage_component
    assert "business_definition" in lineage_component
    assert "generation_type" in lineage_component
    assert "is_system" in lineage_component
    assert "createNode" in lineage_component
    assert "新增人工节点" in lineage_component
    assert "data-lineage-overlay" in lineage_component
    assert "data-lineage-modal-surface" in lineage_component
    assert "data-lineage-drawer-surface" in lineage_component
    assert ".data-lineage-overlay" in globals_css
    assert "background-color: var(--sys-input-bg)" in globals_css
    assert "DataPagination" in lineage_component
    assert "visibleNodes" in lineage_component
    assert "DataPagination" in emoji_component
    assert "visibleEmojis" in emoji_component
    assert "DataPagination" in error_component
    assert "visibleRecords" in error_component
    assert 'mode="parameters"' in parameter_page
    assert 'mode="prompts"' in prompt_page
    assert "/system/ai-config" in component
    assert "/system/prompts" in component
    assert "/system/emojis" in emoji_component
    assert "emoji_code" in emoji_component
    assert "emoji_value" in emoji_component
    assert "emoji_type" in emoji_component
    assert "预览" in emoji_component
    assert "PROFILE_AI_API_KEY" in component
    assert "comment_user_profile" in component
    assert "market_report_summary" in component
    assert "selectedPromptScene" in component
    assert "<textarea" in component
    assert "留空则保持当前密钥" in component


def test_comment_views_render_emoji_text_component() -> None:
    root = Path("frontend")
    emoji_text = (root / "src/components/common/EmojiText.tsx").read_text(encoding="utf-8")
    market_card = (root / "src/components/voc/CommentQualityStoryCard.tsx").read_text(encoding="utf-8")
    post_modal = (root / "src/components/voc/PostDetailModal.tsx").read_text(encoding="utf-8")
    types = (root / "src/types/system.ts").read_text(encoding="utf-8")

    assert "EmojiMapping" in types
    assert "tokenizeCommentText" in emoji_text
    assert "/system/emojis" in emoji_text
    assert 'emoji_type === "image"' in emoji_text
    assert "CommentTextWithEmojis" in market_card
    assert "CommentTextWithEmojis" in post_modal


def test_profile_pages_use_real_api_component_and_shared_design_doc() -> None:
    root = Path("frontend")
    design_doc = Path("docs/design.md").read_text(encoding="utf-8")
    profile_component = (root / "src/components/profiles/ProfileMaintenancePage.tsx").read_text(encoding="utf-8")
    kol_page = (root / "src/app/profiles/kols/page.tsx").read_text(encoding="utf-8")
    comment_user_page = (root / "src/app/profiles/comment-users/page.tsx").read_text(encoding="utf-8")

    assert "#5347CE" in design_doc
    assert "#4896FE" in design_doc
    assert "ProfileMaintenancePage" in kol_page
    assert "ProfileMaintenancePage" in comment_user_page
    assert "PlaceholderPage" not in kol_page
    assert "PlaceholderPage" not in comment_user_page
    assert "/profiles/kols" in kol_page
    assert "/profiles/comment-users" in comment_user_page
    assert "fetch(buildApiUrl(config.listEndpoint" in profile_component
    assert "FormData" in profile_component


def test_competitor_pages_use_real_api_component_and_filters() -> None:
    root = Path("frontend")
    competitor_component = (root / "src/components/competitors/CompetitorLibraryPage.tsx").read_text(encoding="utf-8")
    account_page = (root / "src/app/competitors/accounts/page.tsx").read_text(encoding="utf-8")
    work_page = (root / "src/app/competitors/works/page.tsx").read_text(encoding="utf-8")

    assert "CompetitorLibraryPage" in account_page
    assert "CompetitorLibraryPage" in work_page
    assert "PlaceholderPage" not in account_page
    assert "PlaceholderPage" not in work_page
    assert "/competitors/accounts" in account_page
    assert "/competitors/works" in work_page
    assert "/competitors/options" in competitor_component
    assert "brand_name" in competitor_component
    assert "start_date" in competitor_component
    assert "end_date" in competitor_component


def test_competitor_work_insight_editor_is_limited_to_works_mode() -> None:
    component = Path("frontend/src/components/competitors/CompetitorLibraryPage.tsx").read_text(encoding="utf-8")

    assert "/competitors/works/${encodeURIComponent(workId)}/insight" in component
    assert "维护解读" in component
    assert "已维护" in component
    assert "未维护" in component
    assert "<textarea" in component
    assert "保存解读" in component
    assert "清空解读" in component
    action_start = component.index("onClick={() => openInsight(row)}")
    action_guard_start = component.rfind('{config.mode === "works" ? (', 0, action_start)
    action_guard_end = component.index(") : null}", action_start)
    assert action_guard_start != -1
    assert action_start < action_guard_end
    assert '{config.mode === "works" && selectedWork ? (' in component
    assert 'role="dialog"' in component
    assert 'aria-label="作品解读 Markdown"' in component
    assert 'role="alert"' in component
    assert "onKeyDown={trapInsightFocus}" in component
    assert "insightTextareaRef.current?.focus()" in component
    assert "insightTriggerRefs.current[workId]?.focus()" in component


def test_competitor_work_insight_editor_prefills_the_fixed_markdown_template() -> None:
    component = Path("frontend/src/components/competitors/CompetitorLibraryPage.tsx").read_text(encoding="utf-8")

    assert "const competitorInsightMarkdownTemplate =" in component
    for heading in ("## 视频介绍", "## 要点总结", "## 评论情绪", "## 评论关键词", "## 典型评论", "## 作者回复"):
        assert heading in component
    assert (
        "setInsightMarkdown(insight.insight_markdown?.trim() "
        "? insight.insight_markdown : competitorInsightMarkdownTemplate)"
    ) in component
    assert "if (clear) setInsightMarkdown(competitorInsightMarkdownTemplate)" in component
    assert "报告按以下六个固定标题读取内容，请勿修改标题名称。" in component
    assert "插入标准模板" not in component


def test_competitor_work_insight_get_ignores_stale_responses_after_switch_or_close() -> None:
    component = Path("frontend/src/components/competitors/CompetitorLibraryPage.tsx").read_text(encoding="utf-8")
    open_start = component.index("async function openInsight")
    open_end = component.index("async function saveInsight", open_start)
    open_insight = component[open_start:open_end]
    close_start = component.index("function closeInsight")
    close_end = component.index("function trapInsightFocus", close_start)
    close_insight = component[close_start:close_end]

    assert "const insightRequestSequenceRef = useRef(0)" in component
    assert 'const selectedInsightWorkIdRef = useRef("")' in component
    assert "const requestSequence = ++insightRequestSequenceRef.current" in open_insight
    assert "selectedInsightWorkIdRef.current = workId" in open_insight
    assert "requestSequence === insightRequestSequenceRef.current" in open_insight
    assert "selectedInsightWorkIdRef.current === workId" in open_insight
    assert open_insight.count("isCurrentRequest()") >= 3
    assert "insightRequestSequenceRef.current += 1" in close_insight
    assert 'selectedInsightWorkIdRef.current = ""' in close_insight


def test_competitor_work_insight_save_ignores_completion_after_switch_or_close() -> None:
    component = Path("frontend/src/components/competitors/CompetitorLibraryPage.tsx").read_text(encoding="utf-8")
    save_start = component.index("async function saveInsight")
    save_end = component.index("function closeInsight", save_start)
    save_insight = component[save_start:save_end]

    assert "const requestSequence = ++insightRequestSequenceRef.current" in save_insight
    assert "selectedInsightWorkIdRef.current === workId" in save_insight
    assert save_insight.count("isCurrentRequest()") >= 3


def test_competitor_work_insight_close_and_reopen_reset_saving_state_safely() -> None:
    component = Path("frontend/src/components/competitors/CompetitorLibraryPage.tsx").read_text(encoding="utf-8")
    open_start = component.index("async function openInsight")
    open_end = component.index("async function saveInsight", open_start)
    open_insight = component[open_start:open_end]
    close_start = component.index("function closeInsight")
    close_end = component.index("function trapInsightFocus", close_start)
    close_insight = component[close_start:close_end]

    assert "setIsInsightSaving(false)" in open_insight
    assert "setIsInsightSaving(false)" in close_insight
    assert close_insight.index("insightRequestSequenceRef.current += 1") < close_insight.index("setIsInsightSaving(false)")


def test_retryable_agent_failure_has_explicit_retry_action_without_readding_user_message() -> None:
    home = Path("frontend/src/components/home/AutoVocHomePage.tsx").read_text(encoding="utf-8")
    messages = Path("frontend/src/components/home/ChatMessageList.tsx").read_text(encoding="utf-8")

    assert "retryQuestion" in home
    assert "retryCapability" in home
    assert "appendUserMessage: false" in home
    assert "onRetry" in messages
    assert "重试生成" in messages


def test_competitor_work_insight_urls_encode_work_id_path_segments() -> None:
    component = Path("frontend/src/components/competitors/CompetitorLibraryPage.tsx").read_text(encoding="utf-8")

    encoded_path = "/competitors/works/${encodeURIComponent(workId)}/insight"
    assert component.count(encoded_path) == 3
    assert "/competitors/works/${workId}/insight" not in component


def test_asset_pages_use_real_api_component_and_exports() -> None:
    root = Path("frontend")
    asset_component = (root / "src/components/assets/AssetLibraryPage.tsx").read_text(encoding="utf-8")
    expected_assets = {
        "events": "src/app/assets/events/page.tsx",
        "contents": "src/app/assets/contents/page.tsx",
        "comments": "src/app/assets/comments/page.tsx",
        "authors": "src/app/assets/authors/page.tsx",
        "kols": "src/app/assets/kols/page.tsx",
        "comment_users": "src/app/assets/comment-users/page.tsx",
        "reports": "src/app/assets/reports/page.tsx",
    }

    for asset_key, relative_path in expected_assets.items():
        page = (root / relative_path).read_text(encoding="utf-8")
        assert "AssetLibraryPage" in page
        assert "PlaceholderPage" not in page
        assert f'assetKey: "{asset_key}"' in page

    assert "fetch(buildApiUrl(`/assets/${config.assetKey}`" in asset_component
    assert "`/assets/${config.assetKey}/export`" in asset_component
    assert "报告资产" in (root / "src/app/assets/reports/page.tsx").read_text(encoding="utf-8")
    assert "查看" in asset_component
    assert "StructuredReportView" in asset_component


def test_report_assets_fetch_typed_detail_and_render_html_in_an_origin_isolated_script_iframe() -> None:
    component = Path("frontend/src/components/assets/AssetLibraryPage.tsx").read_text(encoding="utf-8")
    types = Path("frontend/src/types/assets.ts").read_text(encoding="utf-8")

    assert "ReportAssetDetail" in types
    assert 'view_kind: "structured"' in types
    assert 'view_kind: "html"' in types
    assert "structured_report: StructuredReport" in types
    assert "html: string" in types
    assert "`/assets/reports/${reportType}/${reportRunId}`" in component
    assert "window.location.search" in component
    assert 'searchParams.get("report_type")' in component
    assert 'searchParams.get("report_run_id")' in component
    assert "StructuredReportView" in component
    assert "srcDoc={openReport.html}" in component
    sandbox = re.search(r'<iframe\b.*?\bsandbox="([^"]*)"', component, flags=re.DOTALL)
    assert sandbox is not None
    sandbox_tokens = sandbox.group(1).split()
    assert sandbox_tokens == ["allow-scripts"]
    assert set(sandbox_tokens).isdisjoint(
        {
            "allow-same-origin",
            "allow-forms",
            "allow-popups",
            "allow-popups-to-escape-sandbox",
            "allow-top-navigation",
            "allow-top-navigation-by-user-activation",
            "allow-downloads",
        }
    )
    assert "dangerouslySetInnerHTML" not in component


def test_frontend_lists_use_shared_pagination_component() -> None:
    root = Path("frontend")
    pagination = (root / "src/components/shared/DataPagination.tsx").read_text(encoding="utf-8")
    list_components = [
        "src/components/assets/AssetLibraryPage.tsx",
        "src/components/competitors/CompetitorLibraryPage.tsx",
        "src/components/profiles/ProfileMaintenancePage.tsx",
    ]

    assert "pageSizeOptions = [10, 20, 50, 100]" in pagination
    assert "onPageSizeChange" in pagination
    assert "跳转页码" in pagination

    for relative_path in list_components:
        text = (root / relative_path).read_text(encoding="utf-8")
        assert "const defaultPageSize = 10" in text
        assert "<DataPagination" in text
        assert "const pageSize = 50" not in text


def test_task_import_page_uses_real_api_workbench() -> None:
    root = Path("frontend")
    page = (root / "src/app/tasks/import/page.tsx").read_text(encoding="utf-8")
    workbench = (root / "src/components/tasks/TaskImportWorkbench.tsx").read_text(encoding="utf-8")

    assert "TaskImportWorkbench" in page
    assert "Placeholder" not in page
    assert "/tasks/upload" in workbench
    assert "/run" in workbench
    assert "/tables" in workbench
    assert "event_file" in workbench
    assert "content_file" in workbench
    assert "comment_file" in workbench
    assert "<DataPagination" in workbench
    assert "const defaultPageSize = 10" in workbench


def test_etl_flow_page_uses_visual_flow_canvas() -> None:
    root = Path("frontend")
    page = (root / "src/app/tasks/flow/page.tsx").read_text(encoding="utf-8")
    canvas = (root / "src/components/tasks/EtlFlowCanvas.tsx").read_text(encoding="utf-8")

    assert "EtlFlowCanvas" in page
    assert "PlaceholderPage" not in page
    assert "/etl/flow" in canvas
    assert "/tasks" in canvas
    assert "ODS → DWD → ADS → PostgreSQL" in canvas
    assert "FlowLines" in canvas
    assert "nodeLayouts" in canvas


def test_comment_user_ai_profile_flow_page_uses_visual_flow_canvas() -> None:
    root = Path("frontend")
    navigation = (root / "src/config/navigation.ts").read_text(encoding="utf-8")
    page = (root / "src/app/tasks/ai-profile-flow/page.tsx").read_text(encoding="utf-8")
    canvas = (root / "src/components/tasks/CommentUserAiProfileFlowCanvas.tsx").read_text(encoding="utf-8")
    types = (root / "src/types/aiProfileFlow.ts").read_text(encoding="utf-8")

    assert "用户画像AI打标流程" in navigation
    assert "CommentUserAiProfileFlowCanvas" in page
    assert "PlaceholderPage" not in page
    assert "/profiles/comment-users/ai-flow" in canvas
    assert "选择用户范围" in canvas
    assert "抽取全量评论" in canvas
    assert "拼接提示词" in canvas
    assert "调用 LLM" in canvas
    assert "JSON 规范化解析" in canvas
    assert "写入画像表" in canvas
    assert "结果校验" in canvas
    assert "FlowLines" in canvas
    assert "nodeLayouts" in canvas
    assert "AiProfileFlowNode" in types
    assert "AiProfileFlowPayload" in types


def test_task_script_page_uses_real_api_editor() -> None:
    root = Path("frontend")
    page = (root / "src/app/tasks/scripts/page.tsx").read_text(encoding="utf-8")
    editor = (root / "src/components/tasks/ScriptMaintenancePage.tsx").read_text(encoding="utf-8")

    assert "ScriptMaintenancePage" in page
    assert "PlaceholderPage" not in page
    assert "/etl/script" in editor
    assert "/etl/script/test-run" in editor
    assert "/tasks" in editor
    assert "保存并备份" in editor
    assert "用选中批次试跑" in editor


def test_market_hot_posts_support_detail_drilldown_modal() -> None:
    root = Path("frontend")
    market_page = (root / "src/app/voc/events/market/page.tsx").read_text(encoding="utf-8")
    platform_card = (root / "src/components/voc/PlatformStoryCard.tsx").read_text(encoding="utf-8")
    hot_list = (root / "src/components/voc/HotPostList.tsx").read_text(encoding="utf-8")
    modal = (root / "src/components/voc/PostDetailModal.tsx").read_text(encoding="utf-8")

    assert "eventId={dashboard.event.event_id}" in market_page
    assert "hotPosts={dashboard.hot_posts}" in market_page
    assert "HotPostList" in platform_card
    assert "activeEvidence" in platform_card
    assert "效率排行" in platform_card
    assert "热门证据" in platform_card
    assert "PostDetailModal" in hot_list
    assert "setSelectedPost(post)" in hot_list
    assert "/voc/events/" in modal
    assert "/contents/" in modal
    assert "/detail" in modal
    assert "按互动排序" in modal
    assert "按发布时间排序" in modal
    assert "<DataPagination" in modal
    assert "parent_comment_id" in modal
    assert "打开原帖" in modal


def test_market_dashboard_charts_have_tooltips_and_metric_icons() -> None:
    root = Path("frontend")
    market_page = (root / "src/app/voc/events/market/page.tsx").read_text(encoding="utf-8")
    metric_card = (root / "src/components/voc/MetricCard.tsx").read_text(encoding="utf-8")
    trend_chart = (root / "src/components/voc/VolumeTrendChart.tsx").read_text(encoding="utf-8")
    channel_chart = (root / "src/components/voc/ChannelStackedBars.tsx").read_text(encoding="utf-8")
    distribution_chart = (root / "src/components/voc/KolTypeBars.tsx").read_text(encoding="utf-8")

    assert "icon?: React.ReactNode" in metric_card
    assert "icon={<Activity" in market_page
    assert "icon={<MessageCircle" in market_page
    assert "<title>" in trend_chart
    assert "title={tooltip}" in channel_chart
    assert "title={`${item.label}" in distribution_chart


def test_market_dashboard_renders_comment_quality_story_card() -> None:
    root = Path("frontend")
    market_page = (root / "src/app/voc/events/market/page.tsx").read_text(encoding="utf-8")
    types = (root / "src/types/vocMarket.ts").read_text(encoding="utf-8")
    card = (root / "src/components/voc/CommentQualityStoryCard.tsx").read_text(encoding="utf-8")

    assert "CommentQualityStoryCard" in market_page
    assert "eventId={dashboard.event.event_id}" in market_page
    assert "quality={dashboard.comment_quality}" in market_page
    assert "comment_quality?: CommentQuality" in types
    assert "DiscussionPointComment" in types
    assert "DiscussionPointCommentsPayload" in types
    assert "apiBaseUrl" in card
    assert "serverApiBaseUrl" not in card
    assert "用户讨论点与有效反馈" in card
    assert "用户讨论点 Top 8" in card
    assert "DiscussionPointEvidencePanel" in card
    assert "COMMENTS_PER_PAGE = 5" in card
    assert "currentPage" in card
    assert "上一页" in card
    assert "下一页" in card
    assert "onSelectRow(item.label)" in card
    assert "onSelectRow={setSelectedAspect}" in card
    assert "DiscussionPointDrawer" not in card
    assert "fixed inset-0" not in card
    assert "discussion-points" in card
    assert "评论原文与互动证据" in card
    assert "interaction_cnt" in card
    assert "purchase_signal" in card
    assert "mid_high_purchase_signal_rate" in card


def test_market_dashboard_renders_volume_rhythm_story_card() -> None:
    root = Path("frontend")
    market_page = (root / "src/app/voc/events/market/page.tsx").read_text(encoding="utf-8")
    types = (root / "src/types/vocMarket.ts").read_text(encoding="utf-8")
    card = (root / "src/components/voc/VolumeRhythmStoryCard.tsx").read_text(encoding="utf-8")

    assert "VolumeRhythmStoryCard" in market_page
    assert "rhythm={dashboard.volume_rhythm}" in market_page
    assert "volume_rhythm?: VolumeRhythm" in types
    assert "传播规模与节奏" in card
    assert "rule_based_conclusion" in card
    assert "VolumeTrendChart" in card
    assert "查看传播规模与节奏计算规则" in card
    assert "集中爆发：峰值贡献 ≥ 50%" in card
    assert "该结论为规则计算结果，不是 AI 生成" in card


def test_market_dashboard_renders_subject_story_card() -> None:
    root = Path("frontend")
    market_page = (root / "src/app/voc/events/market/page.tsx").read_text(encoding="utf-8")
    types = (root / "src/types/vocMarket.ts").read_text(encoding="utf-8")
    card = (root / "src/components/voc/SubjectStoryCard.tsx").read_text(encoding="utf-8")

    assert "SubjectStoryCard" in market_page
    assert "story={dashboard.subject_story}" in market_page
    assert "subject_story?: SubjectStory" in types
    assert "传播主体与KOL带动" in card
    assert "查看传播主体计算规则" in card
    assert "KOL带动：KOL互动贡献占比 ≥ 50%" in card
    assert "KolTypeBars" in card


def test_market_subject_story_card_compacts_open_ended_lists() -> None:
    root = Path("frontend")
    card = (root / "src/components/voc/SubjectStoryCard.tsx").read_text(encoding="utf-8")
    bars = (root / "src/components/voc/KolTypeBars.tsx").read_text(encoding="utf-8")

    assert "MAX_VISIBLE_SUBJECT_ITEMS = 5" in card
    assert "topAuthors = (story?.top_authors ?? []).slice(0, MAX_VISIBLE_SUBJECT_ITEMS)" in card
    assert "buildCompactRows" in bars
    assert "MAX_VISIBLE_DISTRIBUTION_ITEMS = 5" in bars
    assert "其他类型" in bars
    assert "其他画像" in bars
    assert "slice(0, MAX_VISIBLE_DISTRIBUTION_ITEMS)" in bars


def test_market_dashboard_renders_platform_story_card() -> None:
    root = Path("frontend")
    market_page = (root / "src/app/voc/events/market/page.tsx").read_text(encoding="utf-8")
    types = (root / "src/types/vocMarket.ts").read_text(encoding="utf-8")
    card = (root / "src/components/voc/PlatformStoryCard.tsx").read_text(encoding="utf-8")
    channel_chart = (root / "src/components/voc/ChannelStackedBars.tsx").read_text(encoding="utf-8")

    assert "PlatformStoryCard" in market_page
    assert "story={dashboard.platform_story}" in market_page
    assert "platform_story?: PlatformStory" in types
    assert "平台效率与渠道选择" in card
    assert "查看平台效率计算规则" in card
    assert "有效评论率 = 车相关评论数 / 已打标评论数" in card
    assert "ChannelStackedBars" in card
    assert "maxVisible={10}" in card
    assert "HotPostList" in card
    assert "maxVisible?: number" in channel_chart
    assert "展示前 {rows.length} / 共 {data.length} 个平台" in channel_chart


def test_market_platform_evidence_tabs_share_rank_list_layout() -> None:
    root = Path("frontend")
    card = (root / "src/components/voc/PlatformStoryCard.tsx").read_text(encoding="utf-8")
    hot_list = (root / "src/components/voc/HotPostList.tsx").read_text(encoding="utf-8")
    evidence_list = (root / "src/components/voc/EvidenceRankList.tsx").read_text(encoding="utf-8")

    assert "EvidenceRankList" in card
    assert "EvidenceRankList" in hot_list
    assert "EvidenceRankList" in evidence_list
    assert "MAX_EVIDENCE_RANK_ITEMS = 5" in evidence_list
    assert "items.slice(0, MAX_EVIDENCE_RANK_ITEMS)" in evidence_list
    assert "Flame" in evidence_list
    assert "rankBadge" in evidence_list
    assert "valueLabel" in evidence_list
    assert "efficiencyItems" in card
    assert "valueLabel: \"声量\"" in card
    assert "onSelectItem" in hot_list


def test_market_platform_evidence_rows_keep_same_height_across_tabs() -> None:
    root = Path("frontend")
    hot_list = (root / "src/components/voc/HotPostList.tsx").read_text(encoding="utf-8")
    evidence_list = (root / "src/components/voc/EvidenceRankList.tsx").read_text(encoding="utf-8")
    types = (root / "src/types/vocMarket.ts").read_text(encoding="utf-8")

    assert "min-h-[44px]" in evidence_list
    assert "item.meta ?? \"\\u00a0\"" in evidence_list
    assert "comment_peak_bucket?: string | null" in types
    assert "post.comment_peak_bucket" in hot_list
    assert "评论集中在" in hot_list
    assert "暂无评论节奏" in hot_list


def test_author_drilldown_page_and_market_links_exist() -> None:
    root = Path("frontend")
    subject_card = (root / "src/components/voc/SubjectStoryCard.tsx").read_text(encoding="utf-8")
    page = (root / "src/app/voc/authors/[authorId]/page.tsx").read_text(encoding="utf-8")
    detail = (root / "src/components/voc/AuthorDetailPage.tsx").read_text(encoding="utf-8")
    sankey = (root / "src/components/voc/AuthorSankey.tsx").read_text(encoding="utf-8")
    types = (root / "src/types/vocMarket.ts").read_text(encoding="utf-8")

    assert "AuthorDetailDrawer" in subject_card
    assert "setSelectedAuthorId" in subject_card
    assert "onSelectAuthor(author.author_id as string)" in subject_card
    assert "getAuthorDetail" in page
    assert "/voc/authors/" in page
    assert "AuthorDetailPage" in page
    assert "AuthorSankey" in detail
    assert "作者画像" in detail
    assert "参与事件" in detail
    assert "发布内容" in detail
    assert "作者 -> 事件 -> 用户画像" in detail
    assert "<svg" in sankey
    assert "AuthorDetailPayload" in types
    assert "AuthorSankeyPayload" in types


def test_market_author_drilldown_uses_right_drawer() -> None:
    root = Path("frontend")
    drawer = (root / "src/components/voc/AuthorDetailDrawer.tsx").read_text(encoding="utf-8")
    detail = (root / "src/components/voc/AuthorDetailPage.tsx").read_text(encoding="utf-8")

    assert "fixed inset-0 z-50" in drawer
    assert "max-w-[880px]" in drawer
    assert "buildAuthorDetailUrl" in drawer
    assert "/voc/authors/" in drawer
    assert "AuthorDetailPage payload={payload} showBackLink={false}" in drawer
    assert "[&_.author-back-link]:hidden" in drawer
    assert "showBackLink?: boolean" in detail


def test_author_detail_content_cards_use_stable_dimensions() -> None:
    root = Path("frontend")
    detail = (root / "src/components/voc/AuthorDetailPage.tsx").read_text(encoding="utf-8")

    assert "max-h-[420px] overflow-y-auto pr-1" in detail
    assert "grid-cols-[minmax(0,1fr)_auto]" in detail
    assert "line-clamp-2" in detail
    assert "min-h-[86px]" in detail
    assert "whitespace-nowrap" in detail
    assert "flex flex-wrap items-center justify-between gap-3 rounded-xl" not in detail


def test_product_dashboard_first_story_card_is_wired() -> None:
    root = Path("frontend")
    navigation = (root / "src/config/navigation.ts").read_text(encoding="utf-8")
    page = (root / "src/app/voc/events/product/page.tsx").read_text(encoding="utf-8")
    card = (root / "src/components/voc/ProductFocusStoryCard.tsx").read_text(encoding="utf-8")
    types = (root / "src/types/vocMarket.ts").read_text(encoding="utf-8")

    assert "PackageSearch" in navigation
    assert "href: \"/voc/events/product\"" in navigation
    assert "ProductFocusStoryCard" in page
    assert "/product-dashboard" in page
    assert "产品关注点总览" in card
    assert "产品感知四象限" in card
    assert "X轴：相对提及率" in card
    assert "Y轴：净正向感知" in card
    assert "title={tooltip}" in card
    assert "正向率:" in card
    assert "负向率:" in card
    assert "comment_label_json.mentioned_aspect" in card
    assert "该结论为规则计算结果，不是 AI 生成" in card
    assert "ProductDashboardPayload" in types
    assert "ProductFocusStory" in types


def test_product_dashboard_second_story_card_is_wired() -> None:
    root = Path("frontend")
    page = (root / "src/app/voc/events/product/page.tsx").read_text(encoding="utf-8")
    types = (root / "src/types/vocMarket.ts").read_text(encoding="utf-8")
    card = (root / "src/components/voc/ProductOpportunityStoryCard.tsx").read_text(encoding="utf-8")

    assert "ProductOpportunityStoryCard" in page
    assert "opportunity={dashboard.product_opportunity_story}" in page
    assert "product_opportunity_story: ProductOpportunityStory" in types
    assert "ProductOpportunityStory" in types
    assert "surprise_points" in types
    assert "pain_points" in types
    assert "conversion_points" in types
    assert "产品机会优先级" in card
    assert "Bento Grid" not in card
    assert "惊喜点" in card
    assert "吐槽点" in card
    assert "转化点" in card
    assert "放大传播" in card
    assert "修复异议" in card
    assert "转化话术" in card
    assert "top-1-card" in card
    assert "top-2-card" in card
    assert "top-3-card" in card
    assert "top-4-card" in card
    assert "top-5-card" in card
    assert "buildRankedBentoItems" in card
    assert "AutoScrollComments" in card
    assert "evidence_comments" in card
    assert 'type OpportunityFilter = "all" | "surprise_points" | "pain_points" | "conversion_points"' in card
    assert 'useState<OpportunityFilter>("all")' in card
    assert "filterOptions" in card
    assert "全部" in card
    assert "buildFilteredBentoItems" in card
    assert "action_advice" not in card
    assert "opportunity_score" in card
    assert "该结论为规则计算结果，不是 AI 生成" in card
    assert "Top1 最大卡；Top2、Top3 中卡；Top4、Top5 小卡" not in card
    assert "该结论为规则计算结果，不是 AI 生成</span>" not in card
    assert "机会分数计算公式" in card
    assert "惊喜点机会分数 = 提及率 × 正向率" in card
    assert "吐槽点机会分数 = 提及率 × 负向率" in card
    assert "转化点机会分数 = 提及率 × 中/强购买信号率" in card


def test_product_dashboard_pko_story_card_is_wired() -> None:
    root = Path("frontend")
    page = (root / "src/app/voc/events/product/page.tsx").read_text(encoding="utf-8")
    types = (root / "src/types/vocMarket.ts").read_text(encoding="utf-8")
    card = (root / "src/components/voc/ProductPkoStoryCard.tsx").read_text(encoding="utf-8")

    assert "ProductPkoStoryCard" in page
    assert "pkoStory={dashboard.product_pko_story}" in page
    assert "product_pko_story: ProductPkoStory" in types
    assert "ProductPkoStory" in types
    assert "target_distribution" in types
    assert "dimension_distribution" in types
    assert "result_distribution" in types
    assert "PKO 对比与竞争位置" in card
    assert "对比对象" in card
    assert "对比维度" in card
    assert "胜负判断" in card
    assert "PKO 总览" in card
    assert "PKO 评论" in card
    assert "主要对比对象" in card
    assert "主要对比维度" in card
    assert "主要胜负判断" in card
    assert "典型评论" in card
    assert "OverviewMetricGrid" in card
    assert "StatusBadge" in card
    assert "PrimaryDistributionCard" not in card
    assert "QuoteCard" in card
    assert "displayDistributionLabel" in card
    assert "其他对象" in card
    assert "其他维度" in card
    assert "与谁比较" not in card
    assert "比什么" not in card
    assert "谁占优" not in card
    assert "证据是什么" not in card
    assert "CompetitiveInsightHero" not in card
    assert "TagCloud" not in card
    assert "MiniDistribution" not in card


def test_product_pko_card_groups_target_selection_with_evidence_comments() -> None:
    card = Path("frontend/src/components/voc/ProductPkoStoryCard.tsx").read_text(encoding="utf-8")

    assert "PkoInsightGrid" in card
    assert "对比对象证据区" in card
    assert "该对象的典型评论" in card
    assert "当前选择" in card
    assert "Generic Comparison" not in card
    assert "PrimaryDistributionCard summary=" not in card
    assert "bg-[var(--voc-chart-2)]" not in card
    assert "bg-[var(--theme-border)]" in card
    assert "xl:grid-cols-[0.95fr_1.05fr]" in card
    assert "xl:grid-cols-[minmax(260px,0.8fr)_minmax(0,1.2fr)]" in card
    assert "overflow-hidden" in card
    assert "flex flex-col gap-2" in card
    assert "items-start justify-between gap-3" not in card
    assert card.index("DimensionResultMatrix") < card.index("PkoInsightGrid")


def test_product_dashboard_backend_keeps_chinese_label_sql_literals() -> None:
    source = Path("app/services/event_voc_insights.py").read_text(encoding="utf-8")
    card = Path("frontend/src/components/voc/ProductPkoStoryCard.tsx").read_text(encoding="utf-8")

    assert "coalesce(has_pko, '') IN ('是', '有'" in source
    assert "sentiment = '正向'" in source
    assert "sentiment = '负向'" in source
    assert "purchase_signal IN ('中', '强')" in source
    assert "bg-[#151720]" not in card
    assert "comment_label_json.pko" in card
    assert "pko_result" not in card


def test_market_dashboard_backend_keeps_chinese_label_sql_literals() -> None:
    source = Path("app/services/event_voc_insights.py").read_text(encoding="utf-8")

    assert "comment_label_json ->> 'is_vehicle_related' = '是'" in source
    assert "comment_label_json ->> 'comment_sentiment' = '正向'" in source
    assert "comment_label_json ->> 'comment_sentiment' = '负向'" in source
    assert "comment_label_json ->> 'purchase_signal' IN ('中', '强')" in source
    assert "未维护作者类型" in source
    assert "未知地区" in source


def test_sales_dashboard_backend_keeps_chinese_label_sql_literals() -> None:
    source = Path("app/services/event_voc_insights.py").read_text(encoding="utf-8")

    assert "AS is_vehicle_related" in source
    assert "AS comment_intent" in source
    assert "AS purchase_signal" in source
    assert "'未标注平台'" in source
    assert "'未命名内容'" in source
    assert "'未标注作者'" in source
    assert "'未画像用户'" in source
    assert "{\"中\", \"强\"}" in source


def test_sales_dashboard_first_story_card_is_wired() -> None:
    root = Path("frontend")
    navigation = (root / "src/config/navigation.ts").read_text(encoding="utf-8")
    page = (root / "src/app/voc/events/sales/page.tsx").read_text(encoding="utf-8")
    theme_frame = (root / "src/components/voc/VocDashboardThemeFrame.tsx").read_text(encoding="utf-8")
    globals_css = (root / "src/app/globals.css").read_text(encoding="utf-8")
    types = (root / "src/types/vocMarket.ts").read_text(encoding="utf-8")
    card = (root / "src/components/voc/SalesLeadQualityStoryCard.tsx").read_text(encoding="utf-8")

    assert "href: \"/voc/events/sales\"" in navigation
    assert "销售看板" in navigation
    assert "VocDashboardThemeFrame" in page
    assert "VocDashboardHeader" in page
    assert "data-voc-theme" in theme_frame
    assert "奶茶" in theme_frame
    assert "经典" in theme_frame
    assert 'label: "经典", swatch: "#5B63B7"' in theme_frame
    assert "ChevronDown" in theme_frame
    assert "themeOptions.map" in theme_frame
    assert "页面主题" not in theme_frame
    assert 'useState<DashboardTheme>("soft")' in theme_frame
    assert "--soft-page: #FFFFFF" in globals_css
    assert "--soft-header: #F8F5F1" in globals_css
    assert "--soft-card: #FBFAF8" in globals_css
    assert "--soft-primary: #5D9691" in globals_css
    assert "--soft-primary-hover: #4B7F7A" in globals_css
    assert "--soft-selected-border: #5D9691" in globals_css
    assert "--soft-selected-bg: #EAF3F1" in globals_css
    assert "--soft-selected-text: #3F736F" in globals_css
    assert "--soft-hover-bg: #F5F6F6" in globals_css
    assert "--soft-icon: #5D9691" in globals_css
    assert "--soft-muted: #92979F" in globals_css
    assert "--sales-sankey-root: #5D9B96" in globals_css
    assert "--sales-sankey-sales: #B56F46" in globals_css
    assert "--sales-sankey-strong: #C15F5F" in globals_css
    assert "--sales-sankey-neutral: #D9DDE2" in globals_css
    assert "--sales-chip-strong-text: #A24646" in globals_css
    assert "--sales-chip-mid-text: #8D5635" in globals_css
    assert "--sales-chip-weak-text: #566F83" in globals_css
    assert "--profile-unprofiled: #D9DDE2" in globals_css
    assert "--profile-completed: #438A68" in globals_css
    assert "--profile-missing-bg: #F5F6F6" in globals_css
    assert "--profile-missing-text: #92979F" in globals_css
    assert '[data-voc-theme="nexus"]' in globals_css
    assert "--classic-primary: var(--nexus-primary)" in globals_css
    assert "--classic-accent: var(--nexus-teal)" in globals_css
    assert "--classic-selected-border: var(--nexus-primary)" in globals_css
    assert "all: \"var(--sales-sankey-root)\"" in card
    assert "signal_strong: \"var(--sales-sankey-strong)\"" in card
    assert "signal_none: \"var(--sales-sankey-neutral)\"" in card
    assert "var(--voc-chart-1)" in card
    assert "stroke={isSelected ? \"var(--theme-selected-border)\"" in card
    assert "fill={isSelected ? \"var(--theme-selected-bg)\"" in card
    assert "bg-[var(--theme-selected-bg)]" in card
    assert "text-[var(--theme-selected-border)]" in card
    assert "bg-[var(--profile-missing-bg)]" in card
    assert "text-[var(--profile-missing-text)]" in card
    assert "text-[var(--sales-chip-strong-text)]" in card
    assert "text-[var(--sales-chip-mid-text)]" in card
    assert "text-[var(--sales-chip-weak-text)]" in card
    assert "bg-[#e9fbfa]" not in card
    assert "text-[#0d9e9c]" not in card
    sales_theme_surface = page + theme_frame + card
    assert "#887CFD" not in sales_theme_surface
    assert "#4896FE" not in sales_theme_surface
    assert "rgba(81,70,229" not in sales_theme_surface
    assert "#5146E5" not in globals_css
    assert "#4338CA" not in globals_css
    assert "SalesLeadQualityStoryCard" in page
    assert "/sales-dashboard" in page
    assert "sales_lead_quality" in page
    assert "SalesDashboardPayload" in types
    assert "SalesLeadQuality" in types
    assert "线索质量" in card
    assert "线索意向质量" not in card
    assert "SalesLeadSankey" in card
    assert "sankey: SalesLeadSankeyPayload" in types
    assert '"use client"' in card
    assert "useState" in card
    assert "<svg" in card
    assert "<path" in card
    assert "onSelectSegment" in card
    assert "selectedSegmentId" in card
    assert "ProfileDistributionBars" in card
    assert "ProfilePieChart" not in card
    assert "profile_segments: SalesLeadProfileSegment[]" in types
    assert "用户画像占比" in card
    assert "查看全部用户" in card
    assert "UserListDrawer" in card
    assert "全部用户" in card
    assert "搜索用户昵称 / 评论内容" in card
    assert "购买信号筛选" in card
    assert "画像状态筛选" in card
    assert "按购买信号" in card
    assert "按评论时间" in card
    assert "按画像状态" in card
    assert "评论摘要" in card
    assert "画像状态" in card
    assert "MoreHorizontal" in card
    assert "查看详情" in card
    assert "查看评论" in card
    assert "去画像" in card
    assert "buildUserAiProfileUrl" in card
    assert "/ai-run" in card
    assert "onProfileUser(user)" in card
    assert "profilingUserId" in card
    assert "正在画像" in card
    assert "标记跟进" in card
    assert "max-w-[80vw]" in card
    assert "translate-x-0" in card
    assert "max-w-3xl" not in card
    assert "销售相关意图" in card
    assert "Lead Intelligence" in card
    assert "用户画像覆盖情况" not in card
    assert "画像覆盖率" not in card
    assert "未画像用户" not in card
    assert "topProfileLabel" in card
    assert "最多画像用户" in card
    assert "grid-cols-2" in card
    assert "grid-cols-4" not in card
    assert "h-[58px]" in card
    assert "segment.users.slice(0, 5)" in card
    assert "2xl:grid-cols-[minmax(0,1fr)_360px]" in card
    assert "items-stretch" in card
    assert "SalesLeadSankey" in card
    assert "h-full" in card
    assert "mt-auto" in card
    assert "h-[170px]" not in card
    assert "min-h-[30px]" in card
    assert "space-y-1" in card
    assert "h-9 w-full" in card
    assert "aria-label=\"查看全部用户\"" not in card
    assert "查看全部</button>" not in card
    assert "line-clamp-2 text-[10px]" not in card
    assert "user.representative_comment}</p>" in card
    assert "comment_author_name.slice" not in card
    assert "UserRound" in card
    assert "bg-[var(--theme-soft-panel)]" in card
    assert "画像占比条形" in card
    assert "画像占比堆叠条" in card
    assert "flexGrow" in card
    assert "width: `${Math.max(2" not in card
    assert "xl:max-h-[520px]" not in card
    assert "overflow-hidden" in card
    assert 'viewBox="0 0 800 500"' in card
    assert "min-h-[520px]" in card
    assert "强购买比例" in card
    assert "销售相关意图占比" in card
    assert "PKO" not in card
    assert "purchase_signal_distribution" in types
    assert "purchase_signal: string" in types
    assert "user.purchase_signal" in card
    assert "return user.mid_high_purchase_signal_count > 0 ? \"中/强购买信号\"" not in card
    assert "intent_distribution" in types
    assert "典型高意向评论" not in card
    assert "MessageSquareText" in card
    assert "comment_label_json.purchase_signal" in card
    assert "用户意图分布" not in card
    assert "购买信号分布" not in card


def test_event_department_dashboards_share_theme_frame_and_header_alignment() -> None:
    root = Path("frontend")
    pages = [
        root / "src/app/voc/events/market/page.tsx",
        root / "src/app/voc/events/product/page.tsx",
        root / "src/app/voc/events/sales/page.tsx",
    ]
    frame = (root / "src/components/voc/VocDashboardThemeFrame.tsx").read_text(encoding="utf-8")
    header = (root / "src/components/voc/VocDashboardHeader.tsx").read_text(encoding="utf-8")

    assert "data-voc-theme" in frame
    assert "ThemeSelect" in frame
    assert "奶茶" in frame
    assert "经典" in frame
    assert "voc-dashboard-page-shell" in frame
    assert "children" in frame
    assert "VOC Event Intelligence" in header
    assert "VOC Product Intelligence" in header
    assert "VOC Sales Intelligence" in header
    assert "voc-dashboard-header rounded-[20px]" in header
    assert "voc-dashboard-controls flex w-full flex-col items-stretch gap-2" in header
    assert "voc-dashboard-filter-form flex w-full flex-wrap items-center gap-2" in header
    assert "ThemeSelect" in header
    assert "border-[var(--theme-border)]" in header
    assert "bg-[var(--theme-primary)]" in header

    for page_path in pages:
        page = page_path.read_text(encoding="utf-8")
        assert "VocDashboardThemeFrame" in page
        assert "VocDashboardHeader" in page
        assert "<VocDashboardThemeFrame>" in page
        assert "<VocDashboardHeader" in page
        assert "className=\"mx-auto max-w-[1560px] space-y-5\"" in page
        assert "<header className=\"flex flex-wrap items-start justify-between gap-4\">" not in page
        assert "ThemeSelect" not in page


def test_market_and_product_charts_use_dashboard_theme_tokens() -> None:
    root = Path("frontend")
    themed_chart_components = [
        root / "src/components/voc/VolumeTrendChart.tsx",
        root / "src/components/voc/ChannelStackedBars.tsx",
        root / "src/components/voc/CommentQualityStoryCard.tsx",
        root / "src/components/voc/ProductFocusStoryCard.tsx",
        root / "src/components/voc/ProductOpportunityStoryCard.tsx",
        root / "src/components/voc/ProductPkoStoryCard.tsx",
        root / "src/components/voc/MetricCard.tsx",
    ]

    combined = "\n".join(path.read_text(encoding="utf-8") for path in themed_chart_components)
    assert "var(--voc-chart-1)" in combined
    assert "var(--voc-chart-3)" in combined
    assert "var(--voc-chart-5)" in combined
    assert "var(--voc-chart-6)" in combined
    assert "var(--theme-primary)" in combined
    assert "var(--theme-selected-bg)" in combined
    assert "var(--theme-chip)" in combined

    forbidden_chart_literals = [
        'color: "#5347CE"',
        'color: "#4896FE"',
        'color: "#16C8C7"',
        'accent: "#5347CE"',
        'accent="#5347CE"',
        'accent="#16C8C7"',
        'color="#5347CE"',
        'color="#16C8C7"',
        'bg-[#5347CE]',
        'text-[#5347CE]',
        'text-[#4896FE]',
        'bg-[#16C8C7]',
        'bg-[#4896FE]',
    ]
    for literal in forbidden_chart_literals:
        assert literal not in combined


def test_remaining_market_product_detail_colors_follow_dashboard_theme() -> None:
    root = Path("frontend")
    kol_bars = (root / "src/components/voc/KolTypeBars.tsx").read_text(encoding="utf-8")
    product_focus = (root / "src/components/voc/ProductFocusStoryCard.tsx").read_text(encoding="utf-8")
    product_opportunity = (root / "src/components/voc/ProductOpportunityStoryCard.tsx").read_text(encoding="utf-8")
    product_pko = (root / "src/components/voc/ProductPkoStoryCard.tsx").read_text(encoding="utf-8")

    assert "bg-[var(--voc-chart-4)]" in kol_bars
    assert "text-[var(--theme-primary)]" in kol_bars
    assert "bg-[#887CFD]" not in kol_bars
    assert "text-[#5347CE]" not in kol_bars

    assert 'const positiveTone = "var(--voc-chart-3)"' in product_focus
    assert 'const negativeTone = "var(--voc-chart-6)"' in product_focus
    assert "bg-[var(--theme-chip)]" in product_focus
    assert "text-[var(--theme-primary)]" in product_focus
    assert '"#16C8C7"' not in product_focus

    assert "backgroundColor: item.accent" in product_opportunity
    assert "var(--theme-primary)" in product_opportunity
    assert "var(--voc-chart-3)" in product_opportunity
    assert "var(--theme-selected-bg)" in product_opportunity
    assert '"#5347CE"' not in product_opportunity
    assert '"#16C8C7"' not in product_opportunity

    assert "Quote className=\"h-4 w-4 text-[var(--voc-chart-3)]\"" in product_pko
    assert "bg-[var(--theme-selected-bg)]" in product_pko
    assert "bg-[var(--theme-chip)]" in product_pko
    assert "text-[var(--voc-chart-2)]" not in product_pko
    assert "accent = \"var(--theme-primary)\"" in product_pko
    assert '"#5347CE"' not in product_pko
    assert "#edf6ff" not in product_pko
    assert "#e9fbfa" not in product_pko


def test_sales_dashboard_user_action_menu_is_clickable_after_hover() -> None:
    root = Path("frontend")
    card = (root / "src/components/voc/SalesLeadQualityStoryCard.tsx").read_text(encoding="utf-8")

    assert "pointer-events-none absolute right-0 top-8" not in card
    assert "pointer-events-auto absolute right-0 top-7" in card
    assert "group-hover:block group-focus-within:block" in card


def test_sales_dashboard_user_detail_drawer_uses_profile_radar_and_comment_list() -> None:
    root = Path("frontend")
    types = (root / "src/types/vocMarket.ts").read_text(encoding="utf-8")
    card = (root / "src/components/voc/SalesLeadQualityStoryCard.tsx").read_text(encoding="utf-8")

    assert "SalesLeadUserInsightProfile" in types
    assert "radar_labels" in types
    assert "key_evidence" in types
    assert "comments: SalesLeadUserInsightComment[]" in types
    assert "UserInsightDrawer" in card
    assert "selectedInsightUser" in card
    assert "/insight-profile" in card
    assert "ProfileRadarChart" in card
    assert "profileRadarDimensions" in card
    assert "buildDimensionRadarLabels" in card
    assert "决策风格" in card
    assert "核心关注点" in card
    assert "用车场景" in card
    assert "价格敏感度" in card
    assert "服务偏好" in card
    assert "品牌态度" in card
    assert "命中子标签" in card
    assert "profile_summary.main_score" in card
    assert "evidence.evidence_text" in card
    assert "evidence.reason" in card
    assert "comments.map" in card
    assert "EmotionTimelineChart" in card
    assert "comment_sentiment" in card
    assert "published_at" in card
    assert "情绪曲线" in card
    assert "sentimentToScore" in card
    assert "buildSmoothTimelinePath" in card
    assert '<path d={smoothPath}' in card
    assert "正面" in card
    assert "负面" in card
    assert "积极" not in card
    assert "消极" not in card
    assert "sentimentEmoji" in card
    assert "<text" in card
    assert "😊" in card
    assert "😐" in card
    assert "😟" in card
    assert "标签证据" in card
    assert "全部评论" in card
    assert "CommentListDrawer" in card
    assert "isCommentListOpen" in card
    assert "onOpenComments" in card
    assert "查看全部评论" in card
    assert "<h4 className=\"text-sm font-semibold text-[#151720]\">全部评论</h4>" not in card


def test_sales_dashboard_lead_source_efficiency_uses_lightweight_chart_panel() -> None:
    root = Path("frontend")
    page = (root / "src/app/voc/events/sales/page.tsx").read_text(encoding="utf-8")
    types = (root / "src/types/vocMarket.ts").read_text(encoding="utf-8")
    panel = (root / "src/components/voc/SalesLeadSourceEfficiencyPanel.tsx").read_text(encoding="utf-8")

    assert "SalesLeadSourceEfficiencyPanel" in page
    assert "sourceEfficiency={dashboard.sales_lead_source_efficiency}" in page
    assert "eventId={dashboard.event?.event_id ?? selectedEventId}" in page
    assert "sales_lead_source_efficiency: SalesLeadSourceEfficiency" in types
    assert "SalesLeadSourceEfficiency" in types
    assert "线索来源效率" in panel
    assert "渠道数据量" in panel
    assert "重点内容" in panel
    assert "建议跟进用户" in panel
    assert "SeparatedDonutChart" in panel
    assert "KeyContentList" in panel
    assert "PostDetailModal" in panel
    assert "selectedContent" in panel
    assert "onSelectContent(toHotPostItem(item))" in panel
    assert "onSelectContent={setSelectedContent}" in panel
    assert "toHotPostItem" in panel
    assert "eventId={eventId}" in panel
    assert "post={selectedContent}" in panel
    assert "SuggestedFollowUpUserList" in panel
    assert "sourceModeOptions" in panel
    assert "var(--voc-chart-1)" in panel
    assert "var(--theme-track)" in panel
    assert "var(--theme-card)" in panel
    assert "var(--theme-soft-panel)" in panel
    assert "border-[var(--theme-selected-border)]" in panel
    assert "bg-[var(--theme-selected-bg)]" in panel
    assert "bg-[var(--theme-chip)]" in panel
    assert "text-[var(--theme-selected-text)]" in panel
    assert "text-[var(--sales-chip-strong-text)]" in panel
    assert "text-[var(--sales-chip-mid-text)]" in panel
    assert "text-[var(--sales-chip-weak-text)]" in panel
    assert "bg-[var(--theme-primary)] text-white" in panel
    assert "text-[var(--theme-icon)]" in panel
    assert "全部评论" in panel
    assert "高购买强度" in panel
    assert "中购买强度" in panel
    assert "低购买强度" in panel
    assert "mid_signal_comment_count" in types
    assert "low_signal_comment_count" in types
    assert "openSourceUrl" in panel
    assert "<svg" in panel
    assert "const tooltip =" in panel
    assert "<title>{tooltip}</title>" in panel
    assert "describeDonutSegment" in panel
    assert "strokeLinecap=\"round\"" in panel
    assert "strokeDasharray" in panel
    assert "中心总数" in panel
    assert "用户轻列表" in panel
    assert "grid gap-5 lg:grid-cols-[300px_1fr]" in panel
    assert "rounded-[26px] border border-[var(--theme-track)] bg-[var(--theme-card)]" in panel
    assert "leadComments.slice(0, 5)" in panel
    assert "高意向评论流" not in panel
    assert "平台线索效率排行" not in panel
    assert "ChannelAcquisitionMap" not in panel
    assert "h-1 rounded-full" not in panel
    assert "progress" not in panel.lower()
    assert "bg-[#edf6ff]" not in panel
    assert "text-[#2c7eea]" not in panel
    assert "text-[#8E4525]" not in panel
    assert "text-[#9C5B2B]" not in panel
    assert "text-[#8A6A4D]" not in panel


def test_market_dashboard_renders_region_and_topic_story_cards() -> None:
    root = Path("frontend")
    market_page = (root / "src/app/voc/events/market/page.tsx").read_text(encoding="utf-8")
    types = (root / "src/types/vocMarket.ts").read_text(encoding="utf-8")
    region_card = (root / "src/components/voc/RegionalResponseStoryCard.tsx").read_text(encoding="utf-8")
    topic_card = (root / "src/components/voc/TopicSpreadStoryCard.tsx").read_text(encoding="utf-8")

    assert "RegionalResponseStoryCard" in market_page
    assert "TopicSpreadStoryCard" in market_page
    assert "story={dashboard.regional_response_story}" in market_page
    assert "story={dashboard.topic_spread_story}" in market_page
    assert "eventId={dashboard.event.event_id}" in market_page
    assert "regional_response_story?: RegionalResponseStory" in types
    assert "topic_spread_story?: TopicSpreadStory" in types
    assert "comment_location_only" in types
    assert '"use client"' in region_card
    assert '"use client"' in topic_card
    assert "PostDetailModal" in region_card
    assert "PostDetailModal" in topic_card
    assert "selectedPost" in region_card
    assert "selectedPost" in topic_card
    assert "地区响应与区域讨论" in region_card
    assert "基于评论用户位置统计，不代表内容发布地" in region_card
    assert "话题传播效率" in topic_card
    assert "#话题" in topic_card
    assert "TOPICS_PER_PAGE = 5" in topic_card
    assert "visibleTopics" in topic_card
    assert "setTopicOffset" in topic_card


def test_market_topic_spread_uses_topic_first_drilldown() -> None:
    root = Path("frontend")
    topic_card = (root / "src/components/voc/TopicSpreadStoryCard.tsx").read_text(encoding="utf-8")

    assert "TOPICS_PER_PAGE = 5" in topic_card
    assert "selectedTopic" in topic_card
    assert "TopicContentDrawer" in topic_card
    assert "topic.top_contents.map" in topic_card
    assert "setSelectedTopic(item)" in topic_card
    assert "查看相关内容" in topic_card
    assert "该话题覆盖的内容" in topic_card
    assert "PostDetailModal" in topic_card
    assert "topContentByTopic" not in topic_card


def test_post_detail_modal_renders_comment_timeline_chart() -> None:
    root = Path("frontend")
    types = (root / "src/types/vocMarket.ts").read_text(encoding="utf-8")
    modal = (root / "src/components/voc/PostDetailModal.tsx").read_text(encoding="utf-8")

    assert "PostDetailTimelinePoint" in types
    assert "relative_bucket: string" in types
    assert "comment_timeline: PostDetailTimelinePoint[]" in types
    assert "CommentTimelineChart" in modal
    assert "评论波动时间" in modal
    assert "发布时间" in modal
    assert "content?.published_at" in modal
    assert "payload?.comment_timeline" in modal
    assert "point.relative_bucket" in modal
    assert "发布后发酵节奏" in modal
    assert "<polyline" in modal
    assert "stroke=\"var(--theme-primary)\"" in modal
    assert "fill=\"var(--theme-primary)\"" in modal
    assert "bg-[var(--theme-primary)]" in modal
    assert "stroke=\"#5347CE\"" not in modal
    assert "fill=\"#5347CE\"" not in modal
    assert "bg-[#5347CE]" not in modal
    assert "互动量</span>" not in modal
    assert "<rect" not in modal


def test_market_dashboard_renders_ai_summary_card() -> None:
    root = Path("frontend")
    market_page = (root / "src/app/voc/events/market/page.tsx").read_text(encoding="utf-8")
    card = (root / "src/components/voc/MarketAiSummaryCard.tsx").read_text(encoding="utf-8")
    shared_card = (root / "src/components/voc/ReportAiSummaryCard.tsx").read_text(encoding="utf-8")
    types = (root / "src/types/vocMarket.ts").read_text(encoding="utf-8")

    assert "MarketAiSummaryCard" in market_page
    assert "eventId={dashboard.event.event_id}" in market_page
    assert "/market/report-agent/run" in card
    assert "/market/report-agent/latest" in card
    assert "MarketReportAgentPayload" in types
    assert "MarketReportSummary" in types
    assert "ReportAgentPayload" in types
    assert "isOpen" in shared_card
    assert "loadLatestSummary" in shared_card
    assert "regenerateSummary" in shared_card
    assert "renderInlineMarkdown" in shared_card
    assert "linear-gradient" in shared_card
    assert "AI 总结" in shared_card
    assert "使用的 Prompt" in shared_card
    assert "输入给 AI 的结构化数据" in shared_card
    assert "renderMarkdownReport" in shared_card
    assert "report_markdown" in shared_card
    assert "data_notes" in shared_card
    assert "event_overview" not in shared_card
    assert "market_conclusion" not in shared_card


def test_product_dashboard_renders_ai_summary_card() -> None:
    root = Path("frontend")
    product_page = (root / "src/app/voc/events/product/page.tsx").read_text(encoding="utf-8")
    card = (root / "src/components/voc/ProductAiSummaryCard.tsx").read_text(encoding="utf-8")
    shared_card = (root / "src/components/voc/ReportAiSummaryCard.tsx").read_text(encoding="utf-8")
    types = (root / "src/types/vocMarket.ts").read_text(encoding="utf-8")

    assert "ProductAiSummaryCard" in product_page
    assert "eventId={dashboard.event.event_id}" in product_page
    assert "/product/report-agent/run" in card
    assert "/product/report-agent/latest" in card
    assert "ReportAgentPayload" in types
    assert "AI 总结" in shared_card
    assert "产品部 AI 总结报告" in card
    assert "renderMarkdownReport" in shared_card
    assert "report_markdown" in shared_card
    assert "data_notes" in shared_card


def test_sales_dashboard_renders_ai_summary_card() -> None:
    root = Path("frontend")
    sales_page = (root / "src/app/voc/events/sales/page.tsx").read_text(encoding="utf-8")
    card = (root / "src/components/voc/SalesAiSummaryCard.tsx").read_text(encoding="utf-8")
    shared_card = (root / "src/components/voc/ReportAiSummaryCard.tsx").read_text(encoding="utf-8")
    types = (root / "src/types/vocMarket.ts").read_text(encoding="utf-8")

    assert "SalesAiSummaryCard" in sales_page
    assert "eventId={dashboard.event.event_id}" in sales_page
    assert "/sales/report-agent/run" in card
    assert "/sales/report-agent/latest" in card
    assert "ReportAgentPayload" in types
    assert "销售部" in card
    assert "Sales Report Agent" in card
    assert "renderMarkdownReport" in shared_card
    assert "report_markdown" in shared_card
    assert "data_notes" in shared_card


def test_report_ai_summary_card_generates_when_no_cached_summary() -> None:
    shared_card = Path("frontend/src/components/voc/ReportAiSummaryCard.tsx").read_text(encoding="utf-8")

    assert "response.status === 404" in shared_card
    assert "await regenerateSummary()" in shared_card
    assert shared_card.index("response.status === 404") < shared_card.index("await regenerateSummary()")


def test_report_ai_summary_card_renders_structured_report_charts_evidence_and_calculations() -> None:
    shared_card = Path("frontend/src/components/voc/ReportAiSummaryCard.tsx").read_text(encoding="utf-8")
    types = Path("frontend/src/types/vocMarket.ts").read_text(encoding="utf-8")

    assert "StructuredReport" in types
    assert "ReportChartSpec" in types
    assert "structured_report" in types
    assert "StructuredReportView" in shared_card
    assert "template_sections" in types
    assert "renderTemplateSection" in shared_card
    assert "reportViewMode" in shared_card
    assert 'type ReportViewMode = "summary" | "charts" | "evidence"' in shared_card
    assert 'type EventReportViewMode = "dashboard" | "report"' in shared_card
    assert "DepartmentReportView" in shared_card
    assert "DepartmentReportAgentPayload" in shared_card
    assert "摘要模式" in shared_card
    assert "图表模式" in shared_card
    assert "数据依据" in shared_card
    assert 'reportViewMode === "summary"' in shared_card
    assert 'reportViewMode === "charts"' in shared_card
    assert 'reportViewMode === "evidence"' in shared_card
    assert 'aria-pressed={reportViewMode === "summary"}' in shared_card
    assert 'aria-pressed={reportViewMode === "charts"}' in shared_card
    assert 'aria-pressed={reportViewMode === "evidence"}' in shared_card
    assert "ReportChartRegistry" in shared_card
    assert "<ReportChartRegistry chart={chart}" in shared_card
    assert "report_narrative?: ReportNarrative" in types
    assert "section_insights: Record<string, string>" in types
    assert "reportNarrative && structuredReport" in shared_card
    assert "content_count" in shared_card
    assert "comment_count" in shared_card
    assert "内容" in shared_card
    assert "评论" in shared_card
    assert "产品机会与风险" in shared_card
    assert "Event Report" in shared_card
    assert "({item.source_path})" not in shared_card
    assert "metric_cards" in shared_card
    assert "evidence_references" in shared_card
    assert "calculation_notes" in shared_card
    assert "证据引用" in shared_card
    assert "数据计算方式" in shared_card
    assert ") : reportMarkdown ? (" in shared_card


def test_auto_voc_chat_message_can_open_generated_event_report() -> None:
    home = Path("frontend/src/components/home/AutoVocHomePage.tsx").read_text(encoding="utf-8")
    chat = Path("frontend/src/components/home/ChatMessageList.tsx").read_text(encoding="utf-8")
    report_card = Path("frontend/src/components/voc/ReportAiSummaryCard.tsx").read_text(encoding="utf-8")

    assert "reportPayload" in home
    assert "result.summary?.structured_report" in home
    assert "reportPayload" in chat
    assert "查看报告" in chat
    assert "StructuredReportView" in chat
    assert "export function StructuredReportView" in report_card


def test_report_ai_summary_card_uses_shared_hover_border_gradient_button() -> None:
    shared_card = Path("frontend/src/components/voc/ReportAiSummaryCard.tsx").read_text(encoding="utf-8")
    gradient_component = Path("frontend/src/components/ui/hover-border-gradient.tsx").read_text(encoding="utf-8")

    assert 'from "@/components/ui/hover-border-gradient"' in shared_card
    assert "<HoverBorderGradient" in shared_card
    assert "AI 总结" in shared_card
    assert "export function HoverBorderGradient" in gradient_component


def test_auto_voc_home_copilot_skills_switch_prompt_groups() -> None:
    component = Path("frontend/src/components/home/AutoVocHomePage.tsx").read_text(encoding="utf-8")

    assert "activeSkillId" in component
    assert "promptGroups" in component
    assert "selectedSkill.prompts" in component
    assert 'id: "data"' in component
    assert 'id: "qa"' in component
    assert 'id: "report"' in component
    assert 'id: "insight"' in component
    assert "setActiveSkillId" in component


def test_auto_voc_home_copilot_has_data_question_entry() -> None:
    component = Path("frontend/src/components/home/AutoVocHomePage.tsx").read_text(encoding="utf-8")

    assert "/agents/data-question/run" in component
    assert "apiBaseUrl" in component
    assert "event_id: null" in component
    assert "submitDataQuestion" in component
    assert "history: messages.slice(-10)" in component
    assert "dataQuestionResult.trace" not in component


def test_auto_voc_home_routes_qa_report_and_insight_to_unified_agent() -> None:
    component = Path("frontend/src/components/home/AutoVocHomePage.tsx").read_text(encoding="utf-8")
    qa_route = Path("frontend/src/app/api/agents/run/route.ts").read_text(encoding="utf-8")
    data_question_route = Path("frontend/src/app/api/agents/data-question/run/route.ts").read_text(encoding="utf-8")

    assert "/agents/run" in component
    assert 'const capability: RetryCapability = activeSkillId === "report" ? reportCapability : activeSkillId' in component
    assert "capability," in component
    assert 'activeSkillId === "qa"' in component
    assert 'activeSkillId === "report"' in component
    assert 'activeSkillId === "insight"' in component
    assert '...(capability === "report"' in component
    assert '? { event_id: events[0]?.event_id ?? null }' in component
    assert 'event_id: activeSkillId === "report"' not in component
    assert "问答事件" not in component
    assert "selectedEventId" not in component
    assert "event_id: null" in component
    assert "该能力即将接入" in component
    assert "/agents/data-question/run" in component
    assert "proxyAutovocPost" in qa_route
    assert "maxDuration = 120" in qa_route
    assert "proxyAutovocPost" in data_question_route
    assert "maxDuration = 120" in data_question_route


def test_auto_voc_report_workspace_has_two_explicit_report_types() -> None:
    component = Path("frontend/src/components/home/AutoVocHomePage.tsx").read_text(encoding="utf-8")
    top_level_capabilities = component.split("const aiCapabilities", 1)[1].split("const aiSkillToneClasses", 1)[0]

    assert 'type ReportCapability = "report" | "competitor_report"' in component
    assert 'title: "事件报告"' in component
    assert 'title: "竞品动态报告"' in component
    assert 'useState<ReportCapability>("report")' in component
    assert 'id: "competitor_report"' not in top_level_capabilities
    assert 'report: []' in component
    assert 'activeSkillId === "report" ? []' in component


def test_auto_voc_competitor_report_request_and_asset_action_contract() -> None:
    home = Path("frontend/src/components/home/AutoVocHomePage.tsx").read_text(encoding="utf-8")
    messages = Path("frontend/src/components/home/ChatMessageList.tsx").read_text(encoding="utf-8")
    types = Path("frontend/src/types/vocMarket.ts").read_text(encoding="utf-8")

    assert 'const capability: RetryCapability = activeSkillId === "report" ? reportCapability : activeSkillId' in home
    assert "capability," in home
    assert '...(capability === "report"' in home
    assert '? { event_id: events[0]?.event_id ?? null }' in home
    assert 'event_id: activeSkillId === "report"' not in home
    assert 'suggestions: capability === "report" || capability === "competitor_report" ? undefined : result.suggested_questions' in home
    assert 'report_asset?: { report_run_id?: string | number | null }' in home
    assert 'function toCompetitorReportAsset' in home
    assert 'return { report_run_id: String(asset.report_run_id) }' in home
    assert 'const { reportAsset: storedReportAsset, ...storedMessage }' in home
    assert 'toCompetitorReportAsset(storedReportAsset)' in home
    assert 'toCompetitorReportAsset(result.report_asset)' in home
    assert 'reportAsset: activeSkillId === "report"' not in home
    assert "reportAsset," in home
    assert "export type CompetitorReportAsset" in types
    assert "report_run_id: string" in types
    assert "html" not in types.split("export type CompetitorReportAsset", 1)[1].split("};", 1)[0]
    assert "context" not in types.split("export type CompetitorReportAsset", 1)[1].split("};", 1)[0]
    assert "rendered_prompt" not in types.split("export type CompetitorReportAsset", 1)[1].split("};", 1)[0]
    assert "reportAsset.report_run_id" in messages
    assert (
        "href={`/assets/reports?report_type=competitor_report&report_run_id=${encodeURIComponent(String(message.reportAsset.report_run_id))}`}"
        in messages
    )
    assert "查看竞品报告" in messages


def test_auto_voc_insight_result_renders_only_inside_conversation_cards() -> None:
    home = Path("frontend/src/components/home/AutoVocHomePage.tsx").read_text(encoding="utf-8")
    messages = Path("frontend/src/components/home/ChatMessageList.tsx").read_text(encoding="utf-8")
    card = Path("frontend/src/components/home/InsightResultCard.tsx").read_text(encoding="utf-8")
    types = Path("frontend/src/types/vocMarket.ts").read_text(encoding="utf-8")

    assert "insight_result" in home
    assert "insightPayload" in home
    assert "InsightResultCard" in messages
    assert "message.insightPayload" in messages
    assert "export type InsightResult" in types
    assert "用户反应判断" in card
    assert "受影响用户群" in card
    assert "口碑与购买信号" in card
    assert "表达主题" in card
    assert "真实证据原话" in card
    assert "相似事件与推演边界" in card
    assert "暂无此类数据推演" in card
    assert 'status === "partial" && result.similar_events.length' in card
    assert "部分匹配事件" in card
    assert "cross_brand" in card
    assert "查看报告" not in card
    assert "asset" not in card.lower()


def test_auto_voc_home_copilot_expanded_workspace_can_ask_data_questions() -> None:
    component = Path("frontend/src/components/home/AutoVocHomePage.tsx").read_text(encoding="utf-8")

    assert "ExpandedAiWorkspace" in component
    assert "onSubmit={submitDataQuestion}" in component
    assert "onQuestionChange={setQuestion}" in component
    assert "value={question}" in component
    assert "messages={messages}" in component


def test_auto_voc_home_uses_shared_persistent_chatbi_conversation() -> None:
    component = Path("frontend/src/components/home/AutoVocHomePage.tsx").read_text(encoding="utf-8")
    message_list = Path("frontend/src/components/home/ChatMessageList.tsx").read_text(encoding="utf-8")

    assert "type ChatMessage" in component
    assert 'CHAT_STORAGE_KEY = "auto-voc-chat-history-v1"' in component
    assert "localStorage.getItem(CHAT_STORAGE_KEY)" in component
    assert "localStorage.setItem(CHAT_STORAGE_KEY" in component
    assert "history: messages.slice(-10)" in component
    assert "messages={messages}" in component
    assert "ChatMessageList" in component
    assert "suggested_questions" in component
    assert "dataQuestionResult.trace" not in component
    assert "whitespace-pre-wrap break-words" in message_list


def test_auto_voc_chat_keeps_skill_switcher_and_uses_available_compact_height() -> None:
    component = Path("frontend/src/components/home/AutoVocHomePage.tsx").read_text(encoding="utf-8")

    assert "CompactSkillSwitcher" in component
    assert "hasConversation ? (" in component
    assert "<CompactSkillSwitcher" in component
    assert 'className="mt-5 min-h-0 flex-1"' in component
    assert "max-h-[430px]" not in component


def test_auto_voc_compact_chat_is_capped_to_the_viewport() -> None:
    component = Path("frontend/src/components/home/AutoVocHomePage.tsx").read_text(encoding="utf-8")

    assert "xl:h-[calc(100vh-4rem)]" in component
    assert "xl:max-h-[900px]" in component
    assert 'className="flex h-full min-h-[860px]' not in component


def test_report_visuals_use_native_svg_and_autovoc_tokens() -> None:
    root = Path("frontend/src/components/voc/report-visuals")
    source = "\n".join(path.read_text(encoding="utf-8") for path in root.glob("*.tsx"))

    assert "<svg" in source
    assert "var(--theme-primary)" in source
    prohibited_runtime = re.compile(
        r"""(?:\bfrom\s+|\bimport\s*(?:\(\s*)?|\brequire\s*\(\s*)"""
        r"""["'](?:echarts|chart\.js)(?:/[^"']*)?["']""",
        re.IGNORECASE,
    )
    prohibited_cdn = re.compile(
        r"""https?://[^"'()\s]*(?:echarts|chart(?:\.min)?\.js)[^"'()\s]*""",
        re.IGNORECASE,
    )
    assert prohibited_runtime.search('import * as charts from "echarts"')
    assert prohibited_runtime.search('const charts = require("echarts/core")')
    assert prohibited_cdn.search(
        '<script src="https://cdn.jsdelivr.net/npm/echarts/dist/echarts.min.js">'
    )
    assert prohibited_runtime.search(source) is None
    assert prohibited_cdn.search(source) is None


def test_basics_chart_exports_are_closed() -> None:
    source = Path("frontend/src/components/voc/report-visuals/BasicsCharts.tsx").read_text(
        encoding="utf-8"
    )

    for export_name in [
        "F3HairlineArea",
        "F4TickDonut",
        "F5TickRows",
        "F6PairedRungs",
        "F7StackedRungs",
        "F8PlumbScatter",
    ]:
        assert f"export function {export_name}" in source


def test_basics_charts_handle_zero_values_long_labels_and_accessible_motion() -> None:
    source = Path("frontend/src/components/voc/report-visuals/BasicsCharts.tsx").read_text(
        encoding="utf-8"
    )

    assert "Math.max(1" in source
    assert "textLength" in source or "truncateSvgLabel" in source
    assert "prefers-reduced-motion" in source
    assert "tabIndex={0}" in source
    assert "rows[peakIndex] ??" in source


@lru_cache(maxsize=1)
def _run_basics_chart_probe() -> dict:
    script = r"""
const fs = require("fs");
const path = require("path");
const base = path.resolve("frontend");
const ts = require(path.join(base, "node_modules", "typescript"));
const React = require(path.join(base, "node_modules", "react"));
const jsxRuntime = require(path.join(base, "node_modules", "react", "jsx-runtime"));
const ReactDOMServer = require(path.join(base, "node_modules", "react-dom", "server"));
const themeModule = {
  reportChartTheme: {
    primary: "var(--theme-primary)",
    secondary: "var(--theme-selected-text)",
    ink: "var(--theme-ink)",
    body: "var(--theme-body)",
    muted: "var(--theme-muted)",
    border: "var(--theme-border)",
    panel: "var(--theme-soft-panel)",
    white: "var(--theme-white)",
  },
};

function loadTsx(relativePath, stubs) {
  const source = fs.readFileSync(path.join(base, relativePath), "utf8");
  const output = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.CommonJS,
      target: ts.ScriptTarget.ES2017,
      jsx: ts.JsxEmit.ReactJSX,
      esModuleInterop: true,
    },
  }).outputText;
  const loaded = { exports: {} };
  const localRequire = (id) => {
    if (Object.prototype.hasOwnProperty.call(stubs, id)) return stubs[id];
    if (id === "react/jsx-runtime") return jsxRuntime;
    throw new Error(`Unexpected import: ${id}`);
  };
  new Function("require", "module", "exports", output)(localRequire, loaded, loaded.exports);
  return loaded.exports;
}

const shell = loadTsx(
  "src/components/voc/report-visuals/ReportVisualShell.tsx",
  { "./chartTheme": themeModule },
);
const basics = loadTsx(
  "src/components/voc/report-visuals/BasicsCharts.tsx",
  { "./chartTheme": themeModule, "./ReportVisualShell": shell },
);
const call = (name, ...args) =>
  typeof basics[name] === "function" ? basics[name](...args) : null;
const invalidF8Chart = {
  chart_id: "invalid-f8",
  template_id: "F8",
  title: "平台传播效率",
  subtitle: "规模与反馈效率",
  insight: "",
  source_label: "platform.platform_efficiency",
  data: [{ platform: "仅有规模", total_volume: 120 }],
  meta: {},
};

process.stdout.write(JSON.stringify({
  f5: call("mapF5Rows", [
    { topic: "热门议题", comment_count: 120 },
    { aspect: "空间", comment_count: 57, mention_rate: 28.5 },
    {
      aspect: "转化",
      comment_count: 40,
      mention_rate: 20,
      opportunity_score: 12.5,
    },
    { label: "询价", count: 10, rate: 20 },
    { category: "不允许的标签", value: 99 },
    { topic: "缺失数值" },
    { label: "空值", comment_count: null },
  ]),
  f6Product: call("mapF6Rows", [
    { aspect: "空间", positive_rate: 60, negative_rate: 15 },
    { aspect: "缺少负向", positive_rate: 40 },
  ]),
  f6Sales: call("mapF6Rows", [
    { platform: "抖音", comment_count: 120, high_intent_comment_count: 31 },
    { platform: "缺少线索", comment_count: 20 },
    { label: "伪通用行", primary: 10, secondary: 5 },
  ]),
  f7: call("mapF7Rows", [
    {
      dimension: "价格",
      total_count: 99,
      advantage_count: 2,
      disadvantage_count: 3,
      neutral_count: 1,
      unclear_count: 4,
      random_count: 50,
    },
    { dimension: "只有总数", total_count: 7 },
  ]),
  f8: call("mapF8Points", [
    { platform: "抖音", total_volume: 120, engagement_per_content: 42.5 },
    { platform: "缺少效率", total_volume: 80 },
    { platform: "错误通用坐标", x: 10, y: 20 },
  ]),
  unitCounts: [
    call("boundedUnitCount", 1000, 1000),
    call("boundedUnitCount", 500, 1000),
    call("boundedUnitCount", 1, 1000),
    call("boundedUnitCount", 0, 1000),
  ],
  lengths: [
    call("proportionalLength", 50, 100, 240),
    call("proportionalLength", 25, 100, 240),
  ],
  invalidF8Markup: ReactDOMServer.renderToStaticMarkup(
    React.createElement(basics.F8PlumbScatter, { chart: invalidF8Chart }),
  ),
}));
"""
    completed = subprocess.run(
        ["node", "-e", script],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(completed.stdout)


def test_basics_charts_map_only_real_f5_and_f6_payload_fields() -> None:
    probe = _run_basics_chart_probe()

    assert probe["f5"] == [
        {"label": "热门议题", "value": 120},
        {"label": "空间", "value": 28.5},
        {"label": "转化", "value": 12.5},
        {"label": "询价", "value": 10},
    ]
    assert probe["f6Product"] == [{"label": "空间", "first": 60, "second": 15}]
    assert probe["f6Sales"] == [{"label": "抖音", "first": 120, "second": 31}]


def test_basics_charts_map_real_f7_segments_and_valid_f8_points() -> None:
    probe = _run_basics_chart_probe()

    assert probe["f7"] == [
        {
            "label": "价格",
            "segments": [
                {"label": "优势", "value": 2},
                {"label": "劣势", "value": 3},
                {"label": "中性", "value": 1},
                {"label": "不明确", "value": 4},
            ],
        }
    ]
    assert probe["f8"] == [{"label": "抖音", "x": 120, "y": 42.5}]


def test_basics_charts_cap_unit_nodes_preserve_proportion_and_empty_invalid_f8() -> None:
    probe = _run_basics_chart_probe()
    source = Path("frontend/src/components/voc/report-visuals/BasicsCharts.tsx").read_text(
        encoding="utf-8"
    )

    assert probe["unitCounts"] == [80, 40, 1, 0]
    assert probe["lengths"] == [120, 60]
    assert "暂无可用于此图表的数据" in probe["invalidF8Markup"]
    assert "<svg" not in probe["invalidF8Markup"]
    assert ".report-chart-point:focus-visible" in source


def test_report_chart_registry_is_closed_and_complete() -> None:
    source = Path(
        "frontend/src/components/voc/report-visuals/ReportChartRegistry.tsx"
    ).read_text(encoding="utf-8")

    for template_id in ["F3", "F4", "F5", "F6", "F7", "F8", "L6", "L12", "L13", "L14", "L15", "P1", "P2", "P3", "P4"]:
        assert f"{template_id}:" in source
    assert "satisfies Record<ReportTemplateId" in source
    assert "dangerouslySetInnerHTML" not in source
    assert "eval(" not in source


def test_product_report_visuals_have_dedicated_continuous_components() -> None:
    source = Path("frontend/src/components/voc/report-visuals/ProductCharts.tsx").read_text(encoding="utf-8")

    for export_name in (
        "P1ProductFocusBars",
        "P2SentimentStack",
        "P3OpportunityLanes",
        "P4PkoMatrix",
    ):
        assert f"export function {export_name}" in source
    assert "boundedUnitCount" not in source
    assert "data-product-continuous-bar" in source
    assert "data-product-sentiment-stack" in source
    assert "data-product-opportunity-lane" in source
    assert "data-product-pko-matrix" in source


def test_product_storyline_resolves_allowlisted_metrics_and_l6_evidence() -> None:
    script = r"""
const assert = require("assert");
const fs = require("fs");
const path = require("path");
const base = path.resolve("frontend");
const ts = require(path.join(base, "node_modules", "typescript"));
const source = fs.readFileSync(
  path.join(base, "src/components/voc/report-summary/productStorylineData.ts"),
  "utf8",
);
const output = ts.transpileModule(source, {
  compilerOptions: {
    module: ts.ModuleKind.CommonJS,
    target: ts.ScriptTarget.ES2017,
    esModuleInterop: true,
  },
}).outputText;
const loaded = { exports: {} };
new Function("require", "module", "exports", output)(require, loaded, loaded.exports);

const storyline = {
  headline: "用户讨论由外观吸引，价格比较形成主要分歧",
  lead: "讨论先集中到外观，随后进入价格与竞品比较。",
  chapters: [
    {
      chapter_id: "focus", title: "用户在关注什么", conclusion: "外观最受关注",
      body: "讨论集中在外观。",
      metric_refs: ["product_focus.aspects", "unknown.path", "toString", "__proto__"],
      evidence_refs: [],
    },
    {
      chapter_id: "attitude", title: "用户如何评价", conclusion: "价格风险更集中",
      body: "价格负向反馈更集中。", metric_refs: ["product_opportunity.summary"], evidence_refs: [],
    },
    {
      chapter_id: "comparison", title: "用户在和谁比较", conclusion: "主要比较 ID.4",
      body: "价格是主要对比维度。", metric_refs: ["pko.summary"], evidence_refs: ["pko_001", "missing"],
    },
    {
      chapter_id: "evidence", title: "证据如何支撑", conclusion: "原话支持上述判断",
      body: "证据来自真实评论。", metric_refs: ["pko.dimension_result_matrix"], evidence_refs: ["pko_001"],
    },
  ],
};
const charts = [
  {
    chart_id: "product-focus", template_id: "P1", title: "", subtitle: "", insight: "", source_label: "product_focus.aspects",
    data: [
      { aspect: "外观", mention_rate: 40, comment_count: 48, positive_rate: 72.9 },
      { aspect: "价格", mention_rate: 25, comment_count: 30, positive_rate: 10 },
    ], meta: {},
  },
  {
    chart_id: "product-sentiment", template_id: "P2", title: "", subtitle: "", insight: "", source_label: "product_focus.aspects",
    data: [{ aspect: "外观", positive_rate: 72.9, neutral_rate: 18.8, negative_rate: 8.3 }], meta: {},
  },
  {
    chart_id: "product-opportunity", template_id: "P3", title: "", subtitle: "", insight: "", source_label: "product_opportunity",
    data: [
      { point_type: "surprise", aspect: "外观", opportunity_score: 38.2, mention_rate: 40 },
      { point_type: "surprise", aspect: "空间", opportunity_score: 30.1, mention_rate: 32 },
      { point_type: "surprise", aspect: "内饰", opportunity_score: 26.8, mention_rate: 28 },
      { point_type: "pain", aspect: "价格", opportunity_score: 22.4, mention_rate: 25 },
      { point_type: "conversion", aspect: "品牌", opportunity_score: 14.1, mention_rate: 15 },
    ], meta: {},
  },
  {
    chart_id: "product-pko-evidence", template_id: "L6", title: "", subtitle: "", insight: "", source_label: "pko.evidence_comments",
    data: [{
      comment_id: "pko_001", comment_text: "和ID.4比，价格没优势。", dimension: "价格",
      target: "ID.4", result_bucket: "disadvantage",
    }], meta: { displayed_count: 1, total_count: 1, unit: "条对比评论" },
  },
  {
    chart_id: "product-pko-matrix", template_id: "P4", title: "", subtitle: "", insight: "", source_label: "pko.dimension_result_matrix",
    data: [{
      dimension: "价格", advantage_count: 1, disadvantage_count: 7, neutral_count: 2,
      unclear_count: 0, top_target: "ID.4",
    }], meta: {},
  },
];

const view = loaded.exports.buildProductStorylineView(storyline, charts);
assert.deepEqual(view.chapters.map((item) => item.chapterId), ["focus", "attitude", "comparison", "evidence"]);
assert.equal(view.chapters[0].metrics[0].value, "40%");
assert.deepEqual(view.chapters[0].metrics.map((item) => item.label), ["外观提及率", "价格提及率"]);
assert.deepEqual(view.chapters[1].metrics.map((item) => item.label), [
  "惊喜点 · 外观", "风险点 · 价格", "机会点 · 品牌",
]);
assert.equal(view.chapters[2].evidence[0].commentId, "pko_001");
assert.equal(view.chapters[2].evidence.length, 1);
assert.equal(view.chapters[3].metrics[0].value, "10");

const invalidStoryline = {
  ...storyline,
  chapters: storyline.chapters.slice(0, 3),
};
assert.equal(loaded.exports.buildProductStorylineView(invalidStoryline, charts), null);
"""
    subprocess.run(
        ["node", "-e", script],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


@lru_cache(maxsize=1)
def _run_report_card_boundary_probe() -> dict:
    script = r"""
const fs = require("fs");
const path = require("path");
const base = path.resolve("frontend");
const ts = require(path.join(base, "node_modules", "typescript"));
const React = require(path.join(base, "node_modules", "react"));
const jsxRuntime = require(path.join(base, "node_modules", "react", "jsx-runtime"));
const ReactDOMServer = require(path.join(base, "node_modules", "react-dom", "server"));
const themeModule = {
  reportChartTheme: {
    primary: "var(--theme-primary)", secondary: "var(--theme-selected-text)",
    ink: "var(--theme-ink)", body: "var(--theme-body)", muted: "var(--theme-muted)",
    border: "var(--theme-border)", panel: "var(--theme-soft-panel)", white: "var(--theme-white)",
  },
};

function loadTsx(relativePath, stubs) {
  const source = fs.readFileSync(path.join(base, relativePath), "utf8");
  const output = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.CommonJS,
      target: ts.ScriptTarget.ES2017,
      jsx: ts.JsxEmit.ReactJSX,
      esModuleInterop: true,
    },
  }).outputText;
  const loaded = { exports: {} };
  const localRequire = (id) => {
    if (Object.prototype.hasOwnProperty.call(stubs, id)) return stubs[id];
    if (id === "react") return React;
    if (id === "react/jsx-runtime") return jsxRuntime;
    throw new Error(`Unexpected import: ${id}`);
  };
  new Function("require", "module", "exports", output)(localRequire, loaded, loaded.exports);
  return loaded.exports;
}

const chartStub = ({ chart }) =>
  React.createElement("svg", { "data-chart": chart.template_id });
const shell = loadTsx("src/components/voc/report-visuals/ReportVisualShell.tsx", {
  "./chartTheme": themeModule,
});
const narrative = loadTsx("src/components/voc/report-visuals/NarrativeCharts.tsx", {
  "./chartTheme": themeModule,
  "./ReportVisualShell": shell,
});
const smallData = loadTsx("src/components/voc/report-visuals/SmallDataCharts.tsx", {
  "./chartTheme": themeModule,
  "./ReportVisualShell": shell,
});
const productCharts = loadTsx("src/components/voc/report-visuals/ProductCharts.tsx", {
  "./chartTheme": themeModule,
  "./ReportVisualShell": shell,
});
const registry = loadTsx(
  "src/components/voc/report-visuals/ReportChartRegistry.tsx",
  {
    "./BasicsCharts": {
      F3HairlineArea: chartStub,
      F4TickDonut: chartStub,
      F5TickRows: chartStub,
      F6PairedRungs: chartStub,
      F7StackedRungs: chartStub,
      F8PlumbScatter: chartStub,
    },
    "./NarrativeCharts": narrative,
    "./SmallDataCharts": smallData,
    "./ProductCharts": productCharts,
  },
);
const storylineData = loadTsx(
  "src/components/voc/report-summary/productStorylineData.ts",
  {},
);
const storylineSummary = loadTsx(
  "src/components/voc/report-summary/ReportSummaryStoryline.tsx",
  {},
);

function renderRegistry(chart) {
  try {
    return {
      threw: false,
      markup: ReactDOMServer.renderToStaticMarkup(
        React.createElement(registry.ReportChartRegistry, { chart }),
      ),
    };
  } catch (error) {
    return { threw: true, markup: String(error) };
  }
}

const emptyIcon = () => null;
const reportCard = loadTsx(
  "src/components/voc/ReportAiSummaryCard.tsx",
  {
    "lucide-react": {
      Bot: emptyIcon,
      Check: emptyIcon,
      Clipboard: emptyIcon,
      Loader2: emptyIcon,
      Sparkles: emptyIcon,
      X: emptyIcon,
    },
    "@/components/ui/hover-border-gradient": {
      HoverBorderGradient: ({ children }) => React.createElement("button", null, children),
    },
    "@/components/voc/report-visuals/ReportChartRegistry": {
      ReportChartRegistry: registry.ReportChartRegistry,
      isReportTemplateId: registry.isReportTemplateId,
    },
    "@/components/voc/report-summary/productStorylineData": storylineData,
    "@/components/voc/report-summary/ReportSummaryStoryline": storylineSummary,
    "@/config/navigation": { apiBaseUrl: "" },
  },
);
const resolvePresentation = reportCard.resolveDepartmentReportPresentation;
const malformedV2 = {
  report_markdown: "# 保留的 v1 报告",
  report_narrative: {
    headline: "不完整 v2",
    executive_summary: "缺少 data_notes",
    section_insights: {},
  },
  structured_report: {
    charts: [{
      chart_id: "incomplete-chart",
      template_id: "F3",
      title: "缺少字段",
      data: [],
    }],
  },
};
const completeV2 = {
  report_markdown: "# 旧报告",
  report_narrative: {
    headline: "完整 v2",
    executive_summary: "结构完整",
    section_insights: {
      market_rhythm: "稳定",
      market_topics: "集中",
      market_platforms: "高效",
      market_feedback: "正向",
    },
    data_notes: [],
  },
  structured_report: {
    charts: [
      {
        chart_id: "market-volume-trend",
        template_id: "F3",
        title: "声量走势",
        subtitle: "日趋势",
        insight: "稳定",
        source_label: "volume.daily_trend",
        data: [],
        meta: { empty_reason: "暂无可用数据" },
      },
      {
        chart_id: "market-hot-topics",
        template_id: "F5",
        title: "热门话题",
        subtitle: "讨论量",
        insight: "集中",
        source_label: "topics",
        data: [],
        meta: { empty_reason: "暂无可用数据" },
      },
      {
        chart_id: "market-platform-efficiency",
        template_id: "F8",
        title: "平台效率",
        subtitle: "规模与效率",
        insight: "高效",
        source_label: "platforms",
        data: [],
        meta: { empty_reason: "暂无可用数据" },
      },
      {
        chart_id: "market-feedback-sentiment",
        template_id: "L14",
        title: "反馈构成",
        subtitle: "情感分布",
        insight: "正向",
        source_label: "sentiment",
        data: [],
        meta: { empty_reason: "暂无可用数据" },
      },
    ],
    evidence_references: [],
    calculation_notes: [],
  },
};
const unknownTemplateV2 = JSON.parse(JSON.stringify(completeV2));
unknownTemplateV2.structured_report.charts[2].template_id = "X99";
unknownTemplateV2.report_markdown = "# 未知模板时保留 Markdown";
const emptyChartsV2 = JSON.parse(JSON.stringify(completeV2));
emptyChartsV2.structured_report.charts = [];
emptyChartsV2.report_markdown = "# 图表缺失时保留 Markdown";
const unsafeMetaV2 = JSON.parse(JSON.stringify(completeV2));
unsafeMetaV2.structured_report.charts[0].meta = {
  empty_reason: { unsafe: true },
};
unsafeMetaV2.report_markdown = "# Meta 异常时保留 Markdown";
const completeProductV2 = {
  report_markdown: "# 旧产品报告",
  report_narrative: {
    headline: "完整产品 v2",
    executive_summary: "结构完整",
    section_insights: {
      product_focus: "关注",
      product_sentiment: "情感",
      product_opportunity: "机会",
      product_pko_relationships: "关系",
      product_pko_results: "结果",
    },
    data_notes: [],
  },
  structured_report: {
    charts: [
      ["product-focus", "F5"],
      ["product-sentiment", "F6"],
      ["product-opportunity", "F5"],
      ["product-pko-evidence", "L12"],
      ["product-pko-matrix", "F7"],
    ].map(([chart_id, template_id]) => ({
      chart_id,
      template_id,
      title: chart_id,
      subtitle: "固定副标题",
      insight: "",
      source_label: chart_id,
      data: [],
      meta: template_id === "L12"
        ? {
            displayed_count: 0,
            total_count: 0,
            unit: "条对比评论",
            empty_reason: "暂无可用数据",
          }
        : { empty_reason: "暂无可用数据" },
    })),
  },
};
const unsafeL12MetaV2 = JSON.parse(JSON.stringify(completeProductV2));
unsafeL12MetaV2.structured_report.charts[3].meta.displayed_count = { unsafe: true };
unsafeL12MetaV2.report_markdown = "# L12 Meta 异常时保留 Markdown";
const completeCurrentProductV2 = JSON.parse(JSON.stringify(completeProductV2));
completeCurrentProductV2.report_markdown = "# 新产品契约不应回退";
completeCurrentProductV2.structured_report.charts[0].template_id = "P1";
completeCurrentProductV2.structured_report.charts[0].data = [{
  aspect: "外观", mention_rate: 72,
}];
completeCurrentProductV2.structured_report.charts[0].meta = {};
completeCurrentProductV2.structured_report.charts[1].template_id = "P2";
completeCurrentProductV2.structured_report.charts[1].data = [{
  aspect: "外观", positive_rate: 66.67, neutral_rate: 0, negative_rate: 33.33,
}];
completeCurrentProductV2.structured_report.charts[1].meta = {};
completeCurrentProductV2.structured_report.charts[2].template_id = "P3";
completeCurrentProductV2.structured_report.charts[2].data = [{
  point_type: "surprise", aspect: "外观", opportunity_score: 88,
}];
completeCurrentProductV2.structured_report.charts[2].meta = {};
completeCurrentProductV2.structured_report.charts[3].template_id = "L6";
completeCurrentProductV2.structured_report.charts[3].data = [{
  comment_id: "pko-001", comment_text: "外观比竞品更协调", dimension: "外观",
  target: "竞品A", result_bucket: "advantage",
}];
completeCurrentProductV2.structured_report.charts[3].meta = {
  displayed_count: 1, total_count: 1, unit: "条对比评论",
};
completeCurrentProductV2.structured_report.charts[4].template_id = "P4";
completeCurrentProductV2.structured_report.charts[4].data = [{
  dimension: "外观", advantage_count: 1, disadvantage_count: 0,
  neutral_count: 0, unclear_count: 0,
}];
completeCurrentProductV2.structured_report.charts[4].meta = {};
completeCurrentProductV2.report_narrative.storyline = {
  headline: "外观吸引关注，价格比较形成分歧",
  lead: "讨论从外观进入价格比较。",
  chapters: [
    ["focus", "用户在关注什么"],
    ["attitude", "用户如何评价"],
    ["comparison", "用户在和谁比较"],
    ["evidence", "证据如何支撑"],
  ].map(([chapter_id, title], index) => ({
    chapter_id, title, conclusion: `${title}的结论`, body: "真实数据形成叙事。",
    metric_refs: index === 0 ? ["product_focus.aspects"] : [],
    evidence_refs: index === 3 ? ["pko-001"] : [],
  })),
};
const invalidStorylineProductV2 = JSON.parse(JSON.stringify(completeCurrentProductV2));
invalidStorylineProductV2.report_narrative.storyline.chapters.pop();
const mixedCurrentProductV2 = JSON.parse(JSON.stringify(completeCurrentProductV2));
mixedCurrentProductV2.structured_report.charts[3].template_id = "L12";
mixedCurrentProductV2.report_markdown = "# 混合产品契约回退";
const currentProductPresentation = resolvePresentation(completeCurrentProductV2);
const historicalProductPresentation = resolvePresentation(completeProductV2);
const storylineView = storylineData.buildProductStorylineView(
  currentProductPresentation.reportNarrative.storyline,
  currentProductPresentation.structuredReport.charts,
);
const storylineSummaryMarkup = ReactDOMServer.renderToStaticMarkup(
  React.createElement(storylineSummary.ReportSummaryStoryline, { storyline: storylineView }),
);
const currentProductSummaryMarkup = ReactDOMServer.renderToStaticMarkup(
  React.createElement(reportCard.DepartmentReportView, {
    reportNarrative: currentProductPresentation.reportNarrative,
    structuredReport: currentProductPresentation.structuredReport,
  }),
);
const legacyProductSummaryMarkup = ReactDOMServer.renderToStaticMarkup(
  React.createElement(reportCard.DepartmentReportView, {
    reportNarrative: historicalProductPresentation.reportNarrative,
    structuredReport: historicalProductPresentation.structuredReport,
  }),
);
const currentProductMarkup = currentProductPresentation.kind === "department"
  ? ReactDOMServer.renderToStaticMarkup(React.createElement(
      React.Fragment,
      null,
      currentProductPresentation.structuredReport.charts
        .filter((chart) => chart.template_id === "L6" || chart.template_id === "P2")
        .map((chart) => React.createElement(registry.ReportChartRegistry, {
          key: chart.chart_id,
          chart,
        })),
    ))
  : "";

process.stdout.write(JSON.stringify({
  unknownRegistry: renderRegistry({
    chart_id: "unknown",
    template_id: "X99",
    title: "未知模板",
    subtitle: "",
    insight: "",
    source_label: "test",
    data: [],
    meta: {},
  }),
  missingRegistry: renderRegistry({
    chart_id: "missing",
    title: "缺失模板",
    subtitle: "",
    insight: "",
    source_label: "test",
    data: [],
    meta: {},
  }),
  hasPresentationResolver: typeof resolvePresentation === "function",
  malformedPresentation:
    typeof resolvePresentation === "function"
      ? resolvePresentation(malformedV2)
      : null,
  completePresentation:
    typeof resolvePresentation === "function"
      ? resolvePresentation(completeV2)
      : null,
  unknownTemplatePresentation:
    typeof resolvePresentation === "function"
      ? resolvePresentation(unknownTemplateV2)
      : null,
  emptyChartsPresentation:
    typeof resolvePresentation === "function"
      ? resolvePresentation(emptyChartsV2)
      : null,
  unsafeMetaPresentation:
    typeof resolvePresentation === "function"
      ? resolvePresentation(unsafeMetaV2)
      : null,
  unsafeL12MetaPresentation:
    typeof resolvePresentation === "function"
      ? resolvePresentation(unsafeL12MetaV2)
      : null,
  historicalProductPresentation,
  currentProductPresentation,
  invalidStorylineProductPresentation: resolvePresentation(invalidStorylineProductV2),
  currentProductMarkup,
  storylineSummaryMarkup,
  currentProductSummaryMarkup,
  legacyProductSummaryMarkup,
  mixedCurrentProductPresentation: resolvePresentation(mixedCurrentProductV2),
}));
"""
    completed = subprocess.run(
        ["node", "-e", script],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(completed.stdout)


def test_report_chart_registry_renders_deterministic_empty_state_for_unknown_templates() -> None:
    probe = _run_report_card_boundary_probe()

    for result in [probe["unknownRegistry"], probe["missingRegistry"]]:
        assert result["threw"] is False
        assert "暂不支持该图表模板" in result["markup"]
        assert "<svg" not in result["markup"]


def test_report_card_keeps_markdown_when_v2_fields_are_incomplete() -> None:
    probe = _run_report_card_boundary_probe()

    assert probe["hasPresentationResolver"] is True
    assert probe["malformedPresentation"] == {
        "kind": "markdown",
        "reportMarkdown": "# 保留的 v1 报告",
    }
    assert probe["completePresentation"]["kind"] == "department"
    assert probe["completePresentation"]["reportNarrative"]["headline"] == "完整 v2"
    assert probe["unknownTemplatePresentation"] == {
        "kind": "markdown",
        "reportMarkdown": "# 未知模板时保留 Markdown",
    }
    assert probe["emptyChartsPresentation"] == {
        "kind": "markdown",
        "reportMarkdown": "# 图表缺失时保留 Markdown",
    }
    assert probe["unsafeMetaPresentation"] == {
        "kind": "markdown",
        "reportMarkdown": "# Meta 异常时保留 Markdown",
    }
    assert probe["unsafeL12MetaPresentation"] == {
        "kind": "markdown",
        "reportMarkdown": "# L12 Meta 异常时保留 Markdown",
    }


def test_report_card_accepts_current_product_contract_and_real_ssr_renders_l6_p2() -> None:
    probe = _run_report_card_boundary_probe()

    assert probe["historicalProductPresentation"]["kind"] == "department"
    assert "storyline" not in probe["historicalProductPresentation"]["reportNarrative"]
    assert probe["currentProductPresentation"]["kind"] == "department"
    assert [
        chart["template_id"]
        for chart in probe["currentProductPresentation"]["structuredReport"]["charts"]
    ] == ["P1", "P2", "P3", "L6", "P4"]
    assert "data-product-sentiment-stack" in probe["currentProductMarkup"]
    assert "产品对比点簇图" in probe["currentProductMarkup"]
    assert "外观比竞品更协调" in probe["currentProductMarkup"]
    assert probe["currentProductPresentation"]["reportNarrative"]["storyline"]["chapters"][3]["chapter_id"] == "evidence"
    assert "storyline" not in probe["invalidStorylineProductPresentation"]["reportNarrative"]
    assert probe["mixedCurrentProductPresentation"] == {
        "kind": "markdown",
        "reportMarkdown": "# 混合产品契约回退",
    }


def test_storyline_summary_renders_one_hero_and_four_ordered_chapters() -> None:
    probe = _run_report_card_boundary_probe()
    markup = probe["storylineSummaryMarkup"]
    wired_markup = probe["currentProductSummaryMarkup"]

    assert markup.count("data-report-storyline-hero") == 1
    assert markup.index('data-story-chapter="focus"') < markup.index(
        'data-story-chapter="attitude"'
    )
    assert markup.index('data-story-chapter="attitude"') < markup.index(
        'data-story-chapter="comparison"'
    )
    assert markup.index('data-story-chapter="comparison"') < markup.index(
        'data-story-chapter="evidence"'
    )
    assert "P1" not in markup and "P2" not in markup
    assert "72%" in markup
    assert "外观比竞品更协调" in markup
    assert wired_markup.count("data-report-storyline-hero") == 1
    assert 'data-story-chapter="evidence"' in wired_markup
    assert "完整产品 v2" not in wired_markup
    assert "结构完整" not in wired_markup
    assert "摘要模式" in wired_markup


def test_storyline_summary_uses_only_shared_theme_tokens() -> None:
    source = Path(
        "frontend/src/components/voc/report-summary/ReportSummaryStoryline.tsx"
    ).read_text(encoding="utf-8")

    assert "from-[var(--theme-selected-bg)] to-[var(--theme-white)]" in source
    assert "var(--theme-primary)" in source
    assert "theme-selected-bg" in source
    assert "theme-ink" in source
    assert "theme-border" in source
    assert "theme-soft-panel" in source
    assert "lg:grid-cols-[minmax(0,1fr)_280px]" in source
    assert "rgba(" not in source
    assert "bg-rose-" not in source and "bg-emerald-" not in source


def test_legacy_product_summary_keeps_existing_insight_cards() -> None:
    markup = _run_report_card_boundary_probe()["legacyProductSummaryMarkup"]

    assert "data-report-storyline-hero" not in markup
    assert "完整产品 v2" in markup
    assert "结构完整" in markup
    assert "product-focus" in markup
    assert "product-pko-matrix" in markup
    assert "F5" in markup and "L12" in markup


def test_narrative_charts_use_defined_tokens_and_explicit_interactions() -> None:
    source = Path(
        "frontend/src/components/voc/report-visuals/NarrativeCharts.tsx"
    ).read_text(encoding="utf-8")
    globals_source = Path("frontend/src/app/globals.css").read_text(encoding="utf-8")

    for export_name in ["L12TypeColonnade", "L13HourglassStream", "L14HundredField"]:
        assert f"export function {export_name}" in source
    assert "data-pko-record" in source
    assert "comment_text" in source
    assert "--voc-chart-6" in globals_source
    assert "var(--voc-chart-6)" in source
    assert "var(--theme-negative)" not in source
    assert "prefers-reduced-motion" in source
    assert "Math.random" not in source


@lru_cache(maxsize=1)
def _run_narrative_chart_probe() -> dict:
    script = r"""
const fs = require("fs");
const path = require("path");
const base = path.resolve("frontend");
const ts = require(path.join(base, "node_modules", "typescript"));
const React = require(path.join(base, "node_modules", "react"));
const jsxRuntime = require(path.join(base, "node_modules", "react", "jsx-runtime"));
const ReactDOMServer = require(path.join(base, "node_modules", "react-dom", "server"));
const themeModule = {
  reportChartTheme: {
    primary: "var(--theme-primary)",
    secondary: "var(--theme-selected-text)",
    ink: "var(--theme-ink)",
    body: "var(--theme-body)",
    muted: "var(--theme-muted)",
    border: "var(--theme-border)",
    panel: "var(--theme-soft-panel)",
    white: "var(--theme-white)",
  },
};

function loadTsx(relativePath, stubs) {
  const source = fs.readFileSync(path.join(base, relativePath), "utf8");
  const output = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.CommonJS,
      target: ts.ScriptTarget.ES2017,
      jsx: ts.JsxEmit.ReactJSX,
      esModuleInterop: true,
    },
  }).outputText;
  const loaded = { exports: {} };
  const localRequire = (id) => {
    if (Object.prototype.hasOwnProperty.call(stubs, id)) return stubs[id];
    if (id === "react") return React;
    if (id === "react/jsx-runtime") return jsxRuntime;
    throw new Error(`Unexpected import: ${id}`);
  };
  new Function("require", "module", "exports", output)(localRequire, loaded, loaded.exports);
  return loaded.exports;
}

const shell = loadTsx(
  "src/components/voc/report-visuals/ReportVisualShell.tsx",
  { "./chartTheme": themeModule },
);
const narrative = loadTsx(
  "src/components/voc/report-visuals/NarrativeCharts.tsx",
  { "./chartTheme": themeModule, "./ReportVisualShell": shell },
);
const l12Data = [
  {
    comment_id: "c-1",
    target: "竞品 A",
    dimension: "空间",
    result: "advantage",
    comment_text: "第一条用户原声",
  },
  {
    comment_id: "c-2",
    target: "竞品 A",
    dimension: "价格",
    result: "disadvantage",
    comment_text: "第二条用户原声",
  },
  {
    comment_id: "c-3",
    target: "竞品 B",
    dimension: "空间",
    result: "neutral",
    comment_text: "第三条用户原声",
  },
  {
    comment_id: "c-4",
    target: "竞品 C",
    dimension: "配置",
    result: "unclear",
    comment_text: "第四条用户原声",
  },
  {
    comment_id: "missing-copy",
    target: "竞品 D",
    dimension: "服务",
    result: "unclear",
  },
];
const chartBase = {
  title: "测试图表",
  subtitle: "测试副标题",
  insight: "",
  source_label: "test.source",
  meta: {},
};
const l12Chart = {
  ...chartBase,
  chart_id: "l12",
  template_id: "L12",
  data: l12Data,
  meta: { displayed_count: 4, total_count: 4, unit: "条对比评论" },
};
const l13Data = [
  { stage: "已打标评论", count: 200 },
  { stage: "车相关评论", count: 100 },
  { stage: "销售相关意图", count: 50 },
];
const l13Chart = {
  ...chartBase,
  chart_id: "l13",
  template_id: "L13",
  data: l13Data,
};
const l14Data = [
  { label: "正向", rate: 49.6 },
  { label: "中性", rate: 25.2 },
  { label: "负向", rate: 25.2 },
  { label: "只有数量", count: 10 },
];
const l14Chart = {
  ...chartBase,
  chart_id: "l14",
  template_id: "L14",
  data: l14Data,
};
const l12Markup = ReactDOMServer.renderToStaticMarkup(
  React.createElement(narrative.L12TypeColonnade, { chart: l12Chart }),
);
const l13Markup = ReactDOMServer.renderToStaticMarkup(
  React.createElement(narrative.L13HourglassStream, { chart: l13Chart }),
);
const l14Markup = ReactDOMServer.renderToStaticMarkup(
  React.createElement(narrative.L14HundredField, { chart: l14Chart }),
);
const zeroTailL13Markup = ReactDOMServer.renderToStaticMarkup(
  React.createElement(narrative.L13HourglassStream, {
    chart: {
      ...l13Chart,
      data: [
        { stage: "已打标评论", count: 10 },
        { stage: "车相关评论", count: 0 },
        { stage: "销售相关意图", count: 0 },
      ],
    },
  }),
);

process.stdout.write(JSON.stringify({
  l12Records: narrative.mapL12Records(l12Data),
  l12PathCount: (l12Markup.match(/data-pko-record=/g) || []).length,
  l12ListItemCount: (l12Markup.match(/role="listitem"/g) || []).length,
  l12HasListRole: l12Markup.includes('role="list"'),
  l12HasFakeButtonRole: l12Markup.includes('role="button"'),
  l12DescribedByIds: [...l12Markup.matchAll(/aria-describedby="([^"]+)"/g)].map(
    (match) => match[1],
  ),
  l12DescriptionIdsExist: [...l12Markup.matchAll(/aria-describedby="([^"]+)"/g)].every(
    (match) => l12Markup.includes(`id="${match[1]}"`),
  ),
  l12HasCopy: [
    l12Markup.includes("第一条用户原声"),
    l12Markup.includes("第二条用户原声"),
    l12Markup.includes("第三条用户原声"),
    l12Markup.includes("第四条用户原声"),
  ],
  l12HasCount: l12Markup.includes("展示 4 / 总计 4 条"),
  l12ResultLabels: typeof narrative.resultBucketLabel === "function"
    ? ["advantage", "disadvantage", "neutral", "unclear"].map(narrative.resultBucketLabel)
    : null,
  l12HasResultCopy: ["优势", "劣势", "中性", "不明确"].map(
    (label) => l12Markup.includes(`结果：${label}`),
  ),
  l12ActivationKeys: typeof narrative.isL12ActivationKey === "function"
    ? ["Enter", " ", "Escape"].map(narrative.isL12ActivationKey)
    : null,
  usesRiskToken: l12Markup.includes("var(--voc-chart-6)")
    && l14Markup.includes("var(--voc-chart-6)"),
  l13Stages: narrative.mapL13Stages(l13Data),
  l13Widths: l13Data.map((row) => narrative.stageWidth(row.count, 200)),
  l13Order: [
    l13Markup.indexOf("已打标评论"),
    l13Markup.indexOf("车相关评论"),
    l13Markup.indexOf("销售相关意图"),
  ],
  invalidL13: narrative.mapL13Stages([
    { stage: "第一阶段", count: 10 },
    { stage: "不是子集", count: 11 },
  ]),
  zeroTailL13Markup,
  l14Groups: narrative.allocateHundredCells(l14Data),
  l14CellCount: (l14Markup.match(/data-hundred-cell=/g) || []).length,
  l14HasRemainder: l14Markup.includes("rounding_remainder"),
}));
"""
    completed = subprocess.run(
        ["node", "-e", script],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(completed.stdout)


def test_l12_renders_one_path_per_real_record_and_exposes_original_copy() -> None:
    probe = _run_narrative_chart_probe()

    assert [row["comment_id"] for row in probe["l12Records"]] == ["c-1", "c-2", "c-3", "c-4"]
    assert probe["l12PathCount"] == 4
    assert probe["l12HasCopy"] == [True, True, True, True]
    assert probe["l12HasCount"] is True
    assert probe["l12ResultLabels"] == ["优势", "劣势", "中性", "不明确"]
    assert probe["l12HasResultCopy"] == [True, True, True, True]
    assert probe["usesRiskToken"] is True


def test_l12_exposes_list_semantics_descriptions_and_activation_keys() -> None:
    probe = _run_narrative_chart_probe()

    assert probe["l12HasListRole"] is True
    assert probe["l12HasFakeButtonRole"] is False
    assert probe["l12ListItemCount"] == probe["l12PathCount"] == 4
    assert len(probe["l12DescribedByIds"]) == 4
    assert probe["l12DescriptionIdsExist"] is True
    assert probe["l12ActivationKeys"] == [True, True, False]


def test_l13_preserves_subset_order_and_uses_first_stage_ratio() -> None:
    probe = _run_narrative_chart_probe()

    assert probe["l13Stages"] == [
        {"label": "已打标评论", "count": 200},
        {"label": "车相关评论", "count": 100},
        {"label": "销售相关意图", "count": 50},
    ]
    assert probe["l13Widths"] == [290, 145, 72.5]
    assert probe["l13Order"] == sorted(probe["l13Order"])
    assert probe["invalidL13"] == []
    assert "NaN" not in probe["zeroTailL13Markup"]
    assert "Infinity" not in probe["zeroTailL13Markup"]


def test_l14_allocates_exactly_one_hundred_cells_without_mutating_categories() -> None:
    probe = _run_narrative_chart_probe()

    assert probe["l14Groups"] == [
        {"key": "正向", "label": "正向", "count": 49, "is_remainder": False},
        {"key": "中性", "label": "中性", "count": 25, "is_remainder": False},
        {"key": "负向", "label": "负向", "count": 25, "is_remainder": False},
        {
            "key": "rounding_remainder",
            "label": "舍入余量",
            "count": 1,
            "is_remainder": True,
        },
    ]
    assert probe["l14CellCount"] == 100
    assert probe["l14HasRemainder"] is True


@lru_cache(maxsize=1)
def _run_l6_l15_chart_probe() -> dict:
    script = r"""
const assert = require("assert");
const fs = require("fs");
const path = require("path");
const base = path.resolve("frontend");
const ts = require(path.join(base, "node_modules", "typescript"));
const React = require(path.join(base, "node_modules", "react"));
const jsxRuntime = require(path.join(base, "node_modules", "react", "jsx-runtime"));
const ReactDOMServer = require(path.join(base, "node_modules", "react-dom", "server"));
const themeModule = {
  reportChartTheme: {
    primary: "var(--theme-primary)", secondary: "var(--theme-selected-text)",
    ink: "var(--theme-ink)", body: "var(--theme-body)", muted: "var(--theme-muted)",
    border: "var(--theme-border)", panel: "var(--theme-soft-panel)", white: "var(--theme-white)",
  },
};

function loadTsx(relativePath, stubs) {
  const source = fs.readFileSync(path.join(base, relativePath), "utf8");
  const output = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2017,
      jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true,
    },
  }).outputText;
  const loaded = { exports: {} };
  const localRequire = (id) => {
    if (Object.prototype.hasOwnProperty.call(stubs, id)) return stubs[id];
    if (id === "react") return React;
    if (id === "react/jsx-runtime") return jsxRuntime;
    throw new Error(`Unexpected import: ${id}`);
  };
  new Function("require", "module", "exports", output)(localRequire, loaded, loaded.exports);
  return loaded.exports;
}

const shell = loadTsx("src/components/voc/report-visuals/ReportVisualShell.tsx", {
  "./chartTheme": themeModule,
});
const narrative = loadTsx("src/components/voc/report-visuals/NarrativeCharts.tsx", {
  "./chartTheme": themeModule, "./ReportVisualShell": shell,
});
const smallData = loadTsx("src/components/voc/report-visuals/SmallDataCharts.tsx", {
  "./chartTheme": themeModule, "./ReportVisualShell": shell,
});

const l6Data = [
  { comment_id: "c1", comment_text: "a", dimension: "外观", target: "竞品B", result_bucket: "advantage" },
  { comment_id: "c2", comment_text: "b", dimension: "外观", target: "竞品A", result_bucket: "neutral" },
  { comment_id: "c3", comment_text: "c", dimension: "外观", target: "竞品B", result_bucket: "advantage" },
  { comment_id: "c4", comment_text: "d", dimension: "空间", target: "竞品A", result_bucket: "disadvantage" },
];
const clusters = narrative.mapL6Clusters(l6Data);
assert.deepEqual(clusters.map(({ dimension, totalCount }) => ({ dimension, totalCount })), [
  { dimension: "外观", totalCount: 3 }, { dimension: "空间", totalCount: 1 },
]);
assert.equal(clusters[0].targets[0].target, "竞品B");
assert.equal(clusters[0].targets[0].count, 2);
assert.ok(narrative.bubbleRadius(4, 4) > narrative.bubbleRadius(1, 4));
assert.ok(Math.abs((narrative.bubbleRadius(4, 4) ** 2) / (narrative.bubbleRadius(1, 4) ** 2) - 4) < 1.0);
assert.equal(narrative.bubbleRadius(0, 4), 10);
assert.equal(narrative.bubbleRadius(100, 4), 30);
const denseL6Data = [5, 8].flatMap((targetCount, clusterIndex) =>
  Array.from({ length: targetCount }, (_, targetIndex) => ({
    comment_id: `dense-${clusterIndex}-${targetIndex}`,
    comment_text: `证据-${clusterIndex}-${targetIndex}`,
    dimension: `密集维度${clusterIndex + 1}`,
    target: `竞品${targetIndex + 1}`,
    result_bucket: "neutral",
  })),
);
const denseLayout = narrative.layoutL6Clusters(narrative.mapL6Clusters(denseL6Data));
for (const cluster of denseLayout.clusters) {
  for (let left = 0; left < cluster.targets.length; left += 1) {
    for (let right = left + 1; right < cluster.targets.length; right += 1) {
      const a = cluster.targets[left];
      const b = cluster.targets[right];
      assert.ok(
        Math.hypot(a.x - b.x, a.y - b.y) >= a.radius + b.radius + narrative.L6_LABEL_SAFE_GAP,
      );
    }
  }
  for (const target of cluster.targets) {
    assert.ok(target.x - target.radius >= 0 && target.x + target.radius <= denseLayout.width);
    assert.ok(target.y - target.radius >= 0 && target.y + target.radius <= denseLayout.height);
    assert.ok(target.labelX >= 0 && target.labelX <= denseLayout.width);
    assert.ok(target.labelY >= 0 && target.labelY <= denseLayout.height);
  }
  assert.ok(cluster.centerLabelX >= 0 && cluster.centerLabelX <= denseLayout.width);
  assert.ok(cluster.centerLabelY >= 0 && cluster.centerLabelY <= denseLayout.height);
}
const denseLongLabelData = Array.from({ length: 50 }, (_, index) => ({
  comment_id: `long-${String(index).padStart(2, "0")}`,
  comment_text: `长标签代表评论-${index}`,
  dimension: "单一密集维度",
  target: `九字长标签${String(index).padStart(4, "0")}`,
  result_bucket: "neutral",
}));
const denseLongLayout = narrative.layoutL6Clusters(narrative.mapL6Clusters(denseLongLabelData));
const denseLongBoxes = denseLongLayout.clusters[0].targets
  .map((target) => target.labelBox)
  .filter(Boolean);
const boxesIntersect = (a, b) =>
  a.x < b.x + b.width && a.x + a.width > b.x
  && a.y < b.y + b.height && a.y + a.height > b.y;
const denseLongLabelsNonOverlapping =
  denseLongBoxes.length === 50
  && denseLongBoxes.every((box) =>
    box.x >= 0 && box.y >= 0
    && box.x + box.width <= denseLongLayout.width
    && box.y + box.height <= denseLongLayout.height)
  && denseLongBoxes.every((box, left) =>
    denseLongBoxes.slice(left + 1).every((other) => !boxesIntersect(box, other)));
const deterministicDenseLongLayout =
  JSON.stringify(denseLongLayout)
  === JSON.stringify(narrative.layoutL6Clusters(narrative.mapL6Clusters(denseLongLabelData)));

const l15Data = [
  { aspect: "外观", positive_rate: 62.5, neutral_rate: 12.5, negative_rate: 25 },
  { aspect: "空间", positive_rate: 10, neutral_rate: 20, negative_rate: 70 },
];
const l15PrecisionData = [{
  aspect: "精度", positive_rate: 33.33, neutral_rate: 33.34, negative_rate: 33.33,
}];
const allocation = smallData.allocateSentimentTicks(
  { positiveRate: 62.5, neutralRate: 12.5, negativeRate: 25 }, 20,
);
assert.deepEqual(allocation, { positive: 12, neutral: 3, negative: 5 });
assert.equal(allocation.positive + allocation.neutral + allocation.negative, 20);

const chartBase = {
  title: "测试图表", subtitle: "测试副标题", insight: "", source_label: "test.source", meta: {},
};
const l6Markup = ReactDOMServer.renderToStaticMarkup(React.createElement(
  narrative.L6ClusterField,
  { chart: { ...chartBase, chart_id: "l6", template_id: "L6", data: l6Data,
    meta: { displayed_count: 4, total_count: 4, unit: "条对比评论" } } },
));
const l15Markup = ReactDOMServer.renderToStaticMarkup(React.createElement(
  smallData.L15BallotTally,
  { chart: { ...chartBase, chart_id: "l15", template_id: "L15", data: l15Data } },
));
const l15PrecisionMarkup = ReactDOMServer.renderToStaticMarkup(React.createElement(
  smallData.L15BallotTally,
  { chart: { ...chartBase, chart_id: "l15-precision", template_id: "L15", data: l15PrecisionData } },
));

process.stdout.write(JSON.stringify({
  l6Markup,
  l15Markup,
  l15PrecisionMarkup,
  l15Rows: smallData.normalizeL15Rows(l15Data),
  l15TickCount: (l15Markup.match(/data-sentiment-tick=/g) || []).length,
  l15TickCounts: ["外观", "空间"].map((aspect) => (
    l15Markup.match(new RegExp(`data-sentiment-tick="${aspect}-`, "g")) || []
  ).length),
  initialL6Detail: typeof narrative.resolveL6ActiveDetail === "function"
    ? narrative.resolveL6ActiveDetail(clusters)
    : null,
  secondL6Detail: typeof narrative.resolveL6ActiveDetail === "function"
    ? narrative.resolveL6ActiveDetail(clusters, "外观-竞品A")
    : null,
  denseLongLabelsNonOverlapping,
  deterministicDenseLongLayout,
  denseLongLayoutWidth: denseLongLayout.width,
  l6ScaledMinimumFontAt1480: typeof narrative.L6_MIN_FONT_SIZE === "number"
    ? narrative.L6_MIN_FONT_SIZE * 1480 / denseLongLayout.width
    : 0,
}));
"""
    completed = subprocess.run(
        ["node", "-e", script],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(completed.stdout)


def test_l6_cluster_field_groups_pko_evidence_and_keeps_it_accessible() -> None:
    probe = _run_l6_l15_chart_probe()

    assert "外观" in probe["l6Markup"]
    assert "竞品B" in probe["l6Markup"]
    assert "· 2" in probe["l6Markup"]
    assert 'role="button"' in probe["l6Markup"]
    assert 'tabindex="0"' in probe["l6Markup"]
    assert all(copy in probe["l6Markup"] for copy in ["a", "b", "c", "d"])
    assert 'data-l6-active-detail="true"' in probe["l6Markup"]
    assert "代表评论" in probe["l6Markup"]
    described_by_ids = [
        match.group(1)
        for match in re.finditer(r'aria-describedby="([^"]+)"', probe["l6Markup"])
    ]
    assert described_by_ids
    assert all(f'id="{description_id}"' in probe["l6Markup"] for description_id in described_by_ids)
    assert probe["initialL6Detail"] == {
        "key": "外观-竞品B",
        "dimension": "外观",
        "target": "竞品B",
        "count": 2,
        "comment_text": "a",
    }
    assert probe["secondL6Detail"] == {
        "key": "外观-竞品A",
        "dimension": "外观",
        "target": "竞品A",
        "count": 1,
        "comment_text": "b",
    }


def test_l6_dense_fifty_long_labels_have_pairwise_safe_bboxes_and_readable_scale() -> None:
    probe = _run_l6_l15_chart_probe()

    assert probe["denseLongLabelsNonOverlapping"] is True
    assert probe["deterministicDenseLongLayout"] is True
    assert probe["denseLongLayoutWidth"] <= 2152
    assert probe["l6ScaledMinimumFontAt1480"] >= 5.5


def test_l15_ballot_tally_renders_twenty_ticks_per_aspect_with_exact_rates() -> None:
    probe = _run_l6_l15_chart_probe()

    assert probe["l15Rows"] == [
        {"aspect": "外观", "positiveRate": 62.5, "neutralRate": 12.5, "negativeRate": 25},
        {"aspect": "空间", "positiveRate": 10, "neutralRate": 20, "negativeRate": 70},
    ]
    assert all(rate in probe["l15Markup"] for rate in ["62.5%", "12.5%", "25%", "10%", "20%", "70%"])
    assert probe["l15TickCount"] == 40
    assert probe["l15TickCounts"] == [20, 20]
    assert all(rate in probe["l15PrecisionMarkup"] for rate in ["33.33%", "33.34%"])
    assert 'class="h-auto w-full"' in probe["l15Markup"]
    assert 'class="h-auto w-full"' in probe["l6Markup"]


def test_event_report_uses_shared_svg_registry_and_keeps_legacy_chart_fallback() -> None:
    source = Path("frontend/src/components/voc/ReportAiSummaryCard.tsx").read_text(encoding="utf-8")

    assert "isReportVisualChart(chart)" in source
    assert "<ReportChartRegistry chart={chart}" in source
    assert "renderChart(chart)" in source
    assert "report.charts.map(renderStructuredReportChart)" in source


def test_report_visual_shell_places_nonempty_insight_before_chart_and_omits_empty_state_insight() -> None:
    source = Path("frontend/src/components/voc/report-visuals/ReportVisualShell.tsx").read_text(encoding="utf-8")

    assert source.index("{chart.subtitle}") < source.index("{chart.insight}")
    assert source.index("{chart.insight}") < source.index("{children}")
    assert source.index("{children}") < source.index("数据来源：{chart.source_label}")

    script = r"""
const fs = require("fs");
const path = require("path");
const base = path.resolve("frontend");
const ts = require(path.join(base, "node_modules", "typescript"));
const React = require(path.join(base, "node_modules", "react"));
const jsxRuntime = require(path.join(base, "node_modules", "react", "jsx-runtime"));
const ReactDOMServer = require(path.join(base, "node_modules", "react-dom", "server"));
const source = fs.readFileSync(path.join(base, "src/components/voc/report-visuals/ReportVisualShell.tsx"), "utf8");
const output = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2017, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true },
}).outputText;
const loaded = { exports: {} };
const localRequire = (id) => {
  if (id === "react") return React;
  if (id === "react/jsx-runtime") return jsxRuntime;
  if (id === "./chartTheme") return { reportChartTheme: { ink: "ink", muted: "muted", body: "body", border: "border", white: "white", panel: "panel" } };
  throw new Error(`Unexpected import: ${id}`);
};
new Function("require", "module", "exports", output)(localRequire, loaded, loaded.exports);
process.stdout.write(ReactDOMServer.renderToStaticMarkup(React.createElement(loaded.exports.ReportVisualShell, {
  chart: { title: "空图", subtitle: "无数据", insight: "不应显示的模型解读", source_label: "test", data: [] },
  hasData: false,
  children: React.createElement("svg"),
})));
"""
    completed = subprocess.run(
        ["node", "-e", script],
        cwd=Path.cwd(),
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert completed.returncode == 0, completed.stderr
    assert "不应显示的模型解读" not in completed.stdout
    assert "暂无可用于此图表的数据" in completed.stdout
    assert "<svg" not in completed.stdout


def test_report_modal_uses_wide_viewport_flex_scroller_for_multiline_header() -> None:
    source = Path("frontend/src/components/voc/ReportAiSummaryCard.tsx").read_text(encoding="utf-8")

    assert "w-[94vw]" in source
    assert "max-w-[1480px]" in source
    assert 'className="flex max-h-[92vh] w-[94vw] max-w-[1480px] flex-col overflow-hidden' in source
    assert '<header className="shrink-0 flex items-start justify-between' in source
    assert 'className="min-h-0 flex-1 overflow-auto p-5 md:p-6"' in source
    assert "max-h-[calc(92vh-92px)]" not in source


def test_l6_full_width_in_department_report_chart_grid() -> None:
    source = Path("frontend/src/components/voc/ReportAiSummaryCard.tsx").read_text(encoding="utf-8")

    assert 'chart.template_id === "L6"' in source
    assert '["product-focus", "product-pko-matrix"].includes(chart.chart_id)' in source
    assert "grid gap-4 xl:grid-cols-2" in source


def test_event_report_view_toggle_exposes_pressed_state() -> None:
    source = Path("frontend/src/components/voc/ReportAiSummaryCard.tsx").read_text(encoding="utf-8")

    assert 'aria-pressed={reportViewMode === "dashboard"}' in source
    assert 'aria-pressed={reportViewMode === "report"}' in source


def test_event_report_mixed_svg_and_legacy_charts_render_in_input_order() -> None:
    script = r"""
const fs = require("fs");
const path = require("path");
const base = path.resolve("frontend");
const ts = require(path.join(base, "node_modules", "typescript"));
const React = require(path.join(base, "node_modules", "react"));
const jsxRuntime = require(path.join(base, "node_modules", "react", "jsx-runtime"));
const ReactDOMServer = require(path.join(base, "node_modules", "react-dom", "server"));

const source = fs.readFileSync(path.join(base, "src/components/voc/ReportAiSummaryCard.tsx"), "utf8");
const output = ts.transpileModule(source, {
  compilerOptions: {
    module: ts.ModuleKind.CommonJS,
    target: ts.ScriptTarget.ES2017,
    jsx: ts.JsxEmit.ReactJSX,
    esModuleInterop: true,
  },
}).outputText;
const loaded = { exports: {} };
const emptyIcon = () => null;
const localRequire = (id) => {
  if (id === "react") return React;
  if (id === "react/jsx-runtime") return jsxRuntime;
  if (id === "lucide-react") {
    return {
      Bot: emptyIcon,
      Check: emptyIcon,
      Clipboard: emptyIcon,
      Loader2: emptyIcon,
      Sparkles: emptyIcon,
      X: emptyIcon,
    };
  }
  if (id === "@/components/ui/hover-border-gradient") {
    return { HoverBorderGradient: ({ children }) => React.createElement("button", null, children) };
  }
  if (id === "@/components/voc/report-visuals/ReportChartRegistry") {
    return {
      ReportChartRegistry: ({ chart }) =>
        React.createElement("svg", { "data-chart-id": chart.chart_id }),
      isReportTemplateId: (value) =>
        ["F3", "F4", "F5", "F6", "F7", "F8", "L12", "L13", "L14"].includes(value),
    };
  }
  if (id === "@/components/voc/report-summary/productStorylineData") {
    return { buildProductStorylineView: () => null, isReportStoryline: () => false };
  }
  if (id === "@/components/voc/report-summary/ReportSummaryStoryline") {
    return { ReportSummaryStoryline: () => null };
  }
  if (id === "@/config/navigation") return { apiBaseUrl: "" };
  throw new Error(`Unexpected import: ${id}`);
};
new Function("require", "module", "exports", output)(localRequire, loaded, loaded.exports);

const charts = [
  {
    chart_id: "svg-first",
    template_id: "F3",
    title: "SVG",
    subtitle: "",
    insight: "",
    source_label: "test",
    data: [],
    meta: { empty_reason: "暂无可用数据" },
  },
  {
    chart_id: "legacy-second",
    chart_type: "bar",
    title: "Legacy",
    data: [{ label: "A", value: 2 }],
    x_field: "label",
    y_field: "value",
  },
];
const markup = ReactDOMServer.renderToStaticMarkup(
  React.createElement(
    React.Fragment,
    null,
    charts.map((chart) => loaded.exports.renderStructuredReportChart(chart)),
  ),
);
process.stdout.write(markup);
"""
    completed = subprocess.run(
        ["node", "-e", script],
        cwd=Path.cwd(),
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.index('data-chart-id="svg-first"') < completed.stdout.index("Legacy")
