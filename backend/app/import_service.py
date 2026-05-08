import hashlib
import io
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd
from fastapi import UploadFile

from .config import UPLOAD_DIR
from .database import insert_rows
from .job_store import upsert_job, update_job
from .schemas import ImportJobRecord, ImportJobResponse
from .template_registry import get_template


class ImportValidationError(Exception):
    pass


def _job_id() -> str:
    return f"job-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(column).strip().lower() for column in df.columns]
    return df


def _canonicalize_columns(df: pd.DataFrame, template: dict) -> pd.DataFrame:
    column_map = {str(key).strip().lower(): value for key, value in template.get("column_map", {}).items()}
    df = _normalize_columns(df)
    df = df.rename(columns={column: column_map.get(column, column) for column in df.columns})
    return df


def _read_upload(file: UploadFile, extension: str) -> pd.DataFrame:
    content = file.file.read()
    if extension == "csv":
        return pd.read_csv(io.BytesIO(content))
    if extension == "xlsx":
        return pd.read_excel(io.BytesIO(content))
    if extension == "txt":
        try:
            return pd.read_csv(io.BytesIO(content), sep="\t")
        except Exception:
            rows = []
            for index, line in enumerate(content.decode("utf-8").splitlines(), start=1):
                text = line.strip()
                if text:
                    rows.append({"comment_text": text, "row_no": index})
            return pd.DataFrame(rows)
    raise ImportValidationError(f"Unsupported file format: {extension}")


def _write_upload(file_name: str, raw_bytes: bytes) -> str:
    path = UPLOAD_DIR / file_name
    path.write_bytes(raw_bytes)
    return str(path)


def _sha(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:16]


def _join_parts(*parts: object) -> str:
    return "_".join("" if part is None else str(part) for part in parts)


def _to_bool(value) -> bool:
    if value is None or pd.isna(value):
        return False
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    return text in {"1", "true", "yes", "y", "是", "有"}


def _clean_value(value):
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()
    return value


def _generate_missing_ids(df: pd.DataFrame, source_key: str) -> pd.DataFrame:
    if source_key == "content":
        if "content_id" not in df.columns:
            df["content_id"] = None
        df["content_id"] = df.apply(
            lambda row: row["content_id"]
            if pd.notna(row["content_id"])
            else f"cnt_{_sha(_join_parts(row.get('platform', ''), row.get('source_url', ''), row.get('title', '')))}",
            axis=1,
        )
        if "author_id" not in df.columns:
            df["author_id"] = None
        df["author_id"] = df.apply(
            lambda row: row["author_id"]
            if pd.notna(row["author_id"])
            else f"acc_{_sha(_join_parts(row.get('platform', ''), row.get('author_name', '')))}",
            axis=1,
        )
    elif source_key == "comment":
        if "comment_id" not in df.columns:
            df["comment_id"] = None
        df["comment_id"] = df.apply(
            lambda row: row["comment_id"]
            if pd.notna(row["comment_id"])
            else f"cmt_{_sha(_join_parts(row.get('content_id', ''), row.get('comment_text', '')))}",
            axis=1,
        )
        if "comment_author_id" not in df.columns:
            df["comment_author_id"] = None
        df["comment_author_id"] = df.apply(
            lambda row: row["comment_author_id"]
            if pd.notna(row["comment_author_id"])
            else f"acc_{_sha(_join_parts(row.get('platform', ''), row.get('comment_author_name', '')))}",
            axis=1,
        )
    elif source_key == "account":
        if "account_id" not in df.columns:
            df["account_id"] = None
        df["account_id"] = df.apply(
            lambda row: row["account_id"]
            if pd.notna(row["account_id"])
            else f"acc_{_sha(_join_parts(row.get('platform', ''), row.get('nickname', '')))}",
            axis=1,
        )
    elif source_key == "event":
        if "event_id" not in df.columns:
            raise ImportValidationError("event 模板必须提供 event_id")
    elif source_key.startswith("journey_"):
        if "touchpoint_id" not in df.columns:
            df["touchpoint_id"] = None
        channel = source_key.replace("journey_", "")
        df["touchpoint_id"] = df.apply(
            lambda row: row["touchpoint_id"]
            if pd.notna(row["touchpoint_id"])
            else f"tp_{_sha(_join_parts(channel, row.get('touchpoint_time', ''), row.get('touchpoint_text', '')))}",
            axis=1,
        )
    return df


def _validate_dataframe(df: pd.DataFrame, template: dict) -> tuple[pd.DataFrame, list[str]]:
    df = _canonicalize_columns(df, template).dropna(how="all")
    warnings: list[str] = []
    missing_fields = [field for field in template["required_fields"] if field not in df.columns]
    if missing_fields:
        raise ImportValidationError(f"Missing required fields: {', '.join(missing_fields)}")

    empty_required_rows = []
    for field in template["required_fields"]:
        field_empty = df[df[field].isna() | (df[field].astype(str).str.strip() == "")]
        if not field_empty.empty:
            empty_required_rows.extend(field_empty.index.tolist())

    if empty_required_rows:
        unique_rows = sorted({int(item) + 2 for item in empty_required_rows})
        raise ImportValidationError(f"Required field is empty in rows: {unique_rows[:12]}")

    return df, warnings


def _prepare_rows(df: pd.DataFrame, source_key: str) -> tuple[list[dict], list[dict]]:
    if source_key == "event":
        rows = [
            {
                "event_id": row.get("event_id"),
                "event_name": row.get("event_name"),
                "event_desc": row.get("event_desc"),
                "event_type": row.get("event_type"),
                "brand_name": row.get("brand_name"),
                "model_name": row.get("model_name"),
                "keyword_list": row.get("keyword_list"),
                "start_time": row.get("start_time"),
                "end_time": row.get("end_time"),
                "event_status": row.get("event_status"),
            }
            for row in df.to_dict(orient="records")
        ]
        return rows, []

    if source_key == "content":
        content_rows = []
        rel_rows = []
        for row in df.to_dict(orient="records"):
            content_rows.append(
            {
                "content_id": row.get("content_id"),
                "platform": row.get("platform"),
                "source_url": row.get("source_url"),
                "author_id": row.get("author_id"),
                "author_name": row.get("author_name"),
                "author_type": row.get("author_type"),
                "is_kol": _to_bool(row.get("is_kol")),
                "kol_domain": row.get("kol_domain"),
                "fans_cnt": row.get("fans_cnt") or 0,
                "title": row.get("title"),
                "content_text": row.get("content_text"),
                "content_type": row.get("content_type"),
                "media_form": row.get("media_form"),
                "published_at": row.get("published_at"),
                "like_cnt": row.get("like_cnt") or 0,
                "comment_cnt": row.get("comment_cnt") or 0,
                "share_cnt": row.get("share_cnt") or 0,
                "favorite_cnt": row.get("favorite_cnt") or 0,
                "view_cnt": row.get("view_cnt") or 0,
            }
            )
            if row.get("event_id"):
                rel_rows.append(
                    {
                        "event_id": row.get("event_id"),
                        "content_id": row.get("content_id"),
                        "match_type": "manual",
                        "match_score": 1,
                        "is_primary_event": True,
                    }
                )
        return content_rows, rel_rows

    if source_key == "comment":
        rows = [
            {
                "comment_id": row.get("comment_id"),
                "platform": row.get("platform"),
                "content_id": row.get("content_id"),
                "comment_author_id": row.get("comment_author_id"),
                "comment_author_name": row.get("comment_author_name"),
                "parent_comment_id": row.get("parent_comment_id"),
                "reply_level": row.get("reply_level") or 1,
                "comment_text": row.get("comment_text"),
                "published_at": row.get("published_at"),
                "like_cnt": row.get("like_cnt") or 0,
                "reply_cnt": row.get("reply_cnt") or 0,
                "interaction_cnt": (row.get("like_cnt") or 0) + (row.get("reply_cnt") or 0),
                "source_url": row.get("source_url"),
                "opinion_tag": row.get("opinion_tag"),
                "intention_tag": row.get("intention_tag"),
                "sentiment_tag": row.get("sentiment_tag"),
                "persona_tag": row.get("persona_tag"),
                "stage_tag": row.get("stage_tag"),
                "mindset_tag": row.get("mindset_tag"),
            }
            for row in df.to_dict(orient="records")
        ]
        return rows, []

    if source_key == "account":
        rows = [
            {
                "account_id": row.get("account_id"),
                "snapshot_date": datetime.now().date(),
                "platform": row.get("platform"),
                "platform_account_id": row.get("account_id"),
                "nickname": row.get("nickname"),
                "avatar_url": row.get("avatar_url"),
                "account_type": row.get("account_type"),
                "domain_tag": row.get("domain_tag"),
                "fans_cnt": row.get("fans_cnt") or 0,
                "follow_cnt": row.get("follow_cnt") or 0,
                "liked_cnt": row.get("liked_cnt") or 0,
                "account_desc": row.get("account_desc"),
                "certification_info": row.get("certification_info"),
                "persona_tag": row.get("persona_tag"),
                "stage_tag": row.get("stage_tag"),
                "profile_tags_json": row.get("profile_tags_json"),
            }
            for row in df.to_dict(orient="records")
        ]
        return rows, []

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

    raise ImportValidationError(f"Unsupported source key: {source_key}")


def _normalize_records(rows: list[dict]) -> list[dict]:
    return [{key: _clean_value(value) for key, value in row.items()} for row in rows]


async def process_import(
    *,
    source_key: str,
    template_id: str,
    operator: str,
    upload_file: UploadFile,
) -> ImportJobResponse:
    template = get_template(template_id)
    if not template:
        raise ImportValidationError(f"Unknown template: {template_id}")
    if template["source_key"] != source_key:
        raise ImportValidationError("source_key does not match template")

    file_name = upload_file.filename or f"{template['source_key']}.csv"
    extension = Path(file_name).suffix.lower().replace(".", "")
    if extension not in template["formats"]:
        raise ImportValidationError(
            f"Template {template_id} only supports: {', '.join(template['formats'])}"
        )

    raw_bytes = await upload_file.read()
    upload_file.file.seek(0)
    _write_upload(file_name, raw_bytes)

    job_id = _job_id()
    now = datetime.now()
    record = ImportJobRecord(
        job_id=job_id,
        source_key=source_key,
        source_name=template["source_name"],
        template_id=template_id,
        template_name=template["source_name"],
        file_name=file_name,
        file_format=extension,
        operator=operator,
        status="running",
        created_at=now,
        updated_at=now,
        message="文件已接收，开始模板校验。",
    )
    upsert_job(record)

    try:
        upload_file.file.seek(0)
        dataframe = _read_upload(upload_file, extension)
        dataframe, warnings = _validate_dataframe(dataframe, template)
        dataframe = _generate_missing_ids(dataframe, source_key)
        main_rows, relation_rows = _prepare_rows(dataframe, source_key)
        main_rows = _normalize_records(main_rows)
        relation_rows = _normalize_records(relation_rows)

        inserted_rows = insert_rows(template["target_table"], main_rows)
        if source_key == "content" and relation_rows:
            insert_rows("rel_event_content", relation_rows)

        message = f"模板校验通过，已处理 {len(main_rows)} 行。"
        update_job(
            job_id,
            status="success",
            inserted_rows=inserted_rows,
            rejected_rows=0,
            message=message,
        )
        return ImportJobResponse(
            job_id=job_id,
            accepted=True,
            message=message,
            inserted_rows=inserted_rows,
            rejected_rows=0,
            warnings=warnings,
        )
    except Exception as exc:
        update_job(
            job_id,
            status="failed",
            inserted_rows=0,
            rejected_rows=0,
            message=str(exc),
        )
        if isinstance(exc, ImportValidationError):
            raise
        raise ImportValidationError(str(exc)) from exc
