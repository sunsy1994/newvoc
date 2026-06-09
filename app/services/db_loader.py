from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd
import psycopg
from pandas.errors import EmptyDataError
from psycopg import sql
from psycopg.types.json import Jsonb

from app.config import DATABASE_URL, SCHEMA_SQL_PATH


LOAD_ORDER = [
    "ods_event_upload",
    "ods_content_upload",
    "ods_comment_upload",
    "dwd_event",
    "dwd_author",
    "dwd_content",
    "dwd_comment",
    "rel_event_content",
    "rel_author_content",
    "ads_event_overview",
    "ads_event_trend_daily",
    "ads_event_content_rank",
    "ads_event_location_distribution",
    "rejected_content",
    "rejected_comment",
]

TABLE_PRIMARY_KEYS = {
    "dwd_event": ["event_id"],
    "dwd_author": ["author_id"],
    "dwd_content": ["content_id"],
    "dwd_comment": ["comment_id"],
    "rel_event_content": ["event_id", "content_id"],
    "rel_author_content": ["author_id", "content_id"],
    "ads_event_overview": ["event_id"],
    "ads_event_trend_daily": ["event_id", "stat_date"],
    "ads_event_content_rank": ["rank_id"],
    "ads_event_location_distribution": ["event_id", "location"],
    "rejected_content": ["batch_id", "row_no"],
    "rejected_comment": ["batch_id", "row_no"],
}

GENERATED_COLUMNS = {
    "dwd_content": {"engagement_total"},
    "dwd_comment": {"interaction_cnt"},
}

JSON_COLUMNS = {
    "raw_payload_json",
    "payload_json",
    "required_fields_json",
    "optional_fields_json",
    "input_tables_json",
    "output_tables_json",
    "data_lineage_json",
    "top_platform_json",
    "top_author_json",
}

BOOLEAN_COLUMNS = {"is_kol", "is_enabled"}

INTEGER_COLUMNS = {
    "raw_row_no",
    "like_cnt",
    "comment_cnt",
    "share_cnt",
    "favorite_cnt",
    "view_cnt",
    "fans_cnt",
    "reply_cnt",
    "content_cnt",
    "author_cnt",
    "kol_content_cnt",
    "total_engagement",
    "engagement_cnt",
    "row_no",
}

EMPTY_NUMERIC_TEXTS = {"", "-", "--", "—", "–", "nan", "none", "null", "n/a", "na"}


def init_database(database_url: str = DATABASE_URL) -> None:
    schema_sql = SCHEMA_SQL_PATH.read_text(encoding="utf-8")
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
        conn.commit()


def resolve_load_tables(output_dir: Path) -> list[tuple[str, Path]]:
    return [(table, output_dir / f"{table}.csv") for table in LOAD_ORDER if (output_dir / f"{table}.csv").exists()]


def prepare_dataframe_for_table(table_name: str, dataframe: pd.DataFrame, batch_id: str) -> pd.DataFrame:
    prepared = dataframe.copy()
    if table_name.startswith("ods_"):
        prepared["ingest_batch_id"] = batch_id
        prepared["source_file_name"] = f"{table_name}.csv"
        prepared["raw_row_no"] = [index + 2 for index in range(len(prepared))]
        if "raw_payload_json" not in prepared.columns:
            prepared["raw_payload_json"] = [row_to_payload(row) for row in prepared.to_dict(orient="records")]

    if table_name in {"rejected_content", "rejected_comment"}:
        if prepared.empty:
            return pd.DataFrame(columns=["batch_id", "row_no", "reason", "payload_json"])
        rows = []
        for index, row in enumerate(prepared.to_dict(orient="records"), start=1):
            rows.append(
                {
                    "batch_id": batch_id,
                    "row_no": index,
                    "reason": row.get("reason"),
                    "payload_json": row_to_payload(row),
                }
            )
        prepared = pd.DataFrame(rows)

    drop_columns = GENERATED_COLUMNS.get(table_name, set())
    if drop_columns:
        prepared = prepared.drop(columns=[column for column in drop_columns if column in prepared.columns])
    return prepared


def load_etl_outputs(output_dir: Path, batch_id: str, database_url: str = DATABASE_URL) -> dict[str, int]:
    loaded: dict[str, int] = {}
    init_database(database_url)
    with psycopg.connect(database_url) as conn:
        for table_name, csv_path in resolve_load_tables(output_dir):
            dataframe = read_csv(csv_path)
            dataframe = prepare_dataframe_for_table(table_name, dataframe, batch_id)
            loaded[table_name] = load_table(conn, table_name, dataframe, batch_id)
        conn.commit()
    return loaded


def read_csv(csv_path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(csv_path, encoding="utf-8-sig")
    except EmptyDataError:
        return pd.DataFrame()


def load_table(conn: psycopg.Connection, table_name: str, dataframe: pd.DataFrame, batch_id: str) -> int:
    if table_name.startswith("ods_"):
        delete_batch_rows(conn, table_name, "ingest_batch_id", batch_id)
    elif table_name in {"rejected_content", "rejected_comment"}:
        delete_batch_rows(conn, table_name, "batch_id", batch_id)

    if dataframe.empty:
        return 0

    db_columns = get_insertable_columns(conn, table_name)
    columns = [column for column in db_columns if column in dataframe.columns]
    if not columns:
        return 0

    rows = [[normalize_db_value(row[column], column) for column in columns] for row in dataframe.to_dict(orient="records")]
    placeholders = sql.SQL(", ").join(sql.Placeholder() for _ in columns)
    insert_sql = sql.SQL("INSERT INTO data_asset.{table} ({columns}) VALUES ({placeholders})").format(
        table=sql.Identifier(table_name),
        columns=sql.SQL(", ").join(sql.Identifier(column) for column in columns),
        placeholders=placeholders,
    )

    pk_columns = TABLE_PRIMARY_KEYS.get(table_name)
    if pk_columns:
        update_columns = [column for column in columns if column not in pk_columns]
        conflict_target = sql.SQL(", ").join(sql.Identifier(column) for column in pk_columns)
        if update_columns:
            assignments = sql.SQL(", ").join(
                sql.SQL("{column} = EXCLUDED.{column}").format(column=sql.Identifier(column))
                for column in update_columns
            )
            insert_sql += sql.SQL(" ON CONFLICT ({target}) DO UPDATE SET {assignments}").format(
                target=conflict_target,
                assignments=assignments,
            )
        else:
            insert_sql += sql.SQL(" ON CONFLICT ({target}) DO NOTHING").format(target=conflict_target)

    with conn.cursor() as cur:
        cur.executemany(insert_sql, rows)
    return len(rows)


def delete_batch_rows(conn: psycopg.Connection, table_name: str, batch_column: str, batch_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL("DELETE FROM data_asset.{table} WHERE {column} = %s").format(
                table=sql.Identifier(table_name),
                column=sql.Identifier(batch_column),
            ),
            [batch_id],
        )


def get_insertable_columns(conn: psycopg.Connection, table_name: str) -> list[str]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'data_asset'
              AND table_name = %s
              AND is_generated = 'NEVER'
              AND identity_generation IS NULL
            ORDER BY ordinal_position
            """,
            [table_name],
        )
        return [row[0] for row in cur.fetchall()]


def normalize_db_value(value: Any, column: str) -> Any:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    if column in JSON_COLUMNS:
        if isinstance(value, Jsonb):
            return value
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return None
            try:
                return Jsonb(json.loads(text))
            except json.JSONDecodeError:
                return Jsonb(text)
        return Jsonb(value)
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()
    if column in INTEGER_COLUMNS:
        text = str(value).strip().replace(",", "")
        if text.lower() in EMPTY_NUMERIC_TEXTS:
            return None
        try:
            return int(float(text))
        except ValueError:
            return None
    if column in BOOLEAN_COLUMNS:
        if isinstance(value, bool):
            return value
        text = str(value).strip().lower()
        if text in {"1", "true", "yes", "y", "是", "有", "kol"}:
            return True
        if text in {"0", "false", "no", "n", "否", "无", "非kol"}:
            return False
    return value


def row_to_payload(row: dict[str, Any]) -> dict[str, Any]:
    return {key: normalize_payload_value(value) for key, value in row.items()}


def normalize_payload_value(value: Any) -> Any:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize PostgreSQL schema and load ETL CSV outputs.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--database-url", default=DATABASE_URL)

    load_parser = subparsers.add_parser("load")
    load_parser.add_argument("--output-dir", type=Path, required=True)
    load_parser.add_argument("--batch-id", required=True)
    load_parser.add_argument("--database-url", default=DATABASE_URL)

    args = parser.parse_args()
    if args.command == "init":
        init_database(args.database_url)
        print("database initialized")
    elif args.command == "load":
        result = load_etl_outputs(args.output_dir, args.batch_id, args.database_url)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
