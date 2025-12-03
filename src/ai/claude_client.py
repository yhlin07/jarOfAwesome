"""Claude API client for contextual milestone delivery."""
import logging
from datetime import datetime
from typing import Optional

import anthropic

from src.ai.prompts import (
    SYSTEM_PROMPT,
    get_prompt_for_time,
    format_time
)
from src.data.parser import Milestone

logger = logging.getLogger(__name__)


class InsightfulDeliveryEngine:
    """
    AI engine that transforms milestones into contextual, insightful messages.

    This is the core of the "insightful delivery" feature - it uses Claude
    to rephrase achievements in fresh ways based on time of day and context.
    """

    def __init__(self, api_key: str, model: str = "claude-3-5-haiku-20241022"):
        """
        Initialize the Claude API client.

        Args:
            api_key: Anthropic API key
            model: Claude model to use (default: claude-3-5-haiku for speed/cost)
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        logger.info(f"Initialized InsightfulDeliveryEngine with model: {model}")

    def contextualize(
        self,
        milestone: Milestone,
        hour: Optional[int] = None,
        minute: Optional[int] = None
    ) -> str:
        """
        Transform an milestone into a contextual, insightful message.

        This method:
        1. Selects appropriate prompt based on time of day
        2. Sends to Claude API for creative rephrasing
        3. Returns fresh perspective on the same achievement

        Args:
            milestone: Milestone object to contextualize
            hour: Hour of day (0-23), defaults to current hour
            minute: Minute (0-59), defaults to current minute

        Returns:
            Contextualized message string
        """
        # Use current time if not specified
        if hour is None or minute is None:
            now = datetime.now()
            hour = now.hour
            minute = now.minute

        # Select prompt template based on time
        prompt_template = get_prompt_for_time(hour)
        time_str = format_time(hour, minute)

        # Fill in the prompt with achievement details
        user_prompt = prompt_template.format(
            time=time_str,
            achievement=milestone.text
        )

        logger.debug(f"Sending milestone to Claude: category={milestone.category}, hour={hour}")

        try:
            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=300,  # Enough for detailed response
                temperature=1.0,  # Higher creativity for variety
                system=SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }]
            )

            response_text = message.content[0].text
            logger.info(f"Generated contextualized milestone (tokens: {message.usage.input_tokens} in, {message.usage.output_tokens} out)")

            return response_text.strip()

        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            # Fallback: return original milestone with emoji
            return f"☀️ {milestone.text}"

        except Exception as e:
            logger.error(f"Unexpected error in contextualize: {e}")
            return f"☀️ {milestone.text}"

    def test_delivery(self, milestone: Milestone) -> None:
        """
        Test delivery at different times of day.

        Useful for debugging and seeing how the same milestone
        is delivered differently throughout the day.

        Args:
            milestone: Milestone to test
        """
        test_times = [
            (8, 0, "Morning"),
            (12, 0, "Noon"),
            (16, 0, "Afternoon"),
            (20, 0, "Evening")
        ]

        print(f"\n{'='*60}")
        print(f"Testing milestone: {milestone.text[:60]}...")
        print(f"Category: {milestone.category}")
        print(f"{'='*60}\n")

        for hour, minute, label in test_times:
            print(f"\n{label} ({hour:02d}:{minute:02d}):")
            print("-" * 60)
            result = self.contextualize(milestone, hour, minute)
            print(result)
            print()
