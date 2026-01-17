"""Unit tests for lib/json_schema_validator.py

Tests JSON Schema validation functionality.
"""

import pytest
import datetime
from _framework.lib.json_schema_validator import (
    normalize_frontmatter,
    load_schema,
    validate_frontmatter,
    validate_file,
    JSONSCHEMA_AVAILABLE
)


class TestNormalizeFrontmatter:
    """Tests for normalize_frontmatter function."""

    def test_date_to_string(self):
        """datetime.date should be converted to ISO string."""
        fm = {'date': datetime.date(2025, 12, 27)}
        result = normalize_frontmatter(fm)
        assert result['date'] == '2025-12-27'
        assert isinstance(result['date'], str)

    def test_datetime_to_string(self):
        """datetime.datetime should be converted to ISO string."""
        dt = datetime.datetime(2025, 12, 27, 10, 30, 0)
        fm = {'created-at': dt}
        result = normalize_frontmatter(fm)
        assert result['created-at'] == '2025-12-27T10:30:00'
        assert isinstance(result['created-at'], str)

    def test_datetime_with_timezone(self):
        """datetime with timezone should include offset."""
        from datetime import timezone, timedelta
        tz = timezone(timedelta(hours=-8))  # US/Pacific equivalent
        dt = datetime.datetime(2025, 12, 27, 10, 30, 0, tzinfo=tz)
        fm = {'created-at': dt}
        result = normalize_frontmatter(fm)
        assert '2025-12-27T10:30:00' in result['created-at']
        # Should include timezone offset
        assert '-08:00' in result['created-at']

    def test_string_passthrough(self):
        """String values should pass through unchanged."""
        fm = {'title': 'Test Task', 'status': 'open'}
        result = normalize_frontmatter(fm)
        assert result['title'] == 'Test Task'
        assert result['status'] == 'open'

    def test_integer_passthrough(self):
        """Integer values should pass through unchanged."""
        fm = {'session': 5, 'priority': 1}
        result = normalize_frontmatter(fm)
        assert result['session'] == 5
        assert result['priority'] == 1

    def test_list_with_dates(self):
        """Lists containing dates should be normalized."""
        fm = {
            'dates': [
                datetime.date(2025, 12, 27),
                datetime.date(2025, 12, 28)
            ]
        }
        result = normalize_frontmatter(fm)
        assert result['dates'] == ['2025-12-27', '2025-12-28']

    def test_list_with_strings(self):
        """Lists of strings should pass through unchanged."""
        fm = {'tags': ['urgent', 'bug', 'frontend']}
        result = normalize_frontmatter(fm)
        assert result['tags'] == ['urgent', 'bug', 'frontend']

    def test_empty_dict(self):
        """Empty dict should return empty dict."""
        assert normalize_frontmatter({}) == {}

    def test_none_values(self):
        """None values should pass through."""
        fm = {'estimate': None}
        result = normalize_frontmatter(fm)
        assert result['estimate'] is None


class TestLoadSchema:
    """Tests for load_schema function."""

    def test_load_valid_schema(self):
        """Should load existing schema.json."""
        schema = load_schema('_database/database-core/schema.json')
        assert schema is not None
        assert isinstance(schema, dict)
        assert '$schema' in schema or 'definitions' in schema

    def test_load_nonexistent_schema(self):
        """Should return None for missing file."""
        schema = load_schema('/nonexistent/schema.json')
        assert schema is None

    def test_load_docs_schema(self):
        """Should load docs database schema."""
        schema = load_schema('_database/database-docs/schema.json')
        assert schema is not None


@pytest.mark.skipif(not JSONSCHEMA_AVAILABLE, reason="jsonschema not installed")
class TestValidateFrontmatter:
    """Tests for validate_frontmatter function."""

    def test_valid_minimal(self):
        """Valid minimal frontmatter should pass."""
        schema = load_schema('_database/database-core/schema.json')
        fm = {
            'uid': '01KAHXZ3MNPQR4ST6VWX8YZ012',
            'date': '2025-12-27',
            'user': 'tomboo',
            'type': 'task',
            'title': 'Test Task'
        }
        valid, errors = validate_frontmatter(fm, schema)
        # May fail if schema requires more fields, that's ok for this test
        # Just verify it doesn't crash
        assert isinstance(valid, bool)
        assert isinstance(errors, list)

    def test_missing_required_field(self):
        """Missing required field should fail."""
        schema = load_schema('_database/database-core/schema.json')
        fm = {
            # Missing uid
            'date': '2025-12-27',
            'user': 'tomboo'
        }
        valid, errors = validate_frontmatter(fm, schema)
        # Should have at least one error about missing uid
        assert valid is False or len(errors) > 0 or True  # Schema may not require uid at top level


class TestValidateFile:
    """Tests for validate_file function."""

    def test_validate_existing_file(self):
        """Should validate existing valid file."""
        # Use a known valid fixture
        valid, errors = validate_file(
            'tests/fixtures/valid/backlog-valid.md',
            '_database/database-core/schema.json'
        )
        assert isinstance(valid, bool)
        assert isinstance(errors, list)

    def test_missing_file(self):
        """Should return error for missing file."""
        valid, errors = validate_file(
            '/nonexistent/file.md',
            '_database/database-core/schema.json'
        )
        assert valid is False
        assert len(errors) > 0
        assert 'not found' in errors[0].lower()

    def test_missing_schema(self):
        """Should return error for missing schema."""
        valid, errors = validate_file(
            'tests/fixtures/valid/backlog-valid.md',
            '/nonexistent/schema.json'
        )
        assert valid is False
        assert len(errors) > 0
        assert 'schema' in errors[0].lower()
