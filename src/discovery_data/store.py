"""Bronze-backed store for the discovery.v1 read-only API."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from . import config


class SharedRuntimeUnavailable(RuntimeError):
    """The Solo Empire ``data_lake`` runtime could not be located or imported."""


def _candidate_roots() -> list[Path]:
    roots = []
    if config.SOLO_EMPIRE_ROOT.strip():
        roots.append(Path(config.SOLO_EMPIRE_ROOT).expanduser().resolve())
    project = config.PROJECT_ROOT.resolve()
    roots.extend([project, *project.parents])
    return roots


def _load_product_store():
    for parent in _candidate_roots():
        scripts = parent / "infra" / "scripts"
        if (scripts / "data_lake" / "product_store.py").is_file():
            if str(scripts) not in sys.path:
                sys.path.insert(0, str(scripts))
            break
    try:
        from data_lake import product_store as product_store_module  # type: ignore
    except ImportError as exc:
        raise SharedRuntimeUnavailable(
            "Solo Empire data_lake runtime not found; set SOLO_EMPIRE_ROOT or run "
            "from a Solo Empire checkout"
        ) from exc

    return product_store_module


_PRODUCT_STORE = None


def _ps():
    global _PRODUCT_STORE
    if _PRODUCT_STORE is None:
        _PRODUCT_STORE = _load_product_store()
    return _PRODUCT_STORE


def _lake_uri() -> str | None:
    return config.DATA_LAKE_URI.strip() or None


def _contract():
    _ps()  # locate the shared runtime before importing its adapter
    from data_lake.product_adapter import LakeProductContract  # type: ignore

    return LakeProductContract(
        source=config.LAKE_SOURCE,
        domain=config.LAKE_DOMAIN,
        product_schema_version=config.SCHEMA_VERSION,
        privacy_class=config.LAKE_PRIVACY_CLASS,
        retention_class=config.LAKE_RETENTION_CLASS,
        bronze_schema_version=config.LAKE_BRONZE_SCHEMA_VERSION,
        project_root=config.PROJECT_ROOT,
        data_lake_uri=_lake_uri() or "",
        solo_empire_root=config.SOLO_EMPIRE_ROOT,
        lineage_filename=config.LINEAGE_FILE,
        datasets=(config.LAKE_DATASET_SIGNALS, config.LAKE_DATASET_HISTORY),
    )


def utc_now_iso() -> str:
    return _ps().utc_now_iso()


def make_record_id(row: dict[str, Any]) -> str:
    return _ps().make_record_id(
        row,
        id_fields=config.ID_FIELDS,
        id_sep=config.ID_SEP,
    )


def signal_item_from_bronze(
    row: dict[str, Any], *, history: bool = False, history_idx: int = 0
) -> dict[str, Any]:
    payload = _ps().parse_payload_json(row)
    event_time = str(
        row.get("event_time")
        or payload.get("captured_at")
        or payload.get("observed_at")
        or ""
    )
    item: dict[str, Any] = {}
    for key, value in payload.items():
        if key == "id":
            continue
        item[key] = value if isinstance(value, (dict, list)) else str(value or "")
    item.update(
        {
            "signal_id": str(payload.get("signal_id") or ""),
            "source": str(payload.get("source") or ""),
            "title": str(payload.get("title") or payload.get("name") or ""),
            "canonical_url": str(payload.get("canonical_url") or payload.get("url") or ""),
            "publisher": str(payload.get("publisher") or ""),
            "source_url": str(payload.get("source_url") or ""),
            "observed_at": str(payload.get("observed_at") or event_time),
            "captured_at": str(payload.get("captured_at") or event_time),
            "capture_kind": str(payload.get("capture_kind") or "current_snapshot"),
            "record_kind": str(payload.get("record_kind") or "technology_signal"),
            "attribution_required": bool(payload.get("attribution_required", True)),
            "event_time": event_time,
            "ingest_run_id": str(row.get("ingest_run_id") or ""),
            "source_record_id": str(row.get("source_record_id") or ""),
            "raw_object_key": str(row.get("raw_object_key") or ""),
        }
    )
    record_id = make_record_id(item)
    item["record_id"] = record_id + (f"#h{history_idx}" if history else "")
    return item


def load_records(*, data_lake_uri: str | None = None) -> dict[str, Any]:
    return _ps().load_bronze_dataset(
        _contract(),
        config.LAKE_DATASET_SIGNALS,
        data_lake_uri=data_lake_uri or _lake_uri(),
        latest_only=True,
        id_fields=config.ID_FIELDS,
        id_sep=config.ID_SEP,
        stale_after_hours=config.STALE_AFTER_HOURS,
        item_builder=signal_item_from_bronze,
        read_mode=config.LAKE_READ_MODE,
        read_fallback=config.LAKE_READ_FALLBACK,
    )


def load_history(*, data_lake_uri: str | None = None) -> dict[str, Any]:
    return _ps().load_bronze_dataset(
        _contract(),
        config.LAKE_DATASET_HISTORY,
        data_lake_uri=data_lake_uri or _lake_uri(),
        latest_only=False,
        id_fields=config.ID_FIELDS,
        id_sep=config.ID_SEP,
        stale_after_hours=config.STALE_AFTER_HOURS * 4,
        item_builder=signal_item_from_bronze,
        read_mode=config.LAKE_READ_MODE,
        read_fallback=config.LAKE_READ_FALLBACK,
    )


def get_record(
    record_id: str, *, data_lake_uri: str | None = None
) -> dict[str, Any] | None:
    return _ps().get_record_from_payload(
        record_id,
        load_records(data_lake_uri=data_lake_uri),
    )


def paginate(
    items: list[dict[str, Any]], *, limit: int = 50, cursor: str | None = None
) -> tuple[list[dict[str, Any]], str | None]:
    return _ps().paginate(items, limit=limit, cursor=cursor)


def envelope(
    *,
    items: list[dict[str, Any]],
    data_status: str,
    next_cursor: str | None = None,
    retrieved_at: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _ps().envelope(
        schema_version=config.SCHEMA_VERSION,
        source=config.REPO_NAME,
        items=items,
        data_status=data_status,
        next_cursor=next_cursor,
        retrieved_at=retrieved_at,
        extra=extra,
    )
