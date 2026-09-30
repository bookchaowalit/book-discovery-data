# Upgrade plan — book-discovery-data

Score: 4.5/10 -> 6.5/10 (pass 1) -> 7/10 (pass 2) -> 7.5/10 (pass 3) — before: the only store test crashed with ModuleNotFoundError
outside the monorepo, a lake failure dropped the HTTP connection, and there was no CI.

## Backlog

- P0: Confirm the new GitHub Actions CI is green on the first push.
- P0: Restore the canonical remote (README task #91); this checkout is still a scaffold.
- P1 (cross-repo decision): `/v1/refresh` is acknowledge-only in every `book-*-data` API and
  the portfolio contract fixes it at 403-by-default. Wiring a real job (single-flight
  subprocess of `scripts/ingest.sh` with timeout + `GET` status) should be decided once for
  the whole portfolio; the reply is now truthful (`job_started: false`) meanwhile.
- P2: Validate `LAKE_READ_MODE` / `LAKE_READ_FALLBACK` once the shared lake runtime
  publishes its accepted values (it does not validate them today).

## Done in this pass (pass 1)

- Store: clear `SharedRuntimeUnavailable` instead of a bare ImportError; honours
  `SOLO_EMPIRE_ROOT` (already used for the lake contract) before parent-directory search.
- API: GET failures return JSON 503 without leaking lake paths; 400/403/404/202 envelopes no
  longer require the shared runtime (POST /v1/refresh used to crash without it); refresh token
  compared with `hmac.compare_digest` and scheme parsed case-insensitively.
- API: `/v1/records/{id}` was URL-decoded here and again by the shared store, so ids
  containing `%` resolved to a different record; the raw segment is now passed through.
- Tests: new offline `tests/test_http_api.py` (13 tests over a loopback server); replaced the
  source-text grep for `data_status="forbidden"` with a behavioural 403 test; runtime-only test
  skips with a reason.
- CI: `.github/workflows/ci.yml` (Python 3.11/3.12, ruff + pytest), explicit ruff rules; lint fixed.

## Done in this pass (pass 2)

- `[lake]` extra pins `solo-empire-data-lake[lake]` (commit `3523a62`); it covers every
  helper `store.py` imports (`product_store.*`, `product_adapter.LakeProductContract`).
  Added `[build-system]`, src package discovery and a `dev` extra.
- New `store.shared_runtime_available()` and `tests/test_lake_roundtrip.py` (3 tests):
  `ingest_to_lake` into a temp lake, then `load_records`/`get_record`/`load_history`
  end to end (replaces the "committed Parquet fixture" P1 item).
- CI installs `.[dev,lake]`, asserts the runtime imports and runs the lake tests.
  Verified locally: 18 passed/1 optional skip with the package, 14 passed/5 skips without.

## Done in this pass (pass 3)

- Config: `API_PORT` (0-65535) and `STALE_AFTER_HOURS` (finite, > 0) are validated at import
  and raise `ConfigError` naming the variable; before, `API_PORT=80a` was a bare traceback and
  `STALE_AFTER_HOURS=nan`/`0`/negative silently broke staleness. Blank values use defaults.
- `POST /v1/refresh` 202 reply states `job_started: false` and the operator command, instead
  of implying collection ran (contract 403-by-default unchanged).
- README: configuration table for every environment variable the API reads.
- New `tests/test_config.py` (4 tests, 8 subtests); refresh test asserts the truthful reply.
  22 passed / 1 optional skip; ruff 0.15.8 and 0.16.9 clean.
- `attribution_required` failed open: `bool(payload.get(...))` read an empty
  CSV cell as False (attribution dropped) and the string "False" as True. New
  `store._attribution_required` keeps attribution unless the value is an
  explicit false (`False`, "false", "0", "no", "off"). Two regression tests.
- Bumped the `[lake]` pin `3523a62` -> `4c24c66` (NDJSON/BOM/U+2028/double-decode fixes); 24 passed / 1 optional skip with the new package; ruff 0.15.8 + 0.16.9 clean.
