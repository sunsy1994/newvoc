from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd
import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app.config import DATABASE_URL
from app.services.asset_library import build_like_pattern, normalize_row
from app.services.db_loader import init_database, normalize_db_value
from jisuan import calculate_user_profile


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

COMMENT_USER_PROFILE_COLUMNS = [
    {"key": "comment_user_id", "label": "评论用户ID"},
    {"key": "platform", "label": "平台"},
    {"key": "comment_author_name", "label": "评论用户昵称"},
    {"key": "location", "label": "位置"},
    {"key": "main_dimension", "label": "主维度"},
    {"key": "main_label", "label": "主标签"},
    {"key": "main_score", "label": "主标签分数"},
    {"key": "total_comments", "label": "评论总数"},
    {"key": "valid_comments", "label": "有效评论数"},
    {"key": "profile_batch", "label": "画像批次"},
    {"key": "prompt_version", "label": "提示词版本"},
    {"key": "source_file_name", "label": "来源文件"},
    {"key": "updated_time", "label": "更新时间"},
]

COMMENT_USER_SAMPLE_COLUMNS = [
    "comment_user_id",
    "platform",
    "comment_author_name",
    "location",
    "comment_id",
    "event_name",
    "content_title",
    "content_author_name",
    "source_url",
    "comment_text",
    "published_at",
    "like_cnt",
    "reply_cnt",
]

COMMENT_USER_UPLOAD_COLUMNS = [
    "comment_user_id",
    "profile_batch",
    "prompt_version",
    "llm_result_json",
]

COMMENT_USER_UPLOAD_COLUMN_ALIASES = {
    "评论用户ID": "comment_user_id",
    "用户ID": "comment_user_id",
    "画像批次": "profile_batch",
    "提示词版本": "prompt_version",
    "LLM结果JSON": "llm_result_json",
    "LLM结果": "llm_result_json",
}

KOL_UPLOAD_COLUMNS = [
    "author_id",
    "kol_main_type",
    "content_tendency",
    "car_focus",
    "remark",
    "profile_batch",
]

KOL_UPLOAD_COLUMN_ALIASES = {
    "作者ID": "author_id",
    "KOL主类型": "kol_main_type",
    "内容倾向": "content_tendency",
    "车型关注": "car_focus",
    "判定依据": "remark",
    "备注": "remark",
    "画像批次": "profile_batch",
}


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
    dataframe = dataframe.rename(columns=normalize_upload_columns(dataframe.columns))
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


def normalize_upload_columns(columns: Any) -> dict[str, str]:
    normalized = {}
    for column in columns:
        column_text = str(column).strip().replace("\ufeff", "")
        normalized[column] = KOL_UPLOAD_COLUMN_ALIASES.get(column_text, column_text)
    return normalized


def normalize_comment_user_upload_columns(columns: Any) -> dict[str, str]:
    normalized = {}
    for column in columns:
        column_text = str(column).strip().replace("\ufeff", "")
        normalized[column] = COMMENT_USER_UPLOAD_COLUMN_ALIASES.get(column_text, column_text)
    return normalized


def build_comment_user_id(platform: Any, comment_author_name: Any, location: Any = None) -> str:
    key_parts = [
        clean_text(platform) or "",
        clean_text(comment_author_name) or "",
        clean_text(location) or "",
    ]
    natural_key = "|".join(part.casefold() for part in key_parts)
    digest = hashlib.sha1(natural_key.encode("utf-8")).hexdigest()[:16]
    return f"comment_user_{digest}"


def parse_llm_result_json(value: Any, row_no: int) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    text = clean_text(value)
    if not text:
        raise ValueError(f"第 {row_no} 行 llm_result_json 为空")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"第 {row_no} 行 llm_result_json 不是合法JSON：{exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"第 {row_no} 行 llm_result_json 必须是JSON对象")
    return parsed


def prepare_comment_user_llm_upload(upload_path: Path, source_file_name: str | None = None) -> pd.DataFrame:
    dataframe = pd.read_excel(upload_path, dtype=object).dropna(how="all")
    dataframe = dataframe.rename(columns=normalize_comment_user_upload_columns(dataframe.columns))
    for column in COMMENT_USER_UPLOAD_COLUMNS:
        if column not in dataframe.columns:
            dataframe[column] = None
    rows = []
    for index, row in enumerate(dataframe.to_dict(orient="records"), start=2):
        comment_user_id = clean_text(row.get("comment_user_id"))
        if not comment_user_id:
            continue
        rows.append(
            {
                "comment_user_id": comment_user_id,
                "profile_batch": clean_text(row.get("profile_batch")) or "default",
                "prompt_version": clean_text(row.get("prompt_version")),
                "llm_result_json": parse_llm_result_json(row.get("llm_result_json"), index),
                "source_file_name": source_file_name,
            }
        )
    if not rows:
        return pd.DataFrame(columns=[*COMMENT_USER_UPLOAD_COLUMNS, "source_file_name"])
    return pd.DataFrame(rows).drop_duplicates(["comment_user_id", "profile_batch"], keep="last")


def summarize_comment_user_profile(comment_user_id: str, llm_result: dict[str, Any]) -> dict[str, Any]:
    profile = calculate_user_profile(comment_user_id, llm_result)
    return {
        "comment_user_id": profile.get("user_id") or comment_user_id,
        "total_comments": profile.get("total_comments", 0),
        "valid_comments": profile.get("valid_comments", 0),
        "main_label": profile.get("main_label"),
        "main_dimension": profile.get("main_dimension"),
        "main_score": profile.get("main_score"),
        "label_scores": profile.get("label_scores", []),
    }


def load_kol_profiles(
    upload_path: Path,
    source_file_name: str,
    database_url: str = DATABASE_URL,
) -> dict[str, int]:
    init_database(database_url)
    dataframe = prepare_kol_profile_upload(upload_path, source_file_name)
    if dataframe.empty:
        raw_columns = [str(column).strip().replace("\ufeff", "") for column in pd.read_excel(upload_path, nrows=0).columns]
        raise ValueError(
            "未找到有效的 author_id。请确认上传文件包含 author_id 或 作者ID 列，且至少一行不为空。"
            f" 当前文件列：{', '.join(raw_columns)}"
        )
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


def export_comment_user_profile_samples(database_url: str = DATABASE_URL) -> pd.DataFrame:
    query = """
        SELECT
          coalesce(cm.platform, c.platform) AS platform,
          cm.comment_author_name,
          cm.location,
          cm.comment_id,
          e.event_name,
          c.title AS content_title,
          a.author_name AS content_author_name,
          c.source_url,
          cm.comment_text,
          cm.published_at,
          cm.like_cnt,
          cm.reply_cnt
        FROM data_asset.dwd_comment cm
        LEFT JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
        LEFT JOIN data_asset.dwd_event e ON c.event_id = e.event_id
        LEFT JOIN data_asset.dwd_author a ON c.author_id = a.author_id
        WHERE coalesce(cm.comment_author_name, '') <> ''
        ORDER BY coalesce(cm.platform, c.platform), cm.comment_author_name, cm.location, cm.published_at
    """
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = [normalize_row(dict(row)) for row in cur.fetchall()]
    for row in rows:
        row["comment_user_id"] = build_comment_user_id(
            row.get("platform"),
            row.get("comment_author_name"),
            row.get("location"),
        )
    dataframe = pd.DataFrame(rows)
    for column in COMMENT_USER_SAMPLE_COLUMNS:
        if column not in dataframe.columns:
            dataframe[column] = ""
    return dataframe[COMMENT_USER_SAMPLE_COLUMNS]


def get_comment_user_lookup(conn: psycopg.Connection) -> dict[str, dict[str, Any]]:
    query = """
        SELECT
          coalesce(cm.platform, c.platform) AS platform,
          cm.comment_author_name,
          cm.location,
          count(*) AS comment_count
        FROM data_asset.dwd_comment cm
        LEFT JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
        WHERE coalesce(cm.comment_author_name, '') <> ''
        GROUP BY coalesce(cm.platform, c.platform), cm.comment_author_name, cm.location
    """
    lookup = {}
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query)
        for row in cur.fetchall():
            record = normalize_row(dict(row))
            comment_user_id = build_comment_user_id(
                record.get("platform"),
                record.get("comment_author_name"),
                record.get("location"),
            )
            lookup[comment_user_id] = record
    return lookup


def load_comment_user_profile_records(
    records: list[dict[str, Any]],
    database_url: str = DATABASE_URL,
) -> dict[str, int]:
    init_database(database_url)
    dataframe = pd.DataFrame(records)
    if dataframe.empty:
        return {"raw_loaded": 0, "profiles_loaded": 0, "label_scores_loaded": 0}
    for column in [*COMMENT_USER_UPLOAD_COLUMNS, "source_file_name"]:
        if column not in dataframe.columns:
            dataframe[column] = None
    dataframe = dataframe.drop_duplicates(["comment_user_id", "profile_batch"], keep="last")

    with psycopg.connect(database_url) as conn:
        user_lookup = get_comment_user_lookup(conn)
        raw_loaded = 0
        profiles_loaded = 0
        label_scores_loaded = 0
        with conn.cursor() as cur:
            for row in dataframe.to_dict(orient="records"):
                cur.execute(
                    """
                    INSERT INTO data_asset.user_profile_comment_raw (
                      comment_user_id, profile_batch, prompt_version, llm_result_json, source_file_name
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (comment_user_id, profile_batch) DO UPDATE SET
                      prompt_version = EXCLUDED.prompt_version,
                      llm_result_json = EXCLUDED.llm_result_json,
                      source_file_name = EXCLUDED.source_file_name,
                      created_time = CURRENT_TIMESTAMP
                    RETURNING raw_profile_id
                    """,
                    [
                        row["comment_user_id"],
                        row["profile_batch"],
                        row["prompt_version"],
                        Jsonb(row["llm_result_json"]),
                        row["source_file_name"],
                    ],
                )
                raw_profile_id = cur.fetchone()[0]
                raw_loaded += 1

                profile = summarize_comment_user_profile(row["comment_user_id"], row["llm_result_json"])
                identity = user_lookup.get(row["comment_user_id"], {})
                cur.execute(
                    """
                    INSERT INTO data_asset.user_profile_comment_result (
                      comment_user_id, platform, comment_author_name, location,
                      total_comments, valid_comments, main_dimension, main_label, main_score,
                      label_scores_json, profile_batch, prompt_version, source_raw_profile_id, source_file_name
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (comment_user_id, profile_batch) DO UPDATE SET
                      platform = EXCLUDED.platform,
                      comment_author_name = EXCLUDED.comment_author_name,
                      location = EXCLUDED.location,
                      total_comments = EXCLUDED.total_comments,
                      valid_comments = EXCLUDED.valid_comments,
                      main_dimension = EXCLUDED.main_dimension,
                      main_label = EXCLUDED.main_label,
                      main_score = EXCLUDED.main_score,
                      label_scores_json = EXCLUDED.label_scores_json,
                      prompt_version = EXCLUDED.prompt_version,
                      source_raw_profile_id = EXCLUDED.source_raw_profile_id,
                      source_file_name = EXCLUDED.source_file_name,
                      updated_time = CURRENT_TIMESTAMP
                    """,
                    [
                        profile["comment_user_id"],
                        identity.get("platform"),
                        identity.get("comment_author_name"),
                        identity.get("location"),
                        profile["total_comments"],
                        profile["valid_comments"],
                        profile["main_dimension"],
                        profile["main_label"],
                        profile["main_score"],
                        Jsonb(profile["label_scores"]),
                        row["profile_batch"],
                        row["prompt_version"],
                        raw_profile_id,
                        row["source_file_name"],
                    ],
                )
                profiles_loaded += 1

                cur.execute(
                    """
                    DELETE FROM data_asset.user_profile_comment_label_score
                    WHERE comment_user_id = %s AND profile_batch = %s
                    """,
                    [row["comment_user_id"], row["profile_batch"]],
                )
                for label_score in profile["label_scores"]:
                    cur.execute(
                        """
                        INSERT INTO data_asset.user_profile_comment_label_score (
                          comment_user_id, profile_batch, dimension, label, final_score,
                          feature_level, confidence_level, support_count,
                          evidence_examples_json, evidence_details_json
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        [
                            row["comment_user_id"],
                            row["profile_batch"],
                            label_score.get("dimension"),
                            label_score.get("label"),
                            label_score.get("final_score"),
                            label_score.get("feature_level"),
                            label_score.get("confidence_level"),
                            label_score.get("support_count", 0),
                            Jsonb(label_score.get("evidence_examples", [])),
                            Jsonb(label_score.get("evidence_details", [])),
                        ],
                    )
                    label_scores_loaded += 1
        conn.commit()
    return {
        "raw_loaded": raw_loaded,
        "profiles_loaded": profiles_loaded,
        "label_scores_loaded": label_scores_loaded,
    }


def load_comment_user_profiles(
    upload_path: Path,
    source_file_name: str,
    database_url: str = DATABASE_URL,
) -> dict[str, int]:
    init_database(database_url)
    dataframe = prepare_comment_user_llm_upload(upload_path, source_file_name)
    if dataframe.empty:
        raw_columns = [str(column).strip().replace("\ufeff", "") for column in pd.read_excel(upload_path, nrows=0).columns]
        raise ValueError(
            "未找到有效的 comment_user_id。请确认上传文件包含 comment_user_id 或 评论用户ID 列，且至少一行不为空。"
            f" 当前文件列：{', '.join(raw_columns)}"
        )
    return load_comment_user_profile_records(dataframe.to_dict(orient="records"), database_url=database_url)


def list_comment_user_profiles(
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
        clauses.append("profile_batch = %s")
        params.append(profile_batch)
    if q and q.strip():
        like_pattern = build_like_pattern(q)
        clauses.append(
            "(coalesce(comment_user_id, '') ILIKE %s ESCAPE '\\' OR "
            "coalesce(comment_author_name, '') ILIKE %s ESCAPE '\\' OR "
            "coalesce(main_label, '') ILIKE %s ESCAPE '\\' OR "
            "coalesce(main_dimension, '') ILIKE %s ESCAPE '\\')"
        )
        params.extend([like_pattern, like_pattern, like_pattern, like_pattern])
    where_sql = " WHERE " + " AND ".join(clauses) if clauses else ""
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT count(*) FROM data_asset.user_profile_comment_result{where_sql}", params)
            total = cur.fetchone()["count"]
            cur.execute(
                "SELECT comment_user_id, platform, comment_author_name, location, "
                "main_dimension, main_label, main_score, total_comments, valid_comments, "
                "profile_batch, prompt_version, source_file_name, updated_time "
                "FROM data_asset.user_profile_comment_result "
                f"{where_sql} "
                "ORDER BY updated_time DESC NULLS LAST, main_score DESC NULLS LAST LIMIT %s OFFSET %s",
                [*params, limit, offset],
            )
            rows = [normalize_row(dict(row)) for row in cur.fetchall()]
    return {
        "asset": "comment_user_profiles",
        "label": "评论用户画像",
        "total": int(total),
        "columns": COMMENT_USER_PROFILE_COLUMNS,
        "rows": rows,
    }


def get_comment_user_profile_batches(database_url: str = DATABASE_URL) -> list[str]:
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT DISTINCT profile_batch FROM data_asset.user_profile_comment_result ORDER BY profile_batch"
            )
            return [row[0] for row in cur.fetchall()]
