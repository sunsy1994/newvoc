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
    assert "bg-zinc-950 text-white" in nav_item
    assert "bg-white text-zinc-950 shadow-sm" in nav_item


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
    assert "传播内容" not in navigation
    assert "KOL与用户" not in navigation

    market_page = (root / "src/app/voc/events/market/page.tsx").read_text(encoding="utf-8")
    assert "serverApiBaseUrl" in market_page
    assert "/market-dashboard" in market_page
