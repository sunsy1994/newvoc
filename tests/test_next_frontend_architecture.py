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
    assert "grid-cols-[136px_1fr]" in sidebar
    assert "bg-[#5347CE] text-white" in nav_item
    assert "bg-white text-[#151720]" in nav_item


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
        "src/app/competitors/accounts/page.tsx",
        "src/app/competitors/works/page.tsx",
        "src/app/profiles/kols/page.tsx",
        "src/app/profiles/comment-users/page.tsx",
        "src/app/system/parameters/page.tsx",
        "src/app/system/prompts/page.tsx",
        "src/app/system/emojis/page.tsx",
    ]
    for page in expected_pages:
        assert (root / page).exists()

    assert "apiBaseUrl" in navigation
    assert "serverApiBaseUrl" in navigation
    assert "http://127.0.0.1:8000/api" in navigation
    assert "市场看板" in navigation
    assert "/voc/events/product" in navigation
    assert "/assets/comment-users" in navigation
    assert "/system/parameters" in navigation
    assert "/system/prompts" in navigation
    assert "/system/emojis" in navigation
    assert "/tasks/ai-profile-flow" in navigation
    assert "传播内容" not in navigation
    assert "KOL与用户" not in navigation

    market_page = (root / "src/app/voc/events/market/page.tsx").read_text(encoding="utf-8")
    assert "serverApiBaseUrl" in market_page
    assert "/market-dashboard" in market_page


def test_system_management_pages_use_real_api_components() -> None:
    root = Path("frontend")
    navigation = (root / "src/config/navigation.ts").read_text(encoding="utf-8")
    parameter_page = (root / "src/app/system/parameters/page.tsx").read_text(encoding="utf-8")
    prompt_page = (root / "src/app/system/prompts/page.tsx").read_text(encoding="utf-8")
    emoji_page = (root / "src/app/system/emojis/page.tsx").read_text(encoding="utf-8")
    component = (root / "src/components/system/SystemSettingsPage.tsx").read_text(encoding="utf-8")
    emoji_component = (root / "src/components/system/EmojiDictionaryPage.tsx").read_text(encoding="utf-8")

    assert "系统管理" in navigation
    assert "参数维护" in navigation
    assert "提示词维护" in navigation
    assert "表情包维护" in navigation
    assert "SystemSettingsPage" in parameter_page
    assert "SystemSettingsPage" in prompt_page
    assert "EmojiDictionaryPage" in emoji_page
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
    }

    for asset_key, relative_path in expected_assets.items():
        page = (root / relative_path).read_text(encoding="utf-8")
        assert "AssetLibraryPage" in page
        assert "PlaceholderPage" not in page
        assert f'assetKey: "{asset_key}"' in page

    assert "fetch(buildApiUrl(`/assets/${config.assetKey}`" in asset_component
    assert "`/assets/${config.assetKey}/export`" in asset_component


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
    assert 'label: "经典", swatch: "#5347CE"' in theme_frame
    assert "ChevronDown" in theme_frame
    assert "themeOptions.map" in theme_frame
    assert "页面主题" not in theme_frame
    assert 'useState<DashboardTheme>("soft")' in theme_frame
    assert "--soft-page: #F6F7F9" in globals_css
    assert "--soft-header: #F8F5F1" in globals_css
    assert "--soft-card: #FFFFFF" in globals_css
    assert "--soft-primary: #2D2B31" in globals_css
    assert "--soft-primary-hover: #1F1E22" in globals_css
    assert "--soft-selected-border: #D98252" in globals_css
    assert "--soft-selected-bg: #FFF5EE" in globals_css
    assert "--soft-selected-text: #3A302B" in globals_css
    assert "--soft-hover-bg: #F8F3ED" in globals_css
    assert "--soft-icon: #4B4850" in globals_css
    assert "--soft-muted: #8D8992" in globals_css
    assert "--sales-sankey-root: #87B96B" in globals_css
    assert "--sales-sankey-sales: #F2A56B" in globals_css
    assert "--sales-sankey-strong: #E57C45" in globals_css
    assert "--sales-sankey-neutral: #C8CAD2" in globals_css
    assert "--sales-chip-strong-text: #8E4525" in globals_css
    assert "--sales-chip-mid-text: #9C5B2B" in globals_css
    assert "--sales-chip-weak-text: #8A6A4D" in globals_css
    assert "--profile-unprofiled: #D8DAE2" in globals_css
    assert "--profile-completed: #87B96B" in globals_css
    assert "--profile-missing-bg: #F1EFEC" in globals_css
    assert "--profile-missing-text: #77727B" in globals_css
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
    assert "xl:grid-cols-[2fr_1fr]" in card
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
    assert "bg-[#eef1f6]" in card
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
    assert "MessageSquareText" not in card
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
    assert "className=\"voc-dashboard-header flex flex-wrap items-start justify-between gap-4\"" in header
    assert "className=\"voc-dashboard-controls flex max-w-full flex-col items-end gap-2\"" in header
    assert "className=\"voc-dashboard-filter-form flex flex-wrap items-center justify-end gap-2\"" in header
    assert "ThemeSelect" in header
    assert "border-[var(--theme-border)]" in header
    assert "bg-[var(--theme-primary)]" in header

    for page_path in pages:
        page = page_path.read_text(encoding="utf-8")
        assert "VocDashboardThemeFrame" in page
        assert "VocDashboardHeader" in page
        assert "<VocDashboardThemeFrame>" in page
        assert "<VocDashboardHeader" in page
        assert "className=\"space-y-5\"" in page
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
    assert "var(--voc-chart-2)" in combined
    assert "var(--voc-chart-3)" in combined
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
    assert "payload.key_events[0]?.event_id" not in component
    assert "event_id: null" in component
    assert "submitDataQuestion" in component
    assert "history: messages.slice(-10)" in component
    assert "dataQuestionResult.trace" not in component


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
