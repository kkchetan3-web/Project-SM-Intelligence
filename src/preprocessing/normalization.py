"""Transformations between the representations matka results use.

Three representations of the same draw coexist, and confusing them is the single
easiest way to corrupt an analysis:

``panna``  the 3-digit panel, e.g. ``"128"`` - a fixed-width *string*
``ank``    the single digit, ``digit_sum(panna) % 10`` - an *integer* 0-9
``jodi``   the concatenation ``f"{open_ank}{close_ank}"`` - a fixed-width *string*

``"07"`` is a valid jodi and is not the integer 7. ``"128"`` is not the integer
128. These functions are the only sanctioned conversions, and they preserve
width and type.
"""

from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np
import pandas as pd

from src.core.validation import ValidationError

ANK_SUPPORT: tuple[int, ...] = tuple(range(10))
JODI_SUPPORT: tuple[str, ...] = tuple(f"{i:02d}" for i in range(100))
PANNA_SUPPORT: tuple[str, ...] = tuple(f"{i:03d}" for i in range(1000))


def support_for(space: str) -> tuple:
    if space == "ank":
        return ANK_SUPPORT
    if space == "jodi":
        return JODI_SUPPORT
    if space == "panna":
        return PANNA_SUPPORT
    raise ValidationError(f"unknown outcome space: {space}")


def panna_to_ank(panna: str | int) -> int:
    """Digit-sum-mod-10. Rejects values that are not exactly 3 digits."""
    text = str(panna).strip()
    if len(text) != 3 or not text.isdigit():
        raise ValidationError(f"panna must be a 3-digit string, got {panna!r}")
    return int(sum(int(c) for c in text) % 10)


def anks_to_jodi(open_ank: int, close_ank: int) -> str:
    if not (0 <= int(open_ank) <= 9 and 0 <= int(close_ank) <= 9):
        raise ValidationError(f"ank out of range: {open_ank!r}, {close_ank!r}")
    return f"{int(open_ank)}{int(close_ank)}"


def jodi_to_anks(jodi: str | int) -> tuple[int, int]:
    text = str(jodi).strip().zfill(2)
    if len(text) != 2 or not text.isdigit():
        raise ValidationError(f"jodi must be 2 digits, got {jodi!r}")
    return int(text[0]), int(text[1])


def digits_of(panna: str | int) -> tuple[int, int, int]:
    text = str(panna).strip()
    if len(text) != 3 or not text.isdigit():
        raise ValidationError(f"panna must be 3 digits, got {panna!r}")
    return int(text[0]), int(text[1]), int(text[2])


# ---------------------------------------------------------------------------
# encodings
# ---------------------------------------------------------------------------
def encode_categorical(values: Sequence, support: Sequence) -> np.ndarray:
    """Map labels to 0..K-1 indices, raising on anything unseen."""
    lookup = {str(v): i for i, v in enumerate(support)}
    out = np.empty(len(values), dtype=int)
    for idx, value in enumerate(values):
        key = str(value)
        if key not in lookup:
            raise ValidationError(f"value {value!r} not in declared support")
        out[idx] = lookup[key]
    return out


def one_hot(indices: np.ndarray, k: int) -> np.ndarray:
    out = np.zeros((len(indices), k), dtype=float)
    out[np.arange(len(indices)), np.asarray(indices, dtype=int)] = 1.0
    return out


def numeric_encoding(series: pd.Series, space: str) -> pd.Series:
    """A *meaningful* numeric view of a categorical series.

    For ``ank`` the digit itself is meaningful (0-9 on a line). For ``jodi`` the
    encoded value 0-99 is an arbitrary label and must not be modelled as a
    magnitude - :func:`has_defensible_numeric_representation` says so explicitly,
    and the time-series methods check it before running.
    """
    if space == "ank":
        return pd.to_numeric(series, errors="coerce").astype(float)
    raise ValidationError(
        f"outcome space '{space}' has no defensible numeric representation; "
        "use a categorical method instead"
    )


def has_defensible_numeric_representation(space: str) -> bool:
    """Whether arithmetic on the label means anything at all.

    ``ank``: yes, digits sit on a circle and 7 is 'larger' than 3 in an ordering
    sense, though not in a probabilistic sense - recorded as *weakly* meaningful.
    ``jodi``/``panna``: no. 47 is not more than 12, and 128 is not 128 units of
    anything.
    """
    return space == "ank"


# ---------------------------------------------------------------------------
# digit-level transforms (Category E)
# ---------------------------------------------------------------------------
def digital_root(value: int | str) -> int:
    """Repeated digit sum to a single digit (0 stays 0; 9 -> 9)."""
    total = sum(int(c) for c in str(value))
    while total > 9:
        total = sum(int(c) for c in str(total))
    return total


def digit_sum(value: int | str) -> int:
    return sum(int(c) for c in str(value))


def digit_complement(digit: int) -> int:
    """Decimal complement ``9 - d``."""
    return 9 - int(digit)


def reverse_string(value: str | int) -> str:
    """Reverse a fixed-width sequence, preserving width."""
    return str(value).strip()[::-1]


def hamming_distance(a: str, b: str) -> int:
    """Positional differences between two equal-length strings."""
    if len(a) != len(b):
        raise ValidationError(f"hamming distance needs equal lengths: {a!r} vs {b!r}")
    return sum(1 for x, y in zip(a, b, strict=True) if x != y)


def parity(value: int) -> int:
    return int(value) % 2


def residue(value: int, modulus: int) -> int:
    if modulus <= 0:
        raise ValidationError("modulus must be positive")
    return int(value) % modulus


def digit_sum_series(series: Iterable[str]) -> list[int]:
    return [digit_sum(v) for v in series]


def rot_class(ank: int, modulus: int = 10) -> int:
    """Residue class of the ank - used by the modular-arithmetic methods."""
    return int(ank) % modulus
