"""Frame selection translation mode.

Supports mouse-driven bounding box selection for
translating specific areas (e.g., manga panels).
"""

from typing import Any

from .base import ModeInfo, TranslationMode


class FrameSelectMode(TranslationMode):
    """Frame selection translation mode.

    Users draw bounding boxes to select areas for
    translation, with optional SAM-based segmentation.
    """

    def get_info(self) -> ModeInfo:
        """Get mode metadata."""
        return ModeInfo(
            name="frame_select",
            display_name="Frame Select Translation",
            description=(
                "Select areas with bounding boxes for "
                "targeted translation (manga, images)"
            ),
            icon="crop",
            supported_formats=[
                "png", "jpg", "jpeg", "bmp", "webp",
            ],
        )

    def process(
        self, content: Any, options: dict[str, Any]
    ) -> dict[str, Any]:
        """Process frame selection.

        Args:
            content: Image path or data.
            options: Selection options with bounding boxes.

        Returns:
            Result with selected regions.
        """
        regions = options.get("regions", [])
        return {
            "mode": "frame_select",
            "image": str(content),
            "regions": regions,
            "total_regions": len(regions),
            "use_sam": options.get("use_sam", False),
            "status": "ready",
        }

    def get_options_schema(self) -> dict[str, Any]:
        """Get options schema."""
        return {
            "type": "object",
            "properties": {
                "use_sam": {
                    "type": "boolean",
                    "title": "Use SAM Segmentation",
                    "default": False,
                },
                "auto_detect": {
                    "type": "boolean",
                    "title": "Auto-detect Text Regions",
                    "default": False,
                },
                "font_size": {
                    "type": "integer",
                    "title": "Replacement Font Size",
                    "minimum": 8,
                    "maximum": 72,
                    "default": 14,
                },
                "font_color": {
                    "type": "string",
                    "title": "Font Color",
                    "default": "#000000",
                },
            },
        }

    def get_default_options(self) -> dict[str, Any]:
        """Get default options."""
        return {
            "use_sam": False,
            "auto_detect": False,
            "font_size": 14,
            "font_color": "#000000",
        }
