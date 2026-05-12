from datetime import date
import pytest
from nldate import parse


class TestAbsoluteDates:
    def test_named_month_day_year(self):
        assert parse("December 1st, 2025") == date(2025, 12, 1)

    def test_named_month_ordinal_day(self):
        assert parse("January 15th, 2024") == date(2024, 1, 15)

    def test_named_month_non_ordinal_day(self):
        assert parse("March 3, 2023") == date(2023, 3, 3)

    def test_iso_format(self):
        assert parse("2025-12-01") == date(2025, 12, 1)

    def test_us_numeric_format(self):
        assert parse("12/01/2025") == date(2025, 12, 1)

    def test_iso_format_without_day(self):
        assert parse("2025-12") == date(2025, 12, 1)

    def test_named_month_year_only(self):
        assert parse("December 2025") == date(2025, 12, 1)

    def test_just_month_and_day(self):
        assert parse("December 1st", today=date(2025, 6, 15)) == date(2025, 12, 1)

    def test_leap_year_date(self):
        assert parse("February 29th, 2024") == date(2024, 2, 29)

    def test_new_year_eve(self):
        assert parse("December 31st, 2025") == date(2025, 12, 31)

    def test_new_year_day(self):
        assert parse("January 1st, 2026") == date(2026, 1, 1)


class TestRelativeDays:
    def test_in_days(self):
        assert parse("in 3 days", today=date(2025, 12, 1)) == date(2025, 12, 4)

    def test_days_from_now(self):
        assert parse("3 days from now", today=date(2025, 12, 1)) == date(2025, 12, 4)

    def test_days_from_today(self):
        assert parse("5 days from today", today=date(2025, 12, 1)) == date(2025, 12, 6)

    def test_days_ago(self):
        assert parse("3 days ago", today=date(2025, 12, 10)) == date(2025, 12, 7)

    def test_in_one_day(self):
        assert parse("in 1 day", today=date(2025, 12, 1)) == date(2025, 12, 2)

    def test_singular_day_ago(self):
        assert parse("1 day ago", today=date(2025, 12, 10)) == date(2025, 12, 9)


class TestYesterdayTodayTomorrow:
    def test_today(self):
        assert parse("today", today=date(2025, 12, 1)) == date(2025, 12, 1)

    def test_tomorrow(self):
        assert parse("tomorrow", today=date(2025, 12, 1)) == date(2025, 12, 2)

    def test_yesterday(self):
        assert parse("yesterday", today=date(2025, 12, 10)) == date(2025, 12, 9)


class TestRelativeToReference:
    def test_days_before_absolute_date(self):
        assert parse("5 days before December 1st, 2025") == date(2025, 11, 26)

    def test_days_after_absolute_date(self):
        assert parse("5 days after December 1st, 2025") == date(2025, 12, 6)

    def test_week_before_absolute_date(self):
        assert parse("1 week before December 1st, 2025") == date(2025, 11, 24)

    def test_weeks_after_absolute_date(self):
        assert parse("2 weeks after December 1st, 2025") == date(2025, 12, 15)

    def test_days_before_tomorrow(self):
        assert parse("2 days before tomorrow", today=date(2025, 12, 1)) == date(2025, 11, 30)

    def test_days_after_yesterday(self):
        assert parse("3 days after yesterday", today=date(2025, 12, 10)) == date(2025, 12, 12)

    def test_month_before_date(self):
        assert parse("1 month before March 1st, 2025") == date(2025, 2, 1)

    def test_year_after_date(self):
        assert parse("1 year after December 1st, 2025") == date(2026, 12, 1)


class TestWeekdays:
    def test_next_tuesday(self):
        assert parse("next Tuesday", today=date(2025, 12, 1)) == date(2025, 12, 9)

    def test_next_friday(self):
        assert parse("next Friday", today=date(2025, 12, 1)) == date(2025, 12, 12)

    def test_this_friday(self):
        assert parse("this Friday", today=date(2025, 12, 1)) == date(2025, 12, 5)

    def test_this_monday(self):
        assert parse("this Monday", today=date(2025, 12, 1)) == date(2025, 12, 1)

    def test_last_monday(self):
        assert parse("last Monday", today=date(2025, 12, 10)) == date(2025, 12, 8)

    def test_last_friday(self):
        assert parse("last Friday", today=date(2025, 12, 10)) == date(2025, 12, 5)

    def test_next_monday_from_sunday(self):
        assert parse("next Monday", today=date(2025, 12, 7)) == date(2025, 12, 8)

    def test_next_monday_from_monday(self):
        assert parse("next Monday", today=date(2025, 12, 1)) == date(2025, 12, 8)

    def test_weekday_alone_refers_to_next(self):
        assert parse("Tuesday", today=date(2025, 12, 1)) == date(2025, 12, 2)

    def test_weekday_alone_when_today_is_that_day(self):
        assert parse("Monday", today=date(2025, 12, 1)) == date(2025, 12, 1)


class TestCompoundDurations:
    def test_years_and_months_after_yesterday(self):
        assert parse("1 year and 2 months after yesterday", today=date(2025, 12, 1)) == date(2027, 1, 30)

    def test_years_months_days_before_date(self):
        assert parse("1 year, 2 months, and 3 days before December 1st, 2025") == date(2024, 9, 28)

    def test_weeks_and_days_from_now(self):
        assert parse("2 weeks and 3 days from now", today=date(2025, 12, 1)) == date(2025, 12, 18)

    def test_months_and_days_after_today(self):
        assert parse("3 months and 10 days after today", today=date(2025, 12, 1)) == date(2026, 3, 11)


class TestWeekMonthYearOffsets:
    def test_next_week(self):
        assert parse("next week", today=date(2025, 12, 1)) == date(2025, 12, 8)

    def test_last_week(self):
        assert parse("last week", today=date(2025, 12, 10)) == date(2025, 12, 3)

    def test_next_month(self):
        assert parse("next month", today=date(2025, 12, 1)) == date(2026, 1, 1)

    def test_last_month(self):
        assert parse("last month", today=date(2025, 12, 10)) == date(2025, 11, 10)

    def test_next_year(self):
        assert parse("next year", today=date(2025, 12, 1)) == date(2026, 12, 1)

    def test_last_year(self):
        assert parse("last year", today=date(2025, 12, 10)) == date(2024, 12, 10)

    def test_in_two_weeks(self):
        assert parse("in 2 weeks", today=date(2025, 12, 1)) == date(2025, 12, 15)

    def test_in_three_months(self):
        assert parse("in 3 months", today=date(2025, 12, 1)) == date(2026, 3, 1)

    def test_two_years_from_now(self):
        assert parse("2 years from now", today=date(2025, 12, 1)) == date(2027, 12, 1)


class TestOrdinalDates:
    def test_ordinal_day_of_month_full(self):
        assert parse("the 15th of December, 2025") == date(2025, 12, 15)

    def test_ordinal_day_of_month_without_year(self):
        assert parse("the 1st of December", today=date(2025, 6, 15)) == date(2025, 12, 1)

    def test_ordinal_with_st(self):
        assert parse("the 21st of December 2025") == date(2025, 12, 21)

    def test_ordinal_with_rd(self):
        assert parse("the 3rd of March 2025") == date(2025, 3, 3)

    def test_ordinal_with_th(self):
        assert parse("the 5th of June 2025") == date(2025, 6, 5)


class TestEdgeCases:
    def test_end_of_month_rollover(self):
        assert parse("in 1 month", today=date(2025, 1, 31)) == date(2025, 2, 28)

    def test_end_of_month_leap_year(self):
        assert parse("in 1 month", today=date(2024, 1, 31)) == date(2024, 2, 29)

    def test_december_to_january_rollover(self):
        assert parse("in 1 month", today=date(2025, 12, 1)) == date(2026, 1, 1)

    def test_year_boundary(self):
        assert parse("1 week before January 1st, 2026") == date(2025, 12, 25)

    def test_large_offset(self):
        assert parse("100 days from now", today=date(2025, 1, 1)) == date(2025, 4, 11)

    def test_same_date_different_format(self):
        assert parse("December 25th, 2025") == parse("2025-12-25")
        assert parse("December 25th, 2025") == parse("12/25/2025")


class TestDefaultToday:
    def test_defaults_to_today(self):
        from datetime import date as dt_date
        result = parse("today")
        assert result == dt_date.today()


class TestRaisesOnInvalid:
    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            parse("")

    def test_nonsense_raises(self):
        with pytest.raises(ValueError):
            parse("not a date at all")

    def test_invalid_date_raises(self):
        with pytest.raises(ValueError):
            parse("February 30th, 2025")
