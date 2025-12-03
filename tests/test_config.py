"""Tests for configuration management."""
import pytest
from src.config import Settings


def test_schedule_times_validation():
    """Test that schedule times are validated correctly."""
    # Valid times
    valid_settings = Settings(
        telegram_bot_token="test",
        telegram_user_id=123,
        anthropic_api_key="test",
        schedule_times="08:00,12:00,16:00,20:00"
    )
    assert valid_settings.schedule_times == "08:00,12:00,16:00,20:00"


def test_schedule_times_list_property():
    """Test that schedule_times_list property works correctly."""
    settings = Settings(
        telegram_bot_token="test",
        telegram_user_id=123,
        anthropic_api_key="test",
        schedule_times="08:00,12:30,16:45,20:15"
    )

    times_list = settings.schedule_times_list
    assert times_list == [(8, 0), (12, 30), (16, 45), (20, 15)]


def test_invalid_schedule_time_format():
    """Test that invalid time format raises error."""
    with pytest.raises(Exception):  # Pydantic validation error
        Settings(
            telegram_bot_token="test",
            telegram_user_id=123,
            anthropic_api_key="test",
            schedule_times="25:00,12:00"  # Invalid hour
        )


def test_default_values():
    """Test that default values are set correctly."""
    settings = Settings(
        telegram_bot_token="test",
        telegram_user_id=123,
        anthropic_api_key="test"
    )

    assert settings.model == "claude-3-5-haiku-20241022"
    assert settings.timezone == "Asia/Taipei"
    assert settings.debug is False
    assert settings.milestone_file == "milestones.md"
