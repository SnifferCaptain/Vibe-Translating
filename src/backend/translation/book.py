"""Book translation mode.

Supports background translation of entire books with
original formatting and images preserved.
"""

from typing import Any

from .base import ModeInfo, TranslationMode


class BookMode(TranslationMode):
    """Whole-book translation mode.

    Translates entire books in the background while
    preserving layout, images, and formatting.
    """

    def get_info(self) -> ModeInfo:
        """Get mode metadata."""
        return ModeInfo(
            name="book",
            display_name="Book Translation",
            description=(
                "Translate entire books with formatting "
                "and images preserved"
            ),
            icon="book",
            supported_formats=[
                "txt", "md", "pdf", "mobi", "epub",
                "docx",
            ],
        )

    def process(
        self, content: Any, options: dict[str, Any]
    ) -> dict[str, Any]:
        """Process book content for translation.

        Args:
            content: File path or text content.
            options: Translation options.

        Returns:
            Result with chapter information.
        """
        text = str(content)
        chapters = self._split_chapters(text)
        return {
            "mode": "book",
            "chapters": chapters,
            "total_chapters": len(chapters),
            "background": options.get("background", True),
            "status": "ready",
        }

    def get_options_schema(self) -> dict[str, Any]:
        """Get options schema."""
        return {
            "type": "object",
            "properties": {
                "background": {
                    "type": "boolean",
                    "title": "Background Translation",
                    "default": True,
                },
                "preserve_images": {
                    "type": "boolean",
                    "title": "Preserve Images",
                    "default": True,
                },
                "preserve_layout": {
                    "type": "boolean",
                    "title": "Preserve Layout",
                    "default": True,
                },
                "chapter_split": {
                    "type": "boolean",
                    "title": "Split by Chapters",
                    "default": True,
                },
            },
        }

    def get_default_options(self) -> dict[str, Any]:
        """Get default options."""
        return {
            "background": True,
            "preserve_images": True,
            "preserve_layout": True,
            "chapter_split": True,
        }

    @staticmethod
    def _split_chapters(
        text: str,
    ) -> list[dict[str, Any]]:
        """Split text into chapters.

        Args:
            text: Full book text.

        Returns:
            List of chapter dictionaries.
        """
        lines = text.split("\n")
        chapters: list[dict[str, Any]] = []
        current_title = "Chapter 1"
        current_content: list[str] = []
        chapter_idx = 1

        for line in lines:
            stripped = line.strip()
            if (
                stripped.startswith("#")
                and len(stripped) < 100
            ):
                if current_content:
                    chapters.append({
                        "id": chapter_idx,
                        "title": current_title,
                        "content": "\n".join(current_content),
                        "status": "pending",
                    })
                    chapter_idx += 1
                current_title = stripped.lstrip("#").strip()
                current_content = []
            else:
                current_content.append(line)

        if current_content:
            chapters.append({
                "id": chapter_idx,
                "title": current_title,
                "content": "\n".join(current_content),
                "status": "pending",
            })
        return chapters
