"""Tests for milestone parser."""
import pytest
from pathlib import Path
from src.data.parser import MilestoneParser, Milestone


@pytest.fixture
def parser():
    """Create parser with test markdown file."""
    test_file = Path(__file__).parent.parent / "milestones.md"
    return MilestoneParser(str(test_file))


def test_parser_loads_markdown(parser):
    """Test that parser successfully loads markdown file."""
    assert len(parser) > 0
    assert len(parser.milestones) > 0


def test_parser_extracts_categories(parser):
    """Test that parser extracts categories."""
    categories = parser.get_categories()
    assert len(categories) > 0
    assert all(isinstance(cat, str) for cat in categories)


def test_milestone_has_required_fields(parser):
    """Test that milestones have all required fields."""
    aff = parser.get_random_milestone()

    assert isinstance(aff, Milestone)
    assert hasattr(aff, 'text')
    assert hasattr(aff, 'category')
    assert hasattr(aff, 'raw_line')
    assert hasattr(aff, 'line_number')

    assert len(aff.text) > 0
    assert len(aff.category) > 0


def test_random_milestone_weighted(parser):
    """Test weighted random selection."""
    milestones = [parser.get_random_milestone(weighted=True) for _ in range(10)]

    assert len(milestones) == 10
    assert all(isinstance(aff, Milestone) for aff in milestones)


def test_random_milestone_unweighted(parser):
    """Test unweighted random selection."""
    milestones = [parser.get_random_milestone(weighted=False) for _ in range(10)]

    assert len(milestones) == 10
    assert all(isinstance(aff, Milestone) for aff in milestones)


def test_category_stats(parser):
    """Test category statistics."""
    stats = parser.get_category_stats()

    assert isinstance(stats, dict)
    assert len(stats) > 0
    assert all(isinstance(count, int) for count in stats.values())
    assert sum(stats.values()) == len(parser)


def test_get_random_milestone_by_category(parser):
    """Test getting milestone from specific category."""
    categories = parser.get_categories()

    if categories:
        category = categories[0]
        aff = parser.get_random_milestone(category=category)
        assert aff.category == category


def test_parser_raises_on_missing_file():
    """Test that parser raises error for missing file."""
    with pytest.raises(FileNotFoundError):
        MilestoneParser("nonexistent.md")


def test_parser_repr(parser):
    """Test parser string representation."""
    repr_str = repr(parser)
    assert "MilestoneParser" in repr_str
    assert "milestones" in repr_str
    assert "categories" in repr_str
