# jarOfAwesome ☀️

> Your brain remembers failures. This bot remembers wins.

AI-powered Telegram bot that fights negativity bias by sending daily milestone reminders.

## 🎯 The Problem

**Human brains have a bug**: We naturally remember failures more vividly than successes (negativity bias). Result: Even when making progress, we feel stuck.

This bot systematically reminds you of milestones you've achieved, fighting the natural tendency to forget progress.

## ✨ Features

- 📱 **Telegram Integration** - Reminders delivered where you already are
- ⏰ **4 Daily Reminders** - Configurable times (default: 8am, 12pm, 4pm, 8pm)
- 🎲 **Smart Selection** - Randomly picks from your milestone database
- 💡 **AI-Powered Delivery** - Claude rephrases based on time of day and context
- 📊 **Customizable Data** - Load your own milestones via `milestones.md`
- 🐳 **Docker Ready** - One-command deployment

## 🛠️ Tech Stack

- **Python 3.11+** - Main language
- **python-telegram-bot** - Telegram bot framework
- **APScheduler** - Job scheduling for daily reminders
- **Anthropic Claude API** - AI-powered contextual delivery
- **Docker** - Containerization for easy deployment
- **pydantic** - Configuration management

## 🏗️ Architecture

```
src/
├── bot/telegram_bot.py      # Telegram bot handler & commands
├── data/parser.py          # Parse milestones.md into structured data
├── ai/
│   ├── claude_client.py    # Claude API integration
│   └── prompts.py          # Time-based prompt templates
├── config.py               # Environment configuration
└── main.py                 # Application entry point
```

## 🚀 Quick Start

### Prerequisites

1. **Telegram Bot Token**
   - Message [@BotFather](https://t.me/botfather)
   - Create bot with `/newbot`
   - Save the token

2. **Telegram User ID**
   - Message [@userinfobot](https://t.me/userinfobot)
   - Save your user ID

3. **Anthropic API Key**
   - Sign up at [console.anthropic.com](https://console.anthropic.com/)
   - Create API key

### Setup (Docker - Recommended)

```bash
# 1. Clone repository
git clone https://github.com/yhlin07/jarOfAwesome.git
cd jarOfAwesome

# 2. Create your milestones file
cp milestones.example.md milestones.md
nano milestones.md  # Add your achievements

# 3. Configure environment
cp .env.example .env
nano .env  # Add your tokens

# 4. Run with Docker
docker-compose up -d

# 5. Check logs
docker-compose logs -f
```

### Setup (Local Development)

```bash
# 1. Clone repository
git clone https://github.com/yhlin07/jarOfAwesome.git
cd jarOfAwesome

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create milestones file
cp milestones.example.md milestones.md
nano milestones.md  # Add your achievements

# 5. Configure environment
cp .env.example .env
nano .env  # Add your tokens

# 6. Run bot
python -m src.main
```

## 📱 Bot Commands

Once the bot is running, message it on Telegram:

- `/start` - Welcome message and setup info
- `/milestone` - Get instant milestone reminder
- `/test` - See how same milestone varies by time
- `/stats` - View your milestone statistics
- `/help` - Show help message

## 💡 How "AI-Powered Delivery" Works

Instead of just copy-pasting milestones, the bot uses Claude AI to:

### 1. Contextualize by Time of Day
- **Morning (8am)**: Energy boost for starting the day
- **Noon (12pm)**: Quick power-up during midday slump
- **Afternoon (4pm)**: Reminder of core strengths
- **Evening (8pm)**: Reflection and reassurance

### 2. Rephrase Creatively
- Each delivery is unique, never repetitive
- Connects past achievements to present context
- Reveals patterns and strengths

### 3. Adapt to Emotional Needs
- Morning: Combat the "fresh start" mindset that forgets yesterday's wins
- Afternoon: Fight imposter syndrome with evidence
- Evening: Permission to rest knowing you've already proven yourself

### Example

**Original milestone:**
> "Completed major project under tight deadline - delivered 2 weeks early with 95% test coverage"

**Morning delivery (8am):**
> ☀️ Remember when you delivered that project 2 weeks early? That wasn't luck—that's your standard. Today's challenges are just practice for strengths you've already proven.

**Evening delivery (8pm):**
> 💫 That project you shipped early with 95% test coverage? It proves you don't cut corners even under pressure. That integrity is still yours. Rest well knowing you've got this.

## 📊 Configuration

Edit `.env` file:

```env
# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_USER_ID=your-user-id

# Anthropic
ANTHROPIC_API_KEY=your-api-key
MODEL=claude-3-5-haiku-20241022  # or claude-3-5-sonnet-20241022

# Scheduling
TIMEZONE=America/Los_Angeles
SCHEDULE_TIMES=08:00,12:00,16:00,20:00

# Debug
DEBUG=false
```

## 📝 Creating Your Milestones File

Create `milestones.md` with your achievements:

```markdown
# My Milestones

## Professional Achievements
- Led team to ship product 2 weeks ahead of schedule
- Increased user engagement by 45% through A/B testing
- Built automation that saved 20 hours/week

## Learning Milestones
- Completed Stanford ML course with 98% score
- Published 3 technical blog posts
- Learned Docker and deployed first containerized app

## Personal Growth
- Ran first 10K race
- Learned to cook 5 new recipes
- Read 24 books this year
```

The bot will parse this file and randomly select milestones to remind you about.

## 🚢 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment guides:

- **Docker Compose** (VPS) - $5-10/month
- **Google Cloud Run** - $0-5/month (free tier available)
- **systemd Service** (Linux) - Any VPS
- **Local Machine** - Free (for testing)

## 💰 Cost Estimate

- **Anthropic API**: ~$3-5/year (4 messages/day using Haiku model)
- **Hosting**: $0-10/month depending on platform
- **Total**: ~$5-15/year

## 🧪 Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_parser.py -v
```

## 🎨 Customization

### Change Reminder Times
Edit `SCHEDULE_TIMES` in `.env`:
```env
SCHEDULE_TIMES=07:00,13:00,18:00,22:00
```

### Change AI Model
Use Sonnet for more creative rephrasing (costs more):
```env
MODEL=claude-3-5-sonnet-20241022
```

Use Haiku for faster, cheaper responses (recommended):
```env
MODEL=claude-3-5-haiku-20241022
```

### Customize Prompt Style
Edit `src/ai/prompts.py` to change how milestones are delivered.

## 🤝 Contributing

Contributions welcome! Feel free to:
- Fork for your own use
- Submit issues for bugs
- Share ideas for improvements
- Submit PRs for new features

## 📝 License

MIT License - Use freely for personal or commercial projects

---

*Because sometimes we all need a reminder of how far we've come.*
