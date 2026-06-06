# VOC Event Market Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first real business page for `VOC看事件 / 市场看板`, backed only by PostgreSQL/ETL data and exposed through a dedicated dashboard API.

**Architecture:** Extend the existing `event_voc_insights` service with one aggregate market-dashboard payload, expose it through FastAPI, and render it in the Next.js market page. Keep the first version focused: one secondary nav item, one event selector, cards plus lightweight SVG/CSS charts, no AI summary and no mock data.

**Tech Stack:** Python, FastAPI, psycopg, pytest, Next.js App Router, TypeScript, Tailwind CSS, lucide-react.

---

## File Structure

- Modify `app/services/event_voc_insights.py`
  - Add `get_voc_event_market_dashboard`.
  - Add SQL fetchers for trend, channel distribution, KOL type distribution, and hot posts.
  - Keep existing `get_voc_event_detail` behavior unchanged.
- Modify `app/routers/tasks.py`
  - Import `get_voc_event_market_dashboard`.
  - Add `GET /api/voc/events/{event_id}/market-dashboard`.
- Modify `tests/test_task_api.py`
  - Add a route-level test that proves the new API delegates to the market dashboard service and returns the expected sections.
- Create `tests/test_event_market_dashboard.py`
  - Unit test pure payload builders using monkeypatched fetch functions, so tests do not need PostgreSQL.
- Modify `frontend/src/config/navigation.ts`
  - Keep only `市场看板` under `VOC看事件`.
- Create `frontend/src/types/vocMarket.ts`
  - Define the dashboard response types used by the page and visual components.
- Create `frontend/src/components/voc/MetricCard.tsx`
  - Small card for headline metrics.
- Create `frontend/src/components/voc/VolumeTrendChart.tsx`
  - Lightweight SVG line chart for 主贴声量、评论声量、总声量.
- Create `frontend/src/components/voc/ChannelStackedBars.tsx`
  - Lightweight stacked bars for channel content/comment volume.
- Create `frontend/src/components/voc/KolTypeBars.tsx`
  - Horizontal bars for KOL type distribution.
- Create `frontend/src/components/voc/HotPostList.tsx`
  - Lightweight ranked list that only shows title and total engagement.
- Modify `frontend/src/app/voc/events/market/page.tsx`
  - Fetch event list and selected event dashboard payload.
  - Render event selector, metric cards, charts, and hot posts.
- Modify `tests/test_next_frontend_architecture.py`
  - Assert only the market child is present under `VOC看事件`.
  - Assert the market page fetches `/market-dashboard`.

---

### Task 1: Backend Market Dashboard API

**Files:**
- Modify: `app/services/event_voc_insights.py`
- Modify: `app/routers/tasks.py`
- Create: `tests/test_event_market_dashboard.py`
- Modify: `tests/test_task_api.py`

- [ ] **Step 1: Write the failing service test**

Create `tests/test_event_market_dashboard.py` with:

```python
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
    monkeypatch.setattr(event_voc_insights, "fetch_event_volume_trend", lambda conn, event_id: [{"date": "2026-05-14", "content_count": 2, "comment_count": 3, "total_volume": 5}])
    monkeypatch.setattr(event_voc_insights, "fetch_event_channel_distribution", lambda conn, event_id: [{"channel": "抖音", "content_count": 10, "comment_count": 8, "total_volume": 18}])
    monkeypatch.setattr(event_voc_insights, "fetch_event_kol_type_distribution", lambda conn, event_id: [{"kol_main_type": "车型实测测评KOL", "kol_count": 2, "content_count": 4, "total_engagement": 1200}])
    monkeypatch.setattr(event_voc_insights, "fetch_event_hot_posts", lambda conn, event_id: [{"content_id": "c1", "title": "试驾体验", "total_engagement": 999}])

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
    assert payload["hot_posts"][0]["title"] == "试驾体验"
```

- [ ] **Step 2: Run the service test and confirm it fails**

Run:

```powershell
python -m pytest tests\test_event_market_dashboard.py -q
```

Expected:

```text
FAILED ... AttributeError: module 'app.services.event_voc_insights' has no attribute 'get_voc_event_market_dashboard'
```

- [ ] **Step 3: Implement the service function and fetchers**

In `app/services/event_voc_insights.py`, add:

```python
def get_voc_event_market_dashboard(event_id: str, database_url: str = DATABASE_URL) -> dict[str, Any]:
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        overview = fetch_event_overview(conn, event_id)
        trend = fetch_event_volume_trend(conn, event_id)
        channel_distribution = fetch_event_channel_distribution(conn, event_id)
        kol_type_distribution = fetch_event_kol_type_distribution(conn, event_id)
        hot_posts = fetch_event_hot_posts(conn, event_id)
    return {
        "event": overview,
        "overview_metrics": build_market_overview_metrics(overview, kol_type_distribution),
        "volume_trend": trend,
        "channel_distribution": channel_distribution,
        "kol_type_distribution": kol_type_distribution,
        "hot_posts": hot_posts,
    }


def build_market_overview_metrics(
    overview: dict[str, Any],
    kol_type_distribution: list[dict[str, Any]],
) -> dict[str, Any]:
    content_count = int(overview.get("content_cnt") or 0)
    comment_count = int(overview.get("comment_cnt") or 0)
    return {
        "total_volume": content_count + comment_count,
        "content_count": content_count,
        "comment_count": comment_count,
        "kol_count": sum(int(row.get("kol_count") or 0) for row in kol_type_distribution),
        "kol_content_count": int(overview.get("kol_content_cnt") or 0),
        "total_engagement": int(overview.get("total_engagement") or 0),
    }
```

Add SQL fetchers:

```python
def fetch_event_volume_trend(conn: psycopg.Connection, event_id: str) -> list[dict[str, Any]]:
    query = """
        WITH content_daily AS (
          SELECT date_trunc('day', published_at)::date AS day, count(*)::bigint AS content_count
          FROM data_asset.dwd_content
          WHERE event_id = %s AND published_at IS NOT NULL
          GROUP BY 1
        ),
        comment_daily AS (
          SELECT date_trunc('day', cm.published_at)::date AS day, count(*)::bigint AS comment_count
          FROM data_asset.dwd_comment cm
          JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
          WHERE c.event_id = %s AND cm.published_at IS NOT NULL
          GROUP BY 1
        ),
        days AS (
          SELECT day FROM content_daily
          UNION
          SELECT day FROM comment_daily
        )
        SELECT day::text AS date,
               coalesce(content_count, 0) AS content_count,
               coalesce(comment_count, 0) AS comment_count,
               coalesce(content_count, 0) + coalesce(comment_count, 0) AS total_volume
        FROM days
        LEFT JOIN content_daily USING (day)
        LEFT JOIN comment_daily USING (day)
        ORDER BY day
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [event_id, event_id])
        return [normalize_row(dict(row)) for row in cur.fetchall()]
```

```python
def fetch_event_channel_distribution(conn: psycopg.Connection, event_id: str) -> list[dict[str, Any]]:
    query = """
        WITH content_channel AS (
          SELECT coalesce(nullif(platform, ''), '未知渠道') AS channel, count(*)::bigint AS content_count
          FROM data_asset.dwd_content
          WHERE event_id = %s
          GROUP BY 1
        ),
        comment_channel AS (
          SELECT coalesce(nullif(c.platform, ''), nullif(cm.platform, ''), '未知渠道') AS channel,
                 count(*)::bigint AS comment_count
          FROM data_asset.dwd_comment cm
          JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
          WHERE c.event_id = %s
          GROUP BY 1
        ),
        channels AS (
          SELECT channel FROM content_channel
          UNION
          SELECT channel FROM comment_channel
        )
        SELECT channel,
               coalesce(content_count, 0) AS content_count,
               coalesce(comment_count, 0) AS comment_count,
               coalesce(content_count, 0) + coalesce(comment_count, 0) AS total_volume
        FROM channels
        LEFT JOIN content_channel USING (channel)
        LEFT JOIN comment_channel USING (channel)
        ORDER BY total_volume DESC, channel
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [event_id, event_id])
        return [normalize_row(dict(row)) for row in cur.fetchall()]
```

```python
def fetch_event_kol_type_distribution(conn: psycopg.Connection, event_id: str) -> list[dict[str, Any]]:
    query = """
        WITH latest_kol_profile AS (
          SELECT DISTINCT ON (author_id)
                 author_id, kol_main_type, updated_time
          FROM data_asset.user_profile_kol
          ORDER BY author_id, updated_time DESC NULLS LAST
        )
        SELECT coalesce(nullif(p.kol_main_type, ''), '尚未维护KOL画像') AS kol_main_type,
               count(DISTINCT a.author_id)::bigint AS kol_count,
               count(DISTINCT c.content_id)::bigint AS content_count,
               coalesce(sum(c.engagement_total), 0)::bigint AS total_engagement
        FROM data_asset.dwd_content c
        JOIN data_asset.dwd_author a ON c.author_id = a.author_id
        LEFT JOIN latest_kol_profile p ON a.author_id = p.author_id
        WHERE c.event_id = %s AND a.is_kol = true
        GROUP BY 1
        ORDER BY kol_count DESC, content_count DESC, total_engagement DESC
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [event_id])
        return [normalize_row(dict(row)) for row in cur.fetchall()]
```

```python
def fetch_event_hot_posts(conn: psycopg.Connection, event_id: str, limit: int = 10) -> list[dict[str, Any]]:
    query = """
        SELECT content_id, title, coalesce(engagement_total, 0)::bigint AS total_engagement
        FROM data_asset.dwd_content
        WHERE event_id = %s
        ORDER BY engagement_total DESC NULLS LAST, published_at DESC NULLS LAST
        LIMIT %s
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [event_id, limit])
        return [normalize_row(dict(row)) for row in cur.fetchall()]
```

- [ ] **Step 4: Run service test and confirm it passes**

Run:

```powershell
python -m pytest tests\test_event_market_dashboard.py -q
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Write the failing API route test**

Append to `tests/test_task_api.py`:

```python
def test_voc_event_market_dashboard_api_returns_business_sections(tmp_path: Path, monkeypatch) -> None:
    app = create_test_app(tmp_path)

    def fake_dashboard(event_id):
        return {
            "event": {"event_id": event_id, "event_name": "IDT6上市"},
            "overview_metrics": {"total_volume": 44, "content_count": 25, "comment_count": 19, "kol_count": 2, "kol_content_count": 6, "total_engagement": 65692},
            "volume_trend": [{"date": "2026-05-14", "content_count": 2, "comment_count": 3, "total_volume": 5}],
            "channel_distribution": [{"channel": "抖音", "content_count": 10, "comment_count": 8, "total_volume": 18}],
            "kol_type_distribution": [{"kol_main_type": "车型实测测评KOL", "kol_count": 2, "content_count": 4, "total_engagement": 1200}],
            "hot_posts": [{"content_id": "c1", "title": "试驾体验", "total_engagement": 999}],
        }

    monkeypatch.setattr("app.routers.tasks.get_voc_event_market_dashboard", fake_dashboard)

    response = TestClient(app).get("/api/voc/events/event_001/market-dashboard")

    assert response.status_code == 200
    payload = response.json()
    assert payload["event"]["event_id"] == "event_001"
    assert payload["overview_metrics"]["total_volume"] == 44
    assert payload["hot_posts"][0]["title"] == "试驾体验"
```

- [ ] **Step 6: Run API test and confirm it fails**

Run:

```powershell
python -m pytest tests\test_task_api.py::test_voc_event_market_dashboard_api_returns_business_sections -q
```

Expected:

```text
FAILED ... AttributeError ... get_voc_event_market_dashboard
```

- [ ] **Step 7: Add the FastAPI route**

In `app/routers/tasks.py`, update the import:

```python
from app.services.event_voc_insights import get_voc_event_detail, get_voc_event_market_dashboard, list_voc_events
```

Add the route before `@router.get("/api/voc/events/{event_id}")`:

```python
@router.get("/api/voc/events/{event_id}/market-dashboard")
def get_voc_event_market_dashboard_api(event_id: str) -> dict:
    try:
        payload = get_voc_event_market_dashboard(event_id)
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")
    if not payload.get("event"):
        raise HTTPException(status_code=404, detail="Event not found")
    return payload
```

- [ ] **Step 8: Run backend tests**

Run:

```powershell
python -m pytest tests\test_event_market_dashboard.py tests\test_task_api.py -q
```

Expected:

```text
all selected tests passed
```

- [ ] **Step 9: Commit backend API**

Run:

```powershell
git add app\services\event_voc_insights.py app\routers\tasks.py tests\test_event_market_dashboard.py tests\test_task_api.py
git commit -m "feat: add voc event market dashboard api"
```

---

### Task 2: Frontend Navigation and Types

**Files:**
- Modify: `frontend/src/config/navigation.ts`
- Create: `frontend/src/types/vocMarket.ts`
- Modify: `tests/test_next_frontend_architecture.py`

- [ ] **Step 1: Write the failing navigation/API contract test**

Update `tests/test_next_frontend_architecture.py` so the final test contains:

```python
    assert "市场看板" in navigation
    assert "传播内容" not in navigation
    assert "KOL与用户" not in navigation

    market_page = (root / "src/app/voc/events/market/page.tsx").read_text(encoding="utf-8")
    assert "serverApiBaseUrl" in market_page
    assert "/market-dashboard" in market_page
```

- [ ] **Step 2: Run the frontend architecture test and confirm it fails**

Run:

```powershell
python -m pytest tests\test_next_frontend_architecture.py -q
```

Expected:

```text
FAILED ... assert '传播内容' not in navigation
```

- [ ] **Step 3: Create shared TypeScript types**

Create `frontend/src/types/vocMarket.ts`:

```ts
export type VocEvent = {
  event_id: string;
  event_name: string;
  brand_name?: string | null;
  model_name?: string | null;
  event_type?: string | null;
  event_status?: string | null;
  start_time?: string | null;
  end_time?: string | null;
  content_cnt?: number | null;
  comment_cnt?: number | null;
  kol_content_cnt?: number | null;
  total_engagement?: number | null;
};

export type OverviewMetrics = {
  total_volume: number;
  content_count: number;
  comment_count: number;
  kol_count: number;
  kol_content_count: number;
  total_engagement: number;
};

export type VolumeTrendPoint = {
  date: string;
  content_count: number;
  comment_count: number;
  total_volume: number;
};

export type ChannelDistributionItem = {
  channel: string;
  content_count: number;
  comment_count: number;
  total_volume: number;
};

export type KolTypeDistributionItem = {
  kol_main_type: string;
  kol_count: number;
  content_count: number;
  total_engagement: number;
};

export type HotPostItem = {
  content_id: string;
  title: string;
  total_engagement: number;
};

export type MarketDashboardPayload = {
  event: VocEvent;
  overview_metrics: OverviewMetrics;
  volume_trend: VolumeTrendPoint[];
  channel_distribution: ChannelDistributionItem[];
  kol_type_distribution: KolTypeDistributionItem[];
  hot_posts: HotPostItem[];
};
```

- [ ] **Step 4: Remove extra VOC secondary nav items**

In `frontend/src/config/navigation.ts`, keep only:

```ts
children: [
  { label: "市场看板", href: "/voc/events/market", icon: LayoutDashboard },
],
```

Remove unused imports `Megaphone` if no other navigation item uses it.

- [ ] **Step 5: Run the architecture test**

Run:

```powershell
python -m pytest tests\test_next_frontend_architecture.py -q
```

Expected:

```text
tests fail only because the market page does not fetch /market-dashboard yet
```

- [ ] **Step 6: Commit navigation and types if only the expected page-fetch assertion remains**

Run:

```powershell
git add frontend\src\config\navigation.ts frontend\src\types\vocMarket.ts tests\test_next_frontend_architecture.py
git commit -m "feat: define voc market dashboard frontend contract"
```

If the test still fails at this checkpoint, include the failure in the next task and do not commit until Task 3 passes.

---

### Task 3: Frontend Market Dashboard Page

**Files:**
- Create: `frontend/src/components/voc/MetricCard.tsx`
- Create: `frontend/src/components/voc/VolumeTrendChart.tsx`
- Create: `frontend/src/components/voc/ChannelStackedBars.tsx`
- Create: `frontend/src/components/voc/KolTypeBars.tsx`
- Create: `frontend/src/components/voc/HotPostList.tsx`
- Modify: `frontend/src/app/voc/events/market/page.tsx`
- Modify: `tests/test_next_frontend_architecture.py`

- [ ] **Step 1: Create `MetricCard`**

Create `frontend/src/components/voc/MetricCard.tsx`:

```tsx
type MetricCardProps = {
  label: string;
  value: string;
  hint?: string;
};

export function MetricCard({ label, value, hint }: MetricCardProps) {
  return (
    <article className="rounded-3xl border border-zinc-200/80 bg-white p-5 shadow-sm">
      <p className="text-xs font-medium text-zinc-500">{label}</p>
      <strong className="mt-3 block text-2xl font-semibold tracking-tight text-zinc-950">{value}</strong>
      {hint ? <span className="mt-2 block text-xs text-zinc-400">{hint}</span> : null}
    </article>
  );
}
```

- [ ] **Step 2: Create `VolumeTrendChart`**

Create `frontend/src/components/voc/VolumeTrendChart.tsx` with SVG lines and an empty state:

```tsx
import type { VolumeTrendPoint } from "@/types/vocMarket";

type VolumeTrendChartProps = {
  data: VolumeTrendPoint[];
};

function points(data: VolumeTrendPoint[], key: keyof Pick<VolumeTrendPoint, "content_count" | "comment_count" | "total_volume">, max: number) {
  if (data.length === 1) {
    return `0,${160 - (data[0][key] / max) * 130} 520,${160 - (data[0][key] / max) * 130}`;
  }
  return data
    .map((item, index) => {
      const x = (index / Math.max(data.length - 1, 1)) * 520;
      const y = 160 - ((item[key] || 0) / max) * 130;
      return `${x},${y}`;
    })
    .join(" ");
}

export function VolumeTrendChart({ data }: VolumeTrendChartProps) {
  if (!data.length) {
    return <div className="flex h-64 items-center justify-center rounded-3xl bg-zinc-50 text-sm text-zinc-400">缺少发布时间，暂无法展示声量趋势</div>;
  }
  const max = Math.max(...data.map((item) => item.total_volume), 1);
  return (
    <div className="overflow-hidden rounded-3xl bg-zinc-50 p-4">
      <svg viewBox="0 0 520 190" className="h-64 w-full">
        <polyline points={points(data, "total_volume", max)} fill="none" stroke="#18181b" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
        <polyline points={points(data, "content_count", max)} fill="none" stroke="#60a5fa" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        <polyline points={points(data, "comment_count", max)} fill="none" stroke="#a7f3d0" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
      <div className="mt-3 flex flex-wrap gap-3 text-xs text-zinc-500">
        <span>总声量</span>
        <span>主贴声量</span>
        <span>评论声量</span>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Create `ChannelStackedBars`**

Create `frontend/src/components/voc/ChannelStackedBars.tsx`:

```tsx
import type { ChannelDistributionItem } from "@/types/vocMarket";

type ChannelStackedBarsProps = {
  data: ChannelDistributionItem[];
};

export function ChannelStackedBars({ data }: ChannelStackedBarsProps) {
  if (!data.length) {
    return <div className="flex h-64 items-center justify-center rounded-3xl bg-zinc-50 text-sm text-zinc-400">缺少渠道字段，暂无法展示渠道分布</div>;
  }
  const max = Math.max(...data.map((item) => item.total_volume), 1);
  return (
    <div className="space-y-4 rounded-3xl bg-zinc-50 p-4">
      {data.slice(0, 8).map((item) => {
        const contentWidth = `${(item.content_count / max) * 100}%`;
        const commentWidth = `${(item.comment_count / max) * 100}%`;
        return (
          <div key={item.channel}>
            <div className="mb-2 flex justify-between text-xs text-zinc-500">
              <span>{item.channel}</span>
              <span>{item.total_volume.toLocaleString("zh-CN")}</span>
            </div>
            <div className="flex h-3 overflow-hidden rounded-full bg-white">
              <div className="bg-sky-400" style={{ width: contentWidth }} />
              <div className="bg-emerald-300" style={{ width: commentWidth }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}
```

- [ ] **Step 4: Create `KolTypeBars`**

Create `frontend/src/components/voc/KolTypeBars.tsx`:

```tsx
import type { KolTypeDistributionItem } from "@/types/vocMarket";

type KolTypeBarsProps = {
  data: KolTypeDistributionItem[];
};

export function KolTypeBars({ data }: KolTypeBarsProps) {
  if (!data.length) {
    return <div className="flex h-64 items-center justify-center rounded-3xl bg-zinc-50 text-sm text-zinc-400">尚未维护KOL画像</div>;
  }
  const max = Math.max(...data.map((item) => item.kol_count), 1);
  return (
    <div className="space-y-4 rounded-3xl bg-zinc-50 p-4">
      {data.slice(0, 8).map((item) => (
        <div key={item.kol_main_type}>
          <div className="mb-2 flex justify-between gap-3 text-xs text-zinc-500">
            <span className="truncate">{item.kol_main_type}</span>
            <span>{item.kol_count}位</span>
          </div>
          <div className="h-3 overflow-hidden rounded-full bg-white">
            <div className="h-full rounded-full bg-zinc-900" style={{ width: `${(item.kol_count / max) * 100}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}
```

- [ ] **Step 5: Create `HotPostList`**

Create `frontend/src/components/voc/HotPostList.tsx`:

```tsx
import type { HotPostItem } from "@/types/vocMarket";

type HotPostListProps = {
  posts: HotPostItem[];
};

export function HotPostList({ posts }: HotPostListProps) {
  if (!posts.length) {
    return <div className="flex h-64 items-center justify-center rounded-3xl bg-zinc-50 text-sm text-zinc-400">缺少总互动量字段，暂无法展示热门榜单</div>;
  }
  return (
    <div className="space-y-3">
      {posts.slice(0, 10).map((post, index) => (
        <a key={post.content_id} href={`#post-${post.content_id}`} className="flex items-center gap-3 rounded-2xl bg-zinc-50 px-4 py-3 transition hover:bg-zinc-100">
          <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-white text-xs font-semibold text-zinc-500">{index + 1}</span>
          <span className="min-w-0 flex-1 truncate text-sm font-medium text-zinc-700">{post.title || "未命名帖子"}</span>
          <span className="text-sm font-semibold text-zinc-950">{post.total_engagement.toLocaleString("zh-CN")}</span>
        </a>
      ))}
    </div>
  );
}
```

- [ ] **Step 6: Replace the market page**

Modify `frontend/src/app/voc/events/market/page.tsx` to:

```tsx
import { ChannelStackedBars } from "@/components/voc/ChannelStackedBars";
import { HotPostList } from "@/components/voc/HotPostList";
import { KolTypeBars } from "@/components/voc/KolTypeBars";
import { MetricCard } from "@/components/voc/MetricCard";
import { VolumeTrendChart } from "@/components/voc/VolumeTrendChart";
import { serverApiBaseUrl } from "@/config/navigation";
import type { MarketDashboardPayload, VocEvent } from "@/types/vocMarket";

async function getEvents(): Promise<VocEvent[]> {
  const response = await fetch(`${serverApiBaseUrl}/voc/events`, { cache: "no-store" });
  if (!response.ok) return [];
  const payload = (await response.json()) as { events?: VocEvent[] };
  return payload.events ?? [];
}

async function getMarketDashboard(eventId: string): Promise<MarketDashboardPayload | null> {
  const response = await fetch(`${serverApiBaseUrl}/voc/events/${encodeURIComponent(eventId)}/market-dashboard`, { cache: "no-store" });
  if (!response.ok) return null;
  return (await response.json()) as MarketDashboardPayload;
}

function formatNumber(value: number) {
  return value.toLocaleString("zh-CN");
}

type PageProps = {
  searchParams?: { event_id?: string };
};

export default async function MarketDashboardPage({ searchParams }: PageProps) {
  const events = await getEvents();
  const selectedEventId = searchParams?.event_id ?? events[0]?.event_id;
  const dashboard = selectedEventId ? await getMarketDashboard(selectedEventId) : null;
  const metrics = dashboard?.overview_metrics;

  return (
    <div className="space-y-6">
      <section className="rounded-[32px] border border-zinc-200/80 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-zinc-400">VOC Event</p>
            <h1 className="mt-2 text-2xl font-semibold tracking-tight text-zinc-950">市场看板</h1>
            <p className="mt-2 text-sm text-zinc-500">基于真实入库资产查看事件声量、渠道、KOL类型和热门内容。</p>
          </div>
          <form>
            <select name="event_id" defaultValue={selectedEventId} className="min-w-64 rounded-full border border-zinc-200 bg-zinc-50 px-4 py-2 text-sm text-zinc-700 outline-none">
              {events.map((event) => (
                <option key={event.event_id} value={event.event_id}>{event.event_name}</option>
              ))}
            </select>
            <button className="ml-2 rounded-full bg-zinc-950 px-4 py-2 text-sm font-medium text-white">查看</button>
          </form>
        </div>
        {dashboard?.event ? (
          <div className="mt-5 flex flex-wrap gap-2 text-xs text-zinc-500">
            <span className="rounded-full bg-zinc-100 px-3 py-1">{dashboard.event.event_status ?? "未知状态"}</span>
            <span className="rounded-full bg-zinc-100 px-3 py-1">{dashboard.event.brand_name ?? "未填品牌"}</span>
            <span className="rounded-full bg-zinc-100 px-3 py-1">{dashboard.event.model_name ?? "未填车型"}</span>
            <span className="rounded-full bg-zinc-100 px-3 py-1">{dashboard.event.event_type ?? "未填类型"}</span>
          </div>
        ) : null}
      </section>

      {metrics ? (
        <section className="grid gap-3 md:grid-cols-5">
          <MetricCard label="总声量" value={formatNumber(metrics.total_volume)} hint="主贴 + 评论" />
          <MetricCard label="主贴数" value={formatNumber(metrics.content_count)} />
          <MetricCard label="评论数" value={formatNumber(metrics.comment_count)} />
          <MetricCard label="KOL发声" value={`${formatNumber(metrics.kol_count)} 位`} hint={`贡献 ${formatNumber(metrics.kol_content_count)} 条主贴`} />
          <MetricCard label="总互动量" value={formatNumber(metrics.total_engagement)} />
        </section>
      ) : (
        <div className="rounded-3xl border border-dashed border-zinc-200 bg-white p-10 text-center text-sm text-zinc-400">暂无事件数据，请先导入并运行ETL。</div>
      )}

      {dashboard ? (
        <>
          <section className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
            <article className="rounded-[28px] border border-zinc-200/80 bg-white p-6 shadow-sm">
              <h2 className="text-base font-semibold text-zinc-950">声量趋势</h2>
              <p className="mt-1 text-xs text-zinc-400">按发布时间聚合</p>
              <div className="mt-5"><VolumeTrendChart data={dashboard.volume_trend} /></div>
            </article>
            <article className="rounded-[28px] border border-zinc-200/80 bg-white p-6 shadow-sm">
              <h2 className="text-base font-semibold text-zinc-950">KOL类型分布</h2>
              <p className="mt-1 text-xs text-zinc-400">来自KOL画像表</p>
              <div className="mt-5"><KolTypeBars data={dashboard.kol_type_distribution} /></div>
            </article>
          </section>
          <section className="grid gap-4 lg:grid-cols-[1fr_0.9fr]">
            <article className="rounded-[28px] border border-zinc-200/80 bg-white p-6 shadow-sm">
              <h2 className="text-base font-semibold text-zinc-950">渠道分布</h2>
              <p className="mt-1 text-xs text-zinc-400">主贴 + 评论堆积</p>
              <div className="mt-5"><ChannelStackedBars data={dashboard.channel_distribution} /></div>
            </article>
            <article className="rounded-[28px] border border-zinc-200/80 bg-white p-6 shadow-sm">
              <h2 className="text-base font-semibold text-zinc-950">热门帖子榜</h2>
              <p className="mt-1 text-xs text-zinc-400">按底表总互动量倒序</p>
              <div className="mt-5"><HotPostList posts={dashboard.hot_posts} /></div>
            </article>
          </section>
        </>
      ) : null}
    </div>
  );
}
```

- [ ] **Step 7: Run TypeScript and architecture tests**

Run:

```powershell
python -m pytest tests\test_next_frontend_architecture.py -q
npm run typecheck
```

Expected:

```text
pytest passes
tsc --noEmit exits 0
```

- [ ] **Step 8: Commit frontend page**

Run:

```powershell
git add frontend\src\app\voc\events\market\page.tsx frontend\src\components\voc frontend\src\types\vocMarket.ts tests\test_next_frontend_architecture.py
git commit -m "feat: render voc event market dashboard"
```

---

### Task 4: End-to-End Verification

**Files:**
- No planned code changes unless verification finds a defect.

- [ ] **Step 1: Run backend test suite**

Run:

```powershell
python -m pytest -q
```

Expected:

```text
all tests passed
```

- [ ] **Step 2: Run frontend typecheck and build**

Run:

```powershell
npm run typecheck
npm run build
```

Expected:

```text
tsc --noEmit exits 0
next build exits 0
```

- [ ] **Step 3: Verify live API**

With FastAPI running on `127.0.0.1:8000`, run:

```powershell
$events = Invoke-RestMethod http://127.0.0.1:8000/api/voc/events
$eventId = $events.events[0].event_id
$dashboard = Invoke-RestMethod "http://127.0.0.1:8000/api/voc/events/$eventId/market-dashboard"
$dashboard.overview_metrics
$dashboard.volume_trend.Count
$dashboard.channel_distribution.Count
$dashboard.hot_posts.Count
```

Expected:

```text
overview_metrics is not null
trend/channel/hot post counts are numbers
```

- [ ] **Step 4: Verify live Next page**

With Next running on `127.0.0.1:3000`, run:

```powershell
$html = (Invoke-WebRequest -UseBasicParsing http://127.0.0.1:3000/voc/events/market -TimeoutSec 30).Content
'hasMarket=' + $html.Contains('市场看板')
'hasNoMock=' + (-not $html.ToLower().Contains('mock'))
'hasHotList=' + $html.Contains('热门帖子榜')
```

Expected:

```text
hasMarket=True
hasNoMock=True
hasHotList=True
```

- [ ] **Step 5: Check git status**

Run:

```powershell
git status --short
```

Expected:

```text
Only user sample/input files remain modified or untracked; implementation files are committed.
```

