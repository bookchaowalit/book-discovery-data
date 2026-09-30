"""Runtime configuration for the discovery.v1 read-only API."""

from __future__ import annotations

import math
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPO_NAME = "book-discovery-data"
DOMAIN = "discovery"
SCHEMA_VERSION = "discovery.v1"
LINEAGE_FILE = "lake_lineage.json"
LAKE_SOURCE = REPO_NAME
LAKE_DOMAIN = DOMAIN
LAKE_DATASET_SIGNALS = "technology_signals"
LAKE_DATASET_HISTORY = "technology_signals_history"
LAKE_BRONZE_SCHEMA_VERSION = "1"
LAKE_PRIVACY_CLASS = "public"
LAKE_RETENTION_CLASS = "operational-plus-history"
ID_FIELDS = ["source", "signal_id"]
ID_SEP = "|"


def env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class ConfigError(ValueError):
    """An environment variable holds a value the API cannot run with."""


def env_int(name: str, default: int, *, minimum: int, maximum: int) -> int:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        value = int(raw.strip())
    except ValueError:
        raise ConfigError(f"{name} must be an integer, got {raw!r}") from None
    if not minimum <= value <= maximum:
        raise ConfigError(f"{name} must be between {minimum} and {maximum}, got {value}")
    return value


def env_positive_float(name: str, default: float) -> float:
    """Finite, strictly positive float; NaN/inf/<=0 would mark every read stale or never stale."""
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        value = float(raw.strip())
    except ValueError:
        raise ConfigError(f"{name} must be a number, got {raw!r}") from None
    if not math.isfinite(value) or value <= 0:
        raise ConfigError(f"{name} must be a finite number greater than 0, got {raw!r}")
    return value


FREE_ONLY = env_bool("FREE_ONLY", True)
ALLOW_PAID_PROVIDERS = env_bool("ALLOW_PAID_PROVIDERS", False)
ALLOW_EXTERNAL_WRITES = env_bool("ALLOW_EXTERNAL_WRITES", False)
ALLOW_REFRESH = env_bool("ALLOW_REFRESH", False)
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN", "")
API_HOST = os.environ.get("API_HOST", "127.0.0.1")
API_PORT = env_int("API_PORT", 8110, minimum=0, maximum=65535)
CORS_ALLOWED_ORIGINS = tuple(
    origin.strip().rstrip("/")
    for origin in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
)
STALE_AFTER_HOURS = env_positive_float("STALE_AFTER_HOURS", 36.0)
DATA_LAKE_URI = os.environ.get(
    "SOLO_EMPIRE_DATA_LAKE_URI", os.environ.get("DATA_LAKE_URI", "")
)
SOLO_EMPIRE_ROOT = os.environ.get("SOLO_EMPIRE_ROOT", "")
LAKE_READ_MODE = os.environ.get("LAKE_READ_MODE", "parquet").strip().lower()
LAKE_READ_FALLBACK = os.environ.get("LAKE_READ_FALLBACK", "error").strip().lower()
