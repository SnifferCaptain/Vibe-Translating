"""Real-time translation mode.

Supports translating mobi, PDF, markdown, and web content
in-place with original formatting preserved.
"""

from typing import Any

from .base import ModeInfo, TranslationMode


class RealtimeMode(TranslationMode):
    """Real-time in-place translation mode.

    Translates content while preserving original formatting.
    Supports pure translation, side-by-side comparison,
    and export modes.
    """

    def get_info(self) -> ModeInfo:
        """Get mode metadata."""
        return ModeInfo(
            name="realtime",
            display_name="Real-time Translation",
            description=(
                "Translate documents in-place with "
                "original formatting preserved"
            ),
            icon="translate",
            supported_formats=[
                "txt", "md", "pdf", "mobi", "epub",
                "html", "url",
            ],
        )

    def process(
        self, content: Any, options: dict[str, Any]
    ) -> dict[str, Any]:
        """Process content for real-time translation.

        Args:
            content: Text content or file path.
            options: Translation options.

        Returns:
            Result with translated segments.
        """
        text = str(content)
        display_mode = options.get("display_mode", "translation")
        segments = self._split_segments(text)
        return {
            "mode": "realtime",
            "display_mode": display_mode,
            "segments": segments,
            "total_segments": len(segments),
            "status": "ready",
        }

    def get_options_schema(self) -> dict[str, Any]:
        """Get options schema."""
        return {
            "type": "object",
            "properties": {
                "display_mode": {
                    "type": "string",
                    "enum": [
                        "translation",
                        "comparison",
                        "export",
                    ],
                    "title": "Display Mode",
                    "default": "translation",
                },
                "preserve_formatting": {
                    "type": "boolean",
                    "title": "Preserve Formatting",
                    "default": True,
                },
                "auto_scroll": {
                    "type": "boolean",
                    "title": "Auto Scroll",
                    "default": True,
                },
            },
        }

    def get_default_options(self) -> dict[str, Any]:
        """Get default options."""
        return {
            "display_mode": "translation",
            "preserve_formatting": True,
            "auto_scroll": True,
        }

    @staticmethod
    def _split_segments(text: str) -> list[dict[str, Any]]:
        """Split text into translatable segments.

        Args:
            text: Full text content.

        Returns:
            List of segment dictionaries.
        """
        paragraphs = text.split("\n\n")
        segments = []
        for i, para in enumerate(paragraphs):
            para = para.strip()
            if para:
                segments.append({
                    "id": i,
                    "source": para,
                    "translation": "",
                    "status": "pending",
                })
        return segments
