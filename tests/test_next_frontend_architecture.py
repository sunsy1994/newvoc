from pathlib import Path


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
        "src/app/voc/events/content/page.tsx",
        "src/app/voc/events/kol-users/page.tsx",
        "src/app/tasks/flow/page.tsx",
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
    ]
    for page in expected_pages:
        assert (root / page).exists()

    assert "apiBaseUrl" in navigation
    assert "serverApiBaseUrl" in navigation
    assert "http://127.0.0.1:8000/api" in navigation
    assert "市场看板" in navigation
    assert "/assets/comment-users" in navigation
    assert "传播内容" not in navigation
    assert "KOL与用户" not in navigation

    market_page = (root / "src/app/voc/events/market/page.tsx").read_text(encoding="utf-8")
    assert "serverApiBaseUrl" in market_page
    assert "/market-dashboard" in market_page


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
    hot_list = (root / "src/components/voc/HotPostList.tsx").read_text(encoding="utf-8")
    modal = (root / "src/components/voc/PostDetailModal.tsx").read_text(encoding="utf-8")

    assert "eventId={dashboard.event.event_id}" in market_page
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
