"""
Entry - A human-curated research event that can trigger social posts.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


@dataclass
class EntrySummary:
    """Multi-level summary of a research event."""
    technical: str
    accessible: str
    one_liner: str


@dataclass
class EntrySignificance:
    """Significance metadata for an entry."""
    level: str  # LOW, MEDIUM, HIGH, CRITICAL
    reasoning: str
    connects_to: list[str]  # concept IDs


@dataclass
class PostGuidance:
    """Human guidance for post generation."""
    angle: str
    hooks: list[str]
    avoid: str
    suggested_tone: str


@dataclass
class Entry:
    """
    A research event entry - human-curated trigger for social posts.
    
    Entries capture significant research milestones that should be
    communicated via social media. The human provides context and
    guidance; agents generate the actual posts.
    """
    
    entry_id: str
    timestamp: datetime
    type: str  # validation_result, discovery, milestone, publication, etc.
    summary: EntrySummary
    significance: EntrySignificance
    post_guidance: Optional[PostGuidance] = None
    created_by: str = "unknown"
    posted: bool = False
    post_ids: list[dict] = field(default_factory=list)  # [{platform, id, posted_at}]
    _file_path: Optional[Path] = field(default=None, repr=False)
    
    @classmethod
    def from_dict(cls, data: dict, file_path: Optional[Path] = None) -> "Entry":
        """Create Entry from JSON data."""
        summary = EntrySummary(**data["summary"])
        significance = EntrySignificance(**data["significance"])
        
        post_guidance = None
        if "post_guidance" in data:
            post_guidance = PostGuidance(**data["post_guidance"])
        
        meta = data.get("meta", {})
        
        return cls(
            entry_id=data["entry_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            type=data["type"],
            summary=summary,
            significance=significance,
            post_guidance=post_guidance,
            created_by=meta.get("created_by", "unknown"),
            posted=meta.get("posted", False),
            post_ids=meta.get("post_ids", []),
            _file_path=file_path,
        )
    
    @classmethod
    def from_file(cls, file_path: Path) -> "Entry":
        """Load entry from JSON file."""
        with open(file_path) as f:
            data = json.load(f)
        return cls.from_dict(data, file_path)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        data = {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp.isoformat(),
            "type": self.type,
            "summary": {
                "technical": self.summary.technical,
                "accessible": self.summary.accessible,
                "one_liner": self.summary.one_liner,
            },
            "significance": {
                "level": self.significance.level,
                "reasoning": self.significance.reasoning,
                "connects_to": self.significance.connects_to,
            },
            "meta": {
                "created_by": self.created_by,
                "posted": self.posted,
                "post_ids": self.post_ids,
            }
        }
        
        if self.post_guidance:
            data["post_guidance"] = {
                "angle": self.post_guidance.angle,
                "hooks": self.post_guidance.hooks,
                "avoid": self.post_guidance.avoid,
                "suggested_tone": self.post_guidance.suggested_tone,
            }
        
        return data
    
    def save(self) -> None:
        """Save entry back to file."""
        if self._file_path is None:
            raise RuntimeError("Entry has no file path")
        
        with open(self._file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def to_context(self) -> dict:
        """Convert to context format for agents."""
        return {
            "entry_id": self.entry_id,
            "type": self.type,
            "timestamp": self.timestamp.isoformat(),
            "summary": {
                "technical": self.summary.technical,
                "accessible": self.summary.accessible,
                "one_liner": self.summary.one_liner,
            },
            "significance": self.significance.level,
            "connects_to": self.significance.connects_to,
            "guidance": {
                "angle": self.post_guidance.angle if self.post_guidance else None,
                "hooks": self.post_guidance.hooks if self.post_guidance else [],
                "avoid": self.post_guidance.avoid if self.post_guidance else None,
                "tone": self.post_guidance.suggested_tone if self.post_guidance else "thoughtful",
            }
        }


class EntryManager:
    """Manages research entries in the cip/entries/ directory."""
    
    def __init__(self, entries_path: Path):
        self.entries_path = entries_path
        self._cache: dict[str, Entry] = {}
    
    def get(self, entry_id: str) -> Entry:
        """Get entry by ID."""
        if entry_id in self._cache:
            return self._cache[entry_id]
        
        # Try to find file
        for file_path in self.entries_path.glob("*.json"):
            if entry_id in file_path.stem:
                entry = Entry.from_file(file_path)
                self._cache[entry_id] = entry
                return entry
        
        raise KeyError(f"Entry not found: {entry_id}")
    
    def get_recent(self, days: int = 7, unposted_only: bool = True) -> list[Entry]:
        """Get recent entries."""
        if not self.entries_path.exists():
            return []
        
        cutoff = datetime.now() - timedelta(days=days)
        entries = []
        
        for file_path in self.entries_path.glob("*.json"):
            try:
                entry = Entry.from_file(file_path)
                if entry.timestamp >= cutoff:
                    if not unposted_only or not entry.posted:
                        entries.append(entry)
                        self._cache[entry.entry_id] = entry
            except (json.JSONDecodeError, KeyError):
                continue
        
        # Sort by timestamp descending
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        return entries
    
    def mark_posted(self, entry_id: str, post_id: str, platform: str = "twitter") -> None:
        """Mark entry as posted."""
        entry = self.get(entry_id)
        entry.posted = True
        entry.post_ids.append({
            "platform": platform,
            "id": post_id,
            "posted_at": datetime.now().isoformat(),
        })
        entry.save()
    
    def create(
        self,
        entry_id: str,
        type: str,
        summary: dict,
        significance: dict,
        post_guidance: Optional[dict] = None,
        created_by: str = "unknown",
    ) -> Entry:
        """Create a new entry."""
        data = {
            "entry_id": entry_id,
            "timestamp": datetime.now().isoformat(),
            "type": type,
            "summary": summary,
            "significance": significance,
            "meta": {
                "created_by": created_by,
                "posted": False,
                "post_ids": [],
            }
        }
        
        if post_guidance:
            data["post_guidance"] = post_guidance
        
        file_path = self.entries_path / f"{entry_id}.json"
        self.entries_path.mkdir(parents=True, exist_ok=True)
        
        entry = Entry.from_dict(data, file_path)
        entry.save()
        self._cache[entry_id] = entry
        
        return entry
