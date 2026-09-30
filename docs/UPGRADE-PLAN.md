# Upgrade plan — book-discovery-data

Score: 4.5/10 -> 6.5/10 (pass 1) -> 7/10 (pass 2) — before: the only store test crashed with ModuleNotFoundError
outside the monorepo, a lake failure dropped the HTTP connection, and there was no CI.

## Backlog

- P0: Confirm the new GitHub Actions CI is green on the first push.
- P0: Restore the canonical remote (README task #91); this checkout is still a scaffold.
- P1: `/v1/refresh` only acknowledges; either wire it to an explicit operator job or remove it.
- P2: Document the API env vars (`API_HOST`, `API_PORT`, `CORS_ALLOWED_ORIGINS`,
  `STALE_AFTER_HOURS`, `LAKE_READ_MODE`, `LAKE_READ_FALLBACK`) in the README.

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
