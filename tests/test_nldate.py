"""Test suite for nldate.parse()."""

from datetime import date

import pytest

from nldate import parse

# Reference date: Wednesday, 2025-06-04
TODAY = date(2025, 6, 4)


# ---------------------------------------------------------------------------
# Anchors
# ---------------------------------------------------------------------------


def test_today() -> None:
    assert parse("today", today=TODAY) == TODAY


def test_tomorrow() -> None:
    assert parse("tomorrow", today=TODAY) == date(2025, 6, 5)


def test_yesterday() -> None:
    assert parse("yesterday", today=TODAY) == date(2025, 6, 3)


# ---------------------------------------------------------------------------
# Absolute / ISO dates
# ---------------------------------------------------------------------------


def test_iso_date() -> None:
    assert parse("2025-12-01", today=TODAY) == date(2025, 12, 1)


def test_month_first_with_ordinal() -> None:
    assert parse("December 1st, 2025", today=TODAY) == date(2025, 12, 1)


def test_month_first_no_ordinal() -> None:
    assert parse("Jan 5 2024", today=TODAY) == date(2024, 1, 5)


def test_day_first() -> None:
    assert parse("1 December 2025", today=TODAY) == date(2025, 12, 1)


def test_month_day_no_year_defaults_to_current_year() -> None:
    # No year supplied → defaults to TODAY.year (2025)
    assert parse("March 15", today=TODAY) == date(2025, 3, 15)


# ---------------------------------------------------------------------------
# Relative weekdays
# ---------------------------------------------------------------------------

# TODAY is Wednesday (weekday=2)


def test_next_tuesday() -> None:
    # Next Tue from Wed 2025-06-04 → 2025-06-10
    assert parse("next Tuesday", today=TODAY) == date(2025, 6, 10)


def test_next_wednesday_skips_full_week() -> None:
    # "next Wednesday" from Wednesday → the *following* Wednesday
    assert parse("next Wednesday", today=TODAY) == date(2025, 6, 11)


def test_last_monday() -> None:
    # Last Monday from Wed 2025-06-04 → 2025-06-02
    assert parse("last Monday", today=TODAY) == date(2025, 6, 2)


def test_last_friday() -> None:
    # Last Friday from Wed 2025-06-04 → 2025-05-30
    assert parse("last Friday", today=TODAY) == date(2025, 5, 30)


def test_this_friday() -> None:
    # "this Friday" from Wednesday → coming Friday (2025-06-06)
    assert parse("this Friday", today=TODAY) == date(2025, 6, 6)


# ---------------------------------------------------------------------------
# Relative periods
# ---------------------------------------------------------------------------


def test_next_week() -> None:
    assert parse("next week", today=TODAY) == date(2025, 6, 11)


def test_last_week() -> None:
    assert parse("last week", today=TODAY) == date(2025, 5, 28)


def test_next_month() -> None:
    assert parse("next month", today=TODAY) == date(2025, 7, 4)


def test_last_year() -> None:
    assert parse("last year", today=TODAY) == date(2024, 6, 4)


# ---------------------------------------------------------------------------
# "in N units"
# ---------------------------------------------------------------------------


def test_in_3_days() -> None:
    assert parse("in 3 days", today=TODAY) == date(2025, 6, 7)


def test_in_two_weeks() -> None:
    assert parse("in two weeks", today=TODAY) == date(2025, 6, 18)


def test_in_one_month() -> None:
    assert parse("in one month", today=TODAY) == date(2025, 7, 4)


def test_in_a_year() -> None:
    assert parse("in a year", today=TODAY) == date(2026, 6, 4)


# ---------------------------------------------------------------------------
# "N units ago"
# ---------------------------------------------------------------------------


def test_3_days_ago() -> None:
    assert parse("3 days ago", today=TODAY) == date(2025, 6, 1)


def test_two_weeks_ago() -> None:
    assert parse("two weeks ago", today=TODAY) == date(2025, 5, 21)


def test_1_month_ago() -> None:
    assert parse("1 month ago", today=TODAY) == date(2025, 5, 4)


# ---------------------------------------------------------------------------
# "N units from <anchor>"
# ---------------------------------------------------------------------------


def test_n_days_from_today() -> None:
    assert parse("5 days from today", today=TODAY) == date(2025, 6, 9)


def test_two_weeks_from_tomorrow() -> None:
    assert parse("two weeks from tomorrow", today=TODAY) == date(2025, 6, 19)


def test_3_days_from_yesterday() -> None:
    assert parse("3 days from yesterday", today=TODAY) == date(2025, 6, 6)


# ---------------------------------------------------------------------------
# Offset from a named date
# ---------------------------------------------------------------------------


def test_days_before_named_date() -> None:
    assert parse("5 days before December 1st, 2025", today=TODAY) == date(2025, 11, 26)


def test_weeks_after_named_date() -> None:
    assert parse("3 weeks after Jan 1 2026", today=TODAY) == date(2026, 1, 22)


def test_months_before_named_date() -> None:
    assert parse("2 months before March 15 2026", today=TODAY) == date(2026, 1, 15)


# ---------------------------------------------------------------------------
# Compound offsets  ("1 year and 2 months after yesterday")
# ---------------------------------------------------------------------------


def test_compound_year_and_month_after_anchor() -> None:
    # 1 year and 2 months after 2025-06-03 → 2026-08-03
    assert parse("1 year and 2 months after yesterday", today=TODAY) == date(2026, 8, 3)


def test_compound_weeks_and_days_before() -> None:
    # 1 week (7 days) + 3 days = 10 days before 2025-12-01 → 2025-11-21
    result = parse("1 week and 3 days before December 1st 2025", today=TODAY)
    assert result == date(2025, 11, 21)


# ---------------------------------------------------------------------------
# Case / whitespace insensitivity
# ---------------------------------------------------------------------------


def test_case_insensitive() -> None:
    assert parse("NEXT TUESDAY", today=TODAY) == date(2025, 6, 10)


def test_extra_whitespace() -> None:
    assert parse("  in   3   days  ", today=TODAY) == date(2025, 6, 7)


# ---------------------------------------------------------------------------
# today defaults to date.today() when omitted
# ---------------------------------------------------------------------------


def test_default_today_is_date_today() -> None:
    result = parse("today")
    assert result == date.today()


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


def test_invalid_string_raises() -> None:
    with pytest.raises(ValueError):
        parse("not a date at all", today=TODAY)
