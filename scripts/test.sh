#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EMPIRE_ROOT="$REPO_ROOT"
while [[ "$EMPIRE_ROOT" != "/" && ! -f "$EMPIRE_ROOT/infra/scripts/data_lake/ingest_discovery_captures.py" ]]; do
  EMPIRE_ROOT="$(dirname "$EMPIRE_ROOT")"
done
if [[ ! -f "$EMPIRE_ROOT/infra/scripts/data_lake/ingest_discovery_captures.py" ]]; then
  echo "Solo Empire checkout not found for discovery tests" >&2
  exit 2
fi

PYTHON="${SOLO_EMPIRE_PYTHON:-$EMPIRE_ROOT/.venv/bin/python}"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON="${PYTHON_BIN:-python3}"
fi
export PYTHONPATH="$REPO_ROOT/src:$EMPIRE_ROOT/infra/scripts:${PYTHONPATH:-}"

"$PYTHON" -m unittest discover -s "$REPO_ROOT/tests" -p 'test_*.py' -v
"$PYTHON" "$EMPIRE_ROOT/infra/tests/data_lake/discovery_capture_ingest_test.py"
