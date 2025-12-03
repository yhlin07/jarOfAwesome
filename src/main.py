"""Main entry point for Jar of Awesome bot."""
import logging
import sys
import os
from pathlib import Path

from src.config import settings
from src.ai.claude_client import InsightfulDeliveryEngine
from src.data.parser import MilestoneParser
from src.data.pregenerated_loader import PregeneratedLoader
from src.bot.telegram_bot import MilestoneBot


def setup_logging():
    """Configure logging for the application."""
    log_level = logging.DEBUG if settings.debug else logging.INFO

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )

    # Set specific log levels for noisy libraries
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.INFO)
    logging.getLogger('apscheduler').setLevel(logging.INFO)


def validate_environment():
    """Validate that all required environment variables are set."""
    # Always required
    required_fields = [
        'telegram_bot_token',
        'telegram_user_id'
    ]

    # API key only required if not using pregenerated
    if not settings.use_pregenerated:
        required_fields.append('anthropic_api_key')

    missing_fields = []
    for field in required_fields:
        if not getattr(settings, field, None):
            missing_fields.append(field.upper())

    if missing_fields:
        print("❌ Missing required environment variables:")
        for field in missing_fields:
            print(f"   - {field}")
        print("\nPlease create a .env file based on .env.example")
        sys.exit(1)


def main():
    """Main function to initialize and run the bot."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    # Check if we should run in HTTP mode (for Cloud Run + Cloud Scheduler)
    run_mode = os.getenv('RUN_MODE', 'bot').lower()

    if run_mode == 'http':
        logger.info("🌐 Starting in HTTP mode (Cloud Scheduler)")
        from src.http_server import app
        port = int(os.getenv('PORT', 8080))
        app.run(host="0.0.0.0", port=port, debug=settings.debug)
        return

    logger.info("🌟 Starting Jar of Awesome Bot...")

    # Validate environment
    try:
        validate_environment()
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    # Find milestone file
    milestone_path = Path(settings.milestone_file)
    if not milestone_path.exists():
        # Try relative to project root
        milestone_path = Path(__file__).parent.parent / settings.milestone_file
        if not milestone_path.exists():
            logger.error(f"❌ Milestone file not found: {settings.milestone_file}")
            logger.error(f"   Looked in: {Path(settings.milestone_file).absolute()}")
            logger.error(f"   And in: {milestone_path.absolute()}")
            sys.exit(1)

    logger.info(f"📖 Loading milestones from: {milestone_path}")

    # Initialize components
    try:
        # Choose mode: pregenerated or API
        if settings.use_pregenerated:
            logger.info("📦 Using pre-generated milestones (no API needed)")

            # Find pregenerated file
            pregen_path = Path(settings.pregenerated_file)
            if not pregen_path.exists():
                pregen_path = Path(__file__).parent.parent / settings.pregenerated_file
                if not pregen_path.exists():
                    logger.error(f"❌ Pre-generated file not found: {settings.pregenerated_file}")
                    sys.exit(1)

            # Load pregenerated milestones
            loader = PregeneratedLoader(str(pregen_path))
            logger.info(f"✅ Loaded {len(loader)} pre-generated milestones")

            # Display category breakdown
            stats = loader.get_category_stats()
            logger.info("📊 Category breakdown:")
            for category, count in sorted(stats.items(), key=lambda x: x[1], reverse=True)[:5]:
                logger.info(f"   • {category}: {count} milestones")

            # Initialize bot with pregenerated mode
            bot = MilestoneBot(
                token=settings.telegram_bot_token,
                user_id=settings.telegram_user_id,
                delivery_engine=None,  # No AI engine needed
                milestone_parser=None,  # Using pregenerated instead
                pregenerated_loader=loader,
                schedule_times=settings.schedule_times_list
            )

        else:
            logger.info("🤖 Using Claude API for AI-powered delivery")

            # Parse milestones from markdown
            parser = MilestoneParser(str(milestone_path))
            logger.info(f"✅ Loaded {len(parser)} milestones across {len(parser.get_categories())} categories")

            # Display category breakdown
            stats = parser.get_category_stats()
            logger.info("📊 Category breakdown:")
            for category, count in sorted(stats.items(), key=lambda x: x[1], reverse=True)[:5]:
                logger.info(f"   • {category}: {count} milestones")

            # Initialize AI engine
            engine = InsightfulDeliveryEngine(
                api_key=settings.anthropic_api_key,
                model=settings.model
            )
            logger.info(f"✅ Initialized AI engine with model: {settings.model}")

            # Initialize bot with API mode
            bot = MilestoneBot(
                token=settings.telegram_bot_token,
                user_id=settings.telegram_user_id,
                delivery_engine=engine,
                milestone_parser=parser,
                pregenerated_loader=None,
                schedule_times=settings.schedule_times_list
            )
        logger.info(f"✅ Bot configured for user ID: {settings.telegram_user_id}")
        logger.info(f"⏰ Scheduled times: {', '.join([f'{h:02d}:{m:02d}' for h, m in settings.schedule_times_list])}")

        # Run bot
        logger.info("🚀 Starting bot... Press Ctrl+C to stop")
        bot.run()

    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down gracefully...")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
