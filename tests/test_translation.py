"""Tests for translation modes."""

import pytest

from src.backend.translation.base import ModeRegistry
from src.backend.translation.realtime import RealtimeMode
from src.backend.translation.book import BookMode
from src.backend.translation.frame_select import FrameSelectMode
from src.backend.translation.supervision import SupervisionMode


class TestModeRegistry:
    """Tests for ModeRegistry."""

    def test_register_and_get(self) -> None:
        """Test registering and getting modes."""
        registry = ModeRegistry()
        mode = RealtimeMode()
        registry.register(mode)
        assert registry.get("realtime") is not None

    def test_get_all(self) -> None:
        """Test getting all modes."""
        registry = ModeRegistry()
        registry.register(RealtimeMode())
        registry.register(BookMode())
        all_modes = registry.get_all()
        assert "realtime" in all_modes
        assert "book" in all_modes

    def test_get_names(self) -> None:
        """Test getting mode names."""
        registry = ModeRegistry()
        registry.register(RealtimeMode())
        names = registry.get_names()
        assert "realtime" in names


class TestRealtimeMode:
    """Tests for RealtimeMode."""

    def test_info(self) -> None:
        """Test mode info."""
        mode = RealtimeMode()
        info = mode.get_info()
        assert info.name == "realtime"
        assert "txt" in info.supported_formats

    def test_process(self) -> None:
        """Test processing content."""
        mode = RealtimeMode()
        result = mode.process(
            "Hello world\n\nSecond paragraph",
            {"display_mode": "translation"},
        )
        assert result["mode"] == "realtime"
        assert len(result["segments"]) == 2

    def test_supports_format(self) -> None:
        """Test format support check."""
        mode = RealtimeMode()
        assert mode.supports_format("md")
        assert mode.supports_format("pdf")
        assert not mode.supports_format("xyz")

    def test_options_schema(self) -> None:
        """Test options schema."""
        mode = RealtimeMode()
        schema = mode.get_options_schema()
        assert "properties" in schema
        assert "display_mode" in schema["properties"]


class TestBookMode:
    """Tests for BookMode."""

    def test_info(self) -> None:
        """Test mode info."""
        mode = BookMode()
        info = mode.get_info()
        assert info.name == "book"

    def test_process_with_chapters(self) -> None:
        """Test processing book content with chapters."""
        mode = BookMode()
        content = "# Chapter 1\nContent 1\n# Chapter 2\nContent 2"
        result = mode.process(content, {})
        assert result["mode"] == "book"
        assert len(result["chapters"]) >= 2

    def test_process_without_chapters(self) -> None:
        """Test processing plain text."""
        mode = BookMode()
        result = mode.process("Plain text content", {})
        assert result["mode"] == "book"
        assert len(result["chapters"]) >= 1


class TestFrameSelectMode:
    """Tests for FrameSelectMode."""

    def test_info(self) -> None:
        """Test mode info."""
        mode = FrameSelectMode()
        info = mode.get_info()
        assert info.name == "frame_select"
        assert "png" in info.supported_formats

    def test_process(self) -> None:
        """Test processing."""
        mode = FrameSelectMode()
        result = mode.process(
            "image.png",
            {"regions": [{"x": 0, "y": 0, "w": 100, "h": 50}]},
        )
        assert result["mode"] == "frame_select"
        assert result["total_regions"] == 1


class TestSupervisionMode:
    """Tests for SupervisionMode."""

    def test_info(self) -> None:
        """Test mode info."""
        mode = SupervisionMode()
        info = mode.get_info()
        assert info.name == "supervision"

    def test_process(self) -> None:
        """Test processing text into pairs."""
        mode = SupervisionMode()
        result = mode.process(
            "First sentence. Second sentence.",
            {},
        )
        assert result["mode"] == "supervision"
        assert len(result["pairs"]) >= 2

    def test_options_schema(self) -> None:
        """Test options schema."""
        mode = SupervisionMode()
        schema = mode.get_options_schema()
        assert "segment_by" in schema["properties"]
