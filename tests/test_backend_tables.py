"""Comprehensive integration tests for all _database/ tables.

Tests every file in _database/*-table/ for schema compliance.
"""

import glob
import pytest
from conftest import (
    parse_markdown_frontmatter,
    is_valid_ulid,
    is_kebab_case,
    is_valid_date,
    is_valid_iso_timestamp
)


# =============================================================================
# Table Configurations
# =============================================================================

TABLE_CONFIGS = {
    "tasks": {
        "path": "_database/database-core/tasks-table/task-*.md",
        "type": "task",
        "required": ["uid", "user", "type", "title"],
        "valid_status": ["open", "completed", "canceled"],
        "valid_priority": ["p0", "p1", "p2", "p3"],
    },
    "backlog": {
        "path": "_database/database-core/backlog-table/backlog-*.md",
        "type": "backlog",
        "required": ["uid", "date", "user", "title"],
        "valid_status": ["open", "not-started", "in-progress", "completed", "canceled", "blocked"],
        "valid_priority": ["p0", "p1", "p2", "p3"],
    },
    "sessions": {
        "path": "_database/database-core/sessions-table/session-*.md",
        "type": None,  # Sessions don't have type property
        "required": ["uid", "date", "user", "session"],
    },
    "projects": {
        "path": "_database/database-core/projects-table/project-*.md",
        "type": "project",
        "required": ["uid", "date", "user", "type", "title"],
        "valid_status": ["open", "active", "planned", "completed", "on-hold", "canceled", "archived"],
    },
    "areas": {
        "path": "_database/database-core/areas-table/area-*.md",
        "type": "area",
        "required": ["uid", "user", "type", "title"],
    },
    "subscriptions": {
        "path": "_database/database-core/subscriptions-table/subscription-*.md",
        "type": "subscription",
        "required": ["uid", "date", "user", "type", "title"],
        "valid_status": ["active", "paused", "cancelled", "trial"],
        "valid_frequency": ["weekly", "monthly", "quarterly", "yearly"],
    },
    "notes": {
        "path": "_database/database-core/notes-table/note-*.md",
        "type": "note",
        "required": ["uid", "date", "user", "type", "title"],
        "valid_status": ["draft", "active", "archived"],
        "valid_category": ["learning", "personal", "reference", "tools", "project"],
    },
    "daily-notes": {
        "path": "_database/database-core/daily-notes-table/2*.md",
        "type": "daily-note",
        "required": ["uid", "date", "user", "type"],
    },
    "apps": {
        "path": "_database/database-core/apps-table/app-*.md",
        "type": "app",
        "required": ["uid", "date", "user", "type", "title"],
    },
}


# =============================================================================
# Collect All Files
# =============================================================================

def get_all_database_files():
    """Collect all markdown files from all database tables."""
    files = []
    for config in TABLE_CONFIGS.values():
        files.extend(glob.glob(config["path"]))
    return files


def get_table_for_file(file_path):
    """Determine which table a file belongs to."""
    for table_name, config in TABLE_CONFIGS.items():
        if glob.fnmatch.fnmatch(file_path, config["path"]):
            return table_name, config
    return None, None


all_database_files = get_all_database_files()


# =============================================================================
# Common Property Tests (All Tables)
# =============================================================================

@pytest.mark.parametrize("file_path", all_database_files)
def test_has_uid(file_path):
    """Every database file must have a uid property."""
    item = parse_markdown_frontmatter(file_path)
    assert "uid" in item, f"{file_path}: Missing required property: uid"


@pytest.mark.parametrize("file_path", all_database_files)
def test_uid_is_valid_ulid(file_path):
    """UID must be valid ULID format (26 chars, Base32)."""
    item = parse_markdown_frontmatter(file_path)
    if "uid" in item:
        assert is_valid_ulid(item["uid"]), \
            f"{file_path}: Invalid ULID format: {item['uid']}"


@pytest.mark.parametrize("file_path", all_database_files)
def test_has_user(file_path):
    """Every database file must have a user property."""
    item = parse_markdown_frontmatter(file_path)
    assert "user" in item, f"{file_path}: Missing required property: user"


@pytest.mark.parametrize("file_path", all_database_files)
def test_property_names_kebab_case(file_path):
    """All property names must use kebab-case."""
    item = parse_markdown_frontmatter(file_path)
    violations = [key for key in item.keys() if not is_kebab_case(key)]
    assert len(violations) == 0, \
        f"{file_path}: Non-kebab-case property names: {violations}"


@pytest.mark.parametrize("file_path", all_database_files)
def test_date_format_if_present(file_path):
    """Date must be YYYY-MM-DD format if present."""
    item = parse_markdown_frontmatter(file_path)
    if "date" in item:
        assert is_valid_date(item["date"]), \
            f"{file_path}: Invalid date format: {item['date']}"


@pytest.mark.parametrize("file_path", all_database_files)
def test_tags_is_list_if_present(file_path):
    """Tags must be a list if present."""
    item = parse_markdown_frontmatter(file_path)
    if "tags" in item:
        assert isinstance(item["tags"], list), \
            f"{file_path}: Tags must be list, got {type(item['tags'])}"


@pytest.mark.parametrize("file_path", all_database_files)
def test_created_at_timestamp_if_present(file_path):
    """created-at must be ISO 8601 timestamp if present."""
    item = parse_markdown_frontmatter(file_path)
    if "created-at" in item:
        assert is_valid_iso_timestamp(item["created-at"]), \
            f"{file_path}: Invalid created-at: {item['created-at']}"


@pytest.mark.parametrize("file_path", all_database_files)
def test_modified_at_timestamp_if_present(file_path):
    """modified-at must be ISO 8601 timestamp if present."""
    item = parse_markdown_frontmatter(file_path)
    if "modified-at" in item:
        assert is_valid_iso_timestamp(item["modified-at"]), \
            f"{file_path}: Invalid modified-at: {item['modified-at']}"


# =============================================================================
# Type Property Tests
# =============================================================================

@pytest.mark.parametrize("file_path", all_database_files)
def test_type_matches_table(file_path):
    """Type property must match expected value for table."""
    table_name, config = get_table_for_file(file_path)
    if config and config.get("type"):
        item = parse_markdown_frontmatter(file_path)
        assert "type" in item, f"{file_path}: Missing type property"
        assert item["type"] == config["type"], \
            f"{file_path}: Expected type '{config['type']}', got '{item['type']}'"


# =============================================================================
# Status Validation Tests
# =============================================================================

@pytest.mark.parametrize("file_path", all_database_files)
def test_status_valid_values(file_path):
    """Status must be from valid list for table type."""
    table_name, config = get_table_for_file(file_path)
    if config and "valid_status" in config:
        item = parse_markdown_frontmatter(file_path)
        if "status" in item:
            assert item["status"] in config["valid_status"], \
                f"{file_path}: Invalid status '{item['status']}' (valid: {config['valid_status']})"


# =============================================================================
# Priority Validation Tests
# =============================================================================

@pytest.mark.parametrize("file_path", all_database_files)
def test_priority_valid_values(file_path):
    """Priority must be p0-p3 for tables that use it."""
    table_name, config = get_table_for_file(file_path)
    if config and "valid_priority" in config:
        item = parse_markdown_frontmatter(file_path)
        if "priority" in item:
            assert item["priority"] in config["valid_priority"], \
                f"{file_path}: Invalid priority '{item['priority']}' (valid: {config['valid_priority']})"


# =============================================================================
# Table-Specific Tests
# =============================================================================

# Tasks
task_files = glob.glob("_database/database-core/tasks-table/task-*.md")

@pytest.mark.parametrize("file_path", task_files)
def test_task_has_title(file_path):
    """Tasks must have title."""
    item = parse_markdown_frontmatter(file_path)
    assert "title" in item, f"{file_path}: Missing title"


# Sessions
session_files = glob.glob("_database/database-core/sessions-table/session-*.md")

@pytest.mark.parametrize("file_path", session_files)
def test_session_number_is_positive_int(file_path):
    """Session number must be positive integer."""
    item = parse_markdown_frontmatter(file_path)
    if "session" in item:
        assert isinstance(item["session"], int), \
            f"{file_path}: Session must be int, got {type(item['session'])}"
        assert item["session"] > 0, \
            f"{file_path}: Session must be positive"


@pytest.mark.parametrize("file_path", session_files)
def test_session_focus_is_list(file_path):
    """Focus must be a list."""
    item = parse_markdown_frontmatter(file_path)
    if "focus" in item:
        assert isinstance(item["focus"], list), \
            f"{file_path}: Focus must be list"


# Subscriptions
subscription_files = glob.glob("_database/database-core/subscriptions-table/subscription-*.md")

@pytest.mark.parametrize("file_path", subscription_files)
def test_subscription_amount_is_number(file_path):
    """Amount must be a number."""
    item = parse_markdown_frontmatter(file_path)
    if "amount" in item:
        assert isinstance(item["amount"], (int, float)), \
            f"{file_path}: Amount must be number, got {type(item['amount'])}"


@pytest.mark.parametrize("file_path", subscription_files)
def test_subscription_frequency_valid(file_path):
    """Frequency must be valid value."""
    item = parse_markdown_frontmatter(file_path)
    valid = ["weekly", "monthly", "quarterly", "yearly"]
    if "frequency" in item:
        assert item["frequency"] in valid, \
            f"{file_path}: Invalid frequency '{item['frequency']}'"


# Notes
note_files = glob.glob("_database/database-core/notes-table/note-*.md")

@pytest.mark.parametrize("file_path", note_files)
def test_note_status_valid(file_path):
    """Note status must be draft, active, or archived."""
    item = parse_markdown_frontmatter(file_path)
    valid = ["draft", "active", "archived"]
    if "status" in item:
        assert item["status"] in valid, \
            f"{file_path}: Invalid status '{item['status']}'"


# Areas
area_files = glob.glob("_database/database-core/areas-table/area-*.md")

@pytest.mark.parametrize("file_path", area_files)
def test_area_has_title(file_path):
    """Areas must have title."""
    item = parse_markdown_frontmatter(file_path)
    assert "title" in item, f"{file_path}: Missing title"


# Projects
project_files = glob.glob("_database/database-core/projects-table/project-*.md")

@pytest.mark.parametrize("file_path", project_files)
def test_project_has_title(file_path):
    """Projects must have title."""
    item = parse_markdown_frontmatter(file_path)
    assert "title" in item, f"{file_path}: Missing title"


# Daily Notes
daily_note_files = glob.glob("_database/database-core/daily-notes-table/2*.md")

@pytest.mark.parametrize("file_path", daily_note_files)
def test_daily_note_has_date(file_path):
    """Daily notes must have date."""
    item = parse_markdown_frontmatter(file_path)
    assert "date" in item, f"{file_path}: Missing date"


# Apps
app_files = glob.glob("_database/database-core/apps-table/app-*.md")

@pytest.mark.parametrize("file_path", app_files)
def test_app_has_title(file_path):
    """Apps must have title."""
    item = parse_markdown_frontmatter(file_path)
    assert "title" in item, f"{file_path}: Missing title"
