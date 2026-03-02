"""Agent memory system for term extraction and context storage."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass
class TermEntry:
    """A terminology entry extracted by the agent."""

    source: str
    target: str
    category: str = "general"  # general, name, technical, etc.
    context: str = ""
    count: int = 1

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source": self.source,
            "target": self.target,
            "category": self.category,
            "context": self.context,
            "count": self.count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TermEntry":
        """Create from dictionary."""
        return cls(
            source=data["source"],
            target=data["target"],
            category=data.get("category", "general"),
            context=data.get("context", ""),
            count=data.get("count", 1),
        )


class AgentMemory:
    """Manages agent's long-term and working memory.

    Stores terminology, context summaries, and bookmarks.
    All data persists to YAML files.
    """

    def __init__(self, memory_dir: Optional[Path] = None) -> None:
        """Initialize agent memory.

        Args:
            memory_dir: Directory for memory storage files.
        """
        self._memory_dir = memory_dir or Path("memory")
        self._memory_dir.mkdir(parents=True, exist_ok=True)
        self._terms: dict[str, TermEntry] = {}
        self._summaries: list[dict[str, str]] = []
        self._bookmarks: list[dict[str, Any]] = []
        self._notes: list[str] = []
        self._load()

    def add_term(self, entry: TermEntry) -> None:
        """Add or update a terminology entry.

        Args:
            entry: Term entry to add.
        """
        key = entry.source.lower()
        if key in self._terms:
            self._terms[key].count += 1
            if entry.target:
                self._terms[key].target = entry.target
            if entry.context:
                self._terms[key].context = entry.context
        else:
            self._terms[key] = entry

    def get_term(self, source: str) -> Optional[TermEntry]:
        """Look up a term by source text.

        Args:
            source: Source language term.

        Returns:
            Term entry if found, None otherwise.
        """
        return self._terms.get(source.lower())

    def get_all_terms(self) -> list[TermEntry]:
        """Get all stored terms.

        Returns:
            List of all term entries.
        """
        return list(self._terms.values())

    def get_terms_by_category(
        self, category: str
    ) -> list[TermEntry]:
        """Get terms filtered by category.

        Args:
            category: Category to filter by.

        Returns:
            List of matching term entries.
        """
        return [
            t for t in self._terms.values()
            if t.category == category
        ]

    def add_summary(
        self, summary: str, context_range: str = ""
    ) -> None:
        """Add a context summary.

        Args:
            summary: Summary text.
            context_range: Description of summarized range.
        """
        self._summaries.append({
            "summary": summary,
            "range": context_range,
        })

    def get_summaries(self) -> list[dict[str, str]]:
        """Get all context summaries.

        Returns:
            List of summary entries.
        """
        return list(self._summaries)

    def get_latest_summary(self) -> Optional[dict[str, str]]:
        """Get the most recent summary.

        Returns:
            Latest summary or None.
        """
        return self._summaries[-1] if self._summaries else None

    def add_bookmark(
        self, position: int, label: str = "", note: str = ""
    ) -> None:
        """Add a bookmark at a position.

        Args:
            position: Position/page/line number.
            label: Bookmark label.
            note: Optional note.
        """
        self._bookmarks.append({
            "position": position,
            "label": label,
            "note": note,
        })

    def get_bookmarks(self) -> list[dict[str, Any]]:
        """Get all bookmarks.

        Returns:
            List of bookmark entries.
        """
        return list(self._bookmarks)

    def add_note(self, note: str) -> None:
        """Add a free-form note.

        Args:
            note: Note text.
        """
        self._notes.append(note)

    def get_notes(self) -> list[str]:
        """Get all notes.

        Returns:
            List of notes.
        """
        return list(self._notes)

    def clear(self) -> None:
        """Clear all memory."""
        self._terms.clear()
        self._summaries.clear()
        self._bookmarks.clear()
        self._notes.clear()

    def save(self) -> None:
        """Save memory to YAML files."""
        terms_data = [t.to_dict() for t in self._terms.values()]
        memory_data = {
            "terms": terms_data,
            "summaries": self._summaries,
            "bookmarks": self._bookmarks,
            "notes": self._notes,
        }
        path = self._memory_dir / "memory.yaml"
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(
                memory_data, f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )

    def _load(self) -> None:
        """Load memory from YAML files."""
        path = self._memory_dir / "memory.yaml"
        if not path.exists():
            return
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            return
        for t in data.get("terms", []):
            entry = TermEntry.from_dict(t)
            self._terms[entry.source.lower()] = entry
        self._summaries = data.get("summaries", [])
        self._bookmarks = data.get("bookmarks", [])
        self._notes = data.get("notes", [])

    def to_prompt_context(self) -> str:
        """Generate a prompt context string from memory.

        Returns:
            Formatted string for inclusion in prompts.
        """
        parts = []
        if self._terms:
            terms_str = "\n".join(
                f"  - {t.source} → {t.target} ({t.category})"
                for t in self._terms.values()
            )
            parts.append(f"Known terminology:\n{terms_str}")
        if self._summaries:
            latest = self._summaries[-1]
            parts.append(
                f"Latest context summary:\n  {latest['summary']}"
            )
        return "\n\n".join(parts) if parts else ""
