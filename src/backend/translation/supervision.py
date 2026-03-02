"""Supervision translation mode.

Professional translation review mode with side-by-side
source and target comparison.
"""

from typing import Any

from .base import ModeInfo, TranslationMode


class SupervisionMode(TranslationMode):
    """Supervision mode for professional translators.

    Provides side-by-side view with re-translation
    capabilities and review tools.
    """

    def get_info(self) -> ModeInfo:
        """Get mode metadata."""
        return ModeInfo(
            name="supervision",
            display_name="Supervision Mode",
            description=(
                "Professional translation review with "
                "side-by-side comparison and re-translation"
            ),
            icon="rate_review",
            supported_formats=["txt", "md", "srt", "po"],
        )

    def process(
        self, content: Any, options: dict[str, Any]
    ) -> dict[str, Any]:
        """Process content for supervision mode.

        Args:
            content: Source text content.
            options: Processing options.

        Returns:
            Result with paired source/target segments.
        """
        text = str(content)
        pairs = self._create_pairs(text)
        return {
            "mode": "supervision",
            "pairs": pairs,
            "total_pairs": len(pairs),
            "status": "ready",
        }

    def get_options_schema(self) -> dict[str, Any]:
        """Get options schema."""
        return {
            "type": "object",
            "properties": {
                "auto_retranslate": {
                    "type": "boolean",
                    "title": "Auto Re-translate on Select",
                    "default": True,
                },
                "show_diff": {
                    "type": "boolean",
                    "title": "Show Translation Diff",
                    "default": False,
                },
                "segment_by": {
                    "type": "string",
                    "enum": [
                        "sentence", "paragraph", "line",
                    ],
                    "title": "Segment By",
                    "default": "sentence",
                },
            },
        }

    def get_default_options(self) -> dict[str, Any]:
        """Get default options."""
        return {
            "auto_retranslate": True,
            "show_diff": False,
            "segment_by": "sentence",
        }

    @staticmethod
    def _create_pairs(
        text: str,
    ) -> list[dict[str, Any]]:
        """Create source/target pairs from text.

        Args:
            text: Source text.

        Returns:
            List of pair dictionaries.
        """
        sentences = []
        for para in text.split("\n"):
            para = para.strip()
            if not para:
                continue
            for sent in para.replace("。", "。\n").replace(
                ". ", ".\n"
            ).split("\n"):
                sent = sent.strip()
                if sent:
                    sentences.append(sent)

        return [
            {
                "id": i,
                "source": sent,
                "target": "",
                "status": "pending",
                "approved": False,
            }
            for i, sent in enumerate(sentences)
        ]
