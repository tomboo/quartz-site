"""Unit tests for _framework/lib/youtube_fetcher.py

Tests YouTube URL parsing, duration conversion, and health check functions.
"""

import pytest
import tempfile
from pathlib import Path

from unittest.mock import patch, MagicMock
from _framework.lib.youtube_fetcher import (
    extract_video_id,
    seconds_to_duration,
    format_timestamp,
    check_youtube_health,
    create_content_file,
    DEFAULT_TRANSCRIPT_CATEGORIES,
)


class TestExtractVideoId:
    """Tests for extract_video_id function."""

    def test_youtube_watch_url(self):
        """Parse standard youtube.com/watch URL."""
        video_id = extract_video_id("https://youtube.com/watch?v=dQw4w9WgXcQ")
        assert video_id == "dQw4w9WgXcQ"

    def test_youtube_watch_url_with_www(self):
        """Parse youtube.com URL with www prefix."""
        video_id = extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert video_id == "dQw4w9WgXcQ"

    def test_youtu_be_short_url(self):
        """Parse youtu.be short URL."""
        video_id = extract_video_id("https://youtu.be/dQw4w9WgXcQ")
        assert video_id == "dQw4w9WgXcQ"

    def test_youtube_embed_url(self):
        """Parse youtube.com/embed URL."""
        video_id = extract_video_id("https://youtube.com/embed/dQw4w9WgXcQ")
        assert video_id == "dQw4w9WgXcQ"

    def test_url_with_additional_params(self):
        """Parse URL with additional query parameters."""
        video_id = extract_video_id("https://youtu.be/dQw4w9WgXcQ?si=BEJ5KmHTB6X3vS90")
        assert video_id == "dQw4w9WgXcQ"

    def test_url_with_timestamp(self):
        """Parse URL with timestamp parameter."""
        video_id = extract_video_id("https://youtube.com/watch?v=dQw4w9WgXcQ&t=42s")
        assert video_id == "dQw4w9WgXcQ"

    def test_raw_video_id(self):
        """Parse raw 11-character video ID."""
        video_id = extract_video_id("dQw4w9WgXcQ")
        assert video_id == "dQw4w9WgXcQ"

    def test_video_id_with_dash(self):
        """Parse video ID containing dash."""
        video_id = extract_video_id("abc-def_123")
        assert video_id == "abc-def_123"

    def test_video_id_with_underscore(self):
        """Parse video ID containing underscore."""
        video_id = extract_video_id("abc_def-123")
        assert video_id == "abc_def-123"

    def test_invalid_url_raises(self):
        """Invalid URL raises ValueError."""
        with pytest.raises(ValueError):
            extract_video_id("https://example.com/not-youtube")

    def test_too_short_id_raises(self):
        """ID shorter than 11 chars raises ValueError."""
        with pytest.raises(ValueError):
            extract_video_id("abc123")

    def test_too_long_id_raises(self):
        """ID longer than 11 chars (not a URL) raises ValueError."""
        with pytest.raises(ValueError):
            extract_video_id("abcdefghijkl")  # 12 chars


class TestSecondsToDuration:
    """Tests for seconds_to_duration function."""

    def test_zero_seconds(self):
        """Zero seconds returns 0:00."""
        assert seconds_to_duration(0) == "0:00"

    def test_negative_seconds(self):
        """Negative seconds returns 0:00."""
        assert seconds_to_duration(-10) == "0:00"

    def test_seconds_only(self):
        """Seconds less than 60."""
        assert seconds_to_duration(45) == "0:45"

    def test_one_minute(self):
        """Exactly one minute."""
        assert seconds_to_duration(60) == "1:00"

    def test_minutes_and_seconds(self):
        """Minutes and seconds."""
        assert seconds_to_duration(90) == "1:30"

    def test_one_hour(self):
        """Exactly one hour."""
        assert seconds_to_duration(3600) == "1:00:00"

    def test_hours_and_minutes(self):
        """Hours and minutes."""
        assert seconds_to_duration(3660) == "1:01:00"

    def test_hours_minutes_seconds(self):
        """Hours, minutes, and seconds."""
        assert seconds_to_duration(3661) == "1:01:01"

    def test_multiple_hours(self):
        """Multiple hours."""
        assert seconds_to_duration(7200) == "2:00:00"

    def test_typical_video_duration(self):
        """Typical video duration (7:25)."""
        assert seconds_to_duration(445) == "7:25"

    def test_long_video(self):
        """Long video (1:30:45)."""
        assert seconds_to_duration(5445) == "1:30:45"


class TestFormatTimestamp:
    """Tests for format_timestamp function."""

    def test_zero_seconds(self):
        """Zero seconds."""
        assert format_timestamp(0) == "0:00"

    def test_seconds_only(self):
        """Less than one minute."""
        assert format_timestamp(45) == "0:45"

    def test_one_minute(self):
        """Exactly one minute."""
        assert format_timestamp(60) == "1:00"

    def test_minutes_and_seconds(self):
        """Minutes and seconds."""
        assert format_timestamp(90) == "1:30"

    def test_double_digit_minutes(self):
        """Double digit minutes."""
        assert format_timestamp(600) == "10:00"

    def test_one_hour(self):
        """Exactly one hour."""
        assert format_timestamp(3600) == "1:00:00"

    def test_hours_and_minutes(self):
        """Hours and minutes."""
        assert format_timestamp(3660) == "1:01:00"

    def test_hours_minutes_seconds(self):
        """Hours, minutes, and seconds."""
        assert format_timestamp(3661) == "1:01:01"

    def test_typical_chapter_time(self):
        """Typical chapter timestamp."""
        assert format_timestamp(330) == "5:30"

    def test_float_input(self):
        """Float input (from chapter data)."""
        assert format_timestamp(330.5) == "5:30"


class TestDefaultTranscriptCategories:
    """Tests for DEFAULT_TRANSCRIPT_CATEGORIES constant and category matching."""

    def test_default_categories_exist(self):
        """Default transcript categories are defined."""
        assert DEFAULT_TRANSCRIPT_CATEGORIES is not None
        assert isinstance(DEFAULT_TRANSCRIPT_CATEGORIES, list)
        assert len(DEFAULT_TRANSCRIPT_CATEGORIES) > 0

    def test_learning_in_defaults(self):
        """Learning category is in defaults."""
        assert "learning" in DEFAULT_TRANSCRIPT_CATEGORIES

    def test_tutorial_in_defaults(self):
        """Tutorial category is in defaults."""
        assert "tutorial" in DEFAULT_TRANSCRIPT_CATEGORIES

    def test_research_in_defaults(self):
        """Research category is in defaults."""
        assert "research" in DEFAULT_TRANSCRIPT_CATEGORIES

    def test_entertainment_not_in_defaults(self):
        """Entertainment category is NOT in defaults."""
        assert "entertainment" not in DEFAULT_TRANSCRIPT_CATEGORIES

    def test_music_not_in_defaults(self):
        """Music category is NOT in defaults."""
        assert "music" not in DEFAULT_TRANSCRIPT_CATEGORIES

    def test_category_matching_case_insensitive(self):
        """Category matching should be case-insensitive (tested via logic)."""
        # Test the logic that create_content_file uses
        category = "Learning"  # Mixed case
        cats = DEFAULT_TRANSCRIPT_CATEGORIES
        # The matching logic: category.lower() in [c.lower() for c in cats]
        should_match = category.lower() in [c.lower() for c in cats]
        assert should_match is True

    def test_category_matching_exact(self):
        """Exact category matching."""
        category = "learning"
        cats = DEFAULT_TRANSCRIPT_CATEGORIES
        should_match = category.lower() in [c.lower() for c in cats]
        assert should_match is True

    def test_category_not_matching(self):
        """Non-matching category."""
        category = "entertainment"
        cats = DEFAULT_TRANSCRIPT_CATEGORIES
        should_match = category.lower() in [c.lower() for c in cats]
        assert should_match is False


class TestCreateContentFileTranscript:
    """Tests for create_content_file transcript handling."""

    @patch('_framework.lib.youtube_fetcher.fetch_transcript')
    @patch('_framework.lib.youtube_fetcher.fetch_metadata')
    def test_no_transcript_shows_not_fetched_message(self, mock_metadata, mock_transcript):
        """When transcript is None, content file shows '(Transcript not fetched)'."""
        mock_metadata.return_value = {
            "video_id": "test123video",
            "title": "Test Video",
            "channel": "Test Channel",
        }
        mock_transcript.return_value = None

        with tempfile.TemporaryDirectory() as tmpdir:
            result = create_content_file(
                "test123video",
                output_dir=tmpdir,
                fetch_transcript_flag=True
            )

            content = result.read_text()
            assert "(Transcript not fetched)" in content
            assert "[[transcripts/" not in content

    @patch('_framework.lib.youtube_fetcher.fetch_transcript')
    @patch('_framework.lib.youtube_fetcher.fetch_metadata')
    def test_no_transcript_file_created_when_none(self, mock_metadata, mock_transcript):
        """When transcript is None, no transcript file is created."""
        mock_metadata.return_value = {
            "video_id": "test123video",
            "title": "Test Video",
            "channel": "Test Channel",
        }
        mock_transcript.return_value = None

        with tempfile.TemporaryDirectory() as tmpdir:
            create_content_file(
                "test123video",
                output_dir=tmpdir,
                fetch_transcript_flag=True
            )

            transcript_dir = Path(tmpdir) / "transcripts"
            # Transcripts dir may or may not exist, but file should not
            transcript_file = transcript_dir / "test123video.md"
            assert not transcript_file.exists()

    @patch('_framework.lib.youtube_fetcher.fetch_transcript')
    @patch('_framework.lib.youtube_fetcher.fetch_metadata')
    def test_transcript_file_created_when_available(self, mock_metadata, mock_transcript):
        """When transcript exists, transcript file is created."""
        mock_metadata.return_value = {
            "video_id": "test123video",
            "title": "Test Video",
            "channel": "Test Channel",
        }
        mock_transcript.return_value = "This is the transcript content."

        with tempfile.TemporaryDirectory() as tmpdir:
            result = create_content_file(
                "test123video",
                output_dir=tmpdir,
                fetch_transcript_flag=True
            )

            # Check content file has link
            content = result.read_text()
            assert "[[transcripts/test123video|View transcript]]" in content
            assert "(Transcript not fetched)" not in content

            # Check transcript file exists and has content
            transcript_file = Path(tmpdir) / "transcripts" / "test123video.md"
            assert transcript_file.exists()
            transcript_content = transcript_file.read_text()
            assert "This is the transcript content." in transcript_content
            assert "type: youtube-transcript" in transcript_content

    @patch('_framework.lib.youtube_fetcher.fetch_transcript')
    @patch('_framework.lib.youtube_fetcher.fetch_metadata')
    def test_transcript_not_fetched_for_non_learning_category(self, mock_metadata, mock_transcript):
        """Entertainment category does not trigger transcript fetch."""
        mock_metadata.return_value = {
            "video_id": "test123video",
            "title": "Test Video",
            "channel": "Test Channel",
        }
        mock_transcript.return_value = "Should not be called"

        with tempfile.TemporaryDirectory() as tmpdir:
            create_content_file(
                "test123video",
                output_dir=tmpdir,
                category="entertainment"
            )

            # fetch_transcript should not have been called
            mock_transcript.assert_not_called()

    @patch('_framework.lib.youtube_fetcher.fetch_transcript')
    @patch('_framework.lib.youtube_fetcher.fetch_metadata')
    def test_transcript_fetched_for_learning_category(self, mock_metadata, mock_transcript):
        """Learning category triggers transcript fetch."""
        mock_metadata.return_value = {
            "video_id": "test123video",
            "title": "Test Video",
            "channel": "Test Channel",
        }
        mock_transcript.return_value = "Learning transcript"

        with tempfile.TemporaryDirectory() as tmpdir:
            create_content_file(
                "test123video",
                output_dir=tmpdir,
                category="learning"
            )

            # fetch_transcript should have been called
            mock_transcript.assert_called_once()


class TestCheckYoutubeHealth:
    """Tests for check_youtube_health function."""

    def test_empty_directories(self):
        """Empty directories return zero counts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_dir = Path(tmpdir) / "queue"
            content_dir = Path(tmpdir) / "content"
            queue_dir.mkdir()
            content_dir.mkdir()

            health = check_youtube_health(str(queue_dir), str(content_dir))
            assert health["queue_count"] == 0
            assert health["content_count"] == 0
            assert health["orphaned_content"] == []
            assert health["missing_content"] == []
            assert health["unlinked_items"] == []

    def test_matched_items(self):
        """Queue items with matching content files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_dir = Path(tmpdir) / "queue"
            content_dir = Path(tmpdir) / "content"
            queue_dir.mkdir()
            content_dir.mkdir()

            # Create queue item
            queue_item = queue_dir / "01TEST123456789012345678.md"
            queue_item.write_text("""---
type: youtube
video-id: dQw4w9WgXcQ
content-file: "[[../../content/dQw4w9WgXcQ]]"
---
# Test Video
""")

            # Create matching content file
            content_file = content_dir / "dQw4w9WgXcQ.md"
            content_file.write_text("""---
type: youtube-content
content-id: dQw4w9WgXcQ
---
# Test Content
""")

            health = check_youtube_health(str(queue_dir), str(content_dir))
            assert health["queue_count"] == 1
            assert health["content_count"] == 1
            assert health["orphaned_content"] == []
            assert health["missing_content"] == []
            assert health["unlinked_items"] == []

    def test_orphaned_content(self):
        """Content file without corresponding queue item."""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_dir = Path(tmpdir) / "queue"
            content_dir = Path(tmpdir) / "content"
            queue_dir.mkdir()
            content_dir.mkdir()

            # Create orphaned content file only
            content_file = content_dir / "orphaned123.md"
            content_file.write_text("""---
type: youtube-content
content-id: orphaned123
---
# Orphaned Content
""")

            health = check_youtube_health(str(queue_dir), str(content_dir))
            assert health["queue_count"] == 0
            assert health["content_count"] == 1
            assert health["orphaned_content"] == ["orphaned123.md"]

    def test_missing_content(self):
        """Queue item without corresponding content file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_dir = Path(tmpdir) / "queue"
            content_dir = Path(tmpdir) / "content"
            queue_dir.mkdir()
            content_dir.mkdir()

            # Create queue item without content file
            queue_item = queue_dir / "01TEST123456789012345678.md"
            queue_item.write_text("""---
type: youtube
video-id: missing12345
content-file: "[[../../content/missing12345]]"
---
# Missing Content Video
""")

            health = check_youtube_health(str(queue_dir), str(content_dir))
            assert health["queue_count"] == 1
            assert health["content_count"] == 0
            assert health["missing_content"] == ["01TEST123456789012345678.md"]

    def test_unlinked_items(self):
        """Queue item without content-file property."""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_dir = Path(tmpdir) / "queue"
            content_dir = Path(tmpdir) / "content"
            queue_dir.mkdir()
            content_dir.mkdir()

            # Create queue item without content-file link
            queue_item = queue_dir / "01TEST123456789012345678.md"
            queue_item.write_text("""---
type: youtube
video-id: unlinked1234
---
# Unlinked Video
""")

            # Create matching content file
            content_file = content_dir / "unlinked1234.md"
            content_file.write_text("""---
type: youtube-content
content-id: unlinked1234
---
# Content
""")

            health = check_youtube_health(str(queue_dir), str(content_dir))
            assert health["queue_count"] == 1
            assert health["content_count"] == 1
            assert health["unlinked_items"] == ["01TEST123456789012345678.md"]
            # Not missing because content exists, just not linked
            assert health["missing_content"] == []
