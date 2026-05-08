# Customer Journey VOC Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first production-shaped “VOC看用户” capability as a channel-level customer journey system with real data lineage and no cross-channel identity stitching.

**Architecture:** Add a unified touchpoint layer, derive journey stages through deterministic rules, aggregate into stage/matrix/painpoint ADS tables, expose `/api/journey/*` endpoints, then build a frontend page that renders only API-backed data. Public social, 400, WeCom, DCC, and Dianping data are normalized into touchpoints without claiming the same person across channels.

**Tech Stack:** PostgreSQL SQL schema, FastAPI, SQLAlchemy, pandas ETL tasks, Pydantic schemas, React 19, TypeScript, Vite, Tailwind, lucide-react.

---

## File Structure

New backend files:

- `backend/app/journey_rules.py`: Pure journey stage and suggested action rules. No database access.
- `backend/app/tasks/customer_touchpoint_standardize.py`: Converts existing `dwd_comment` records into `dwd_customer_touchpoint`; later source-specific imports also land here.
- `backend/app/tasks/journey_stage_summary.py`: Aggregates `ads_journey_stage_summary`.
- `backend/app/tasks/journey_channel_matrix.py`: Aggregates `ads_journey_channel_matrix`.
- `backend/app/tasks/journey_painpoint_summary.py`: Aggregates `ads_journey_painpoint_summary`.
- `backend/app/journey_service.py`: Reads ADS/detail tables and returns API models.
- `backend/tests/test_journey_rules.py`: Standard-library tests for stage and action rules.

Modified backend files:

- `docs/postgresql/data_access_schema.sql`: Add journey touchpoint and ADS tables.
- `backend/app/template_registry.py`: Add import templates for 400, WeCom, DCC, Dianping touchpoints.
- `backend/app/import_service.py`: Insert generic journey touchpoint rows for those templates.
- `backend/app/task_registry.py`: Register journey ETL tasks.
- `backend/app/schemas.py`: Add Pydantic models for journey API responses.
- `backend/app/api.py`: Add `/api/journey/*` routes.

New frontend files:

- `app/src/types/customerJourney.ts`: Frontend journey DTOs.
- `app/src/lib/customer-journey-api.ts`: Journey API client with no mock fallback.
- `app/src/components/voc/customer-journey/CustomerJourneyPage.tsx`: Main page.
- `app/src/components/voc/customer-journey/StageOverviewRail.tsx`: Journey stage cards.
- `app/src/components/voc/customer-journey/ChannelStageMatrix.tsx`: Channel × stage matrix.
- `app/src/components/voc/customer-journey/TouchpointEvidenceList.tsx`: Evidence list.
- `app/src/components/voc/customer-journey/ActionSuggestions.tsx`: Rule-based suggestions.
- `app/src/components/voc/customer-journey/customerJourneyApi.test.mjs`: Lightweight API mapping test.

Modified frontend files:

- `app/src/App.tsx` or existing navigation host: Add route/navigation entry for “VOC看用户”.
- `app/package.json`: Add `test:customer-journey` script.

## Task 1: Schema And Import Templates

**Files:**
- Modify: `docs/postgresql/data_access_schema.sql`
- Modify: `backend/app/template_registry.py`
- Modify: `backend/app/import_service.py`

- [ ] **Step 1: Add journey schema tables**

Append the following SQL after `ads_kol_event_summary` in `docs/postgresql/data_access_schema.sql`:

```sql
CREATE TABLE IF NOT EXISTS data_asset.dwd_customer_touchpoint (
  touchpoint_id       VARCHAR(64) PRIMARY KEY,
  source_channel      VARCHAR(64) NOT NULL,
  source_system       VARCHAR(128),
  source_record_id    VARCHAR(128),
  channel_user_key    VARCHAR(255),
  user_display_name   VARCHAR(255),
  touchpoint_text     TEXT NOT NULL,
  touchpoint_time     TIMESTAMP NOT NULL,
  brand_name          VARCHAR(128),
  model_name          VARCHAR(128),
  city_name           VARCHAR(128),
  store_id            VARCHAR(128),
  store_name          VARCHAR(255),
  event_id            VARCHAR(64),
  content_id          VARCHAR(64),
  journey_stage       VARCHAR(64) NOT NULL,
  stage_confidence    NUMERIC(8,4) DEFAULT 0,
  stage_reason        TEXT,
  intent_tag          VARCHAR(128),
  issue_tag           VARCHAR(128),
  sentiment_tag       VARCHAR(128),
  mindset_tag         VARCHAR(128),
  business_status     VARCHAR(128),
  rating_score        NUMERIC(8,2),
  created_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_asset.ads_journey_stage_summary (
  summary_id                     VARCHAR(128) PRIMARY KEY,
  brand_name                     VARCHAR(128),
  model_name                     VARCHAR(128),
  journey_stage                  VARCHAR(64) NOT NULL,
  date_from                      DATE,
  date_to                        DATE,
  touchpoint_cnt                 BIGINT DEFAULT 0,
  channel_cnt                    BIGINT DEFAULT 0,
  negative_touchpoint_cnt        BIGINT DEFAULT 0,
  negative_ratio                 NUMERIC(10,4) DEFAULT 0,
  intent_top_json                JSONB,
  issue_top_json                 JSONB,
  channel_distribution_json      JSONB,
  representative_touchpoints_json JSONB,
  data_lineage_json              JSONB,
  updated_time                   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_asset.ads_journey_channel_matrix (
  matrix_id          VARCHAR(128) PRIMARY KEY,
  brand_name         VARCHAR(128),
  model_name         VARCHAR(128),
  source_channel     VARCHAR(64) NOT NULL,
  journey_stage      VARCHAR(64) NOT NULL,
  date_from          DATE,
  date_to            DATE,
  touchpoint_cnt     BIGINT DEFAULT 0,
  negative_ratio     NUMERIC(10,4) DEFAULT 0,
  issue_top_json     JSONB,
  intent_top_json    JSONB,
  data_lineage_json  JSONB,
  updated_time       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_asset.ads_journey_painpoint_summary (
  painpoint_id        VARCHAR(128) PRIMARY KEY,
  brand_name          VARCHAR(128),
  model_name          VARCHAR(128),
  journey_stage       VARCHAR(64) NOT NULL,
  issue_tag           VARCHAR(128) NOT NULL,
  touchpoint_cnt      BIGINT DEFAULT 0,
  negative_ratio      NUMERIC(10,4) DEFAULT 0,
  source_channels_json JSONB,
  sample_texts_json   JSONB,
  suggested_owner     VARCHAR(64),
  suggested_action    TEXT,
  data_lineage_json   JSONB,
  updated_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_customer_touchpoint_stage ON data_asset.dwd_customer_touchpoint(journey_stage);
CREATE INDEX IF NOT EXISTS idx_customer_touchpoint_channel ON data_asset.dwd_customer_touchpoint(source_channel);
CREATE INDEX IF NOT EXISTS idx_customer_touchpoint_time ON data_asset.dwd_customer_touchpoint(touchpoint_time);
```

- [ ] **Step 2: Add journey import templates**

In `backend/app/template_registry.py`, append four entries to `TEMPLATES` with these normalized field maps. Use one generic target table: `dwd_customer_touchpoint`.

```python
{
    "id": "tpl-journey-400",
    "source_key": "journey_400",
    "source_name": "400触点数据",
    "file_name": "journey-400-template.xlsx",
    "formats": ["csv", "xlsx"],
    "description": "用于导入400电话摘要或工单记录，生成用户旅程触点。",
    "required_headers": ["触点ID", "触点时间", "文本摘要"],
    "optional_headers": ["用户昵称", "品牌", "车型", "城市", "业务状态", "意图标签", "问题标签", "情绪标签"],
    "required_fields": ["touchpoint_id", "touchpoint_time", "touchpoint_text"],
    "optional_fields": ["user_display_name", "brand_name", "model_name", "city_name", "business_status", "intent_tag", "issue_tag", "sentiment_tag"],
    "column_map": {
        "触点id": "touchpoint_id",
        "触点时间": "touchpoint_time",
        "文本摘要": "touchpoint_text",
        "用户昵称": "user_display_name",
        "品牌": "brand_name",
        "车型": "model_name",
        "城市": "city_name",
        "业务状态": "business_status",
        "意图标签": "intent_tag",
        "问题标签": "issue_tag",
        "情绪标签": "sentiment_tag",
    },
    "target_table": "dwd_customer_touchpoint",
}
```

Add these three additional entries explicitly:

```python
{
    "id": "tpl-journey-wecom",
    "source_key": "journey_wecom",
    "source_name": "企业微信触点数据",
    "file_name": "journey-wecom-template.xlsx",
    "formats": ["csv", "xlsx"],
    "description": "用于导入企业微信会话摘要或跟进记录，生成用户旅程触点。",
    "required_headers": ["触点ID", "触点时间", "文本摘要"],
    "optional_headers": ["用户昵称", "品牌", "车型", "城市", "业务状态", "意图标签", "问题标签", "情绪标签"],
    "required_fields": ["touchpoint_id", "touchpoint_time", "touchpoint_text"],
    "optional_fields": ["user_display_name", "brand_name", "model_name", "city_name", "business_status", "intent_tag", "issue_tag", "sentiment_tag"],
    "column_map": {
        "触点id": "touchpoint_id",
        "触点时间": "touchpoint_time",
        "文本摘要": "touchpoint_text",
        "用户昵称": "user_display_name",
        "品牌": "brand_name",
        "车型": "model_name",
        "城市": "city_name",
        "业务状态": "business_status",
        "意图标签": "intent_tag",
        "问题标签": "issue_tag",
        "情绪标签": "sentiment_tag",
    },
    "target_table": "dwd_customer_touchpoint",
},
{
    "id": "tpl-journey-dcc",
    "source_key": "journey_dcc",
    "source_name": "DCC触点数据",
    "file_name": "journey-dcc-template.xlsx",
    "formats": ["csv", "xlsx"],
    "description": "用于导入DCC线索、外呼和邀约结果，生成用户旅程触点。",
    "required_headers": ["触点ID", "触点时间", "文本摘要"],
    "optional_headers": ["用户昵称", "品牌", "车型", "城市", "业务状态", "意图标签", "问题标签", "情绪标签"],
    "required_fields": ["touchpoint_id", "touchpoint_time", "touchpoint_text"],
    "optional_fields": ["user_display_name", "brand_name", "model_name", "city_name", "business_status", "intent_tag", "issue_tag", "sentiment_tag"],
    "column_map": {
        "触点id": "touchpoint_id",
        "触点时间": "touchpoint_time",
        "文本摘要": "touchpoint_text",
        "用户昵称": "user_display_name",
        "品牌": "brand_name",
        "车型": "model_name",
        "城市": "city_name",
        "业务状态": "business_status",
        "意图标签": "intent_tag",
        "问题标签": "issue_tag",
        "情绪标签": "sentiment_tag",
    },
    "target_table": "dwd_customer_touchpoint",
},
{
    "id": "tpl-journey-dianping",
    "source_key": "journey_dianping",
    "source_name": "大众点评店铺触点数据",
    "file_name": "journey-dianping-template.xlsx",
    "formats": ["csv", "xlsx"],
    "description": "用于导入大众点评店铺评价，生成到店、交付和售后旅程触点。",
    "required_headers": ["触点ID", "触点时间", "文本摘要"],
    "optional_headers": ["用户昵称", "品牌", "车型", "城市", "店铺ID", "店铺名称", "评分", "业务状态", "意图标签", "问题标签", "情绪标签"],
    "required_fields": ["touchpoint_id", "touchpoint_time", "touchpoint_text"],
    "optional_fields": ["user_display_name", "brand_name", "model_name", "city_name", "store_id", "store_name", "rating_score", "business_status", "intent_tag", "issue_tag", "sentiment_tag"],
    "column_map": {
        "触点id": "touchpoint_id",
        "触点时间": "touchpoint_time",
        "文本摘要": "touchpoint_text",
        "用户昵称": "user_display_name",
        "品牌": "brand_name",
        "车型": "model_name",
        "城市": "city_name",
        "店铺id": "store_id",
        "店铺名称": "store_name",
        "评分": "rating_score",
        "业务状态": "business_status",
        "意图标签": "intent_tag",
        "问题标签": "issue_tag",
        "情绪标签": "sentiment_tag",
    },
    "target_table": "dwd_customer_touchpoint",
},
```

- [ ] **Step 3: Support generic journey imports**

In `backend/app/import_service.py`, update `_prepare_rows` before the final unsupported-source error:

```python
    if source_key.startswith("journey_"):
        channel = source_key.replace("journey_", "")
        rows = []
        for row in df.to_dict(orient="records"):
            rows.append(
                {
                    "touchpoint_id": row.get("touchpoint_id"),
                    "source_channel": channel,
                    "source_system": row.get("source_system") or channel,
                    "source_record_id": row.get("source_record_id") or row.get("touchpoint_id"),
                    "channel_user_key": row.get("channel_user_key") or row.get("user_display_name"),
                    "user_display_name": row.get("user_display_name"),
                    "touchpoint_text": row.get("touchpoint_text"),
                    "touchpoint_time": row.get("touchpoint_time"),
                    "brand_name": row.get("brand_name"),
                    "model_name": row.get("model_name"),
                    "city_name": row.get("city_name"),
                    "store_id": row.get("store_id"),
                    "store_name": row.get("store_name"),
                    "event_id": row.get("event_id"),
                    "content_id": row.get("content_id"),
                    "journey_stage": row.get("journey_stage") or "兴趣咨询",
                    "stage_confidence": row.get("stage_confidence") or 0.3,
                    "stage_reason": row.get("stage_reason") or "导入时未提供阶段，由渠道默认阶段兜底。",
                    "intent_tag": row.get("intent_tag"),
                    "issue_tag": row.get("issue_tag"),
                    "sentiment_tag": row.get("sentiment_tag"),
                    "mindset_tag": row.get("mindset_tag"),
                    "business_status": row.get("business_status"),
                    "rating_score": row.get("rating_score"),
                }
            )
        return rows, []
```

- [ ] **Step 4: Verify schema and import code compile**

Run:

```powershell
python -m py_compile backend/app/template_registry.py backend/app/import_service.py
```

Expected: command exits with code `0`.

- [ ] **Step 5: Commit**

```powershell
git add docs/postgresql/data_access_schema.sql backend/app/template_registry.py backend/app/import_service.py
git commit -m "feat: add customer journey touchpoint schema"
```

## Task 2: Journey Rules

**Files:**
- Create: `backend/app/journey_rules.py`
- Create: `backend/tests/test_journey_rules.py`

- [ ] **Step 1: Write failing rule tests**

Create `backend/tests/test_journey_rules.py`:

```python
import unittest

from backend.app.journey_rules import infer_journey_stage, suggest_owner_and_action


class JourneyRulesTest(unittest.TestCase):
    def test_business_status_overrides_text(self):
        result = infer_journey_stage(
            source_channel="dcc",
            text="用户还想看看价格",
            business_status="到店",
            rating_score=None,
        )
        self.assertEqual(result["stage"], "试驾/到店")
        self.assertGreaterEqual(result["confidence"], 0.8)

    def test_price_text_maps_to_quote_stage(self):
        result = infer_journey_stage(
            source_channel="public_social",
            text="这车优惠多少，金融方案怎么算",
            business_status="",
            rating_score=None,
        )
        self.assertEqual(result["stage"], "报价/权益")

    def test_dianping_defaults_to_store_visit(self):
        result = infer_journey_stage(
            source_channel="dianping",
            text="销售接待很耐心，店里环境不错",
            business_status="",
            rating_score=4.5,
        )
        self.assertEqual(result["stage"], "试驾/到店")

    def test_suggest_sales_owner_for_price_issue(self):
        owner, action = suggest_owner_and_action("报价/权益", "价格贵")
        self.assertEqual(owner, "销售")
        self.assertIn("权益", action)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m unittest backend.tests.test_journey_rules -v
```

Expected: FAIL with `ModuleNotFoundError` or missing functions.

- [ ] **Step 3: Implement rules**

Create `backend/app/journey_rules.py`:

```python
from __future__ import annotations


JOURNEY_STAGES = [
    "曝光认知",
    "兴趣咨询",
    "对比评估",
    "留资/外呼",
    "试驾/到店",
    "报价/权益",
    "下订/战败",
    "交付/售后",
    "复购/推荐",
]

NEGATIVE_SENTIMENTS = {"负向", "强负面", "负面", "消极"}


BUSINESS_STATUS_STAGE = {
    "线索": "留资/外呼",
    "外呼": "留资/外呼",
    "邀约": "试驾/到店",
    "到店": "试驾/到店",
    "试驾": "试驾/到店",
    "报价": "报价/权益",
    "下订": "下订/战败",
    "战败": "下订/战败",
    "投诉": "交付/售后",
    "售后": "交付/售后",
}

TEXT_RULES = [
    ("复购/推荐", ("推荐朋友", "还会买", "第二台", "转介绍")),
    ("交付/售后", ("提车", "交付", "售后", "维修", "保养", "投诉", "首保")),
    ("下订/战败", ("已订", "下订", "退订", "买了竞品", "放弃", "等优惠")),
    ("报价/权益", ("报价", "优惠", "金融", "置换", "保险", "权益", "落地价")),
    ("试驾/到店", ("试驾", "到店", "门店", "销售接待", "预约")),
    ("对比评估", ("对比", "竞品", "值不值", "续航", "空间", "配置")),
    ("兴趣咨询", ("多少钱", "价格", "什么时候上市", "哪里看车", "参数")),
    ("曝光认知", ("刷到", "看到发布", "第一次听说", "发布会")),
]

CHANNEL_DEFAULT_STAGE = {
    "public_social": "曝光认知",
    "400": "兴趣咨询",
    "wecom": "留资/外呼",
    "dcc": "留资/外呼",
    "dianping": "试驾/到店",
}


def infer_journey_stage(
    *,
    source_channel: str,
    text: str,
    business_status: str | None,
    rating_score: float | None,
) -> dict:
    status = (business_status or "").strip()
    for keyword, stage in BUSINESS_STATUS_STAGE.items():
        if keyword in status:
            return {"stage": stage, "confidence": 0.9, "reason": f"业务状态命中“{keyword}”。"}

    text_value = (text or "").strip()
    for stage, keywords in TEXT_RULES:
        matched = next((keyword for keyword in keywords if keyword in text_value), "")
        if matched:
            return {"stage": stage, "confidence": 0.75, "reason": f"文本命中“{matched}”。"}

    if source_channel == "dianping" and rating_score is not None:
        return {"stage": "试驾/到店", "confidence": 0.6, "reason": "大众点评评分默认归入到店体验。"}

    fallback = CHANNEL_DEFAULT_STAGE.get(source_channel, "兴趣咨询")
    return {"stage": fallback, "confidence": 0.3, "reason": f"渠道默认阶段：{source_channel}。"}


def suggest_owner_and_action(journey_stage: str, issue_tag: str) -> tuple[str, str]:
    issue = issue_tag or "未标注问题"
    if journey_stage == "报价/权益" or "价格" in issue or "优惠" in issue:
        return "销售", f"围绕“{issue}”补充权益解释、报价透明度和销售话术。"
    if journey_stage == "试驾/到店":
        return "门店", f"排查“{issue}”对应的到店接待、试驾体验和门店服务流程。"
    if journey_stage == "留资/外呼":
        return "DCC", f"复盘“{issue}”相关外呼节奏、邀约话术和线索跟进状态。"
    if journey_stage == "交付/售后":
        return "售后", f"沉淀“{issue}”对应的交付/维修/保养解释口径和处理流程。"
    return "市场", f"针对“{issue}”补充内容解释、竞品对比或用户教育素材。"
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
python -m unittest backend.tests.test_journey_rules -v
```

Expected: 4 tests pass.

- [ ] **Step 5: Commit**

```powershell
git add backend/app/journey_rules.py backend/tests/test_journey_rules.py
git commit -m "feat: add journey stage rules"
```

## Task 3: Touchpoint Standardization ETL

**Files:**
- Create: `backend/app/tasks/customer_touchpoint_standardize.py`
- Modify: `backend/app/task_registry.py`

- [ ] **Step 1: Add ETL script**

Create `backend/app/tasks/customer_touchpoint_standardize.py`:

```python
import hashlib

import pandas as pd

from backend.app.journey_rules import infer_journey_stage
from ._event_asset_utils import write_refresh_table


def _sha(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:16]


def _text(row) -> str:
    return str(row.get("comment_text", "") or "")


def run(engine, params: dict) -> dict:
    comment_df = pd.read_sql(
        """
        SELECT
          cm.comment_id, cm.platform, cm.content_id, cm.comment_author_id, cm.comment_author_name,
          cm.comment_text, cm.published_at, cm.opinion_tag, cm.intention_tag,
          cm.sentiment_tag, cm.mindset_tag, cm.stage_tag,
          rel.event_id, ev.brand_name, ev.model_name
        FROM data_asset.dwd_comment cm
        LEFT JOIN data_asset.rel_event_content rel ON rel.content_id = cm.content_id
        LEFT JOIN data_asset.dwd_event ev ON ev.event_id = rel.event_id
        """,
        engine,
    )

    existing_df = pd.read_sql(
        """
        SELECT *
        FROM data_asset.dwd_customer_touchpoint
        WHERE source_channel <> 'public_social'
        """,
        engine,
    )

    records = []
    for _, row in comment_df.iterrows():
        inferred = infer_journey_stage(
            source_channel="public_social",
            text=_text(row),
            business_status=str(row.get("stage_tag", "") or ""),
            rating_score=None,
        )
        records.append(
            {
                "touchpoint_id": f"tp_public_{_sha(str(row.get('comment_id', '')))}",
                "source_channel": "public_social",
                "source_system": str(row.get("platform", "") or "public_social"),
                "source_record_id": str(row.get("comment_id", "") or ""),
                "channel_user_key": str(row.get("comment_author_id", "") or row.get("comment_author_name", "") or ""),
                "user_display_name": str(row.get("comment_author_name", "") or ""),
                "touchpoint_text": _text(row),
                "touchpoint_time": row.get("published_at"),
                "brand_name": row.get("brand_name"),
                "model_name": row.get("model_name"),
                "city_name": None,
                "store_id": None,
                "store_name": None,
                "event_id": row.get("event_id"),
                "content_id": row.get("content_id"),
                "journey_stage": inferred["stage"],
                "stage_confidence": inferred["confidence"],
                "stage_reason": inferred["reason"],
                "intent_tag": row.get("intention_tag"),
                "issue_tag": row.get("opinion_tag"),
                "sentiment_tag": row.get("sentiment_tag"),
                "mindset_tag": row.get("mindset_tag"),
                "business_status": row.get("stage_tag"),
                "rating_score": None,
                "updated_time": pd.Timestamp.now(),
            }
        )

    result = pd.DataFrame(records)
    if not existing_df.empty:
        result = pd.concat([existing_df, result], ignore_index=True, sort=False)

    if result.empty:
        result = pd.DataFrame(columns=[
            "touchpoint_id", "source_channel", "source_system", "source_record_id",
            "channel_user_key", "user_display_name", "touchpoint_text", "touchpoint_time",
            "brand_name", "model_name", "city_name", "store_id", "store_name", "event_id",
            "content_id", "journey_stage", "stage_confidence", "stage_reason", "intent_tag",
            "issue_tag", "sentiment_tag", "mindset_tag", "business_status", "rating_score",
            "updated_time",
        ])

    write_refresh_table(engine, "dwd_customer_touchpoint", result)
    return {
        "processed_rows": int(len(comment_df) + len(existing_df)),
        "output_rows": int(len(result)),
        "message": "用户旅程触点标准化完成",
    }
```

- [ ] **Step 2: Register ETL task**

Add this dictionary to `TASKS` in `backend/app/task_registry.py`:

```python
    {
        "task_id": "customer_touchpoint_standardize",
        "task_name": "用户旅程触点标准化",
        "task_group": "用户旅程",
        "task_desc": "将公网评论和已导入业务触点统一到 dwd_customer_touchpoint。",
        "script_path": "backend/app/tasks/customer_touchpoint_standardize.py",
        "module_path": "backend.app.tasks.customer_touchpoint_standardize",
        "entry_func": "run",
        "input_tables": ["dwd_comment", "rel_event_content", "dwd_event", "dwd_customer_touchpoint"],
        "output_tables": ["dwd_customer_touchpoint"],
        "run_mode": "manual",
        "is_enabled": True,
    },
```

- [ ] **Step 3: Compile**

Run:

```powershell
python -m py_compile backend/app/tasks/customer_touchpoint_standardize.py backend/app/task_registry.py
```

Expected: command exits with code `0`.

- [ ] **Step 4: Commit**

```powershell
git add backend/app/tasks/customer_touchpoint_standardize.py backend/app/task_registry.py
git commit -m "feat: add customer touchpoint standardization task"
```

## Task 4: Journey Aggregation ETL

**Files:**
- Create: `backend/app/tasks/journey_stage_summary.py`
- Create: `backend/app/tasks/journey_channel_matrix.py`
- Create: `backend/app/tasks/journey_painpoint_summary.py`
- Modify: `backend/app/task_registry.py`

- [ ] **Step 1: Add shared aggregation helpers inside each script**

Each script should use these local helpers:

```python
import json
import hashlib

import pandas as pd

from backend.app.journey_rules import NEGATIVE_SENTIMENTS, suggest_owner_and_action
from ._event_asset_utils import write_refresh_table


def _sha(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:16]


def _top_json(series: pd.Series, limit: int = 5) -> str:
    cleaned = series.fillna("").astype(str).str.strip()
    cleaned = cleaned[cleaned != ""]
    if cleaned.empty:
        return "[]"
    rows = cleaned.value_counts().head(limit).reset_index()
    rows.columns = ["label", "value"]
    return json.dumps(rows.to_dict(orient="records"), ensure_ascii=False)


def _sample_json(group: pd.DataFrame, limit: int = 3) -> str:
    rows = group.sort_values("touchpoint_time", ascending=False).head(limit)
    return json.dumps(
        [
            {
                "touchpointId": str(row["touchpoint_id"]),
                "channel": str(row["source_channel"]),
                "text": str(row["touchpoint_text"]),
                "time": str(row["touchpoint_time"]),
            }
            for _, row in rows.iterrows()
        ],
        ensure_ascii=False,
    )
```

- [ ] **Step 2: Implement stage summary**

Create `backend/app/tasks/journey_stage_summary.py` using helpers from Step 1 and this `run` body:

```python
def run(engine, params: dict) -> dict:
    df = pd.read_sql("SELECT * FROM data_asset.dwd_customer_touchpoint", engine)
    records = []
    if not df.empty:
        df["negative_flag"] = df["sentiment_tag"].fillna("").isin(NEGATIVE_SENTIMENTS).astype(int)
        for (brand, model, stage), group in df.groupby(["brand_name", "model_name", "journey_stage"], dropna=False):
            date_from = pd.to_datetime(group["touchpoint_time"]).min().date()
            date_to = pd.to_datetime(group["touchpoint_time"]).max().date()
            touchpoint_cnt = int(group["touchpoint_id"].nunique())
            negative_cnt = int(group["negative_flag"].sum())
            records.append(
                {
                    "summary_id": f"stage_{_sha(str(brand) + str(model) + str(stage))}",
                    "brand_name": brand,
                    "model_name": model,
                    "journey_stage": stage,
                    "date_from": date_from,
                    "date_to": date_to,
                    "touchpoint_cnt": touchpoint_cnt,
                    "channel_cnt": int(group["source_channel"].nunique()),
                    "negative_touchpoint_cnt": negative_cnt,
                    "negative_ratio": round(negative_cnt / touchpoint_cnt, 4) if touchpoint_cnt else 0,
                    "intent_top_json": _top_json(group["intent_tag"]),
                    "issue_top_json": _top_json(group["issue_tag"]),
                    "channel_distribution_json": _top_json(group["source_channel"]),
                    "representative_touchpoints_json": _sample_json(group),
                    "data_lineage_json": json.dumps(["dwd_customer_touchpoint"], ensure_ascii=False),
                    "updated_time": pd.Timestamp.now(),
                }
            )
    result = pd.DataFrame(records)
    write_refresh_table(engine, "ads_journey_stage_summary", result)
    return {"processed_rows": len(df), "output_rows": len(result), "message": "旅程阶段汇总完成"}
```

- [ ] **Step 3: Implement channel matrix**

Create `backend/app/tasks/journey_channel_matrix.py` with the helpers from Step 1 and this `run` body:

```python
def run(engine, params: dict) -> dict:
    df = pd.read_sql("SELECT * FROM data_asset.dwd_customer_touchpoint", engine)
    records = []
    if not df.empty:
        df["negative_flag"] = df["sentiment_tag"].fillna("").isin(NEGATIVE_SENTIMENTS).astype(int)
        for (brand, model, channel, stage), group in df.groupby(["brand_name", "model_name", "source_channel", "journey_stage"], dropna=False):
            date_from = pd.to_datetime(group["touchpoint_time"]).min().date()
            date_to = pd.to_datetime(group["touchpoint_time"]).max().date()
            touchpoint_cnt = int(group["touchpoint_id"].nunique())
            negative_cnt = int(group["negative_flag"].sum())
            records.append(
                {
                    "matrix_id": f"matrix_{_sha(str(brand) + str(model) + str(channel) + str(stage))}",
                    "brand_name": brand,
                    "model_name": model,
                    "source_channel": channel,
                    "journey_stage": stage,
                    "date_from": date_from,
                    "date_to": date_to,
                    "touchpoint_cnt": touchpoint_cnt,
                    "negative_ratio": round(negative_cnt / touchpoint_cnt, 4) if touchpoint_cnt else 0,
                    "issue_top_json": _top_json(group["issue_tag"]),
                    "intent_top_json": _top_json(group["intent_tag"]),
                    "data_lineage_json": json.dumps(["dwd_customer_touchpoint"], ensure_ascii=False),
                    "updated_time": pd.Timestamp.now(),
                }
            )
    result = pd.DataFrame(records)
    write_refresh_table(engine, "ads_journey_channel_matrix", result)
    return {"processed_rows": len(df), "output_rows": len(result), "message": "旅程渠道矩阵汇总完成"}
```

- [ ] **Step 4: Implement painpoint summary**

Create `backend/app/tasks/journey_painpoint_summary.py` with the helpers from Step 1 and this `run` body:

```python
def run(engine, params: dict) -> dict:
    df = pd.read_sql("SELECT * FROM data_asset.dwd_customer_touchpoint", engine)
    records = []
    if not df.empty:
        df["issue_tag"] = df["issue_tag"].fillna("未标注问题")
        df["negative_flag"] = df["sentiment_tag"].fillna("").isin(NEGATIVE_SENTIMENTS).astype(int)
        for (brand, model, stage, issue), group in df.groupby(["brand_name", "model_name", "journey_stage", "issue_tag"], dropna=False):
            touchpoint_cnt = int(group["touchpoint_id"].nunique())
            negative_cnt = int(group["negative_flag"].sum())
            owner, action = suggest_owner_and_action(str(stage), str(issue))
            records.append(
                {
                    "painpoint_id": f"pain_{_sha(str(brand) + str(model) + str(stage) + str(issue))}",
                    "brand_name": brand,
                    "model_name": model,
                    "journey_stage": stage,
                    "issue_tag": issue,
                    "touchpoint_cnt": touchpoint_cnt,
                    "negative_ratio": round(negative_cnt / touchpoint_cnt, 4) if touchpoint_cnt else 0,
                    "source_channels_json": _top_json(group["source_channel"]),
                    "sample_texts_json": _sample_json(group),
                    "suggested_owner": owner,
                    "suggested_action": action,
                    "data_lineage_json": json.dumps(["dwd_customer_touchpoint", "journey_rules"], ensure_ascii=False),
                    "updated_time": pd.Timestamp.now(),
                }
            )
    result = pd.DataFrame(records)
    write_refresh_table(engine, "ads_journey_painpoint_summary", result)
    return {"processed_rows": len(df), "output_rows": len(result), "message": "旅程痛点汇总完成"}
```

- [ ] **Step 5: Register three ETL tasks**

Add task registry entries for:

- `journey_stage_summary`
- `journey_channel_matrix`
- `journey_painpoint_summary`

Each task group is `用户旅程`, input table is `dwd_customer_touchpoint`, and output table is the corresponding ADS table.

- [ ] **Step 6: Compile**

Run:

```powershell
python -m py_compile backend/app/tasks/journey_stage_summary.py backend/app/tasks/journey_channel_matrix.py backend/app/tasks/journey_painpoint_summary.py backend/app/task_registry.py
```

Expected: command exits with code `0`.

- [ ] **Step 7: Commit**

```powershell
git add backend/app/tasks/journey_stage_summary.py backend/app/tasks/journey_channel_matrix.py backend/app/tasks/journey_painpoint_summary.py backend/app/task_registry.py
git commit -m "feat: add customer journey aggregation tasks"
```

## Task 5: Journey API

**Files:**
- Modify: `backend/app/schemas.py`
- Create: `backend/app/journey_service.py`
- Modify: `backend/app/api.py`

- [ ] **Step 1: Add Pydantic schemas**

Append to `backend/app/schemas.py`:

```python
class DataLineage(BaseModel):
    tables: list[str] = Field(default_factory=list)
    formula: str = ""


class JourneyStageSummaryItem(BaseModel):
    stage: str
    touchpoint_count: int = 0
    channel_count: int = 0
    negative_ratio: float = 0
    intent_top: list[dict] = Field(default_factory=list)
    issue_top: list[dict] = Field(default_factory=list)
    channel_distribution: list[dict] = Field(default_factory=list)
    representative_touchpoints: list[dict] = Field(default_factory=list)
    data_lineage: DataLineage = Field(default_factory=DataLineage)


class JourneyOverviewResponse(BaseModel):
    brand_name: str = ""
    model_name: str = ""
    stages: list[JourneyStageSummaryItem]
    data_lineage: DataLineage


class JourneyMatrixCell(BaseModel):
    source_channel: str
    journey_stage: str
    touchpoint_count: int = 0
    negative_ratio: float = 0
    issue_top: list[dict] = Field(default_factory=list)
    intent_top: list[dict] = Field(default_factory=list)
    data_lineage: DataLineage = Field(default_factory=DataLineage)


class JourneyTouchpointItem(BaseModel):
    id: str
    source_channel: str
    source_system: str = ""
    user_display_name: str = ""
    text: str
    touchpoint_time: str = ""
    brand_name: str = ""
    model_name: str = ""
    city_name: str = ""
    store_name: str = ""
    journey_stage: str
    stage_reason: str = ""
    intent_tag: str = ""
    issue_tag: str = ""
    sentiment_tag: str = ""


class JourneyTouchpointListResponse(BaseModel):
    total: int
    items: list[JourneyTouchpointItem]
    data_lineage: DataLineage


class JourneyPainpointItem(BaseModel):
    journey_stage: str
    issue_tag: str
    touchpoint_count: int
    negative_ratio: float
    source_channels: list[dict] = Field(default_factory=list)
    sample_texts: list[dict] = Field(default_factory=list)
    suggested_owner: str = ""
    suggested_action: str = ""
    data_lineage: DataLineage = Field(default_factory=DataLineage)
```

- [ ] **Step 2: Implement journey service**

Create `backend/app/journey_service.py` with functions:

```python
import json

import pandas as pd
from sqlalchemy import text

from .database import engine
from .schemas import (
    DataLineage,
    JourneyMatrixCell,
    JourneyOverviewResponse,
    JourneyPainpointItem,
    JourneyStageSummaryItem,
    JourneyTouchpointItem,
    JourneyTouchpointListResponse,
)


class JourneyError(Exception):
    pass


def _ensure_engine():
    if engine is None:
        raise JourneyError("DATABASE_URL not configured")
    return engine


def _json_list(value) -> list:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []
    return []


def _lineage(tables: list[str], formula: str) -> DataLineage:
    return DataLineage(tables=tables, formula=formula)
```

Then implement:

- `get_journey_overview(brand_name=None, model_name=None)`
- `get_journey_matrix(brand_name=None, model_name=None)`
- `list_journey_touchpoints(stage=None, channel=None, brand_name=None, model_name=None, page=1, page_size=50)`
- `list_journey_painpoints(brand_name=None, model_name=None)`

Each query reads only from the ADS/detail tables and maps JSON columns using `_json_list`.

- [ ] **Step 3: Add API routes**

In `backend/app/api.py`, import service functions and add:

```python
@router.get("/journey/overview", response_model=JourneyOverviewResponse)
def get_journey_overview_api(brand_name: str | None = None, model_name: str | None = None):
    try:
        return get_journey_overview(brand_name=brand_name, model_name=model_name)
    except JourneyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/journey/matrix", response_model=list[JourneyMatrixCell])
def get_journey_matrix_api(brand_name: str | None = None, model_name: str | None = None):
    try:
        return get_journey_matrix(brand_name=brand_name, model_name=model_name)
    except JourneyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/journey/touchpoints", response_model=JourneyTouchpointListResponse)
def get_journey_touchpoints_api(
    stage: str | None = None,
    channel: str | None = None,
    brand_name: str | None = None,
    model_name: str | None = None,
    page: int = 1,
    page_size: int = 50,
):
    try:
        return list_journey_touchpoints(stage=stage, channel=channel, brand_name=brand_name, model_name=model_name, page=page, page_size=page_size)
    except JourneyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/journey/painpoints", response_model=list[JourneyPainpointItem])
def get_journey_painpoints_api(brand_name: str | None = None, model_name: str | None = None):
    try:
        return list_journey_painpoints(brand_name=brand_name, model_name=model_name)
    except JourneyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
```

- [ ] **Step 4: Compile**

Run:

```powershell
python -m py_compile backend/app/schemas.py backend/app/journey_service.py backend/app/api.py
```

Expected: command exits with code `0`.

- [ ] **Step 5: Commit**

```powershell
git add backend/app/schemas.py backend/app/journey_service.py backend/app/api.py
git commit -m "feat: expose customer journey APIs"
```

## Task 6: Frontend Customer Journey Page

**Files:**
- Create: `app/src/types/customerJourney.ts`
- Create: `app/src/lib/customer-journey-api.ts`
- Create: `app/src/components/voc/customer-journey/CustomerJourneyPage.tsx`
- Create: `app/src/components/voc/customer-journey/StageOverviewRail.tsx`
- Create: `app/src/components/voc/customer-journey/ChannelStageMatrix.tsx`
- Create: `app/src/components/voc/customer-journey/TouchpointEvidenceList.tsx`
- Create: `app/src/components/voc/customer-journey/ActionSuggestions.tsx`
- Create: `app/src/components/voc/customer-journey/customerJourneyApi.test.mjs`
- Modify: `app/src/App.tsx` or existing route/sidebar file
- Modify: `app/package.json`

- [ ] **Step 1: Add frontend types**

Create `app/src/types/customerJourney.ts`:

```ts
export interface DataLineage {
  tables: string[];
  formula: string;
}

export interface JourneyStageSummaryItem {
  stage: string;
  touchpointCount: number;
  channelCount: number;
  negativeRatio: number;
  intentTop: Array<{ label: string; value: number }>;
  issueTop: Array<{ label: string; value: number }>;
  channelDistribution: Array<{ label: string; value: number }>;
  representativeTouchpoints: Array<{ touchpointId: string; channel: string; text: string; time: string }>;
  dataLineage: DataLineage;
}

export interface JourneyOverviewResponse {
  brandName: string;
  modelName: string;
  stages: JourneyStageSummaryItem[];
  dataLineage: DataLineage;
}

export interface JourneyMatrixCell {
  sourceChannel: string;
  journeyStage: string;
  touchpointCount: number;
  negativeRatio: number;
  issueTop: Array<{ label: string; value: number }>;
  intentTop: Array<{ label: string; value: number }>;
  dataLineage: DataLineage;
}

export interface JourneyTouchpointItem {
  id: string;
  sourceChannel: string;
  sourceSystem: string;
  userDisplayName: string;
  text: string;
  touchpointTime: string;
  brandName: string;
  modelName: string;
  cityName: string;
  storeName: string;
  journeyStage: string;
  stageReason: string;
  intentTag: string;
  issueTag: string;
  sentimentTag: string;
}

export interface JourneyPainpointItem {
  journeyStage: string;
  issueTag: string;
  touchpointCount: number;
  negativeRatio: number;
  sourceChannels: Array<{ label: string; value: number }>;
  sampleTexts: Array<{ touchpointId: string; channel: string; text: string; time: string }>;
  suggestedOwner: string;
  suggestedAction: string;
  dataLineage: DataLineage;
}
```

- [ ] **Step 2: Add API client with no mock fallback**

Create `app/src/lib/customer-journey-api.ts` with `safeJson`, normalizers, and exports:

```ts
export async function getJourneyOverview(): Promise<JourneyOverviewResponse>
export async function getJourneyMatrix(): Promise<JourneyMatrixCell[]>
export async function getJourneyTouchpoints(params?: { stage?: string; channel?: string }): Promise<{ total: number; items: JourneyTouchpointItem[]; dataLineage: DataLineage }>
export async function getJourneyPainpoints(): Promise<JourneyPainpointItem[]>
```

If any request fails, throw the error. Do not return mock data.

- [ ] **Step 3: Add API mapping test**

Create `app/src/components/voc/customer-journey/customerJourneyApi.test.mjs`:

```js
import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync(new URL('../../../lib/customer-journey-api.ts', import.meta.url), 'utf8');

assert.match(source, /getJourneyOverview/);
assert.match(source, /getJourneyMatrix/);
assert.match(source, /getJourneyTouchpoints/);
assert.match(source, /getJourneyPainpoints/);
assert.doesNotMatch(source, /mock/i);
assert.doesNotMatch(source, /fallback/i);

console.log('customer journey api tests passed');
```

- [ ] **Step 4: Add package script**

In `app/package.json`, add:

```json
"test:customer-journey": "node src/components/voc/customer-journey/customerJourneyApi.test.mjs"
```

- [ ] **Step 5: Build UI components**

Create the four UI components. Each component must receive data through props and render an explicit empty state if arrays are empty. Do not import static mock data files.

Required empty state copy:

```tsx
<p className="text-sm text-slate-500">暂无真实数据，请先导入触点并运行用户旅程ETL。</p>
```

- [ ] **Step 6: Add page container**

Create `CustomerJourneyPage.tsx` to load all four APIs with `Promise.all`. If an API fails, show:

```tsx
<div className="rounded-3xl border border-amber-200 bg-amber-50 p-6 text-amber-900">
  未展示样例数据。请先启动后端、导入触点数据并运行用户旅程ETL。
</div>
```

- [ ] **Step 7: Add navigation entry**

Modify the existing app route/sidebar entry to include `VOC看用户` and render `CustomerJourneyPage`.

- [ ] **Step 8: Verify frontend**

Run:

```powershell
npm run test:customer-journey
npm run build
```

Expected: test passes and Vite build succeeds.

- [ ] **Step 9: Commit**

```powershell
git add app/src/types/customerJourney.ts app/src/lib/customer-journey-api.ts app/src/components/voc/customer-journey app/src/App.tsx app/package.json
git commit -m "feat: add customer journey VOC page"
```

## Task 7: Final Verification

**Files:**
- Read: `docs/superpowers/specs/2026-05-08-story1-customer-journey-voc-design.md`
- Read: `docs/superpowers/plans/2026-05-08-story1-customer-journey-voc.md`

- [ ] **Step 1: Run backend compile checks**

```powershell
python -m py_compile backend/app/journey_rules.py backend/app/journey_service.py backend/app/api.py backend/app/import_service.py backend/app/task_registry.py
python -m py_compile backend/app/tasks/customer_touchpoint_standardize.py backend/app/tasks/journey_stage_summary.py backend/app/tasks/journey_channel_matrix.py backend/app/tasks/journey_painpoint_summary.py
```

Expected: both commands exit with code `0`.

- [ ] **Step 2: Run backend rule tests**

```powershell
python -m unittest backend.tests.test_journey_rules -v
```

Expected: all tests pass.

- [ ] **Step 3: Run frontend tests and build**

```powershell
npm run test:asset-strategy
npm run test:customer-journey
npm run build
```

Expected: both tests pass and build succeeds.

- [ ] **Step 4: Search for forbidden claims**

Run:

```powershell
rg -n "跨渠道打通|单用户路径|转化率|成交率|复购率|真实成交" app/src backend/app docs/superpowers/specs/2026-05-08-story1-customer-journey-voc-design.md
```

Expected: matches are only in design/spec text that explicitly says these are not supported or not displayed. No frontend visible claim should say the system can perform them.

- [ ] **Step 5: Final commit if needed**

```powershell
git status --short
git add docs/superpowers/plans/2026-05-08-story1-customer-journey-voc.md
git commit -m "docs: add customer journey VOC implementation plan"
```

Expected: plan is committed if it was not already committed before execution.
