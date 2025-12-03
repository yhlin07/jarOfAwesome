#!/bin/bash
# Fix Cloud Scheduler timezone by deleting and recreating jobs

set -e

PROJECT_ID="${GCP_PROJECT_ID}"
REGION="asia-east1"
TIMEZONE="America/Los_Angeles"

echo "🔧 Fixing Cloud Scheduler timezone..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Target Timezone: $TIMEZONE"
echo ""

# Get service URL
SERVICE_URL=$(gcloud run services describe jar-of-awesome \
  --platform managed \
  --region $REGION \
  --format 'value(status.url)' \
  --project $PROJECT_ID)

echo "Service URL: $SERVICE_URL"
echo ""

# Delete existing jobs
echo "🗑️  Deleting old jobs..."
for JOB_NAME in "jar-of-awesome-morning" "jar-of-awesome-noon" "jar-of-awesome-afternoon" "jar-of-awesome-evening"; do
  echo "  Deleting $JOB_NAME..."
  gcloud scheduler jobs delete $JOB_NAME \
    --location=$REGION \
    --project=$PROJECT_ID \
    --quiet 2>/dev/null && echo "    ✅ Deleted" || echo "    ⚠️  Not found (skipping)"
done

echo ""
echo "✨ Creating new jobs with correct timezone..."

# Create 4 jobs for 8am, 12pm, 4pm, 8pm (America/Los_Angeles)
for TIME_INFO in "morning:8" "noon:12" "afternoon:16" "evening:20"; do
  IFS=':' read -r LABEL HOUR <<< "$TIME_INFO"
  JOB_NAME="jar-of-awesome-$LABEL"

  echo "  Creating $JOB_NAME at ${HOUR}:00 $TIMEZONE..."

  gcloud scheduler jobs create http $JOB_NAME \
    --location=$REGION \
    --schedule="0 ${HOUR} * * *" \
    --uri="$SERVICE_URL/cron/send-affirmation" \
    --http-method=POST \
    --time-zone="$TIMEZONE" \
    --attempt-deadline=60s \
    --project=$PROJECT_ID && echo "    ✅ Created" || echo "    ❌ Failed"
done

echo ""
echo "📊 Verifying jobs..."
gcloud scheduler jobs list --location=$REGION --project=$PROJECT_ID

echo ""
echo "✅ Done! Jobs should now trigger at:"
echo "   08:00 $TIMEZONE (morning)"
echo "   12:00 $TIMEZONE (noon)"
echo "   16:00 $TIMEZONE (afternoon)"
echo "   20:00 $TIMEZONE (evening)"
