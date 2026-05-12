"""Natural-language date parser."""

import re
from datetime import date, timedelta

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
    "mon": 0,
    "tue": 1,
    "wed": 2,
    "thu": 3,
    "fri": 4,
    "sat": 5,
    "sun": 6,
}

MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

WORD_TO_INT: dict[str, int] = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "a": 1,
    "an": 1,
}


def _resolve_number(token: str) -> int:
    """Parse a numeric token that may be a digit string or an English word."""
    token = token.lower().strip()
    if token in WORD_TO_INT:
        return WORD_TO_INT[token]
    return int(token)


def _resolve_anchor(anchor: str, today: date) -> date:
    """Turn an anchor keyword (today/tomorrow/yesterday) into a date."""
    anchor = anchor.lower().strip()
    if anchor in ("today", "now"):
        return today
    if anchor == "tomorrow":
        return today + timedelta(days=1)
    if anchor == "yesterday":
        return today - timedelta(days=1)
    raise ValueError(f"Unknown anchor: {anchor!r}")


def _apply_delta(base: date, amount: int, unit: str, direction: int) -> date:
    """
    Add or subtract a calendar delta.

    direction: +1 = forward (after/from), -1 = backward (before/ago)
    """
    unit = unit.rstrip("s").lower()  # normalise plural

    if unit == "day":
        return base + timedelta(days=direction * amount)
    if unit == "week":
        return base + timedelta(weeks=direction * amount)
    if unit == "month":
        month = base.month + direction * amount
        year = base.year + (month - 1) // 12
        month = (month - 1) % 12 + 1
        day = min(base.day, _days_in_month(year, month))
        return date(year, month, day)
    if unit == "year":
        year = base.year + direction * amount
        day = min(base.day, _days_in_month(year, base.month))
        return date(year, base.month, day)
    raise ValueError(f"Unknown unit: {unit!r}")


def _days_in_month(year: int, month: int) -> int:
    """Return the number of days in a given month."""
    if month == 12:
        return (date(year + 1, 1, 1) - date(year, 12, 1)).days
    return (date(year, month + 1, 1) - date(year, month, 1)).days


# ---------------------------------------------------------------------------
# Sub-parsers — each returns a date or None
# ---------------------------------------------------------------------------

_ANCHOR_RE = re.compile(r"^(today|tomorrow|yesterday|now)$", re.I)

_ISO_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")

# "December 1st, 2025" / "1 December 2025" / "Dec 1 2025"
_NAMED_DATE_RE = re.compile(
    r"^(?:(\d{1,2})(?:st|nd|rd|th)?\s+)?([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?(?:,?\s+(\d{4}))?$"
    r"|^([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?(?:,?\s+(\d{4}))?$",
    re.I,
)

# Compiled separately for clarity
_NAMED_DATE1_RE = re.compile(
    r"^(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)(?:,?\s+(\d{4}))?$", re.I
)
_NAMED_DATE2_RE = re.compile(
    r"^([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?(?:,?\s+(\d{4}))?$", re.I
)

# "next Tuesday" / "last Friday" / "this Wednesday"
_RELATIVE_WEEKDAY_RE = re.compile(r"^(next|last|this)\s+([a-z]+)$", re.I)

# "in 3 days" / "in two weeks"
_IN_N_UNITS_RE = re.compile(r"^in\s+(\w+)\s+(days?|weeks?|months?|years?)$", re.I)

# "3 days ago" / "two weeks ago"
_N_UNITS_AGO_RE = re.compile(r"^(\w+)\s+(days?|weeks?|months?|years?)\s+ago$", re.I)

# "3 days from now/today/tomorrow/yesterday"
_N_UNITS_FROM_RE = re.compile(
    r"^(\w+)\s+(days?|weeks?|months?|years?)"
    r"\s+from\s+(today|tomorrow|yesterday|now)$",
    re.I,
)

# --- compound: "X and Y <direction> <anchor>" ---------------------------------
# e.g. "1 year and 2 months after yesterday"
_COMPOUND_RE = re.compile(
    r"^(\w+)\s+(days?|weeks?|months?|years?)"
    r"(?:\s+and\s+(\w+)\s+(days?|weeks?|months?|years?))*"
    r"\s+(before|after|from)\s+(.+)$",
    re.I,
)

# "5 days before December 1st, 2025" / "3 weeks after tomorrow"
_OFFSET_FROM_DATE_RE = re.compile(
    r"^(\w+)\s+(days?|weeks?|months?|years?)\s+(before|after|from)\s+(.+)$", re.I
)

# "next/last week/month/year"
_RELATIVE_PERIOD_RE = re.compile(r"^(next|last|this)\s+(week|month|year)$", re.I)


def _try_anchor(s: str, today: date) -> date | None:
    if _ANCHOR_RE.match(s):
        return _resolve_anchor(s, today)
    return None


def _try_iso(s: str, _today: date) -> date | None:
    m = _ISO_RE.match(s)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None


def _try_named_date(s: str, today: date) -> date | None:
    """Match 'December 1st, 2025', 'Jan 5 2024', '1 December 2025', etc."""
    # Day-first: "1 December 2025"
    m = _NAMED_DATE1_RE.match(s)
    if m:
        day, month_str, year_str = m.group(1), m.group(2), m.group(3)
        month = MONTHS.get(month_str.lower())
        if month:
            year = int(year_str) if year_str else today.year
            return date(year, month, int(day))

    # Month-first: "December 1st, 2025" or "Dec 1 2025"
    m = _NAMED_DATE2_RE.match(s)
    if m:
        month_str, day, year_str = m.group(1), m.group(2), m.group(3)
        month = MONTHS.get(month_str.lower())
        if month:
            year = int(year_str) if year_str else today.year
            return date(year, month, int(day))

    return None


def _try_relative_weekday(s: str, today: date) -> date | None:
    m = _RELATIVE_WEEKDAY_RE.match(s)
    if not m:
        return None
    qualifier, day_name = m.group(1).lower(), m.group(2).lower()
    target_wd = WEEKDAYS.get(day_name)
    if target_wd is None:
        return None

    current_wd = today.weekday()
    if qualifier == "next":
        delta = (target_wd - current_wd) % 7
        delta = delta if delta != 0 else 7
        return today + timedelta(days=delta)
    if qualifier == "last":
        delta = (current_wd - target_wd) % 7
        delta = delta if delta != 0 else 7
        return today - timedelta(days=delta)
    if qualifier == "this":
        delta = (target_wd - current_wd) % 7
        return today + timedelta(days=delta)
    return None


def _try_relative_period(s: str, today: date) -> date | None:
    m = _RELATIVE_PERIOD_RE.match(s)
    if not m:
        return None
    qualifier, period = m.group(1).lower(), m.group(2).lower()
    direction = 1 if qualifier == "next" else (-1 if qualifier == "last" else 0)
    if period == "week":
        return today + timedelta(weeks=direction)
    if period == "month":
        return _apply_delta(today, 1, "month", direction)
    if period == "year":
        return _apply_delta(today, 1, "year", direction)
    return None


def _try_in_n_units(s: str, today: date) -> date | None:
    m = _IN_N_UNITS_RE.match(s)
    if not m:
        return None
    amount = _resolve_number(m.group(1))
    unit = m.group(2)
    return _apply_delta(today, amount, unit, +1)


def _try_n_units_ago(s: str, today: date) -> date | None:
    m = _N_UNITS_AGO_RE.match(s)
    if not m:
        return None
    amount = _resolve_number(m.group(1))
    unit = m.group(2)
    return _apply_delta(today, amount, unit, -1)


def _try_n_units_from(s: str, today: date) -> date | None:
    m = _N_UNITS_FROM_RE.match(s)
    if not m:
        return None
    amount = _resolve_number(m.group(1))
    unit = m.group(2)
    anchor = _resolve_anchor(m.group(3), today)
    return _apply_delta(anchor, amount, unit, +1)


def _try_offset_from_date(s: str, today: date) -> date | None:
    """
    Handle: "<n> <unit> before|after|from <date_expression>"
    Also handles compound offsets like "1 year and 2 months after yesterday".
    """
    # First try compound form: "1 year and 2 months after yesterday"
    compound_re = re.compile(
        r"^((?:\w+\s+(?:days?|weeks?|months?|years?)(?:\s+and\s+)?)+)\s+(before|after|from)\s+(.+)$",
        re.I,
    )
    mc = compound_re.match(s)
    if mc:
        offset_part = mc.group(1).strip()
        direction_str = mc.group(2).lower()
        anchor_str = mc.group(3).strip()
        direction = -1 if direction_str == "before" else +1

        # Parse anchor
        anchor = _parse_inner(anchor_str, today)
        if anchor is None:
            return None

        # Parse offset_part: "1 year and 2 months" or "5 days"
        token_re = re.compile(r"(\w+)\s+(days?|weeks?|months?|years?)", re.I)
        tokens = token_re.findall(offset_part)
        if not tokens:
            return None
        result = anchor
        for amount_str, unit in tokens:
            amount = _resolve_number(amount_str)
            result = _apply_delta(result, amount, unit, direction)
        return result

    return None


def _parse_inner(s: str, today: date) -> date | None:
    """Try all sub-parsers on a (possibly sub-) expression."""
    s = s.strip()
    for fn in (
        _try_anchor,
        _try_iso,
        _try_named_date,
        _try_relative_weekday,
        _try_relative_period,
        _try_in_n_units,
        _try_n_units_ago,
        _try_n_units_from,
        _try_offset_from_date,
    ):
        result = fn(s, today)
        if result is not None:
            return result
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def parse(s: str, today: date | None = None) -> date:
    """
    Parse a natural-language date string and return a :class:`datetime.date`.

    Parameters
    ----------
    s:
        A natural-language date expression, e.g. ``"next Tuesday"``,
        ``"5 days before December 1st, 2025"``, ``"in 3 weeks"``.
    today:
        Reference date for relative expressions. Defaults to
        :func:`datetime.date.today`.

    Raises
    ------
    ValueError
        If *s* cannot be parsed.
    """
    if today is None:
        today = date.today()

    normalised = " ".join(s.strip().lower().split())

    result = _parse_inner(normalised, today)
    if result is not None:
        return result

    raise ValueError(f"Could not parse date string: {s!r}")
