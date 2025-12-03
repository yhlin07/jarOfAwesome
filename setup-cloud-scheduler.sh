#!/bin/bash
# Setup Cloud Scheduler for Jar of Awesome Bot
# This creates 4 scheduled jobs to trigger affirmations at specific times

set -e

# Configuration
PROJECT_ID="jar-of-awesome-bot"
REGION="asia-east1"
SERVICE_URL="https://jar-of-awesome-okltujfhpa-de.a.run.app"
TIMEZONE="Asia/Taipei"

echo "🔧 Setting up Cloud Scheduler..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service URL: $SERVICE_URL"
echo "Timezone: $TIMEZONE"
echo ""

# Enable Cloud Scheduler API (if not already enabled)
echo "📡 Enabling Cloud Scheduler API..."
gcloud services enable cloudscheduler.googleapis.com --project=$PROJECT_ID

# Create scheduler jobs for 8am, 12pm, 4pm, 8pm

echo "⏰ Creating morning job (8:00 AM)..."
gcloud scheduler jobs create http jar-of-awesome-morning \
  --location=$REGION \
  --schedule="0 8 * * *" \
  --uri="$SERVICE_URL/cron/send-affirmation" \
  --http-method=POST \
  --time-zone="$TIMEZONE" \
  --attempt-deadline=60s \
  --project=$PROJECT_ID \
  || echo "Job already exists, skipping..."

echo "🌞 Creating noon job (12:00 PM)..."
gcloud scheduler jobs create http jar-of-awesome-noon \
  --location=$REGION \
  --schedule="0 12 * * *" \
  --uri="$SERVICE_URL/cron/send-affirmation" \
  --http-method=POST \
  --time-zone="$TIMEZONE" \
  --attempt-deadline=60s \
  --project=$PROJECT_ID \
  || echo "Job already exists, skipping..."

echo "🌤️ Creating afternoon job (4:00 PM)..."
gcloud scheduler jobs create http jar-of-awesome-afternoon \
  --location=$REGION \
  --schedule="0 16 * * *" \
  --uri="$SERVICE_URL/cron/send-affirmation" \
  --http-method=POST \
  --time-zone="$TIMEZONE" \
  --attempt-deadline=60s \
  --project=$PROJECT_ID \
  || echo "Job already exists, skipping..."

echo "🌙 Creating evening job (8:00 PM)..."
gcloud scheduler jobs create http jar-of-awesome-evening \
  --location=$REGION \
  --schedule="0 20 * * *" \
  --uri="$SERVICE_URL/cron/send-affirmation" \
  --http-method=POST \
  --time-zone="$TIMEZONE" \
  --attempt-deadline=60s \
  --project=$PROJECT_ID \
  || echo "Job already exists, skipping..."

echo ""
echo "✅ Cloud Scheduler setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Verify jobs: gcloud scheduler jobs list --location=$REGION --project=$PROJECT_ID"
echo "2. Test a job: gcloud scheduler jobs run jar-of-awesome-morning --location=$REGION --project=$PROJECT_ID"
echo "3. View logs: gcloud logging read \"resource.type=cloud_scheduler_job\" --limit=10 --project=$PROJECT_ID"
echo ""
echo "💰 Cost estimate: ~\$0.10/month (4 jobs, first 3 free)"
