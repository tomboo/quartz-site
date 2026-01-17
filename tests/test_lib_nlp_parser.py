"""Unit tests for lib/nlp_parser.py

Tests natural language parsing for backlog item creation.
"""

import pytest
from datetime import datetime, timedelta
from _framework.lib.nlp_parser import (
    parse_date_expression,
    parse_priority,
    parse_estimate,
    parse_category,
    parse_tags,
    clean_title,
    parse_backlog_input
)


class TestParseDateExpression:
    """Tests for parse_date_expression function."""

    def test_tomorrow(self):
        """Parse 'tomorrow' keyword."""
        date, remaining = parse_date_expression("do something tomorrow")
        expected = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        assert date == expected
        assert "tomorrow" not in remaining.lower()

    def test_today(self):
        """Parse 'today' keyword."""
        date, remaining = parse_date_expression("task for today")
        expected = datetime.now().strftime('%Y-%m-%d')
        assert date == expected
        assert "today" not in remaining.lower()

    def test_next_week(self):
        """Parse 'next week' keyword."""
        date, remaining = parse_date_expression("schedule next week")
        expected = (datetime.now() + timedelta(weeks=1)).strftime('%Y-%m-%d')
        assert date == expected
        assert "next week" not in remaining.lower()

    def test_next_month(self):
        """Parse 'next month' keyword."""
        date, remaining = parse_date_expression("do next month")
        expected = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        assert date == expected

    def test_in_n_days(self):
        """Parse 'in N days' pattern."""
        date, remaining = parse_date_expression("finish in 5 days")
        expected = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
        assert date == expected

    def test_in_n_weeks(self):
        """Parse 'in N weeks' pattern."""
        date, remaining = parse_date_expression("review in 2 weeks")
        expected = (datetime.now() + timedelta(weeks=2)).strftime('%Y-%m-%d')
        assert date == expected

    def test_next_monday(self):
        """Parse 'next Monday' pattern."""
        date, remaining = parse_date_expression("meeting next monday")
        assert date is not None
        # Verify it's a Monday
        parsed = datetime.strptime(date, '%Y-%m-%d')
        assert parsed.weekday() == 0  # Monday is 0

    def test_month_day_short(self):
        """Parse 'Jan 15' pattern."""
        date, remaining = parse_date_expression("appointment jan 15")
        assert date is not None
        parsed = datetime.strptime(date, '%Y-%m-%d')
        assert parsed.month == 1
        assert parsed.day == 15

    def test_month_day_long(self):
        """Parse 'January 15' pattern."""
        date, remaining = parse_date_expression("event on January 15")
        assert date is not None
        parsed = datetime.strptime(date, '%Y-%m-%d')
        assert parsed.month == 1
        assert parsed.day == 15

    def test_iso_date(self):
        """Parse ISO format '2025-01-15'."""
        date, remaining = parse_date_expression("task due 2025-01-15")
        assert date == "2025-01-15"
        assert "2025-01-15" not in remaining

    def test_slash_date(self):
        """Parse '12/15' pattern."""
        date, remaining = parse_date_expression("deadline 12/15")
        assert date is not None
        parsed = datetime.strptime(date, '%Y-%m-%d')
        assert parsed.month == 12
        assert parsed.day == 15

    def test_slash_date_with_year(self):
        """Parse '12/15/2025' pattern."""
        date, remaining = parse_date_expression("deadline 12/15/2025")
        assert date == "2025-12-15"

    def test_no_date(self):
        """No date expression returns None."""
        date, remaining = parse_date_expression("just a task")
        assert date is None
        assert remaining == "just a task"


class TestParsePriority:
    """Tests for parse_priority function."""

    def test_critical(self):
        """Parse 'critical' as 0."""
        priority, remaining = parse_priority("critical bug fix")
        assert priority == 0
        assert "critical" not in remaining.lower()

    def test_urgent(self):
        """Parse 'urgent' as 0."""
        priority, remaining = parse_priority("urgent issue")
        assert priority == 0

    def test_p0(self):
        """Parse 'p0' directly."""
        priority, remaining = parse_priority("p0 task")
        assert priority == 0

    def test_high(self):
        """Parse 'high' as 1."""
        priority, remaining = parse_priority("high priority task")
        assert priority == 1
        # "priority" should also be removed
        assert "priority" not in remaining.lower()

    def test_important(self):
        """Parse 'important' as 1."""
        priority, remaining = parse_priority("important meeting")
        assert priority == 1

    def test_p1(self):
        """Parse 'p1' directly."""
        priority, remaining = parse_priority("p1 task")
        assert priority == 1

    def test_medium(self):
        """Parse 'medium' as 2."""
        priority, remaining = parse_priority("medium priority")
        assert priority == 2

    def test_normal(self):
        """Parse 'normal' as 2."""
        priority, remaining = parse_priority("normal task")
        assert priority == 2

    def test_low(self):
        """Parse 'low' as 3."""
        priority, remaining = parse_priority("low priority item")
        assert priority == 3

    def test_p3(self):
        """Parse 'p3' directly."""
        priority, remaining = parse_priority("p3 backlog")
        assert priority == 3

    def test_no_priority(self):
        """No priority returns None."""
        priority, remaining = parse_priority("just a task")
        assert priority is None
        assert remaining == "just a task"


class TestParseEstimate:
    """Tests for parse_estimate function."""

    def test_minutes(self):
        """Parse minutes estimate."""
        estimate, remaining = parse_estimate("quick 15m task")
        assert estimate == "PT15M"
        assert "15m" not in remaining.lower()

    def test_minutes_long(self):
        """Parse 'minutes' word."""
        estimate, remaining = parse_estimate("30 minutes task")
        assert estimate == "PT30M"

    def test_hours_integer(self):
        """Parse whole hours."""
        estimate, remaining = parse_estimate("2h task")
        assert estimate == "P2H"

    def test_hours_long(self):
        """Parse 'hours' word."""
        estimate, remaining = parse_estimate("2 hours work")
        assert estimate == "P2H"

    def test_hours_decimal(self):
        """Parse decimal hours."""
        estimate, remaining = parse_estimate("1.5h meeting")
        assert estimate == "P1H30M"

    def test_hours_decimal_quarter(self):
        """Parse quarter hour."""
        estimate, remaining = parse_estimate("2.5h session")
        assert estimate == "P2H30M"

    def test_days(self):
        """Parse days estimate."""
        estimate, remaining = parse_estimate("1d project")
        assert estimate == "P1D"

    def test_days_long(self):
        """Parse 'days' word."""
        estimate, remaining = parse_estimate("2 days work")
        assert estimate == "P2D"

    def test_weeks(self):
        """Parse weeks estimate (converted to days)."""
        estimate, remaining = parse_estimate("1w project")
        assert estimate == "P7D"  # 1 week = 7 days

    def test_no_estimate(self):
        """No estimate returns None."""
        estimate, remaining = parse_estimate("just a task")
        assert estimate is None
        assert remaining == "just a task"


class TestParseCategory:
    """Tests for parse_category function."""

    def test_simple_category(self):
        """Parse @category."""
        category, remaining = parse_category("task @learning")
        assert category == "learning"
        assert "@learning" not in remaining

    def test_kebab_category(self):
        """Parse @kebab-case category."""
        category, remaining = parse_category("task @health-fitness")
        assert category == "health-fitness"

    def test_category_with_numbers(self):
        """Parse category with numbers."""
        category, remaining = parse_category("task @phase2")
        assert category == "phase2"

    def test_no_category(self):
        """No category returns None."""
        category, remaining = parse_category("just a task")
        assert category is None
        assert remaining == "just a task"

    def test_category_case_insensitive(self):
        """Category is lowercased."""
        category, remaining = parse_category("task @Learning")
        assert category == "learning"


class TestParseTags:
    """Tests for parse_tags function."""

    def test_single_tag(self):
        """Parse single #tag."""
        tags, remaining = parse_tags("task #urgent")
        assert tags == ["urgent"]
        assert "#urgent" not in remaining

    def test_multiple_tags(self):
        """Parse multiple tags."""
        tags, remaining = parse_tags("task #urgent #bug #frontend")
        assert set(tags) == {"urgent", "bug", "frontend"}

    def test_kebab_tag(self):
        """Parse kebab-case tag."""
        tags, remaining = parse_tags("task #follow-up")
        assert tags == ["follow-up"]

    def test_tag_with_numbers(self):
        """Parse tag with numbers."""
        tags, remaining = parse_tags("task #phase2")
        assert tags == ["phase2"]

    def test_no_tags(self):
        """No tags returns empty list."""
        tags, remaining = parse_tags("just a task")
        assert tags == []
        assert remaining == "just a task"

    def test_tags_lowercased(self):
        """Tags are lowercased."""
        tags, remaining = parse_tags("#Urgent #BUG")
        assert set(tags) == {"urgent", "bug"}


class TestCleanTitle:
    """Tests for clean_title function."""

    def test_basic_cleanup(self):
        """Basic whitespace cleanup."""
        assert clean_title("  hello world  ") == "Hello world"

    def test_multiple_spaces(self):
        """Collapse multiple spaces."""
        assert clean_title("hello   world") == "Hello world"

    def test_strip_punctuation(self):
        """Strip leading/trailing punctuation."""
        assert clean_title("- hello -") == "Hello"
        assert clean_title(", hello,") == "Hello"

    def test_capitalize_first(self):
        """Capitalize first letter."""
        assert clean_title("hello") == "Hello"

    def test_empty_string(self):
        """Empty string stays empty."""
        assert clean_title("") == ""

    def test_preserves_internal_punctuation(self):
        """Preserve punctuation inside title."""
        assert clean_title("hello, world!") == "Hello, world!"


class TestParseBacklogInput:
    """Integration tests for parse_backlog_input function."""

    def test_full_input(self):
        """Parse full natural language input."""
        result = parse_backlog_input(
            "research Obsidian plugin API tomorrow @learning #technical high 2h"
        )
        assert result['title'] == "Research Obsidian plugin API"
        assert result['priority'] == 1
        assert result['category'] == 'learning'
        assert 'technical' in result['tags']
        assert result['estimate'] == 'P2H'
        # date should be tomorrow
        expected_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        assert result['date'] == expected_date

    def test_minimal_input(self):
        """Parse minimal input (title only)."""
        result = parse_backlog_input("just a simple task")
        assert result['title'] == "Just a simple task"
        assert 'date' not in result
        assert 'priority' not in result

    def test_with_defaults(self):
        """Apply defaults for missing fields."""
        result = parse_backlog_input(
            "a task",
            defaults={'priority': 'p2', 'status': 'not-started'}
        )
        assert result['title'] == "A task"
        assert result['priority'] == 'p2'
        assert result['status'] == 'not-started'

    def test_explicit_overrides_default(self):
        """Explicit value overrides default."""
        result = parse_backlog_input(
            "high priority task",
            defaults={'priority': 3}
        )
        assert result['priority'] == 1  # Explicit 'high' beats default

    def test_critical_bug(self):
        """Parse critical bug pattern."""
        result = parse_backlog_input("fix critical bug 30m")
        assert result['title'] == "Fix bug"
        assert result['priority'] == 0
        assert result['estimate'] == 'PT30M'

    def test_meeting_pattern(self):
        """Parse meeting pattern."""
        result = parse_backlog_input("team meeting next monday @work 1h")
        assert "team meeting" in result['title'].lower()
        assert result['category'] == 'work'
        assert result['estimate'] == 'P1H'
        # Should be a Monday
        parsed = datetime.strptime(result['date'], '%Y-%m-%d')
        assert parsed.weekday() == 0
