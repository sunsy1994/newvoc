from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import psycopg
from psycopg import sql
from psycopg.rows import dict_row

from app.config import DATABASE_URL
from app.services.asset_library import build_like_pattern, normalize_row
from app.services.db_loader import init_database, normalize_db_value


KOL_PROFILE_COLUMNS = [
    {"key": "author_id", "label": "作者ID"},
    {"key": "platform", "label": "平台"},
    {"key": "author_name", "label": "作者名称"},
    {"key": "author_home_url", "label": "作者主页"},
    {"key": "kol_main_type", "label": "KOL主类型"},
    {"key": "content_tendency", "label": "内容倾向"},
    {"key": "car_focus", "label": "车型关注"},
    {"key": "remark", "label": "判定依据"},
    {"key": "profile_batch", "label": "画像批次"},
    {"key": "source_file_name", "label": "来源文件"},
    {"key": "updated_time", "label": "更新时间"},
]

KOL_SAMPLE_COLUMNS = [
    "author_id",
    "platform",
    "author_name",
    "author_home_url",
    "content_count",
    "content_text",
    "total_engagement",
]

KOL_UPLOAD_COLUMNS = [
    "author_id",
    "kol_main_type",
    "content_tendency",
    "car_focus",
    "remark",
    "profile_batch",
]


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


def prepare_kol_profile_upload(upload_path: Path, source_file_name: str | None = None) -> pd.DataFrame:
    dataframe = pd.read_excel(upload_path, dtype=object).dropna(how="all")
    for column in KOL_UPLOAD_COLUMNS:
        if column not in dataframe.columns:
            dataframe[column] = None
    rows = []
    for row in dataframe.to_dict(orient="records"):
        author_id = clean_text(row.get("author_id"))
        if not author_id:
            continue
        rows.append(
            {
                "author_id": author_id,
                "kol_main_type": clean_text(row.get("kol_main_type")),
                "content_tendency": clean_text(row.get("content_tendency")),
                "car_focus": clean_text(row.get("car_focus")),
                "remark": clean_text(row.get("remark")),
                "profile_batch": clean_text(row.get("profile_batch")) or "default",
                "source_file_name": source_file_name,
            }
        )
    if not rows:
        return pd.DataFrame(columns=[*KOL_UPLOAD_COLUMNS, "source_file_name"])
    return pd.DataFrame(rows).drop_duplicates(["author_id", "profile_batch"], keep="last")


def load_kol_profiles(
    upload_path: Path,
    source_file_name: str,
    database_url: str = DATABASE_URL,
) -> dict[str, int]:
    init_database(database_url)
    dataframe = prepare_kol_profile_upload(upload_path, source_file_name)
    if dataframe.empty:
        return {"loaded": 0}
    with psycopg.connect(database_url) as conn:
        columns = dataframe.columns.tolist()
        placeholders = sql.SQL(", ").join(sql.Placeholder() for _ in columns)
        insert_sql = sql.SQL("INSERT INTO data_asset.user_profile_kol ({columns}) VALUES ({placeholders})").format(
            columns=sql.SQL(", ").join(sql.Identifier(column) for column in columns),
            placeholders=placeholders,
        )
        update_columns = [column for column in columns if column not in {"author_id", "profile_batch"}]
        assignments = sql.SQL(", ").join(
            sql.SQL("{column} = EXCLUDED.{column}").format(column=sql.Identifier(column))
            for column in update_columns
        )
        assignments += sql.SQL(", updated_time = CURRENT_TIMESTAMP")
        insert_sql += sql.SQL(
            " ON CONFLICT (author_id, profile_batch) DO UPDATE SET {assignments}"
        ).format(assignments=assignments)
        rows = [
            [normalize_db_value(row[column], column) for column in columns]
            for row in dataframe.to_dict(orient="records")
        ]
        with conn.cursor() as cur:
            cur.executemany(insert_sql, rows)
        conn.commit()
    return {"loaded": len(dataframe)}


def export_kol_profile_samples(days: int = 7, database_url: str = DATABASE_URL) -> pd.DataFrame:
    days = max(1, min(days, 365))
    query = """
        SELECT
          a.author_id,
          a.platform,
          a.author_name,
          a.author_home_url,
          count(c.content_id) AS content_count,
          string_agg(
            concat_ws(' ', coalesce(c.title, ''), coalesce(c.content_text, '')),
            E'\n---\n'
            ORDER BY c.published_at DESC NULLS LAST
          ) AS content_text,
          coalesce(sum(c.engagement_total), 0) AS total_engagement
        FROM data_asset.dwd_author a
        LEFT JOIN data_asset.dwd_content c
          ON a.author_id = c.author_id
         AND c.published_at >= (CURRENT_DATE - (%s::int * INTERVAL '1 day'))
        WHERE a.is_kol = true
        GROUP BY a.author_id, a.platform, a.author_name, a.author_home_url
        ORDER BY total_engagement DESC NULLS LAST, content_count DESC NULLS LAST, a.author_name ASC
    """
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(query, [days])
            rows = [normalize_row(dict(row)) for row in cur.fetchall()]
    dataframe = pd.DataFrame(rows)
    for column in KOL_SAMPLE_COLUMNS:
        if column not in dataframe.columns:
            dataframe[column] = ""
    return dataframe[KOL_SAMPLE_COLUMNS]


def list_kol_profiles(
    q: str | None = None,
    profile_batch: str | None = None,
    limit: int = 50,
    offset: int = 0,
    database_url: str = DATABASE_URL,
    max_limit: int = 200,
) -> dict[str, Any]:
    limit = max(1, min(limit, max_limit))
    offset = max(0, offset)
    clauses = []
    params: list[Any] = []
    if profile_batch:
        clauses.append("p.profile_batch = %s")
        params.append(profile_batch)
    if q and q.strip():
        like_pattern = build_like_pattern(q)
        clauses.append(
            "(coalesce(p.author_id, '') ILIKE %s ESCAPE '\\' OR "
            "coalesce(a.author_name, '') ILIKE %s ESCAPE '\\' OR "
            "coalesce(p.kol_main_type, '') ILIKE %s ESCAPE '\\')"
        )
        params.extend([like_pattern, like_pattern, like_pattern])
    where_sql = " WHERE " + " AND ".join(clauses) if clauses else ""
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) "
                "FROM data_asset.user_profile_kol p "
                "LEFT JOIN data_asset.dwd_author a ON p.author_id = a.author_id"
                f"{where_sql}",
                params,
            )
            total = cur.fetchone()["count"]
            cur.execute(
                "SELECT p.author_id, a.platform, a.author_name, a.author_home_url, "
                "p.kol_main_type, p.content_tendency, p.car_focus, p.remark, "
                "p.profile_batch, p.source_file_name, p.updated_time "
                "FROM data_asset.user_profile_kol p "
                "LEFT JOIN data_asset.dwd_author a ON p.author_id = a.author_id "
                f"{where_sql} "
                "ORDER BY p.updated_time DESC NULLS LAST, a.author_name ASC LIMIT %s OFFSET %s",
                [*params, limit, offset],
            )
            rows = [normalize_row(dict(row)) for row in cur.fetchall()]
    return {
        "asset": "kol_profiles",
        "label": "KOL画像",
        "total": int(total),
        "columns": KOL_PROFILE_COLUMNS,
        "rows": rows,
    }


def get_kol_profile_batches(database_url: str = DATABASE_URL) -> list[str]:
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT profile_batch FROM data_asset.user_profile_kol ORDER BY profile_batch")
            return [row[0] for row in cur.fetchall()]
