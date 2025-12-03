"""Parse 好棒棒罐.md into structured milestone data."""
import random
import re
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class Milestone:
    """Represents a single milestone with metadata."""

    def __init__(self, text: str, category: str, raw_line: str, line_number: int):
        self.text = text
        self.category = category
        self.raw_line = raw_line
        self.line_number = line_number
        # Remove emojis for cleaner text processing
        self.text_clean = self._remove_emojis(text)

    def _remove_emojis(self, text: str) -> str:
        """Remove emojis from text (optional, for AI processing)."""
        # Keep emoji for now - Claude handles them well
        return text

    def __repr__(self):
        return f"Milestone(category='{self.category}', text='{self.text[:50]}...')"


class MilestoneParser:
    """Parse 好棒棒罐.md markdown file into structured milestones."""

    def __init__(self, markdown_path: str):
        """
        Initialize parser with path to markdown file.

        Args:
            markdown_path: Path to 好棒棒罐.md file
        """
        self.markdown_path = Path(markdown_path)
        if not self.markdown_path.exists():
            raise FileNotFoundError(f"Milestone file not found: {markdown_path}")

        self.milestones: List[Milestone] = []
        self.categories: Dict[str, List[Milestone]] = {}
        self._parse()
        logger.info(f"Parsed {len(self.milestones)} milestones from {markdown_path}")

    def _parse(self) -> None:
        """Parse markdown file into milestones grouped by category."""
        current_category = "未分類"
        line_number = 0

        with open(self.markdown_path, 'r', encoding='utf-8') as f:
            for line in f:
                line_number += 1
                line = line.rstrip()

                # Skip empty lines
                if not line.strip():
                    continue

                # Detect section headers (## or ###)
                if line.startswith('##'):
                    # Extract category name, remove markdown headers and emojis at start
                    current_category = re.sub(r'^#+\s*', '', line).strip()
                    # Remove leading emoji if present
                    current_category = re.sub(r'^[^\w\s]+\s*', '', current_category).strip()
                    if current_category not in self.categories:
                        self.categories[current_category] = []
                    logger.debug(f"Found category: {current_category}")

                # Extract bullet points (lines starting with -)
                elif line.strip().startswith('-'):
                    # Remove leading '- ' and any markdown formatting
                    text = line.strip()[1:].strip()

                    # Skip empty bullet points
                    if not text:
                        continue

                    # Skip metadata lines (like dates, section dividers)
                    if text.startswith('---') or text.startswith('*'):
                        continue

                    milestone = Milestone(
                        text=text,
                        category=current_category,
                        raw_line=line,
                        line_number=line_number
                    )

                    self.milestones.append(milestone)
                    self.categories[current_category].append(milestone)

        logger.info(f"Parsed {len(self.milestones)} milestones across {len(self.categories)} categories")

    def get_random_milestone(self, weighted: bool = True, category: Optional[str] = None) -> Milestone:
        """
        Get a random milestone.

        Args:
            weighted: If True, favor more recent milestones (later in file)
            category: If specified, select only from this category

        Returns:
            A random Milestone object
        """
        if not self.milestones:
            raise ValueError("No milestones available")

        # Filter by category if specified
        if category:
            if category not in self.categories:
                raise ValueError(f"Category '{category}' not found. Available: {list(self.categories.keys())}")
            pool = self.categories[category]
        else:
            pool = self.milestones

        if not pool:
            raise ValueError(f"No milestones available for category: {category}")

        # Weighted random selection (favor later/more recent entries)
        if weighted:
            # Create weights: 1, 2, 3, ..., n
            weights = list(range(1, len(pool) + 1))
            return random.choices(pool, weights=weights, k=1)[0]
        else:
            return random.choice(pool)

    def get_categories(self) -> List[str]:
        """Get list of all categories."""
        return list(self.categories.keys())

    def get_category_stats(self) -> Dict[str, int]:
        """Get count of milestones per category."""
        return {cat: len(affs) for cat, affs in self.categories.items()}

    def __len__(self) -> int:
        """Return total number of milestones."""
        return len(self.milestones)

    def __repr__(self):
        return f"MilestoneParser({len(self.milestones)} milestones, {len(self.categories)} categories)"
