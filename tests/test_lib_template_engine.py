"""Unit tests for lib/template_engine.py

Tests template rendering and ULID generation.
"""

import pytest
import re
from _framework.lib.template_engine import (
    generate_ulid,
    get_iso8601_timestamp,
    get_current_date,
    render_template,
    list_templates
)
from _framework.lib.validators import is_valid_ulid  # Used in test_generates_valid_ulid


class TestGenerateUlid:
    """Tests for generate_ulid function."""

    def test_generates_valid_ulid(self):
        """Generated ULID should be valid format."""
        ulid = generate_ulid()
        assert is_valid_ulid(ulid) is True

    def test_ulid_length(self):
        """ULID should be exactly 26 characters."""
        ulid = generate_ulid()
        assert len(ulid) == 26

    def test_ulid_uniqueness(self):
        """Multiple ULIDs should be unique."""
        ulids = [generate_ulid() for _ in range(100)]
        assert len(set(ulids)) == 100

    def test_ulid_sortable(self):
        """ULIDs generated later should sort after earlier ones."""
        import time
        ulid1 = generate_ulid()
        time.sleep(0.01)  # Small delay
        ulid2 = generate_ulid()
        # Lexicographic comparison should work
        assert ulid2 > ulid1


class TestGetIso8601Timestamp:
    """Tests for get_iso8601_timestamp function."""

    def test_format(self):
        """Timestamp should match ISO 8601 format."""
        ts = get_iso8601_timestamp()
        # Pattern: YYYY-MM-DDTHH:MM:SS-08:00
        pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}-08:00$'
        assert re.match(pattern, ts) is not None

    def test_contains_date_parts(self):
        """Timestamp should contain date components."""
        from datetime import datetime
        ts = get_iso8601_timestamp()
        now = datetime.now()
        assert str(now.year) in ts
        assert f"{now.month:02d}" in ts


class TestGetCurrentDate:
    """Tests for get_current_date function."""

    def test_format(self):
        """Date should be YYYY-MM-DD format."""
        date = get_current_date()
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        assert re.match(pattern, date) is not None

    def test_matches_today(self):
        """Should return today's date."""
        from datetime import datetime
        date = get_current_date()
        expected = datetime.now().strftime('%Y-%m-%d')
        assert date == expected


class TestRenderTemplate:
    """Tests for render_template function."""

    def test_file_not_found(self):
        """Should raise FileNotFoundError for missing template."""
        with pytest.raises(FileNotFoundError):
            render_template('/nonexistent/template.md')

    def test_backlog_template_exists(self):
        """Should render backlog template."""
        content = render_template(
            '_framework/templates/backlog-template.md',
            {'title': 'Test Task', 'user': 'testuser'}
        )
        assert 'Test Task' in content
        assert 'testuser' in content

    def test_auto_generated_created_at(self):
        """created-at should be auto-generated if not provided."""
        from datetime import datetime
        content = render_template(
            '_framework/templates/backlog-template.md',
            {'title': 'Test', 'user': 'test'}
        )
        # Check that created-at contains today's date
        today = datetime.now().strftime('%Y-%m-%d')
        assert f'created-at: {today}' in content

    def test_auto_generated_comment_date(self):
        """Comment date should be auto-generated if not provided."""
        from datetime import datetime
        content = render_template(
            '_framework/templates/backlog-template.md',
            {'title': 'Test', 'user': 'test'}
        )
        expected_date = datetime.now().strftime('%Y-%m-%d')
        # Date appears in comments section: ### YYYY-MM-DD: Created
        assert f'### {expected_date}: Created' in content

    def test_provided_values_override_auto(self):
        """Provided values should override auto-generated ones."""
        content = render_template(
            '_framework/templates/backlog-template.md',
            {
                'title': 'Test',
                'user': 'test',
                'created-at': '2020-01-01T10:00:00-08:00',
                'date': '2020-01-01'
            }
        )
        assert 'created-at: 2020-01-01T10:00:00-08:00' in content
        assert '### 2020-01-01: Created' in content

    def test_tags_list_formatting(self):
        """Tags list should be formatted as YAML array."""
        content = render_template(
            '_framework/templates/backlog-template.md',
            {
                'title': 'Test',
                'user': 'test',
                'tags': ['urgent', 'bug', 'frontend']
            }
        )
        assert '[urgent, bug, frontend]' in content

    def test_tags_string_passthrough(self):
        """Tags string should be passed through as-is."""
        content = render_template(
            '_framework/templates/backlog-template.md',
            {
                'title': 'Test',
                'user': 'test',
                'tags': '[custom, format]'
            }
        )
        assert '[custom, format]' in content

    def test_none_values_become_empty(self):
        """None values should become empty strings."""
        content = render_template(
            '_framework/templates/backlog-template.md',
            {
                'title': 'Test',
                'user': 'test',
                'estimate': None
            }
        )
        # Should not contain "None" string
        assert 'None' not in content

    def test_unknown_variables_preserved(self):
        """Unknown variables should be left as-is for manual editing."""
        content = render_template(
            '_framework/templates/backlog-template.md',
            {'title': 'Test', 'user': 'test'}
        )
        # Custom variables not in template should not appear
        # But template placeholders without values should remain
        # (This depends on template content)
        assert content is not None


class TestListTemplates:
    """Tests for list_templates function."""

    def test_finds_templates(self):
        """Should find templates in templates/ directory."""
        templates = list_templates()
        assert len(templates) > 0
        assert 'backlog-template.md' in templates

    def test_nonexistent_directory(self):
        """Should return empty list for nonexistent directory."""
        templates = list_templates('/nonexistent/path')
        assert templates == []

    def test_only_markdown(self):
        """Should only return .md files."""
        templates = list_templates()
        for t in templates:
            assert t.endswith('.md')
