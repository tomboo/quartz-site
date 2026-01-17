"""Schema validation tests for vault frontmatter compliance."""

import pytest
from conftest import (
    parse_markdown_frontmatter,
    is_valid_ulid,
    is_kebab_case,
    is_valid_date,
    is_valid_iso_timestamp
)


# Backlog schema tests

def test_backlog_has_required_properties(valid_backlog):
    """Backlog items must have uid, date, user, title."""
    assert "uid" in valid_backlog, "Missing required property: uid"
    assert "date" in valid_backlog, "Missing required property: date"
    assert "user" in valid_backlog, "Missing required property: user"
    assert "title" in valid_backlog, "Missing required property: title"


def test_backlog_priority_valid_values(valid_backlog):
    """Priority must be p0, p1, p2, or p3."""
    valid_priorities = ["p0", "p1", "p2", "p3"]
    assert valid_backlog["priority"] in valid_priorities, \
        f"Invalid priority: {valid_backlog['priority']} (must be one of {valid_priorities})"


def test_backlog_status_valid_values(valid_backlog):
    """Status must be one of defined values."""
    valid_statuses = ["open", "not-started", "in-progress", "completed", "canceled", "blocked"]
    assert valid_backlog["status"] in valid_statuses, \
        f"Invalid status: {valid_backlog['status']} (must be one of {valid_statuses})"


def test_backlog_uid_format(valid_backlog):
    """UID must be valid ULID format (26 chars, Base32)."""
    assert is_valid_ulid(valid_backlog["uid"]), \
        f"Invalid ULID format: {valid_backlog['uid']}"


def test_backlog_date_format(valid_backlog):
    """Date must be YYYY-MM-DD format."""
    assert is_valid_date(valid_backlog["date"]), \
        f"Invalid date format: {valid_backlog['date']} (must be YYYY-MM-DD)"


def test_backlog_property_names_kebab_case(valid_backlog):
    """All property names must use kebab-case."""
    for key in valid_backlog.keys():
        assert is_kebab_case(key), \
            f"Property name '{key}' is not kebab-case"


# Session schema tests

def test_session_has_required_properties(valid_session):
    """Sessions must have uid, date, user, session."""
    assert "uid" in valid_session, "Missing required property: uid"
    assert "date" in valid_session, "Missing required property: date"
    assert "user" in valid_session, "Missing required property: user"
    assert "session" in valid_session, "Missing required property: session"


def test_session_number_is_integer(valid_session):
    """Session number must be positive integer."""
    assert isinstance(valid_session["session"], int), \
        f"Session number must be integer, got {type(valid_session['session'])}"
    assert valid_session["session"] > 0, \
        f"Session number must be positive, got {valid_session['session']}"


def test_session_focus_is_list(valid_session):
    """Focus must be a list of strings."""
    assert isinstance(valid_session["focus"], list), \
        f"Focus must be list, got {type(valid_session['focus'])}"
    assert len(valid_session["focus"]) > 0, \
        "Focus list cannot be empty"
    assert all(isinstance(item, str) for item in valid_session["focus"]), \
        "All focus items must be strings"


def test_session_uid_format(valid_session):
    """UID must be valid ULID format."""
    assert is_valid_ulid(valid_session["uid"]), \
        f"Invalid ULID format: {valid_session['uid']}"


def test_session_property_names_kebab_case(valid_session):
    """All property names must use kebab-case."""
    for key in valid_session.keys():
        assert is_kebab_case(key), \
            f"Property name '{key}' is not kebab-case"


# Common property tests (applicable to both)

@pytest.mark.parametrize("fixture_name", ["valid_backlog", "valid_session"])
def test_created_at_timestamp_format(fixture_name, request):
    """created-at must be ISO 8601 timestamp with timezone."""
    fixture = request.getfixturevalue(fixture_name)
    if "created-at" in fixture:
        assert is_valid_iso_timestamp(fixture["created-at"]), \
            f"Invalid timestamp format: {fixture['created-at']} (must be ISO 8601 with timezone)"


@pytest.mark.parametrize("fixture_name", ["valid_backlog", "valid_session"])
def test_modified_at_timestamp_format(fixture_name, request):
    """modified-at must be ISO 8601 timestamp with timezone."""
    fixture = request.getfixturevalue(fixture_name)
    if "modified-at" in fixture:
        assert is_valid_iso_timestamp(fixture["modified-at"]), \
            f"Invalid timestamp format: {fixture['modified-at']} (must be ISO 8601 with timezone)"


@pytest.mark.parametrize("fixture_name", ["valid_backlog", "valid_session"])
def test_tags_is_list(fixture_name, request):
    """Tags must be a list if present."""
    fixture = request.getfixturevalue(fixture_name)
    if "tags" in fixture:
        assert isinstance(fixture["tags"], list), \
            f"Tags must be list, got {type(fixture['tags'])}"


# Invalid fixture tests

def test_backlog_without_uid_fails(backlog_no_uid):
    """Backlog without UID should be detected as invalid."""
    assert "uid" not in backlog_no_uid, "Fixture should not have uid"
    # This test confirms the fixture is set up correctly
    # Actual validation logic would be in a validator function


def test_backlog_with_wrong_priority_fails(backlog_wrong_priority):
    """Backlog with old priority format should be invalid."""
    assert backlog_wrong_priority["priority"] == "high", \
        "Fixture should have old priority format"
    # Confirm it's not a valid priority
    valid_priorities = ["p0", "p1", "p2", "p3"]
    assert backlog_wrong_priority["priority"] not in valid_priorities, \
        "Old priority format should not be in valid list"
