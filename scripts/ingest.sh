#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LAKE_ROOT="${SOLO_DATA_LAKE_ROOT:-}"
if [[ -z "$LAKE_ROOT" || ! -f "$LAKE_ROOT/infra/scripts/data_lake/ingest_discovery_captures.py" ]]; then
  echo "Set SOLO_DATA_LAKE_ROOT to a data-lake checkout (discovery replay)" >&2
  exit 2
fi

PYTHON="${SOLO_DATA_LAKE_PYTHON:-$LAKE_ROOT/.venv/bin/python}"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON="${PYTHON_BIN:-python3}"
fi
exec "$PYTHON" "$LAKE_ROOT/infra/scripts/data_lake/ingest_discovery_captures.py" "$@"
