"""Integration tests for all session notes in the vault."""

import glob
import pytest
from conftest import (
    parse_markdown_frontmatter,
    is_valid_ulid,
    is_kebab_case,
    is_valid_date,
    is_valid_iso_timestamp
)


# Collect all session files for parameterized testing
session_files = glob.glob("_database/database-core/sessions-table/session-*.md")


@pytest.mark.parametrize("file_path", session_files)
def test_session_has_required_properties(file_path):
    """Every session note must have required properties."""
    item = parse_markdown_frontmatter(file_path)

    required_props = ["uid", "date", "user", "session"]
    missing = [prop for prop in required_props if prop not in item]

    assert len(missing) == 0, \
        f"{file_path}: Missing required properties: {missing}"


@pytest.mark.parametrize("file_path", session_files)
def test_session_uid_valid_format(file_path):
    """Every session UID must be valid ULID format."""
    item = parse_markdown_frontmatter(file_path)

    if "uid" in item:
        assert is_valid_ulid(item["uid"]), \
            f"{file_path}: Invalid ULID format: {item['uid']}"


@pytest.mark.parametrize("file_path", session_files)
def test_session_date_valid_format(file_path):
    """Every session date must be valid YYYY-MM-DD format."""
    item = parse_markdown_frontmatter(file_path)

    if "date" in item:
        assert is_valid_date(item["date"]), \
            f"{file_path}: Invalid date format: {item['date']}"


@pytest.mark.parametrize("file_path", session_files)
def test_session_number_is_positive_integer(file_path):
    """Session number must be positive integer."""
    item = parse_markdown_frontmatter(file_path)

    if "session" in item:
        assert isinstance(item["session"], int), \
            f"{file_path}: Session number must be integer, got {type(item['session'])}"

        assert item["session"] > 0, \
            f"{file_path}: Session number must be positive, got {item['session']}"


@pytest.mark.parametrize("file_path", session_files)
def test_session_focus_is_list(file_path):
    """Focus must be a list of strings if present."""
    item = parse_markdown_frontmatter(file_path)

    if "focus" in item:
        assert isinstance(item["focus"], list), \
            f"{file_path}: Focus must be list, got {type(item['focus'])}"

        assert len(item["focus"]) > 0, \
            f"{file_path}: Focus list cannot be empty"

        assert all(isinstance(f, str) for f in item["focus"]), \
            f"{file_path}: All focus items must be strings"


@pytest.mark.parametrize("file_path", session_files)
def test_session_property_names_kebab_case(file_path):
    """All property names must use kebab-case."""
    item = parse_markdown_frontmatter(file_path)

    violations = [key for key in item.keys() if not is_kebab_case(key)]

    assert len(violations) == 0, \
        f"{file_path}: Non-kebab-case property names: {violations}"


@pytest.mark.parametrize("file_path", session_files)
def test_session_created_at_timestamp(file_path):
    """created-at must be valid ISO 8601 timestamp if present."""
    item = parse_markdown_frontmatter(file_path)

    if "created-at" in item:
        assert is_valid_iso_timestamp(item["created-at"]), \
            f"{file_path}: Invalid created-at timestamp: {item['created-at']}"


@pytest.mark.parametrize("file_path", session_files)
def test_session_modified_at_timestamp(file_path):
    """modified-at must be valid ISO 8601 timestamp if present."""
    item = parse_markdown_frontmatter(file_path)

    if "modified-at" in item:
        assert is_valid_iso_timestamp(item["modified-at"]), \
            f"{file_path}: Invalid modified-at timestamp: {item['modified-at']}"


@pytest.mark.parametrize("file_path", session_files)
def test_session_tags_is_list(file_path):
    """Tags must be a list if present."""
    item = parse_markdown_frontmatter(file_path)

    if "tags" in item:
        assert isinstance(item["tags"], list), \
            f"{file_path}: Tags must be list, got {type(item['tags'])}"


@pytest.mark.parametrize("file_path", session_files)
def test_session_commits_is_list(file_path):
    """Commits must be a list if present."""
    item = parse_markdown_frontmatter(file_path)

    if "commits" in item:
        assert isinstance(item["commits"], list), \
            f"{file_path}: Commits must be list, got {type(item['commits'])}"


@pytest.mark.parametrize("file_path", session_files)
def test_session_context_usage_format(file_path):
    """context-usage should be string if present (e.g., '39K/200K')."""
    item = parse_markdown_frontmatter(file_path)

    if "context-usage" in item:
        assert isinstance(item["context-usage"], str), \
            f"{file_path}: context-usage must be string, got {type(item['context-usage'])}"

        # Optional: check format like "39K/200K"
        if "/" in item["context-usage"]:
            parts = item["context-usage"].split("/")
            assert len(parts) == 2, \
                f"{file_path}: context-usage format should be 'used/total', got {item['context-usage']}"


@pytest.mark.parametrize("file_path", session_files)
def test_session_duration_estimate_format(file_path):
    """duration-estimate should be string if present (e.g., '~2h', '1-2h')."""
    item = parse_markdown_frontmatter(file_path)

    if "duration-estimate" in item:
        assert isinstance(item["duration-estimate"], str), \
            f"{file_path}: duration-estimate must be string, got {type(item['duration-estimate'])}"

        assert len(item["duration-estimate"]) > 0, \
            f"{file_path}: duration-estimate cannot be empty string"
