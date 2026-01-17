"""Shared pytest fixtures and utility functions for vault testing.

This module imports validators from lib/ and provides pytest fixtures for testing.
The validators themselves are now in lib/ for reuse by /health-check and other tools.
"""

import pytest

# Import validators from _framework/lib/ (shared with /health-check)
from _framework.lib.validators import (
    parse_markdown_frontmatter,
    is_valid_ulid,
    is_kebab_case,
    is_valid_date,
    is_valid_iso_timestamp
)


# Fixtures for valid examples

@pytest.fixture
def valid_backlog():
    """Load valid backlog fixture."""
    return parse_markdown_frontmatter("tests/fixtures/valid/backlog-valid.md")


@pytest.fixture
def valid_session():
    """Load valid session fixture."""
    return parse_markdown_frontmatter("tests/fixtures/valid/session-valid.md")


# Fixtures for invalid examples

@pytest.fixture
def backlog_no_uid():
    """Load backlog with missing UID."""
    return parse_markdown_frontmatter("tests/fixtures/invalid/backlog-no-uid.md")


@pytest.fixture
def backlog_wrong_priority():
    """Load backlog with invalid priority value."""
    return parse_markdown_frontmatter("tests/fixtures/invalid/backlog-wrong-priority.md")
