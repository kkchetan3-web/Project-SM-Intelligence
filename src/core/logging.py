"""Centralised logging with a run-correlation id and a file sink."""

from __future__ import annotations

import logging
import logging.handlers
import os
import sys
import uuid
from pathlib import Path

_CONFIGURED = False
RUN_ID = uuid.uuid4().hex[:12]


def configure_logging(level: str | None = None, log_file: str | Path | None = None) -> None:
    """Idempotent logging setup.

    Called by the CLI entrypoint and by the test suite; safe to call repeatedly.
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    level_name = (level or os.environ.get("SM_INTEL_LOG_LEVEL") or "INFO").upper()
    fmt = "%(asctime)s | %(levelname)-7s | %(name)-28s | %(message)s"

    root = logging.getLogger()
    root.setLevel(getattr(logging, level_name, logging.INFO))

    console = logging.StreamHandler(stream=sys.stderr)
    console.setFormatter(logging.Formatter(fmt, datefmt="%H:%M:%S"))
    root.addHandler(console)

    if log_file is None:
        from src.core.configuration import REPO_ROOT

        log_file = REPO_ROOT / "artifacts" / "run.log"
    try:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            path, maxBytes=4_000_000, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(logging.Formatter(fmt))
        root.addHandler(file_handler)
    except OSError:  # pragma: no cover - read-only filesystem fallback
        root.warning("could not open log file %s; continuing with console only", log_file)

    # Third-party noise control.
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)


def banner(logger: logging.Logger, text: str) -> None:
    line = "=" * max(60, len(text) + 8)
    logger.info(line)
    logger.info("  %s", text)
    logger.info(line)
