"""Unit tests for lib/validators.py

Tests edge cases and error handling for validation functions.
"""

import pytest
import datetime
from _framework.lib.validators import (
    is_valid_ulid,
    is_kebab_case,
    is_valid_date,
    is_valid_iso_timestamp,
    parse_markdown_frontmatter
)


class TestIsValidUlid:
    """Tests for is_valid_ulid function."""

    def test_valid_ulid(self):
        """Standard valid ULID."""
        assert is_valid_ulid("01KAHXZ3MNPQR4ST6VWX8YZ012") is True

    def test_valid_ulid_lowercase(self):
        """Lowercase should also be valid (case insensitive)."""
        assert is_valid_ulid("01kahxz3mnpqr4st6vwx8yz012") is True

    def test_valid_ulid_mixed_case(self):
        """Mixed case should be valid."""
        assert is_valid_ulid("01KAhxz3MNpqr4ST6vwx8YZ012") is True

    def test_invalid_too_short(self):
        """ULID must be exactly 26 characters."""
        assert is_valid_ulid("01KAHXZ3MNPQR4ST6VWX") is False

    def test_invalid_too_long(self):
        """ULID must be exactly 26 characters."""
        assert is_valid_ulid("01KAHXZ3MNPQR4ST6VWX8YZ012XX") is False

    def test_invalid_characters(self):
        """ULID excludes I, L, O, U from Crockford's Base32."""
        # Contains 'I'
        assert is_valid_ulid("01KAHIZ3MNPQR4ST6VWX8YZ012") is False
        # Contains 'L'
        assert is_valid_ulid("01KAHLZ3MNPQR4ST6VWX8YZ012") is False
        # Contains 'O'
        assert is_valid_ulid("01KAHOZ3MNPQR4ST6VWX8YZ012") is False
        # Contains 'U'
        assert is_valid_ulid("01KAHUZ3MNPQR4ST6VWX8YZ012") is False

    def test_invalid_special_characters(self):
        """ULID must not contain special characters."""
        assert is_valid_ulid("01KAHXZ3-NPQR4ST6VWX8YZ01") is False
        assert is_valid_ulid("01KAHXZ3_NPQR4ST6VWX8YZ01") is False
        assert is_valid_ulid("01KAHXZ3.NPQR4ST6VWX8YZ01") is False

    def test_empty_string(self):
        """Empty string is invalid."""
        assert is_valid_ulid("") is False

    def test_none_input(self):
        """None input should return False, not raise."""
        assert is_valid_ulid(None) is False

    def test_integer_input(self):
        """Non-string input should return False."""
        assert is_valid_ulid(12345678901234567890123456) is False

    def test_list_input(self):
        """List input should return False."""
        assert is_valid_ulid(["01KAHXZ3MNPQR4ST6VWX8YZ012"]) is False


class TestIsKebabCase:
    """Tests for is_kebab_case function."""

    def test_simple_kebab_case(self):
        """Simple kebab-case string."""
        assert is_kebab_case("hello-world") is True

    def test_single_word(self):
        """Single word is valid kebab-case."""
        assert is_kebab_case("hello") is True

    def test_multiple_hyphens(self):
        """Multiple segments with hyphens."""
        assert is_kebab_case("one-two-three-four") is True

    def test_with_numbers(self):
        """Numbers are allowed."""
        assert is_kebab_case("task-123") is True
        assert is_kebab_case("v2-api") is True

    def test_invalid_uppercase(self):
        """Uppercase letters are not allowed."""
        assert is_kebab_case("Hello-World") is False
        assert is_kebab_case("helloWorld") is False

    def test_invalid_underscore(self):
        """Underscores are not allowed (that's snake_case)."""
        assert is_kebab_case("hello_world") is False

    def test_invalid_starts_with_hyphen(self):
        """Cannot start with hyphen."""
        assert is_kebab_case("-hello") is False

    def test_invalid_ends_with_hyphen(self):
        """Cannot end with hyphen."""
        assert is_kebab_case("hello-") is False

    def test_invalid_double_hyphen(self):
        """Cannot have consecutive hyphens."""
        assert is_kebab_case("hello--world") is False

    def test_allows_numbers_at_start(self):
        """Numbers at start are allowed per regex."""
        # The regex ^[a-z0-9]+(-[a-z0-9]+)*$ allows leading numbers
        assert is_kebab_case("123-hello") is True
        assert is_kebab_case("v2-api") is True

    def test_empty_string(self):
        """Empty string is invalid."""
        assert is_kebab_case("") is False

    def test_none_input(self):
        """None input should return False."""
        assert is_kebab_case(None) is False

    def test_integer_input(self):
        """Non-string input should return False."""
        assert is_kebab_case(123) is False

    def test_spaces(self):
        """Spaces are not allowed."""
        assert is_kebab_case("hello world") is False


class TestIsValidDate:
    """Tests for is_valid_date function."""

    def test_valid_string_date(self):
        """Valid YYYY-MM-DD string."""
        assert is_valid_date("2025-12-27") is True
        assert is_valid_date("2020-01-01") is True

    def test_valid_datetime_date_object(self):
        """datetime.date object is valid."""
        assert is_valid_date(datetime.date(2025, 12, 27)) is True

    def test_invalid_wrong_format(self):
        """Wrong date formats."""
        assert is_valid_date("12/27/2025") is False  # MM/DD/YYYY
        assert is_valid_date("27-12-2025") is False  # DD-MM-YYYY
        assert is_valid_date("2025/12/27") is False  # Wrong separator

    def test_invalid_incomplete_date(self):
        """Incomplete date strings."""
        assert is_valid_date("2025-12") is False
        assert is_valid_date("2025") is False

    def test_invalid_with_time(self):
        """Date with time component."""
        assert is_valid_date("2025-12-27T10:30:00") is False

    def test_empty_string(self):
        """Empty string is invalid."""
        assert is_valid_date("") is False

    def test_none_input(self):
        """None input should return False."""
        assert is_valid_date(None) is False

    def test_integer_input(self):
        """Integer input should return False."""
        assert is_valid_date(20251227) is False

    def test_datetime_object(self):
        """datetime.datetime is also a date, but we want date only."""
        # datetime is a subclass of date, so this should work
        dt = datetime.datetime(2025, 12, 27, 10, 30, 0)
        assert is_valid_date(dt) is True  # datetime is a subclass of date


class TestIsValidIsoTimestamp:
    """Tests for is_valid_iso_timestamp function."""

    def test_valid_timestamp_string(self):
        """Valid ISO 8601 timestamp string with timezone."""
        assert is_valid_iso_timestamp("2025-12-27T10:30:00-08:00") is True
        assert is_valid_iso_timestamp("2025-12-27T10:30:00+00:00") is True
        assert is_valid_iso_timestamp("2025-01-01T00:00:00+05:30") is True

    def test_valid_datetime_with_timezone(self):
        """datetime object with timezone info."""
        from datetime import timezone, timedelta
        tz = timezone(timedelta(hours=-8))  # US/Pacific equivalent
        dt = datetime.datetime(2025, 12, 27, 10, 30, 0, tzinfo=tz)
        assert is_valid_iso_timestamp(dt) is True

    def test_invalid_datetime_without_timezone(self):
        """datetime object without timezone is invalid."""
        dt = datetime.datetime(2025, 12, 27, 10, 30, 0)
        assert is_valid_iso_timestamp(dt) is False

    def test_invalid_no_timezone(self):
        """Timestamp string without timezone."""
        assert is_valid_iso_timestamp("2025-12-27T10:30:00") is False

    def test_invalid_space_separator(self):
        """Space instead of T separator."""
        assert is_valid_iso_timestamp("2025-12-27 10:30:00-08:00") is False

    def test_invalid_wrong_timezone_format(self):
        """Wrong timezone formats."""
        assert is_valid_iso_timestamp("2025-12-27T10:30:00Z") is False  # Z not supported
        assert is_valid_iso_timestamp("2025-12-27T10:30:00-8:00") is False  # Missing leading 0

    def test_empty_string(self):
        """Empty string is invalid."""
        assert is_valid_iso_timestamp("") is False

    def test_none_input(self):
        """None input should return False."""
        assert is_valid_iso_timestamp(None) is False

    def test_date_only(self):
        """Date without time is invalid."""
        assert is_valid_iso_timestamp("2025-12-27") is False


class TestParseMarkdownFrontmatter:
    """Tests for parse_markdown_frontmatter function."""

    def test_nonexistent_file(self):
        """Should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            parse_markdown_frontmatter("/nonexistent/path/file.md")
