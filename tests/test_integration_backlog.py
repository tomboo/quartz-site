"""Integration tests for all backlog items in the vault."""

import glob
import pytest
from conftest import (
    parse_markdown_frontmatter,
    is_valid_ulid,
    is_kebab_case,
    is_valid_date,
    is_valid_iso_timestamp
)


# Collect all backlog files for parameterized testing
backlog_files = glob.glob("_database/database-core/backlog-table/backlog-*.md")


@pytest.mark.parametrize("file_path", backlog_files)
def test_backlog_has_required_properties(file_path):
    """Every backlog item must have required properties."""
    item = parse_markdown_frontmatter(file_path)

    required_props = ["uid", "date", "user", "title"]
    missing = [prop for prop in required_props if prop not in item]

    assert len(missing) == 0, \
        f"{file_path}: Missing required properties: {missing}"


@pytest.mark.parametrize("file_path", backlog_files)
def test_backlog_uid_valid_format(file_path):
    """Every backlog UID must be valid ULID format."""
    item = parse_markdown_frontmatter(file_path)

    if "uid" in item:
        assert is_valid_ulid(item["uid"]), \
            f"{file_path}: Invalid ULID format: {item['uid']}"


@pytest.mark.parametrize("file_path", backlog_files)
def test_backlog_date_valid_format(file_path):
    """Every backlog date must be valid YYYY-MM-DD format."""
    item = parse_markdown_frontmatter(file_path)

    if "date" in item:
        assert is_valid_date(item["date"]), \
            f"{file_path}: Invalid date format: {item['date']}"


@pytest.mark.parametrize("file_path", backlog_files)
def test_backlog_priority_valid_values(file_path):
    """Priority must be p0, p1, p2, or p3."""
    item = parse_markdown_frontmatter(file_path)

    if "priority" in item:
        valid_priorities = ["p0", "p1", "p2", "p3"]
        assert item["priority"] in valid_priorities, \
            f"{file_path}: Invalid priority '{item['priority']}' (must be {valid_priorities})"


@pytest.mark.parametrize("file_path", backlog_files)
def test_backlog_status_valid_values(file_path):
    """Status must be one of defined values."""
    item = parse_markdown_frontmatter(file_path)

    if "status" in item:
        valid_statuses = ["open", "not-started", "in-progress", "completed", "canceled", "blocked"]
        assert item["status"] in valid_statuses, \
            f"{file_path}: Invalid status '{item['status']}' (must be {valid_statuses})"


@pytest.mark.parametrize("file_path", backlog_files)
def test_backlog_property_names_kebab_case(file_path):
    """All property names must use kebab-case."""
    item = parse_markdown_frontmatter(file_path)

    violations = [key for key in item.keys() if not is_kebab_case(key)]

    assert len(violations) == 0, \
        f"{file_path}: Non-kebab-case property names: {violations}"


@pytest.mark.parametrize("file_path", backlog_files)
def test_backlog_created_at_timestamp(file_path):
    """created-at must be valid ISO 8601 timestamp if present."""
    item = parse_markdown_frontmatter(file_path)

    if "created-at" in item:
        assert is_valid_iso_timestamp(item["created-at"]), \
            f"{file_path}: Invalid created-at timestamp: {item['created-at']}"


@pytest.mark.parametrize("file_path", backlog_files)
def test_backlog_modified_at_timestamp(file_path):
    """modified-at must be valid ISO 8601 timestamp if present."""
    item = parse_markdown_frontmatter(file_path)

    if "modified-at" in item:
        assert is_valid_iso_timestamp(item["modified-at"]), \
            f"{file_path}: Invalid modified-at timestamp: {item['modified-at']}"


@pytest.mark.parametrize("file_path", backlog_files)
def test_backlog_tags_is_list(file_path):
    """Tags must be a list if present."""
    item = parse_markdown_frontmatter(file_path)

    if "tags" in item:
        assert isinstance(item["tags"], list), \
            f"{file_path}: Tags must be list, got {type(item['tags'])}"


@pytest.mark.parametrize("file_path", backlog_files)
def test_backlog_category_kebab_case(file_path):
    """Category value must be kebab-case if present."""
    item = parse_markdown_frontmatter(file_path)

    if "category" in item and isinstance(item["category"], str):
        assert is_kebab_case(item["category"]), \
            f"{file_path}: Category '{item['category']}' is not kebab-case"


@pytest.mark.parametrize("file_path", backlog_files)
def test_backlog_estimate_format(file_path):
    """Estimate should be string if present (e.g., '2h', '1-2h', '30m')."""
    item = parse_markdown_frontmatter(file_path)

    if "estimate" in item:
        # Just verify it's a string - don't enforce specific format
        # Users may use various formats: "2h", "1-2h", "30m", "2-3 hours"
        assert isinstance(item["estimate"], str), \
            f"{file_path}: Estimate must be string, got {type(item['estimate'])}"

        assert len(item["estimate"]) > 0, \
            f"{file_path}: Estimate cannot be empty string"
