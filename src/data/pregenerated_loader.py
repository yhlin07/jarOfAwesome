"""Loader for pre-generated milestones (no API needed)."""
import json
import random
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)


class PregeneratedMilestone:
    """Represents a pre-generated milestone."""

    def __init__(self, data: Dict):
        self.id = data["id"]
        self.category = data["category"]
        self.original = data["original"]
        self.message = data["message"]

    def get_message_with_greeting(self, hour: Optional[int] = None) -> str:
        """
        Get message with time-appropriate greeting.

        Args:
            hour: Hour of day (0-23), defaults to current hour in configured timezone

        Returns:
            Message with greeting prefix
        """
        if hour is None:
            # Get timezone from environment variable, default to UTC
            timezone_name = os.getenv('TIMEZONE', 'UTC')
            try:
                tz = ZoneInfo(timezone_name)
                hour = datetime.now(tz).hour
                logger.debug(f"Using timezone: {timezone_name}, current hour: {hour}")
            except Exception as e:
                logger.warning(f"Failed to use timezone {timezone_name}, falling back to UTC: {e}")
                hour = datetime.now().hour

        # Add greeting prefix based on time
        if 6 <= hour < 11:
            greeting = "早安！☀️\n"
        elif 11 <= hour < 14:
            greeting = "午安！💫\n"
        elif 14 <= hour < 18:
            greeting = "下午好！🌟\n"
        elif 18 <= hour < 22:
            greeting = "晚上好！🌙\n"
        else:
            greeting = ""

        # Some messages already have emoji at start, avoid double
        if self.message.strip().startswith(("☀️", "💫", "🌟", "🌙", "💪", "🚀", "💝")):
            return self.message
        else:
            return greeting + self.message

    def __repr__(self):
        return f"PregeneratedMilestone(id={self.id}, category='{self.category}')"


class PregeneratedLoader:
    """Load and manage pre-generated milestones."""

    def __init__(self, json_path: str):
        """
        Initialize loader with JSON file path.

        Args:
            json_path: Path to milestones JSON file
        """
        self.json_path = Path(json_path)
        if not self.json_path.exists():
            raise FileNotFoundError(f"Pregenerated file not found: {json_path}")

        self.milestones: List[PregeneratedMilestone] = []
        self.categories: Dict[str, List[PregeneratedMilestone]] = {}
        self.metadata: Dict = {}
        self._used_ids: set = set()  # Track used IDs to avoid repeats

        self._load()
        logger.info(f"Loaded {len(self.milestones)} pre-generated milestones")

    def _load(self) -> None:
        """Load JSON file and parse milestones."""
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Store metadata
        self.metadata = {
            "version": data.get("version"),
            "generated_date": data.get("generated_date"),
            "total_count": data.get("total_count"),
            "description": data.get("description")
        }

        # Parse milestones
        for item in data["milestones"]:
            aff = PregeneratedMilestone(item)
            self.milestones.append(aff)

            # Group by category
            if aff.category not in self.categories:
                self.categories[aff.category] = []
            self.categories[aff.category].append(aff)

        logger.info(f"Loaded {len(self.milestones)} milestones across {len(self.categories)} categories")

    def get_random_milestone(
        self,
        category: Optional[str] = None,
        avoid_repeats: bool = True
    ) -> PregeneratedMilestone:
        """
        Get a random milestone.

        Args:
            category: If specified, select only from this category
            avoid_repeats: If True, avoid recently used milestones

        Returns:
            A random PregeneratedMilestone object
        """
        # Select pool
        if category:
            if category not in self.categories:
                raise ValueError(f"Category '{category}' not found")
            pool = self.categories[category]
        else:
            pool = self.milestones

        # Avoid repeats if requested
        if avoid_repeats and len(self._used_ids) < len(pool):
            available = [aff for aff in pool if aff.id not in self._used_ids]
            if available:
                pool = available

        # Reset used IDs if we've gone through all
        if len(self._used_ids) >= len(self.milestones):
            logger.info("Resetting used IDs - all milestones have been seen once")
            self._used_ids.clear()

        # Random selection
        selected = random.choice(pool)
        self._used_ids.add(selected.id)

        logger.debug(f"Selected milestone: id={selected.id}, category={selected.category}")
        return selected

    def get_categories(self) -> List[str]:
        """Get list of all categories."""
        return list(self.categories.keys())

    def get_category_stats(self) -> Dict[str, int]:
        """Get count of milestones per category."""
        return {cat: len(affs) for cat, affs in self.categories.items()}

    def reset_usage(self) -> None:
        """Reset usage tracking (allow all milestones to be selected again)."""
        self._used_ids.clear()
        logger.info("Usage tracking reset")

    def __len__(self) -> int:
        """Return total number of milestones."""
        return len(self.milestones)

    def __repr__(self):
        return f"PregeneratedLoader({len(self.milestones)} milestones, {len(self.categories)} categories)"
