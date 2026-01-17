"""Naming convention tests for files, directories, and properties."""

import os
import glob
import pytest
from conftest import is_kebab_case, parse_markdown_frontmatter


# File naming exceptions (uppercase allowed)
FILE_EXCEPTIONS = {
    "README.md",
    "CLAUDE.md",
    "CHANGELOG.md",
    "Index.md"
}

# Directories to skip (special cases)
SKIP_DIRS = {
    ".git",
    ".obsidian",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
    "assets",  # May contain uploaded files with various naming
    "tmp",  # Archived/temporary content - not framework files
    "_database",  # Database backend - underscore prefix exception per user preference
    "_framework"  # Framework code - underscore prefix exception per user preference
}


def get_basename_without_ext(file_path):
    """Get filename without extension."""
    basename = os.path.basename(file_path)
    if '.' in basename:
        return basename.rsplit('.', 1)[0]
    return basename


def should_skip_path(path):
    """Check if path should be skipped in naming checks."""
    parts = path.split(os.sep)
    return any(skip_dir in parts for skip_dir in SKIP_DIRS)


# File naming tests

def test_markdown_files_are_kebab_case():
    """All markdown files should use kebab-case naming (except exceptions)."""
    all_md_files = glob.glob("**/*.md", recursive=True)

    violations = []
    for file_path in all_md_files:
        # Skip certain directories
        if should_skip_path(file_path):
            continue

        basename = os.path.basename(file_path)

        # Skip exceptions
        if basename in FILE_EXCEPTIONS:
            continue

        # Check if filename (without .md) is kebab-case
        name_without_ext = get_basename_without_ext(file_path)

        if not is_kebab_case(name_without_ext):
            violations.append(file_path)

    assert len(violations) == 0, \
        f"Files not following kebab-case naming:\n  " + "\n  ".join(violations)


def test_directories_are_kebab_case():
    """All directories should use kebab-case naming."""
    violations = []

    # Walk through all directories
    for root, dirs, _ in os.walk("."):
        # Filter out skip dirs
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for dir_name in dirs:
            # Skip hidden directories
            if dir_name.startswith('.'):
                continue

            # Check if directory name is kebab-case
            if not is_kebab_case(dir_name):
                dir_path = os.path.join(root, dir_name)
                violations.append(dir_path)

    assert len(violations) == 0, \
        f"Directories not following kebab-case naming:\n  " + "\n  ".join(violations)


def test_no_spaces_in_filenames():
    """Filenames should not contain spaces."""
    all_files = glob.glob("**/*", recursive=True)

    violations = []
    for file_path in all_files:
        if should_skip_path(file_path):
            continue

        basename = os.path.basename(file_path)

        # Skip if it's a directory
        if os.path.isdir(file_path):
            continue

        if ' ' in basename:
            violations.append(file_path)

    assert len(violations) == 0, \
        f"Files with spaces in name:\n  " + "\n  ".join(violations)


# Property naming tests

def test_backlog_property_names_kebab_case():
    """All backlog item properties should use kebab-case."""
    backlog_files = glob.glob("planning/backlog/backlog-*.md")

    violations = []
    for file_path in backlog_files:
        item = parse_markdown_frontmatter(file_path)

        for prop_name in item.keys():
            if not is_kebab_case(prop_name):
                violations.append(f"{file_path}: property '{prop_name}' is not kebab-case")

    assert len(violations) == 0, \
        f"Property naming violations:\n  " + "\n  ".join(violations)


def test_session_property_names_kebab_case():
    """All session note properties should use kebab-case."""
    session_files = glob.glob("planning/sessions/session-*.md")

    violations = []
    for file_path in session_files:
        item = parse_markdown_frontmatter(file_path)

        for prop_name in item.keys():
            if not is_kebab_case(prop_name):
                violations.append(f"{file_path}: property '{prop_name}' is not kebab-case")

    assert len(violations) == 0, \
        f"Property naming violations:\n  " + "\n  ".join(violations)


# Property value tests

def test_backlog_status_values_kebab_case():
    """Backlog status values should use kebab-case."""
    backlog_files = glob.glob("planning/backlog/backlog-*.md")

    violations = []
    for file_path in backlog_files:
        item = parse_markdown_frontmatter(file_path)

        if "status" in item:
            status = item["status"]
            if isinstance(status, str) and not is_kebab_case(status):
                violations.append(f"{file_path}: status '{status}' is not kebab-case")

    assert len(violations) == 0, \
        f"Status value violations:\n  " + "\n  ".join(violations)


def test_backlog_category_values_kebab_case():
    """Backlog category values should use kebab-case."""
    backlog_files = glob.glob("planning/backlog/backlog-*.md")

    violations = []
    for file_path in backlog_files:
        item = parse_markdown_frontmatter(file_path)

        if "category" in item:
            category = item["category"]
            if isinstance(category, str) and not is_kebab_case(category):
                violations.append(f"{file_path}: category '{category}' is not kebab-case")

    assert len(violations) == 0, \
        f"Category value violations:\n  " + "\n  ".join(violations)


def test_priority_values_use_new_format():
    """Priority values should use p0/p1/p2/p3 format, not old kebab-case."""
    all_app_files = (
        glob.glob("planning/backlog/backlog-*.md") +
        glob.glob("planning/sessions/session-*.md")
    )

    valid_priorities = ["p0", "p1", "p2", "p3"]
    old_format_violations = []

    for file_path in all_app_files:
        item = parse_markdown_frontmatter(file_path)

        if "priority" in item:
            priority = item["priority"]

            # Check if using old format (critical, high, medium, low)
            if priority in ["critical", "high", "medium", "low"]:
                old_format_violations.append(
                    f"{file_path}: priority '{priority}' uses old format (should be p0/p1/p2/p3)"
                )

            # Check if using invalid value
            elif priority not in valid_priorities:
                old_format_violations.append(
                    f"{file_path}: priority '{priority}' is invalid (must be p0/p1/p2/p3)"
                )

    assert len(old_format_violations) == 0, \
        f"Priority format violations:\n  " + "\n  ".join(old_format_violations)


# Test fixture naming

def test_fixture_files_are_kebab_case():
    """Fixture files should follow kebab-case naming."""
    fixture_files = glob.glob("tests/fixtures/**/*.md", recursive=True)

    violations = []
    for file_path in fixture_files:
        basename = os.path.basename(file_path)
        name_without_ext = get_basename_without_ext(file_path)

        if not is_kebab_case(name_without_ext):
            violations.append(file_path)

    assert len(violations) == 0, \
        f"Fixture files not following kebab-case:\n  " + "\n  ".join(violations)


# Pattern compliance tests

def test_backlog_files_follow_naming_pattern():
    """Backlog files should follow pattern: backlog-YYYYMMDD-NNN.md"""
    import re

    backlog_files = glob.glob("planning/backlog/backlog-*.md")

    pattern = r'^backlog-\d{8}-\d{3}\.md$'
    violations = []

    for file_path in backlog_files:
        basename = os.path.basename(file_path)

        if not re.match(pattern, basename):
            violations.append(f"{file_path}: doesn't match pattern backlog-YYYYMMDD-NNN.md")

    assert len(violations) == 0, \
        f"Backlog filename pattern violations:\n  " + "\n  ".join(violations)


def test_session_files_follow_naming_pattern():
    """Session files should follow pattern: session-YYYYMMDD-NNN.md"""
    import re

    session_files = glob.glob("planning/sessions/session-*.md")

    pattern = r'^session-\d{8}-\d{3}\.md$'
    violations = []

    for file_path in session_files:
        basename = os.path.basename(file_path)

        if not re.match(pattern, basename):
            violations.append(f"{file_path}: doesn't match pattern session-YYYYMMDD-NNN.md")

    assert len(violations) == 0, \
        f"Session filename pattern violations:\n  " + "\n  ".join(violations)


# Special file tests

def test_readme_files_uppercase():
    """README.md files should be uppercase (not readme.md)."""
    # On case-insensitive filesystems (macOS), glob matches both cases
    # We need to check the actual basename case
    all_readme_files = glob.glob("**/[Rr][Ee][Aa][Dd][Mm][Ee].md", recursive=True)

    violations = []
    for file_path in all_readme_files:
        if should_skip_path(file_path):
            continue

        basename = os.path.basename(file_path)
        # Check if the actual basename is lowercase
        if basename == "readme.md":
            violations.append(file_path)

    assert len(violations) == 0, \
        f"Found lowercase readme.md files (should be README.md):\n  " + "\n  ".join(violations)


def test_test_files_follow_pattern():
    """Test files should follow pattern: test_*.py"""
    import re

    test_files = glob.glob("tests/test_*.py")

    pattern = r'^test_[a-z_]+\.py$'
    violations = []

    for file_path in test_files:
        basename = os.path.basename(file_path)

        if not re.match(pattern, basename):
            violations.append(f"{file_path}: doesn't match pattern test_*.py")

    assert len(violations) == 0, \
        f"Test file naming violations:\n  " + "\n  ".join(violations)
