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
explicit operator action.

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
