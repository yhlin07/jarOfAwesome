"""Configuration management for Jar of Awesome bot."""
import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Telegram Configuration
    telegram_bot_token: str = Field(..., description="Telegram bot token from @BotFather")
    telegram_user_id: int = Field(..., description="Your Telegram user ID")

    # Anthropic API Configuration (optional - only needed if not using pregenerated)
    anthropic_api_key: str = Field(default="", description="Anthropic API key (optional)")
    model: str = Field(
        default="claude-3-5-haiku-20241022",
        description="Claude model to use for AI enhancement"
    )

    # Pregenerated milestones (no API needed)
    use_pregenerated: bool = Field(
        default=True,
        description="Use pre-generated milestones instead of API"
    )
    pregenerated_file: str = Field(
        default="milestones_pregenerated.json",
        description="Path to pre-generated milestones JSON file"
    )

    # Scheduling Configuration
    timezone: str = Field(default="Asia/Taipei", description="Timezone for scheduling")
    schedule_times: str = Field(
        default="08:00,12:00,16:00,20:00",
        description="Comma-separated times for daily milestones"
    )

    # Application Configuration
    debug: bool = Field(default=False, description="Enable debug logging")
    milestone_file: str = Field(
        default="milestones.md",
        description="Path to milestone markdown file"
    )

    @field_validator("schedule_times")
    def validate_schedule_times(cls, v: str) -> str:
        """Validate schedule times format (HH:MM)."""
        times = [t.strip() for t in v.split(",")]
        for time_str in times:
            try:
                hour, minute = time_str.split(":")
                if not (0 <= int(hour) < 24 and 0 <= int(minute) < 60):
                    raise ValueError(f"Invalid time: {time_str}")
            except (ValueError, IndexError) as e:
                raise ValueError(f"Invalid time format: {time_str}. Use HH:MM format.") from e
        return v

    @property
    def schedule_times_list(self) -> List[tuple]:
        """Parse schedule_times into list of (hour, minute) tuples."""
        result = []
        for time_str in self.schedule_times.split(","):
            hour, minute = time_str.strip().split(":")
            result.append((int(hour), int(minute)))
        return result


# Global settings instance
settings = Settings()
