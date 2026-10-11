#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LAKE_ROOT="${SOLO_DATA_LAKE_ROOT:-}"
if [[ -z "$LAKE_ROOT" || ! -f "$LAKE_ROOT/infra/scripts/data_lake/ingest_discovery_captures.py" ]]; then
  echo "Set SOLO_DATA_LAKE_ROOT to a solo-data-lake checkout (discovery tests)" >&2
  exit 2
fi

PYTHON="${SOLO_DATA_LAKE_PYTHON:-$LAKE_ROOT/.venv/bin/python}"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON="${SOLO_DATA_LAKE_PYTHON_WIN:-$LAKE_ROOT/.venv/Scripts/python.exe}"
fi
if [[ ! -x "$PYTHON" ]]; then
  PYTHON="${PYTHON_BIN:-python3}"
fi
PYTHONPATH_SEPARATOR="$("$PYTHON" -c 'import os; print(os.pathsep)')"
SOURCE_PATH="$REPO_ROOT/src"
INFRA_PATH="$LAKE_ROOT/infra/scripts"
if [[ "$PYTHONPATH_SEPARATOR" == ";" ]]; then
  SOURCE_PATH="$(cygpath -w "$SOURCE_PATH")"
  INFRA_PATH="$(cygpath -w "$INFRA_PATH")"
fi
export PYTHONPATH="$SOURCE_PATH${PYTHONPATH_SEPARATOR}$INFRA_PATH${PYTHONPATH:+${PYTHONPATH_SEPARATOR}$PYTHONPATH}"

"$PYTHON" -m unittest discover -s "$REPO_ROOT/tests" -p 'test_*.py' -v
"$PYTHON" "$LAKE_ROOT/infra/tests/data_lake/discovery_capture_ingest_test.py"
