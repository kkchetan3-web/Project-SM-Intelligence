"""Typed, validated access to the YAML configuration tree.

Design notes
------------
* Configuration is resolved **once** into frozen dataclasses so that no code path
  can silently mutate experiment settings mid-run.
* Every config file is hashed; the hash is written into ``extraction_runs`` and
  ``method_results`` so any reported number can be tied to the exact settings
  that produced it.
* The *dataset root* is a first-class concept. Synthetic control data and real
  market data live in different directory trees, and the resolved
  :class:`Config` refuses to mix them.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "config"

LIVE_DATASET = "live"


class ConfigurationError(RuntimeError):
    """Raised when configuration is missing, malformed, or internally inconsistent."""


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ConfigurationError(f"missing config file: {path}")
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:  # pragma: no cover - defensive
        raise ConfigurationError(f"invalid YAML in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigurationError(f"config file {path} must contain a mapping at top level")
    return data


def file_hash(path: Path) -> str:
    """Stable content hash used for provenance stamping."""
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]


def config_hashes() -> dict[str, str]:
    return {p.name: file_hash(p) for p in sorted(CONFIG_DIR.glob("*.yaml"))}


# ---------------------------------------------------------------------------
# dataclasses
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class TargetSpec:
    name: str
    field: str
    space: str


@dataclass(frozen=True)
class MarketSpec:
    market_id: str
    display_name: str
    status: str
    components: tuple[str, ...]
    targets: dict[str, TargetSpec]
    primary_source: str
    secondary_sources: tuple[str, ...]
    publication_order: tuple[str, ...]
    outcomes: dict[str, Any]
    timezone: str
    draw_frequency: str
    notes: str = ""

    def target(self, name: str) -> TargetSpec:
        if name not in self.targets:
            available = ", ".join(sorted(self.targets))
            raise ConfigurationError(
                f"market '{self.market_id}' has no target '{name}' (available: {available})"
            )
        return self.targets[name]


@dataclass(frozen=True)
class SourceSpec:
    source_id: str
    market_id: str | None
    authority: int
    kind: str
    base_url: str
    pages: dict[str, str]
    expected_format: str
    parser: str
    notes: str = ""


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    root: Path
    description: str

    @property
    def is_live(self) -> bool:
        return self.name == LIVE_DATASET


@dataclass(frozen=True)
class HttpSpec:
    user_agent: str
    timeout_seconds: float
    max_retries: int
    backoff_base_seconds: float
    backoff_max_seconds: float
    min_delay_seconds: float
    respect_robots_txt: bool
    max_pages_per_run: int
    max_consecutive_failures: int


@dataclass(frozen=True)
class Config:
    """Fully resolved, immutable configuration for one process."""

    project: dict[str, Any]
    paths: dict[str, Path]
    dataset: DatasetSpec
    markets: dict[str, MarketSpec]
    market_order: tuple[str, ...]
    cross_market_pairs: tuple[tuple[str, str], ...]
    sources: dict[str, SourceSpec]
    http: HttpSpec
    research: dict[str, Any]
    #: Declared publication precedence: [[a, b]] means market a's Open is
    #: published before market b's Close. Empty tuple = channel switched off.
    cross_open_precedence: tuple[tuple[str, str], ...] = ()
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    # -- convenience -------------------------------------------------------
    def market(self, market_id: str) -> MarketSpec:
        key = market_id.strip().lower().replace("-", "_").replace(" ", "_")
        if key not in self.markets:
            known = ", ".join(self.market_order)
            raise ConfigurationError(f"unknown market '{market_id}' (configured: {known})")
        return self.markets[key]

    def seed(self) -> int:
        return int(self.research.get("random_seed", 20250101))

    def database_path(self, market_id: str) -> Path:
        market = self.market(market_id)
        return self.dataset.root / market.market_id / f"{market.market_id}.db"

    def raw_dir(self, market_id: str) -> Path:
        market = self.market(market_id)
        return self.paths["raw_root"] / self.dataset.name / market.market_id

    def processed_dir(self, market_id: str) -> Path:
        market = self.market(market_id)
        return self.paths["processed_root"] / self.dataset.name / market.market_id

    def research_dir(self, kind: str) -> Path:
        return self.paths["research_root"] / kind

    def fingerprint(self) -> str:
        payload = json.dumps(
            {
                "dataset": self.dataset.name,
                "hashes": config_hashes(),
                "code_version": self.project.get("code_version"),
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------
def load_config(
    config_dir: Path | str | None = None,
    dataset: str = LIVE_DATASET,
    database_root: str | Path | None = None,
) -> Config:
    """Load and validate the whole configuration tree.

    Parameters
    ----------
    dataset:
        Which surrogate tree to operate on: ``live``, ``synthetic_null`` or
        ``synthetic_signal``. Synthetic runs are configured to be impossible to
        mistake for live results (their rows carry a distinct verification
        status and their reports are watermarked).
    database_root:
        Optional override of the database directory (used by tests).
    """
    cdir = Path(config_dir) if config_dir is not None else CONFIG_DIR

    project_cfg = _read_yaml(cdir / "project.yaml")
    markets_cfg = _read_yaml(cdir / "markets.yaml")
    sources_cfg = _read_yaml(cdir / "sources.yaml")
    research_cfg = _read_yaml(cdir / "research.yaml")

    paths = {k: REPO_ROOT / v for k, v in project_cfg.get("paths", {}).items()}

    dataset_defs = project_cfg.get("databases", {}).get("datasets", {})
    if dataset not in dataset_defs:
        raise ConfigurationError(
            f"unknown dataset '{dataset}'; configure it under databases.datasets "
            f"(known: {', '.join(dataset_defs)})"
        )
    if database_root is not None:
        root = Path(database_root).expanduser().resolve()
    else:
        root = REPO_ROOT / dataset_defs[dataset]["root"]
    dataset_spec = DatasetSpec(
        name=dataset,
        root=root,
        description=dataset_defs[dataset].get("description", ""),
    )

    defaults = markets_cfg.get("defaults", {})
    markets: dict[str, MarketSpec] = {}
    order: list[str] = []
    for entry in markets_cfg.get("markets", []):
        mid = entry["market_id"].strip().lower()
        if mid in markets:
            raise ConfigurationError(f"duplicate market_id '{mid}' in markets.yaml")
        targets = {
            name: TargetSpec(name=name, field=spec["field"], space=spec["space"])
            for name, spec in entry.get("targets", {}).items()
        }
        if not targets:
            raise ConfigurationError(f"market '{mid}' declares no targets")
        for tname, tspec in targets.items():
            if tspec.space not in defaults.get("outcomes", {}):
                raise ConfigurationError(
                    f"market '{mid}' target '{tname}' references unknown outcome space '{tspec.space}'"
                )
        markets[mid] = MarketSpec(
            market_id=mid,
            display_name=entry.get("display_name", mid.title()),
            status=entry.get("status", "configured"),
            components=tuple(entry.get("components", [])),
            targets=targets,
            primary_source=entry.get("primary_source", ""),
            secondary_sources=tuple(entry.get("secondary_sources", [])),
            publication_order=tuple(defaults.get("publication_order", ["open", "close"])),
            outcomes=defaults.get("outcomes", {}),
            timezone=defaults.get("timezone", "Asia/Kolkata"),
            draw_frequency=defaults.get("draw_frequency", "daily"),
            notes=entry.get("notes", ""),
        )
        order.append(mid)

    if not markets:
        raise ConfigurationError("no markets configured")

    pairs: list[tuple[str, str]] = []
    for pair in markets_cfg.get("cross_market_pairs", []):
        if len(pair) != 2:
            raise ConfigurationError(f"cross_market_pairs entries must be 2-element lists, got {pair!r}")
        a, b = (p.strip().lower() for p in pair)
        if a not in markets or b not in markets:
            raise ConfigurationError(f"cross_market_pairs references unknown market in {pair!r}")
        if a == b:
            raise ConfigurationError(f"cross_market_pairs cannot pair a market with itself: {pair!r}")
        pairs.append((a, b))

    precedence: list[tuple[str, str]] = []
    for entry in markets_cfg.get("cross_open_precedence", []) or []:
        if len(entry) != 2:
            raise ConfigurationError(
                f"cross_open_precedence entries must be 2-element lists, got {entry!r}")
        a, b = (p.strip().lower() for p in entry)
        if a not in markets or b not in markets:
            raise ConfigurationError(f"cross_open_precedence references unknown market in {entry!r}")
        if a == b:
            raise ConfigurationError("cross_open_precedence cannot state that a market precedes itself")
        precedence.append((a, b))

    http_cfg = sources_cfg.get("http", {})
    http = HttpSpec(
        user_agent=http_cfg.get(
            "user_agent", "sm-intel-research/0.3 (+academic reproducibility)"
        ),
        timeout_seconds=float(http_cfg.get("timeout_seconds", 20)),
        max_retries=int(http_cfg.get("max_retries", 3)),
        backoff_base_seconds=float(http_cfg.get("backoff_base_seconds", 1.5)),
        backoff_max_seconds=float(http_cfg.get("backoff_max_seconds", 30)),
        min_delay_seconds=float(http_cfg.get("min_delay_seconds", 1.2)),
        respect_robots_txt=bool(http_cfg.get("respect_robots_txt", True)),
        max_pages_per_run=int(http_cfg.get("max_pages_per_run", 5000)),
        max_consecutive_failures=int(http_cfg.get("max_consecutive_failures", 8)),
    )

    sources: dict[str, SourceSpec] = {}
    for entry in sources_cfg.get("sources", []):
        sid = entry["source_id"]
        sources[sid] = SourceSpec(
            source_id=sid,
            market_id=entry.get("market_id"),
            authority=int(entry.get("authority", 5)),
            kind=entry.get("kind", "secondary"),
            base_url=entry.get("base_url", ""),
            pages=dict(entry.get("pages", {})),
            expected_format=entry.get("expected_format", "html"),
            parser=entry.get("parser", "default"),
            notes=entry.get("notes", ""),
        )

    for market in markets.values():
        if market.primary_source and market.primary_source not in sources:
            raise ConfigurationError(
                f"market '{market.market_id}' references unregistered primary_source "
                f"'{market.primary_source}'"
            )

    # environment overrides
    if os.environ.get("SM_INTEL_DATABASE_ROOT") and database_root is None:
        dataset_spec = DatasetSpec(
            name=dataset,
            root=Path(os.environ["SM_INTEL_DATABASE_ROOT"]).expanduser().resolve(),
            description=dataset_spec.description,
        )

    return Config(
        project=project_cfg,
        paths={**paths, "database_root": dataset_spec.root},
        dataset=dataset_spec,
        markets=markets,
        market_order=tuple(order),
        cross_market_pairs=tuple(pairs),
        cross_open_precedence=tuple(precedence),
        sources=sources,
        http=http,
        research=research_cfg,
        raw={"projects": project_cfg, "markets": markets_cfg, "sources": sources_cfg},
    )


@lru_cache(maxsize=8)
def get_config(dataset: str = LIVE_DATASET) -> Config:
    """Cached configuration accessor for call sites that do not need overrides."""
    return load_config(dataset=dataset)


def normalise_market_id(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")
