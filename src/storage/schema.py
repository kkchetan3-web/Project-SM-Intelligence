"""Physical schema for a per-market database.

Every market gets its own SQLite file and its own copy of this schema. There is
deliberately **no** shared "all markets" table: a record always belongs to
exactly one market file, which makes cross-market contamination a schema error
rather than a subtle analytical bias.

The schema is versioned. :func:`MIGRATIONS` is an ordered list of
``(version, description, sql)`` tuples; :mod:`src.storage.migrations` applies
the ones a given file has not yet seen.
"""

from __future__ import annotations

SCHEMA_VERSION = 3

# ---------------------------------------------------------------------------
# v1 - core record keeping
# ---------------------------------------------------------------------------
_V1 = """
CREATE TABLE IF NOT EXISTS historical_results (
    record_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    market_id            TEXT    NOT NULL,
    result_date          TEXT    NOT NULL,              -- ISO 'YYYY-MM-DD'
    open_panna           TEXT,                          -- fixed-width 3-char string
    open_ank             INTEGER,                       -- 0..9
    close_panna          TEXT,
    close_ank            INTEGER,
    jodi                 TEXT,                          -- fixed-width 2-char string
    source_id            TEXT    NOT NULL,
    source_url           TEXT,
    source_timestamp     TEXT,
    extraction_timestamp TEXT    NOT NULL,
    verification_status  TEXT    NOT NULL,
    dataset              TEXT    NOT NULL,
    raw_payload          TEXT,                          -- verbatim source snippet / JSON
    record_version       INTEGER NOT NULL DEFAULT 1,
    is_active            INTEGER NOT NULL DEFAULT 1,    -- 0 = superseded, kept for audit
    notes                TEXT,
    CHECK (open_ank  IS NULL OR (open_ank  BETWEEN 0 AND 9)),
    CHECK (close_ank IS NULL OR (close_ank IS NULL OR close_ank BETWEEN 0 AND 9)),
    CHECK (length(jodi) = 2 OR jodi IS NULL),
    CHECK (length(open_panna) = 3 OR open_panna IS NULL),
    CHECK (length(close_panna) = 3 OR close_panna IS NULL)
);

-- One active row per (market, date). Revisions deactivate the old row and
-- insert a new one, so history is never destroyed.
CREATE UNIQUE INDEX IF NOT EXISTS ux_results_market_date_active
    ON historical_results (market_id, result_date) WHERE is_active = 1;
CREATE INDEX IF NOT EXISTS ix_results_date ON historical_results (result_date);
CREATE INDEX IF NOT EXISTS ix_results_market ON historical_results (market_id);

CREATE TABLE IF NOT EXISTS result_revisions (
    revision_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id    INTEGER NOT NULL,
    field_name   TEXT    NOT NULL,
    old_value    TEXT,
    new_value    TEXT,
    observed_at  TEXT    NOT NULL,
    source_id    TEXT,
    source_url   TEXT,
    reason       TEXT,
    FOREIGN KEY (record_id) REFERENCES historical_results (record_id)
);
CREATE INDEX IF NOT EXISTS ix_revisions_record ON result_revisions (record_id);

CREATE TABLE IF NOT EXISTS extraction_runs (
    run_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    market_id          TEXT,
    source_id          TEXT,
    started_at         TEXT NOT NULL,
    finished_at        TEXT,
    status             TEXT NOT NULL DEFAULT 'running',
    pages_requested    INTEGER DEFAULT 0,
    pages_ok           INTEGER DEFAULT 0,
    pages_failed       INTEGER DEFAULT 0,
    records_seen       INTEGER DEFAULT 0,
    records_inserted   INTEGER DEFAULT 0,
    records_revised    INTEGER DEFAULT 0,
    error_text         TEXT,
    config_fingerprint TEXT
);
CREATE INDEX IF NOT EXISTS ix_runs_started ON extraction_runs (started_at);

CREATE TABLE IF NOT EXISTS source_records (
    source_record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id           INTEGER,
    source_id        TEXT NOT NULL,
    market_id        TEXT,
    url              TEXT NOT NULL,
    fetched_at       TEXT NOT NULL,
    http_status      INTEGER,
    content_hash     TEXT,
    byte_size        INTEGER,
    parse_status     TEXT DEFAULT 'pending',
    raw_path         TEXT,
    notes            TEXT,
    FOREIGN KEY (run_id) REFERENCES extraction_runs (run_id)
);
CREATE INDEX IF NOT EXISTS ix_source_records_url ON source_records (url);

CREATE TABLE IF NOT EXISTS data_quality (
    check_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id       INTEGER,
    market_id    TEXT NOT NULL,
    check_name   TEXT NOT NULL,
    severity     TEXT NOT NULL,
    passed       INTEGER NOT NULL,
    metric_name  TEXT,
    metric_value TEXT,
    detail       TEXT,
    created_at   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_quality_market ON data_quality (market_id, check_name);
"""

# ---------------------------------------------------------------------------
# v2 - analytics
# ---------------------------------------------------------------------------
_V2 = """
CREATE TABLE IF NOT EXISTS market_features (
    feature_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    market_id       TEXT NOT NULL,
    result_date     TEXT NOT NULL,
    target          TEXT NOT NULL,          -- 'open' | 'close'
    feature_name    TEXT NOT NULL,
    feature_value   REAL,
    feature_version TEXT NOT NULL,
    computed_at     TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_features
    ON market_features (market_id, result_date, target, feature_name, feature_version);

CREATE TABLE IF NOT EXISTS method_results (
    result_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    method_id     TEXT NOT NULL,            -- 'M001' .. 'M100'
    method_name   TEXT NOT NULL,
    category      TEXT NOT NULL,
    market_id     TEXT,
    target        TEXT,                     -- 'open' | 'close' | 'jodi' | NULL
    scope         TEXT NOT NULL,            -- 'full_sample' | 'walk_forward' | 'theoretical'
    metric_name   TEXT NOT NULL,
    metric_value  REAL,
    statistic     REAL,
    p_value       REAL,
    p_adjusted    REAL,
    effect_size   REAL,
    sample_size   INTEGER,
    extra_json    TEXT,
    run_id        TEXT,
    computed_at   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_method_results_method ON method_results (method_id, market_id, target);

CREATE TABLE IF NOT EXISTS model_registry (
    model_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    market_id      TEXT NOT NULL,
    target         TEXT NOT NULL,
    model_name     TEXT NOT NULL,
    model_version  TEXT NOT NULL,
    config_json    TEXT,
    feature_version TEXT,
    trained_from   TEXT,
    trained_to     TEXT,
    train_size     INTEGER,
    metrics_json   TEXT,
    is_selected    INTEGER NOT NULL DEFAULT 0,
    artifact_path  TEXT,
    created_at     TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_models_lookup ON model_registry (market_id, target, is_selected);

CREATE TABLE IF NOT EXISTS backtest_results (
    backtest_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id      INTEGER,
    market_id     TEXT NOT NULL,
    target        TEXT NOT NULL,
    scheme        TEXT NOT NULL,
    test_start    TEXT,
    test_end      TEXT,
    n_predictions INTEGER,
    log_loss      REAL,
    brier         REAL,
    accuracy      REAL,
    top3          REAL,
    top5          REAL,
    calibration_json TEXT,
    baseline_json TEXT,
    metrics_json  TEXT,
    created_at    TEXT NOT NULL,
    FOREIGN KEY (model_id) REFERENCES model_registry (model_id)
);

CREATE TABLE IF NOT EXISTS predictions (
    prediction_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    market_id       TEXT NOT NULL,
    target          TEXT NOT NULL,
    target_date     TEXT NOT NULL,
    model_id        INTEGER,
    model_version   TEXT NOT NULL,
    cutoff_date     TEXT,
    train_size      INTEGER,
    feature_version TEXT,
    prob_json       TEXT NOT NULL,          -- {outcome: probability}, sums to 1
    ranked_json     TEXT NOT NULL,
    created_at      TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_predictions
    ON predictions (market_id, target, target_date, model_version);

CREATE TABLE IF NOT EXISTS prediction_outcomes (
    outcome_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    prediction_id INTEGER NOT NULL,
    actual_value  TEXT NOT NULL,
    correct_exact INTEGER NOT NULL,
    rank_of_actual INTEGER,
    log_loss_i    REAL,
    brier_i       REAL,
    resolved_at   TEXT NOT NULL,
    FOREIGN KEY (prediction_id) REFERENCES predictions (prediction_id)
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_outcomes_pred ON prediction_outcomes (prediction_id);
"""

# ---------------------------------------------------------------------------
# v3 - cross-market layer
# ---------------------------------------------------------------------------
_V3 = """
CREATE TABLE IF NOT EXISTS cross_market_features (
    xfeature_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    target_market  TEXT NOT NULL,
    target         TEXT NOT NULL,
    source_market  TEXT NOT NULL,
    source_component TEXT NOT NULL,
    lag            INTEGER NOT NULL,
    target_date    TEXT NOT NULL,
    value_json     TEXT,
    available_at   TEXT NOT NULL,           -- publication time actually used
    feature_version TEXT NOT NULL,
    computed_at    TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_xfeatures
    ON cross_market_features (target_market, target, source_market, source_component,
                              lag, target_date, feature_version);

CREATE TABLE IF NOT EXISTS cross_market_tests (
    xtest_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    market_a     TEXT NOT NULL,
    market_b     TEXT NOT NULL,
    component_a  TEXT NOT NULL,
    component_b  TEXT NOT NULL,
    lag          INTEGER NOT NULL,
    method       TEXT NOT NULL,
    statistic    REAL,
    p_value      REAL,
    p_adjusted   REAL,
    effect_size  REAL,
    n_obs        INTEGER,
    stability    REAL,
    verdict      TEXT,
    extra_json   TEXT,
    created_at   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_xtests_pair ON cross_market_tests (market_a, market_b);

CREATE TABLE IF NOT EXISTS update_history (
    update_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    market_id       TEXT NOT NULL,
    run_type        TEXT NOT NULL,
    started_at      TEXT NOT NULL,
    finished_at     TEXT,
    status          TEXT NOT NULL,
    new_records     INTEGER DEFAULT 0,
    revised_records INTEGER DEFAULT 0,
    new_watermark   TEXT,
    error_text      TEXT
);
"""

MIGRATIONS: list[tuple[int, str, str]] = [
    (1, "core record keeping: results, revisions, sources, extraction runs, quality", _V1),
    (2, "analytics: features, method results, model registry, backtests, prediction ledger", _V2),
    (3, "cross-market layer and incremental update history", _V3),
]

# Convenience views built after migrations.
VIEWS = """
DROP VIEW IF EXISTS v_results_clean;
CREATE VIEW v_results_clean AS
SELECT market_id, result_date, open_panna, open_ank, close_panna, close_ank, jodi,
       source_id, source_url, extraction_timestamp, verification_status, dataset,
       record_id
  FROM historical_results
 WHERE is_active = 1
 ORDER BY result_date;

DROP VIEW IF EXISTS v_latest_result;
CREATE VIEW v_latest_result AS
SELECT * FROM v_results_clean
 WHERE result_date = (SELECT MAX(result_date) FROM v_results_clean);
"""

REQUIRED_TABLES = [
    "historical_results",
    "source_records",
    "extraction_runs",
    "data_quality",
    "market_features",
    "method_results",
    "model_registry",
    "backtest_results",
    "predictions",
    "prediction_outcomes",
    "cross_market_features",
    "cross_market_tests",
    "result_revisions",
    "update_history",
    "database_migrations",
]
