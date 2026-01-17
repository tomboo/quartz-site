"""Unit tests for YouTube schema validation.

Tests YouTube queue items and content storage schema compliance.
"""

import pytest
import json
from pathlib import Path
from jsonschema import validate, ValidationError, Draft202012Validator
from jsonschema.validators import RefResolver


# Load schemas
SCHEMA_DIR = Path(__file__).parent.parent / "_framework" / "schemas"


def load_schema(name: str) -> dict:
    """Load a JSON schema file."""
    with open(SCHEMA_DIR / name) as f:
        return json.load(f)


@pytest.fixture
def core_schema():
    """Load the core schema."""
    return load_schema("core.schema.json")


@pytest.fixture
def youtube_schema():
    """Load the YouTube schema."""
    return load_schema("youtube.schema.json")


@pytest.fixture
def youtube_content_schema():
    """Load the YouTube content schema."""
    return load_schema("youtube-content.schema.json")


@pytest.fixture
def resolver(core_schema):
    """Create a schema resolver for $ref resolution."""
    schema_store = {
        "core.schema.json": core_schema,
    }
    return RefResolver.from_schema(core_schema, store=schema_store)


class TestYouTubeQueueSchema:
    """Tests for YouTube queue item schema."""

    def test_valid_minimal_item(self, youtube_schema, resolver):
        """Minimal valid YouTube queue item."""
        item = {
            "type": "youtube",
            "user": "tomboo",
            "title": "Test Video",
            "created-at": "2026-01-15T10:00:00-08:00",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "video-id": "dQw4w9WgXcQ",
        }
        validate(item, youtube_schema, resolver=resolver)

    def test_valid_full_item(self, youtube_schema, resolver):
        """Fully populated YouTube queue item."""
        item = {
            "type": "youtube",
            "user": "tomboo",
            "title": "Complete Video",
            "created-at": "2026-01-15T10:00:00-08:00",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "video-id": "dQw4w9WgXcQ",
            "status": "watched",
            "priority": 1,
            "channel": "Test Channel",
            "duration": "PT15M30S",
            "category": "learning",
            "watched-at": "2026-01-15T12:00:00-08:00",
            "rating": 5,
            "description": "A brief description",
            "synopsis": "Detailed summary of the video",
            "content-file": "[[../../content-storage/youtube/dQw4w9WgXcQ]]",
            "tags": ["test", "video"],
        }
        validate(item, youtube_schema, resolver=resolver)

    def test_missing_required_user(self, youtube_schema, resolver):
        """Missing required user field."""
        item = {
            "type": "youtube",
            "title": "Test Video",
            "created-at": "2026-01-15T10:00:00-08:00",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "video-id": "dQw4w9WgXcQ",
        }
        with pytest.raises(ValidationError):
            validate(item, youtube_schema, resolver=resolver)

    def test_missing_required_title(self, youtube_schema, resolver):
        """Missing required title field."""
        item = {
            "type": "youtube",
            "user": "tomboo",
            "created-at": "2026-01-15T10:00:00-08:00",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "video-id": "dQw4w9WgXcQ",
        }
        with pytest.raises(ValidationError):
            validate(item, youtube_schema, resolver=resolver)

    def test_missing_required_url(self, youtube_schema, resolver):
        """Missing required url field."""
        item = {
            "type": "youtube",
            "user": "tomboo",
            "title": "Test Video",
            "created-at": "2026-01-15T10:00:00-08:00",
            "video-id": "dQw4w9WgXcQ",
        }
        with pytest.raises(ValidationError):
            validate(item, youtube_schema, resolver=resolver)

    def test_missing_required_video_id(self, youtube_schema, resolver):
        """Missing required video-id field."""
        item = {
            "type": "youtube",
            "user": "tomboo",
            "title": "Test Video",
            "created-at": "2026-01-15T10:00:00-08:00",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
        }
        with pytest.raises(ValidationError):
            validate(item, youtube_schema, resolver=resolver)

    def test_invalid_video_id_too_short(self, youtube_schema, resolver):
        """Video ID shorter than 11 characters."""
        item = {
            "type": "youtube",
            "user": "tomboo",
            "title": "Test Video",
            "created-at": "2026-01-15T10:00:00-08:00",
            "url": "https://youtube.com/watch?v=abc123",
            "video-id": "abc123",
        }
        with pytest.raises(ValidationError):
            validate(item, youtube_schema, resolver=resolver)

    def test_invalid_video_id_too_long(self, youtube_schema, resolver):
        """Video ID longer than 11 characters."""
        item = {
            "type": "youtube",
            "user": "tomboo",
            "title": "Test Video",
            "created-at": "2026-01-15T10:00:00-08:00",
            "url": "https://youtube.com/watch?v=abcdefghijkl",
            "video-id": "abcdefghijkl",
        }
        with pytest.raises(ValidationError):
            validate(item, youtube_schema, resolver=resolver)

    def test_valid_video_id_with_special_chars(self, youtube_schema, resolver):
        """Video ID with dashes and underscores."""
        item = {
            "type": "youtube",
            "user": "tomboo",
            "title": "Test Video",
            "created-at": "2026-01-15T10:00:00-08:00",
            "url": "https://youtube.com/watch?v=abc-def_123",
            "video-id": "abc-def_123",
        }
        validate(item, youtube_schema, resolver=resolver)

    def test_valid_status_queued(self, youtube_schema, resolver):
        """Valid status: queued."""
        item = {
            "type": "youtube",
            "user": "tomboo",
            "title": "Test Video",
            "created-at": "2026-01-15T10:00:00-08:00",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "video-id": "dQw4w9WgXcQ",
            "status": "queued",
        }
        validate(item, youtube_schema, resolver=resolver)

    def test_valid_status_watching(self, youtube_schema, resolver):
        """Valid status: watching."""
        item = {
            "type": "youtube",
            "user": "tomboo",
            "title": "Test Video",
            "created-at": "2026-01-15T10:00:00-08:00",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "video-id": "dQw4w9WgXcQ",
            "status": "watching",
        }
        validate(item, youtube_schema, resolver=resolver)

    def test_valid_status_watched(self, youtube_schema, resolver):
        """Valid status: watched."""
        item = {
            "type": "youtube",
            "user": "tomboo",
            "title": "Test Video",
            "created-at": "2026-01-15T10:00:00-08:00",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "video-id": "dQw4w9WgXcQ",
            "status": "watched",
        }
        validate(item, youtube_schema, resolver=resolver)

    def test_valid_status_abandoned(self, youtube_schema, resolver):
        """Valid status: abandoned."""
        item = {
            "type": "youtube",
            "user": "tomboo",
            "title": "Test Video",
            "created-at": "2026-01-15T10:00:00-08:00",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "video-id": "dQw4w9WgXcQ",
            "status": "abandoned",
        }
        validate(item, youtube_schema, resolver=resolver)

    def test_invalid_status(self, youtube_schema, resolver):
        """Invalid status value."""
        item = {
            "type": "youtube",
            "user": "tomboo",
            "title": "Test Video",
            "created-at": "2026-01-15T10:00:00-08:00",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "video-id": "dQw4w9WgXcQ",
            "status": "invalid-status",
        }
        with pytest.raises(ValidationError):
            validate(item, youtube_schema, resolver=resolver)

    def test_valid_categories(self, youtube_schema, resolver):
        """All valid category values."""
        categories = ["learning", "entertainment", "research", "tutorial",
                      "news", "music", "podcast", "other"]
        for category in categories:
            item = {
                "type": "youtube",
                "user": "tomboo",
                "title": "Test Video",
                "created-at": "2026-01-15T10:00:00-08:00",
                "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
                "video-id": "dQw4w9WgXcQ",
                "category": category,
            }
            validate(item, youtube_schema, resolver=resolver)

    def test_invalid_category(self, youtube_schema, resolver):
        """Invalid category value."""
        item = {
            "type": "youtube",
            "user": "tomboo",
            "title": "Test Video",
            "created-at": "2026-01-15T10:00:00-08:00",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "video-id": "dQw4w9WgXcQ",
            "category": "invalid-category",
        }
        with pytest.raises(ValidationError):
            validate(item, youtube_schema, resolver=resolver)

    def test_valid_priority_values(self, youtube_schema, resolver):
        """Valid priority values 0-3."""
        for priority in [0, 1, 2, 3]:
            item = {
                "type": "youtube",
                "user": "tomboo",
                "title": "Test Video",
                "created-at": "2026-01-15T10:00:00-08:00",
                "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
                "video-id": "dQw4w9WgXcQ",
                "priority": priority,
            }
            validate(item, youtube_schema, resolver=resolver)

    def test_valid_rating_values(self, youtube_schema, resolver):
        """Valid rating values 1-5."""
        for rating in [1, 2, 3, 4, 5]:
            item = {
                "type": "youtube",
                "user": "tomboo",
                "title": "Test Video",
                "created-at": "2026-01-15T10:00:00-08:00",
                "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
                "video-id": "dQw4w9WgXcQ",
                "rating": rating,
            }
            validate(item, youtube_schema, resolver=resolver)

    def test_invalid_rating_zero(self, youtube_schema, resolver):
        """Rating of 0 is invalid."""
        item = {
            "type": "youtube",
            "user": "tomboo",
            "title": "Test Video",
            "created-at": "2026-01-15T10:00:00-08:00",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "video-id": "dQw4w9WgXcQ",
            "rating": 0,
        }
        with pytest.raises(ValidationError):
            validate(item, youtube_schema, resolver=resolver)

    def test_invalid_rating_six(self, youtube_schema, resolver):
        """Rating of 6 is invalid."""
        item = {
            "type": "youtube",
            "user": "tomboo",
            "title": "Test Video",
            "created-at": "2026-01-15T10:00:00-08:00",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "video-id": "dQw4w9WgXcQ",
            "rating": 6,
        }
        with pytest.raises(ValidationError):
            validate(item, youtube_schema, resolver=resolver)

    def test_null_rating_valid(self, youtube_schema, resolver):
        """Null rating is valid."""
        item = {
            "type": "youtube",
            "user": "tomboo",
            "title": "Test Video",
            "created-at": "2026-01-15T10:00:00-08:00",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "video-id": "dQw4w9WgXcQ",
            "rating": None,
        }
        validate(item, youtube_schema, resolver=resolver)

    def test_valid_duration_format(self, youtube_schema, resolver):
        """Valid ISO 8601 duration."""
        item = {
            "type": "youtube",
            "user": "tomboo",
            "title": "Test Video",
            "created-at": "2026-01-15T10:00:00-08:00",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "video-id": "dQw4w9WgXcQ",
            "duration": "PT1H30M45S",
        }
        validate(item, youtube_schema, resolver=resolver)

    def test_valid_youtu_be_url(self, youtube_schema, resolver):
        """Valid youtu.be short URL."""
        item = {
            "type": "youtube",
            "user": "tomboo",
            "title": "Test Video",
            "created-at": "2026-01-15T10:00:00-08:00",
            "url": "https://youtu.be/dQw4w9WgXcQ",
            "video-id": "dQw4w9WgXcQ",
        }
        validate(item, youtube_schema, resolver=resolver)


class TestYouTubeContentSchema:
    """Tests for YouTube content storage schema."""

    def test_valid_minimal_content(self, youtube_content_schema, resolver):
        """Minimal valid content file."""
        content = {
            "type": "youtube-content",
            "content-id": "dQw4w9WgXcQ",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "fetched-at": "2026-01-15T10:00:00-08:00",
            "title": "Test Video",
            "channel": "Test Channel",
        }
        validate(content, youtube_content_schema, resolver=resolver)

    def test_valid_full_content(self, youtube_content_schema, resolver):
        """Fully populated content file."""
        content = {
            "type": "youtube-content",
            "content-id": "dQw4w9WgXcQ",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "fetched-at": "2026-01-15T10:00:00-08:00",
            "title": "Test Video",
            "channel": "Test Channel",
            "channel-url": "https://youtube.com/@testchannel",
            "duration": "PT5M30S",
            "upload-date": "2025-06-15",
            "view-count": 1000000,
            "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
        }
        validate(content, youtube_content_schema, resolver=resolver)

    def test_missing_required_content_id(self, youtube_content_schema, resolver):
        """Missing required content-id field."""
        content = {
            "type": "youtube-content",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "fetched-at": "2026-01-15T10:00:00-08:00",
            "title": "Test Video",
            "channel": "Test Channel",
        }
        with pytest.raises(ValidationError):
            validate(content, youtube_content_schema, resolver=resolver)

    def test_missing_required_url(self, youtube_content_schema, resolver):
        """Missing required url field."""
        content = {
            "type": "youtube-content",
            "content-id": "dQw4w9WgXcQ",
            "fetched-at": "2026-01-15T10:00:00-08:00",
            "title": "Test Video",
            "channel": "Test Channel",
        }
        with pytest.raises(ValidationError):
            validate(content, youtube_content_schema, resolver=resolver)

    def test_missing_required_fetched_at(self, youtube_content_schema, resolver):
        """Missing required fetched-at field."""
        content = {
            "type": "youtube-content",
            "content-id": "dQw4w9WgXcQ",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "title": "Test Video",
            "channel": "Test Channel",
        }
        with pytest.raises(ValidationError):
            validate(content, youtube_content_schema, resolver=resolver)

    def test_missing_required_title(self, youtube_content_schema, resolver):
        """Missing required title field."""
        content = {
            "type": "youtube-content",
            "content-id": "dQw4w9WgXcQ",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "fetched-at": "2026-01-15T10:00:00-08:00",
            "channel": "Test Channel",
        }
        with pytest.raises(ValidationError):
            validate(content, youtube_content_schema, resolver=resolver)

    def test_missing_required_channel(self, youtube_content_schema, resolver):
        """Missing required channel field."""
        content = {
            "type": "youtube-content",
            "content-id": "dQw4w9WgXcQ",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "fetched-at": "2026-01-15T10:00:00-08:00",
            "title": "Test Video",
        }
        with pytest.raises(ValidationError):
            validate(content, youtube_content_schema, resolver=resolver)

    def test_invalid_content_id_pattern(self, youtube_content_schema, resolver):
        """Invalid content-id pattern."""
        content = {
            "type": "youtube-content",
            "content-id": "invalid",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "fetched-at": "2026-01-15T10:00:00-08:00",
            "title": "Test Video",
            "channel": "Test Channel",
        }
        with pytest.raises(ValidationError):
            validate(content, youtube_content_schema, resolver=resolver)

    def test_valid_view_count(self, youtube_content_schema, resolver):
        """Valid view count."""
        content = {
            "type": "youtube-content",
            "content-id": "dQw4w9WgXcQ",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "fetched-at": "2026-01-15T10:00:00-08:00",
            "title": "Test Video",
            "channel": "Test Channel",
            "view-count": 0,
        }
        validate(content, youtube_content_schema, resolver=resolver)

    def test_invalid_negative_view_count(self, youtube_content_schema, resolver):
        """Negative view count is invalid."""
        content = {
            "type": "youtube-content",
            "content-id": "dQw4w9WgXcQ",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "fetched-at": "2026-01-15T10:00:00-08:00",
            "title": "Test Video",
            "channel": "Test Channel",
            "view-count": -1,
        }
        with pytest.raises(ValidationError):
            validate(content, youtube_content_schema, resolver=resolver)

    def test_null_channel_url_valid(self, youtube_content_schema, resolver):
        """Null channel-url is valid."""
        content = {
            "type": "youtube-content",
            "content-id": "dQw4w9WgXcQ",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "fetched-at": "2026-01-15T10:00:00-08:00",
            "title": "Test Video",
            "channel": "Test Channel",
            "channel-url": None,
        }
        validate(content, youtube_content_schema, resolver=resolver)

    def test_null_view_count_valid(self, youtube_content_schema, resolver):
        """Null view-count is valid."""
        content = {
            "type": "youtube-content",
            "content-id": "dQw4w9WgXcQ",
            "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "fetched-at": "2026-01-15T10:00:00-08:00",
            "title": "Test Video",
            "channel": "Test Channel",
            "view-count": None,
        }
        validate(content, youtube_content_schema, resolver=resolver)
