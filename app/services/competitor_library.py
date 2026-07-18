from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import psycopg
from psycopg import sql
from psycopg.rows import dict_row

from app.config import DATABASE_URL
from app.services.asset_library import build_like_pattern, normalize_row
from app.services.db_loader import init_database, normalize_db_value


ACCOUNT_COLUMNS = [
    {"key": "account_name", "label": "账号名称"},
    {"key": "brand_name", "label": "品牌"},
    {"key": "account_type", "label": "账号类型"},
    {"key": "is_official", "label": "是否官方号"},
    {"key": "is_enabled", "label": "是否启用"},
    {"key": "account_home_url", "label": "账号主页"},
    {"key": "remark", "label": "备注"},
]

WORK_COLUMNS = [
    {"key": "work_id", "label": "作品ID"},
    {"key": "title", "label": "标题"},
    {"key": "author_name", "label": "作者"},
    {"key": "brand_name", "label": "品牌"},
    {"key": "account_type", "label": "账号类型"},
    {"key": "is_official", "label": "是否官方号"},
    {"key": "home_like_cnt", "label": "首页点赞数"},
    {"key": "interaction_like_cnt", "label": "互动点赞数"},
    {"key": "comment_cnt", "label": "评论数"},
    {"key": "favorite_cnt", "label": "收藏数"},
    {"key": "share_cnt", "label": "分享数"},
    {"key": "published_at", "label": "发布时间"},
    {"key": "is_pinned", "label": "是否置顶"},
    {"key": "video_url", "label": "视频链接"},
    {"key": "cover_url", "label": "封面图"},
    {"key": "topic_tags", "label": "话题标签"},
    {"key": "first_seen_at", "label": "首次发现时间"},
    {"key": "last_seen_at", "label": "最近更新时间"},
    {"key": "has_insight", "label": "是否有作品解读"},
    {"key": "insight_updated_at", "label": "作品解读更新时间"},
]

COMPETITOR_WORK_INSIGHT_TABLE_SQL = """
CREATE SCHEMA IF NOT EXISTS data_asset;
CREATE TABLE IF NOT EXISTS data_asset.competitor_work_insight (
    work_id TEXT PRIMARY KEY REFERENCES data_asset.competitor_work(work_id),
    insight_markdown TEXT NOT NULL DEFAULT '',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT
);
"""

ACCOUNT_COLUMN_MAP = {
    "账号名称": "account_name",
    "账号主页URL": "account_home_url",
    "账号类型": "account_type",
    "是否官方号": "is_official",
    "品牌": "brand_name",
    "是否启用": "is_enabled",
    "备注": "remark",
}

WORK_COLUMN_MAP = {
    "作品ID": "work_id",
    "标题": "title",
    "作者": "author_name",
    "品牌": "brand_name",
    "账号类型": "account_type",
    "是否官方号": "is_official",
    "首页点赞数": "home_like_cnt",
    "互动点赞数": "interaction_like_cnt",
    "评论数": "comment_cnt",
    "收藏数": "favorite_cnt",
    "分享数": "share_cnt",
    "发布时间": "published_at",
    "是否置顶": "is_pinned",
    "视频链接": "video_url",
    "封面图URL": "cover_url",
    "话题标签": "topic_tags",
    "来源文件": "source_file",
    "首次发现时间": "first_seen_at",
    "最近更新时间": "last_seen_at",
    "run_id": "run_id",
}


@dataclass(frozen=True)
class CompetitorLoadResult:
    accounts: int
    works: int


def stable_hash(*parts: Any) -> str:
    text = "||".join("" if part is None else str(part).strip().lower() for part in parts)
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]


def to_bool(value: Any) -> bool:
    text = "" if value is None else str(value).strip().lower()
    return text in {"1", "true", "yes", "y", "是", "启用", "官方", "官方号"}


def to_int(value: Any) -> int:
    if value is None:
        return 0
    try:
        if pd.isna(value):
            return 0
    except TypeError:
        pass
    try:
        return int(float(str(value).strip()))
    except ValueError:
        return 0


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    text = str(value).strip()
    return text or None


def clean_id(value: Any) -> str | None:
    text = clean_text(value)
    if text and text.endswith(".0"):
        return text[:-2]
    return text


def parse_time(value: Any) -> Any:
    text = clean_text(value)
    if not text:
        return None
    return pd.to_datetime(text, errors="coerce").to_pydatetime() if not pd.isna(pd.to_datetime(text, errors="coerce")) else None


def read_excel(path: Path) -> pd.DataFrame:
    return pd.read_excel(path, dtype=object).dropna(how="all")


def prepare_accounts(path: Path) -> pd.DataFrame:
    dataframe = read_excel(path).rename(columns=ACCOUNT_COLUMN_MAP)
    rows = []
    for row in dataframe.to_dict(orient="records"):
        home_url = clean_text(row.get("account_home_url"))
        account_name = clean_text(row.get("account_name")) or ""
        account_key = f"account_{stable_hash(home_url or account_name, row.get('brand_name'))}"
        rows.append(
            {
                "account_id": account_key,
                "account_key": account_key,
                "account_name": account_name,
                "account_home_url": home_url,
                "account_type": clean_text(row.get("account_type")),
                "is_official": to_bool(row.get("is_official")),
                "brand_name": clean_text(row.get("brand_name")),
                "is_enabled": to_bool(row.get("is_enabled")),
                "remark": clean_text(row.get("remark")),
            }
        )
    return pd.DataFrame(rows).drop_duplicates("account_key", keep="last")


def prepare_works(path: Path) -> pd.DataFrame:
    dataframe = read_excel(path).rename(columns=WORK_COLUMN_MAP)
    rows = []
    for row in dataframe.to_dict(orient="records"):
        video_url = clean_text(row.get("video_url"))
        work_id = clean_id(row.get("work_id")) or f"work_{stable_hash(video_url, row.get('title'))}"
        rows.append(
            {
                "work_id": work_id,
                "work_key": work_id,
                "title": clean_text(row.get("title")),
                "author_name": clean_text(row.get("author_name")),
                "brand_name": clean_text(row.get("brand_name")),
                "account_type": clean_text(row.get("account_type")),
                "is_official": to_bool(row.get("is_official")),
                "home_like_cnt": to_int(row.get("home_like_cnt")),
                "interaction_like_cnt": to_int(row.get("interaction_like_cnt")),
                "comment_cnt": to_int(row.get("comment_cnt")),
                "favorite_cnt": to_int(row.get("favorite_cnt")),
                "share_cnt": to_int(row.get("share_cnt")),
                "published_at": parse_time(row.get("published_at")),
                "is_pinned": to_bool(row.get("is_pinned")),
                "video_url": video_url,
                "cover_url": clean_text(row.get("cover_url")),
                "topic_tags": clean_text(row.get("topic_tags")),
                "source_file": clean_text(row.get("source_file")),
                "first_seen_at": parse_time(row.get("first_seen_at")),
                "last_seen_at": parse_time(row.get("last_seen_at")),
                "run_id": clean_text(row.get("run_id")),
            }
        )
    return pd.DataFrame(rows).drop_duplicates("work_key", keep="last")


def load_competitor_excels(accounts_path: Path, works_path: Path, database_url: str = DATABASE_URL) -> CompetitorLoadResult:
    init_database(database_url)
    accounts = prepare_accounts(accounts_path)
    works = prepare_works(works_path)
    with psycopg.connect(database_url) as conn:
        account_count = upsert_dataframe(conn, "competitor_account", accounts, ["account_id"])
        work_count = upsert_dataframe(conn, "competitor_work", works, ["work_id"])
        conn.commit()
    return CompetitorLoadResult(accounts=account_count, works=work_count)


def upsert_dataframe(conn: psycopg.Connection, table_name: str, dataframe: pd.DataFrame, pk_columns: list[str]) -> int:
    if dataframe.empty:
        return 0
    columns = dataframe.columns.tolist()
    placeholders = sql.SQL(", ").join(sql.Placeholder() for _ in columns)
    insert_sql = sql.SQL("INSERT INTO data_asset.{table} ({columns}) VALUES ({placeholders})").format(
        table=sql.Identifier(table_name),
        columns=sql.SQL(", ").join(sql.Identifier(column) for column in columns),
        placeholders=placeholders,
    )
    update_columns = [column for column in columns if column not in pk_columns]
    assignments = sql.SQL(", ").join(
        sql.SQL("{column} = EXCLUDED.{column}").format(column=sql.Identifier(column))
        for column in update_columns
    )
    insert_sql += sql.SQL(" ON CONFLICT ({target}) DO UPDATE SET {assignments}").format(
        target=sql.SQL(", ").join(sql.Identifier(column) for column in pk_columns),
        assignments=assignments,
    )
    rows = [
        [normalize_db_value(row[column], column) for column in columns]
        for row in dataframe.to_dict(orient="records")
    ]
    with conn.cursor() as cur:
        cur.executemany(insert_sql, rows)
    return len(rows)


def build_work_filters(
    q: str | None = None,
    brand_name: str | None = None,
    account_name: str | None = None,
    account_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> tuple[str, list[Any]]:
    clauses = []
    params: list[Any] = []
    if brand_name:
        clauses.append("w.brand_name = %s")
        params.append(brand_name)
    if account_name:
        clauses.append("w.author_name = %s")
        params.append(account_name)
    if account_type:
        clauses.append("w.account_type = %s")
        params.append(account_type)
    if start_date:
        clauses.append("w.published_at >= %s")
        params.append(start_date)
    if end_date:
        clauses.append("w.published_at < (%s::date + INTERVAL '1 day')")
        params.append(end_date)
    if q and q.strip():
        clauses.append(
            "(coalesce(w.title, '') ILIKE %s ESCAPE '\\' OR "
            "coalesce(w.author_name, '') ILIKE %s ESCAPE '\\' OR "
            "coalesce(w.topic_tags, '') ILIKE %s ESCAPE '\\')"
        )
        like_pattern = build_like_pattern(q)
        params.extend([like_pattern, like_pattern, like_pattern])
    return (" WHERE " + " AND ".join(clauses), params) if clauses else ("", params)


def ensure_competitor_work_insight_table(database_url: str = DATABASE_URL) -> None:
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(COMPETITOR_WORK_INSIGHT_TABLE_SQL)
        conn.commit()


def get_competitor_work_insight(work_id: str, database_url: str = DATABASE_URL) -> dict[str, Any]:
    ensure_competitor_work_insight_table(database_url)
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT w.work_id, coalesce(i.insight_markdown, '') AS insight_markdown, i.updated_at, i.updated_by "
                "FROM data_asset.competitor_work w "
                "LEFT JOIN data_asset.competitor_work_insight i ON i.work_id = w.work_id "
                "WHERE w.work_id = %s",
                (work_id,),
            )
            row = cur.fetchone()
    if row is None:
        raise ValueError("Competitor work not found")
    return normalize_row(dict(row))


def save_competitor_work_insight(
    work_id: str,
    insight_markdown: str,
    updated_by: str | None = None,
    database_url: str = DATABASE_URL,
) -> dict[str, Any]:
    ensure_competitor_work_insight_table(database_url)
    content = insight_markdown.strip()
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT work_id FROM data_asset.competitor_work WHERE work_id = %s", (work_id,))
            if cur.fetchone() is None:
                raise ValueError("Competitor work not found")
            cur.execute(
                "INSERT INTO data_asset.competitor_work_insight (work_id, insight_markdown, updated_by) "
                "VALUES (%s, %s, %s) "
                "ON CONFLICT (work_id) DO UPDATE SET insight_markdown = EXCLUDED.insight_markdown, "
                "updated_by = EXCLUDED.updated_by, updated_at = CURRENT_TIMESTAMP "
                "RETURNING work_id, insight_markdown, updated_at, updated_by",
                (work_id, content, updated_by),
            )
            row = cur.fetchone()
        conn.commit()
    return normalize_row(dict(row))


def list_competitor_accounts(
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
    database_url: str = DATABASE_URL,
    max_limit: int = 200,
) -> dict[str, Any]:
    limit = max(1, min(limit, max_limit))
    offset = max(0, offset)
    where_sql = ""
    params: list[Any] = []
    if q and q.strip():
        like_pattern = build_like_pattern(q)
        where_sql = (
            " WHERE coalesce(account_name, '') ILIKE %s ESCAPE '\\' "
            "OR coalesce(brand_name, '') ILIKE %s ESCAPE '\\' "
            "OR coalesce(account_type, '') ILIKE %s ESCAPE '\\'"
        )
        params = [like_pattern, like_pattern, like_pattern]
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT count(*) FROM data_asset.competitor_account{where_sql}", params)
            total = cur.fetchone()["count"]
            cur.execute(
                "SELECT account_name, brand_name, account_type, is_official, is_enabled, account_home_url, remark "
                f"FROM data_asset.competitor_account{where_sql} "
                "ORDER BY brand_name ASC NULLS LAST, account_type ASC NULLS LAST, account_name ASC LIMIT %s OFFSET %s",
                [*params, limit, offset],
            )
            rows = [normalize_row(dict(row)) for row in cur.fetchall()]
    return {"asset": "competitor_accounts", "label": "竞品账号库", "total": int(total), "columns": ACCOUNT_COLUMNS, "rows": rows}


def list_competitor_works(
    q: str | None = None,
    brand_name: str | None = None,
    account_name: str | None = None,
    account_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 50,
    offset: int = 0,
    database_url: str = DATABASE_URL,
    max_limit: int = 200,
) -> dict[str, Any]:
    limit = max(1, min(limit, max_limit))
    offset = max(0, offset)
    ensure_competitor_work_insight_table(database_url)
    where_sql, params = build_work_filters(q, brand_name, account_name, account_type, start_date, end_date)
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT count(*) FROM data_asset.competitor_work w{where_sql}", params)
            total = cur.fetchone()["count"]
            cur.execute(
                "SELECT work_id, title, author_name, brand_name, account_type, is_official, home_like_cnt, "
                "interaction_like_cnt, comment_cnt, favorite_cnt, share_cnt, published_at, is_pinned, video_url, "
                "cover_url, topic_tags, first_seen_at, last_seen_at, "
                "length(trim(coalesce(i.insight_markdown, ''))) > 0 AS has_insight, i.updated_at AS insight_updated_at "
                "FROM data_asset.competitor_work w "
                "LEFT JOIN data_asset.competitor_work_insight i ON i.work_id = w.work_id"
                f"{where_sql} "
                "ORDER BY published_at DESC NULLS LAST, interaction_like_cnt DESC NULLS LAST LIMIT %s OFFSET %s",
                [*params, limit, offset],
            )
            rows = [normalize_row(dict(row)) for row in cur.fetchall()]
    return {"asset": "competitor_works", "label": "竞品作品库", "total": int(total), "columns": WORK_COLUMNS, "rows": rows}


def get_competitor_options(database_url: str = DATABASE_URL) -> dict[str, list[str]]:
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT brand_name FROM data_asset.competitor_work WHERE brand_name IS NOT NULL ORDER BY brand_name")
            brands = [row[0] for row in cur.fetchall()]
            cur.execute("SELECT DISTINCT account_type FROM data_asset.competitor_work WHERE account_type IS NOT NULL ORDER BY account_type")
            account_types = [row[0] for row in cur.fetchall()]
    return {"brands": brands, "account_types": account_types}


def main() -> None:
    parser = argparse.ArgumentParser(description="Load competitor account and work Excel files into PostgreSQL.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    load_parser = subparsers.add_parser("load")
    load_parser.add_argument("--accounts", type=Path, required=True)
    load_parser.add_argument("--works", type=Path, required=True)
    load_parser.add_argument("--database-url", default=DATABASE_URL)
    args = parser.parse_args()
    if args.command == "load":
        result = load_competitor_excels(args.accounts, args.works, args.database_url)
        print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
