# book-discovery-data

Lake-first technology discovery data boundary for discovery.v1.

The canonical remote checkout is currently unavailable, so this path is a
local scaffold that restores the declared product boundary and test command.
The approved producer remains book-job-scraping; this product reads its four
public capture families, archives exact bytes through the shared lake adapter,
and exposes a read-only API over committed Bronze Parquet.

    book-job-scraping captures
      -> exact bytes in landing/
      -> Bronze discovery.v1 Parquet
      -> manifest and lineage
      -> read-only API :8110 / DuckDB

## Run locally

From the Solo Empire root, the task runs the replay from the infra working
directory:

    task scraping:discovery:ingest -- --lake-uri ../data/lake-w5 --json

From this checkout, use an explicit lake path:

    ./scripts/ingest.sh --lake-uri ../../../../../../../../../data/lake-w5 --json
    ./scripts/test.sh

The test runner uses the parent virtualenv on POSIX or Windows/Git Bash.
API contract and capture replay tests run offline with fixtures, without local
exports. Only the optional `book-job-scraping/data/exported` directory check
is skipped with an explicit reason when that directory is absent.

The API reads only the technology_signals and technology_signals_history
Bronze datasets. POST /v1/refresh is disabled by default; collection is an
explicit operator action. When enabled, it only acknowledges (202) a request
whose bearer token matches REFRESH_TOKEN (constant-time comparison); the reply
says `job_started: false` and names the operator command
(`task scraping:discovery:ingest`), because no collection runs from the API.

## Configuration

| Variable | Default | Meaning |
| --- | --- | --- |
| `API_HOST` | `127.0.0.1` | Bind address (loopback by default) |
| `API_PORT` | `8110` | Port, integer 0-65535 |
| `CORS_ALLOWED_ORIGINS` | empty | Comma-separated extra origins; loopback origins are always allowed |
| `STALE_AFTER_HOURS` | `36` | Records older than this report stale (history uses 4x); finite, > 0 |
| `SOLO_EMPIRE_DATA_LAKE_URI` / `DATA_LAKE_URI` | empty | Lake root to read Bronze from |
| `SOLO_EMPIRE_ROOT` | empty | Solo Empire checkout used to locate the shared runtime |
| `LAKE_READ_MODE` | `parquet` | Passed to the shared lake reader |
| `LAKE_READ_FALLBACK` | `error` | Passed to the shared lake reader |
| `ALLOW_REFRESH` / `REFRESH_TOKEN` | off / empty | Enable the acknowledge-only `POST /v1/refresh` |
| `FREE_ONLY`, `ALLOW_PAID_PROVIDERS`, `ALLOW_EXTERNAL_WRITES` | on / off / off | Policy flags reported by `/v1/metadata` |

Invalid `API_PORT` or `STALE_AFTER_HOURS` values stop start-up with a
`ConfigError` naming the variable (blank values use the default).

The shared `data_lake` runtime comes from the `[lake]` extra
(`solo-empire-data-lake`, pinned to a commit) or, inside Solo Empire, from
`SOLO_EMPIRE_ROOT` / the parent directories of this checkout. If it is missing or the lake read
fails, GET endpoints answer `503` with `data_status: "unavailable"` and no
paths or exception text; 404/403/400 responses never need the runtime.

## Standalone checks and CI

Without a Solo Empire checkout (as in `.github/workflows/ci.yml`):

    python -m pip install -e ".[dev,lake]"
    ruff check .
    python -m pytest -q -rs

`tests/test_http_api.py` drives the real HTTP handler on a loopback port with
in-memory store stubs (pagination, single record, CORS, refresh auth, 503).
`tests/test_lake_roundtrip.py` lands Bronze rows into a temporary lake and
reads them back through `load_records`/`get_record`/`load_history`. It and the
item-builder test skip with an explicit reason when the `[lake]` runtime is
absent (install only `.[dev]` for a dependency-free run); `./scripts/test.sh` still runs the full suite plus the
monorepo capture-replay test inside a Solo Empire checkout.

## Contract

The boundary follows the repository's discovery-data-contract-v1.yaml:

- source book-discovery-data, domain discovery, schema discovery.v1;
- approved public captures from GitHub, Hacker News, DEV.to, and Product Hunt;
- attribution and source URLs are retained on every normalized signal;
- malformed or ambiguous capture rows fail closed before any projection;
- consumers use the API or Bronze DuckDB and never read scraper CSVs directly.

This scaffold has no published remote or deployment. Keep task #91 open until
the canonical source is supplied and the checkout receives its normal review,
origin, and release evidence.
