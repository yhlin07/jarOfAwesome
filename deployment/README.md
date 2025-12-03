# Deployment Guide

This directory contains deployment configurations for different platforms.

## Prerequisites

1. **Telegram Bot Setup:**
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Create new bot with `/newbot`
   - Save the bot token

2. **Get Your Telegram User ID:**
   - Message [@userinfobot](https://t.me/userinfobot)
   - Save your user ID

3. **Anthropic API Key:**
   - Sign up at [console.anthropic.com](https://console.anthropic.com/)
   - Create API key
   - Save the key

4. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

---

## Option 1: Docker Compose (Recommended for VPS)

**Best for:** Running on any server (DigitalOcean, AWS EC2, etc.)

### Setup:

```bash
# 1. Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 2. Configure environment
cp .env.example .env
nano .env  # Edit with your values

# 3. Build and run
docker-compose up -d

# 4. Check logs
docker-compose logs -f

# 5. Stop
docker-compose down
```

### Update milestones without restart:
```bash
# Edit milestones.md
nano milestones.md

# Restart to reload (takes 2 seconds)
docker-compose restart
```

**Cost:** $5-10/month for basic VPS

---

## Option 2: Google Cloud Run

**Best for:** Serverless, auto-scaling, generous free tier

### Setup:

```bash
# 1. Install Google Cloud SDK
# See: https://cloud.google.com/sdk/docs/install

# 2. Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 3. Build and push container
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/jar-of-awesome

# 4. Deploy
gcloud run deploy jar-of-awesome \
  --image gcr.io/YOUR_PROJECT_ID/jar-of-awesome \
  --platform managed \
  --region us-central1 \
  --set-env-vars TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN,TELEGRAM_USER_ID=$TELEGRAM_USER_ID,ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  --memory 256Mi \
  --timeout 3600s \
  --no-allow-unauthenticated \
  --min-instances 1
```

**Cost:** ~$0-5/month (within free tier)

---

## Option 3: Local Development

**Best for:** Testing before deployment

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
nano .env

# 4. Run
python -m src.main
```

---

## Option 4: systemd Service (Linux VPS)

**Best for:** Running as background service on Linux

### Setup:

1. **Copy files to server:**
   ```bash
   scp -r . user@your-server:/opt/jar-of-awesome
   ```

2. **Install dependencies:**
   ```bash
   cd /opt/jar-of-awesome
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Create systemd service:**
   ```bash
   sudo nano /etc/systemd/system/jar-of-awesome.service
   ```

   ```ini
   [Unit]
   Description=Jar of Awesome Bot
   After=network.target

   [Service]
   Type=simple
   User=botuser
   WorkingDirectory=/opt/jar-of-awesome
   Environment="PATH=/opt/jar-of-awesome/venv/bin"
   EnvironmentFile=/opt/jar-of-awesome/.env
   ExecStart=/opt/jar-of-awesome/venv/bin/python -m src.main
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

4. **Start service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable jar-of-awesome
   sudo systemctl start jar-of-awesome
   sudo systemctl status jar-of-awesome
   ```

5. **View logs:**
   ```bash
   sudo journalctl -u jar-of-awesome -f
   ```

---

## Monitoring

### Check if bot is running:
```bash
# Docker
docker-compose ps

# systemd
sudo systemctl status jar-of-awesome

# Local
ps aux | grep "src.main"
```

### View logs:
```bash
# Docker
docker-compose logs -f --tail=100

# systemd
sudo journalctl -u jar-of-awesome -f -n 100
```

---

## Troubleshooting

### Bot not sending messages:

1. **Check credentials:**
   ```bash
   cat .env  # Verify values
   ```

2. **Test bot token:**
   ```bash
   curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe
   ```

3. **Check logs for errors:**
   - Look for API errors (invalid token)
   - Check timezone configuration
   - Verify milestone file path

### Bot crashes on startup:

1. **Missing .env file:**
   ```bash
   cp .env.example .env
   ```

2. **Invalid schedule times:**
   - Must be in HH:MM format
   - Example: `SCHEDULE_TIMES=08:00,12:00,16:00,20:00`

3. **Missing milestone file:**
   - Ensure `milestones.md` exists in project root

---

## Security Notes

⚠️ **Important:**
- Never commit `.env` file to git
- Keep API keys secure
- Use environment variables in production
- Run bot as non-root user (handled in Docker)

---

## Cost Estimates

| Platform | Monthly Cost | Uptime | Maintenance |
|----------|-------------|--------|-------------|
| Cloud Run | $0-5 | 99.9% | Low |
| VPS (DigitalOcean) | $5-10 | 99.99% | Medium |
| Local Machine | $0 | Depends | High |

**Anthropic API:** ~$3-5/year (4 messages/day × 365 days × ~150 tokens)

---

## Next Steps

1. Choose deployment option
2. Follow setup instructions above
3. Test with `/start` command in Telegram
4. Monitor logs for first 24 hours
5. Enjoy your daily milestones! ☀️
