"""Telegram bot for daily milestone delivery."""
import logging
from datetime import time as datetime_time
from typing import Optional

from telegram import Update, BotCommand, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from src.ai.claude_client import InsightfulDeliveryEngine
from src.data.parser import MilestoneParser
from src.data.pregenerated_loader import PregeneratedLoader

logger = logging.getLogger(__name__)


class MilestoneBot:
    """
    Telegram bot that sends daily milestones.

    Features:
    - Scheduled milestones (4x daily by default)
    - Manual trigger via /milestone command
    - Test delivery at different times via /test
    """

    def __init__(
        self,
        token: str,
        user_id: int,
        schedule_times: list[tuple[int, int]],
        delivery_engine: Optional[InsightfulDeliveryEngine] = None,
        milestone_parser: Optional[MilestoneParser] = None,
        pregenerated_loader: Optional[PregeneratedLoader] = None
    ):
        """
        Initialize the milestone bot.

        Args:
            token: Telegram bot token
            user_id: Telegram user ID to send messages to
            schedule_times: List of (hour, minute) tuples for scheduled sends
            delivery_engine: AI engine for contextualizing (optional, for API mode)
            milestone_parser: Parser for milestone data (optional, for API mode)
            pregenerated_loader: Loader for pregenerated milestones (optional, for pregenerated mode)
        """
        self.token = token
        self.user_id = user_id
        self.engine = delivery_engine
        self.parser = milestone_parser
        self.pregenerated = pregenerated_loader
        self.schedule_times = schedule_times
        self.application: Optional[Application] = None

        # Determine mode
        self.use_pregenerated = pregenerated_loader is not None

        logger.info(f"Initialized MilestoneBot for user {user_id}")
        if self.use_pregenerated:
            logger.info(f"Mode: Pre-generated (no API)")
            logger.info(f"Loaded {len(self.pregenerated)} milestones")
        else:
            logger.info(f"Mode: Claude API")
            logger.info(f"Loaded {len(self.parser)} milestones")
        logger.info(f"Scheduled times: {schedule_times}")

    def _get_reply_keyboard(self) -> ReplyKeyboardMarkup:
        """Create the reply keyboard with quick action buttons."""
        keyboard = [
            [KeyboardButton("✨ Milestone"), KeyboardButton("❓ Help")],
            [KeyboardButton("🧪 Test")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        user = update.effective_user
        welcome_message = f"""☀️ **歡迎來到好棒棒罐！**

Hi {user.first_name}！我是你的每日肯定機器人。

**功能：**
• 每天 4 次提醒你有多棒
• 時間：{', '.join([f'{h:02d}:{m:02d}' for h, m in self.schedule_times])}
• 每次都會用新鮮的方式講述你的成就

**快速按鈕：**
使用下方的按鈕快速操作，或輸入以下指令：

/milestone - 立即獲得一個肯定
/test - 測試不同時間段的傳遞方式
/stats - 查看好棒棒罐統計
/help - 顯示幫助

記住：你一直都很棒，只是有時候忘記了 💫
"""
        await update.message.reply_text(
            welcome_message,
            parse_mode='Markdown',
            reply_markup=self._get_reply_keyboard()
        )
        logger.info(f"User {user.id} started the bot")

    async def milestone_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /milestone command - send immediate milestone."""
        try:
            if self.use_pregenerated:
                # Use pregenerated milestones
                milestone = self.pregenerated.get_random_milestone()
                message = milestone.get_message_with_greeting()
                category = milestone.category
            else:
                # Use API mode
                milestone = self.parser.get_random_milestone(weighted=True)
                message = self.engine.contextualize(milestone)
                category = milestone.category

            # Send to user
            await update.message.reply_text(message)
            logger.info(f"Sent manual milestone: category={category}")

        except Exception as e:
            logger.error(f"Error sending milestone: {e}")
            await update.message.reply_text("❌ 哎呀，出錯了。請稍後再試。")

    async def test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /test command - show how milestones work."""
        if self.use_pregenerated:
            await update.message.reply_text("🧪 測試模式：隨機選擇 3 個不同的肯定...\n")

            try:
                # Show 3 random pregenerated milestones
                for i in range(3):
                    milestone = self.pregenerated.get_random_milestone(avoid_repeats=False)
                    await update.message.reply_text(
                        f"**範例 {i+1}：{milestone.category}**\n{milestone.message}\n",
                        parse_mode='Markdown'
                    )

                logger.info(f"Sent test delivery for user {update.effective_user.id}")

            except Exception as e:
                logger.error(f"Error in test command: {e}")
                await update.message.reply_text("❌ 測試時出錯了")

        else:
            await update.message.reply_text("🧪 測試模式：同一個成就在不同時間的傳遞方式...\n")

            try:
                # Get one milestone
                milestone = self.parser.get_random_milestone(weighted=True)

                # Test at different times
                test_times = [
                    (8, 0, "早上"),
                    (12, 0, "中午"),
                    (16, 0, "下午"),
                    (20, 0, "晚上")
                ]

                await update.message.reply_text(f"**原始成就：**\n{milestone.text}\n", parse_mode='Markdown')

                for hour, minute, label in test_times:
                    message = self.engine.contextualize(milestone, hour, minute)
                    await update.message.reply_text(f"**{label} ({hour:02d}:{minute:02d})：**\n{message}\n", parse_mode='Markdown')

                logger.info(f"Sent test delivery for user {update.effective_user.id}")

            except Exception as e:
                logger.error(f"Error in test command: {e}")
                await update.message.reply_text("❌ 測試時出錯了")

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /stats command - show milestone statistics."""
        if self.use_pregenerated:
            stats = self.pregenerated.get_category_stats()
            total = len(self.pregenerated)
        else:
            stats = self.parser.get_category_stats()
            total = len(self.parser)

        message = f"📊 **好棒棒罐統計**\n\n"
        message += f"總計：{total} 個成就\n"
        message += f"分類數：{len(stats)} 個\n\n"
        message += "**各分類成就數：**\n"

        for category, count in sorted(stats.items(), key=lambda x: x[1], reverse=True)[:10]:
            message += f"• {category}: {count}\n"

        await update.message.reply_text(message, parse_mode='Markdown')
        logger.info(f"Sent stats to user {update.effective_user.id}")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        help_text = """📖 **好棒棒罐使用指南**

**自動提醒：**
機器人會在以下時間自動發送肯定：
""" + '\n'.join([f"• {h:02d}:{m:02d}" for h, m in self.schedule_times]) + """

**手動指令：**
• `/milestone` - 立即獲得一個肯定
• `/test` - 看同一個成就如何隨時間變化
• `/stats` - 查看你的成就統計
• `/help` - 顯示此幫助訊息

**設計理念：**
這個機器人對抗 ADHD 的「每天早上價值歸零」bug。
每次都會用 AI 重新詮釋你的成就，保持新鮮感。

有問題？這是開源專案：github.com/yourusername/jar-of-awesome
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def handle_button_press(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle button presses from the reply keyboard."""
        text = update.message.text

        if text == "✨ Milestone":
            await self.milestone_command(update, context)
        elif text == "🧪 Test":
            await self.test_command(update, context)
        elif text == "❓ Help":
            await self.help_command(update, context)

    async def send_scheduled_milestone(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Send scheduled milestone.

        This is called by the job queue at scheduled times.
        """
        try:
            if self.use_pregenerated:
                # Use pregenerated milestones
                milestone = self.pregenerated.get_random_milestone()
                message = milestone.get_message_with_greeting()
                category = milestone.category
            else:
                # Use API mode
                milestone = self.parser.get_random_milestone(weighted=True)
                message = self.engine.contextualize(milestone)
                category = milestone.category

            # Send to user
            await context.bot.send_message(
                chat_id=self.user_id,
                text=message
            )

            logger.info(f"Sent scheduled milestone: category={category}")

        except Exception as e:
            logger.error(f"Error sending scheduled milestone: {e}")
            # Optionally send error notification to user
            await context.bot.send_message(
                chat_id=self.user_id,
                text="❌ 今天的肯定發送失敗了，但記住：你依然很棒 ☀️"
            )

    async def post_init(self, application: Application) -> None:
        """Post-initialization hook to set bot commands."""
        await application.bot.set_my_commands([
            BotCommand("start", "開始使用好棒棒罐"),
            BotCommand("milestone", "立即獲得肯定"),
            BotCommand("test", "測試模式"),
            BotCommand("help", "顯示幫助"),
        ])
        logger.info("Bot commands menu set")

    def setup_application(self) -> Application:
        """Build and configure the Telegram application."""
        # Build application
        self.application = Application.builder().token(self.token).post_init(self.post_init).build()

        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("milestone", self.milestone_command))
        self.application.add_handler(CommandHandler("test", self.test_command))
        self.application.add_handler(CommandHandler("help", self.help_command))

        # Add button handler (for reply keyboard buttons)
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.handle_button_press
            )
        )

        # Add scheduled jobs
        job_queue = self.application.job_queue

        for hour, minute in self.schedule_times:
            job_queue.run_daily(
                self.send_scheduled_milestone,
                time=datetime_time(hour=hour, minute=minute),
                name=f"milestone_{hour:02d}_{minute:02d}"
            )
            logger.info(f"Scheduled job at {hour:02d}:{minute:02d}")

        logger.info("Application setup complete")
        return self.application

    def run(self) -> None:
        """Start the bot (blocking)."""
        if not self.application:
            self.setup_application()

        logger.info("Starting bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

    async def start_async(self) -> None:
        """Start the bot (non-blocking, for async contexts)."""
        if not self.application:
            self.setup_application()

        logger.info("Starting bot (async)...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
