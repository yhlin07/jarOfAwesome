"""
HTTP server for Cloud Run deployment with Cloud Scheduler.
This provides an HTTP endpoint that Cloud Scheduler can call to trigger milestones.
"""
import asyncio
import logging
from pathlib import Path

from flask import Flask, request, jsonify
from telegram import Bot

from src.config import settings
from src.data.pregenerated_loader import PregeneratedLoader

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Global bot and loader (initialized on first request)
_bot = None
_loader = None


def _ensure_initialized():
    """Lazy initialization of bot and loader."""
    global _bot, _loader

    if _bot is None:
        logger.info("Initializing bot and loader...")
        _bot = Bot(token=settings.telegram_bot_token)

        # Load pregenerated milestones
        pregen_path = Path(settings.pregenerated_file)
        if not pregen_path.exists():
            pregen_path = Path(__file__).parent.parent / settings.pregenerated_file

        _loader = PregeneratedLoader(str(pregen_path))
        logger.info(f"Loaded {len(_loader)} milestones")


async def _send_milestone():
    """Send a random milestone (async)."""
    _ensure_initialized()

    try:
        # Get random milestone
        milestone = _loader.get_random_milestone()
        message = milestone.get_message_with_greeting()

        # Send to user
        await _bot.send_message(
            chat_id=settings.telegram_user_id,
            text=message
        )

        logger.info(f"✅ Sent milestone: category={milestone.category}")
        return True, milestone.category

    except Exception as e:
        logger.error(f"❌ Error sending milestone: {e}")
        return False, str(e)


@app.route('/')
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "jar-of-awesome",
        "mode": "cloud-scheduler"
    })


@app.route('/cron/send-milestone', methods=['POST', 'GET'])
def trigger_milestone():
    """
    Endpoint called by Cloud Scheduler to trigger milestone.

    Cloud Scheduler will call this endpoint at scheduled times.
    """
    # Verify this is coming from Cloud Scheduler (optional security)
    # You can add a secret token check here if needed

    logger.info("🔔 Received trigger from Cloud Scheduler")

    # Run async function in sync context
    success, info = asyncio.run(_send_milestone())

    if success:
        return jsonify({
            "success": True,
            "category": info,
            "message": "Milestone sent successfully"
        }), 200
    else:
        return jsonify({
            "success": False,
            "error": info,
            "message": "Failed to send milestone"
        }), 500


if __name__ == "__main__":
    # For local testing
    import sys
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    port = int(settings.port) if hasattr(settings, 'port') else 8080
    app.run(host="0.0.0.0", port=port, debug=settings.debug)
