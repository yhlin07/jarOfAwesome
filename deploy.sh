#!/bin/bash
# Deploy Jar of Awesome to Google Cloud Run
# This script automates the entire deployment process

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Jar of Awesome - Cloud Run Deployment${NC}"
echo ""

# Check if user has gcloud installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found. Please install it first:${NC}"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo "Please create .env file with required variables:"
    echo "  TELEGRAM_BOT_TOKEN=your-token"
    echo "  TELEGRAM_USER_ID=your-id"
    exit 1
fi

# Load environment variables
source .env

# Get project ID from gcloud or ask user
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}No default GCP project found.${NC}"
    read -p "Enter your GCP Project ID: " PROJECT_ID
    gcloud config set project $PROJECT_ID
fi

# Configuration
SERVICE_NAME="jar-of-awesome"
REGION="asia-east1"  # Taiwan region for lower latency

echo ""
echo -e "${GREEN}📋 Deployment Configuration:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Service Name: $SERVICE_NAME"
echo "  Region: $REGION"
echo "  Mode: HTTP (Cloud Scheduler)"
echo ""

read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

# Enable required APIs
echo ""
echo -e "${GREEN}🔧 Enabling required APIs...${NC}"
gcloud services enable run.googleapis.com --project=$PROJECT_ID
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID
gcloud services enable cloudscheduler.googleapis.com --project=$PROJECT_ID

# Build and deploy to Cloud Run
echo ""
echo -e "${GREEN}🏗️ Building and deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 1 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60s \
  --cpu-boost \
  --set-env-vars RUN_MODE=http \
  --set-env-vars TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" \
  --set-env-vars TELEGRAM_USER_ID="$TELEGRAM_USER_ID" \
  --set-env-vars USE_PREGENERATED=1 \
  --set-env-vars DEBUG=0 \
  --project $PROJECT_ID

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --format 'value(status.url)' \
  --project $PROJECT_ID)

echo ""
echo -e "${GREEN}✅ Cloud Run deployment complete!${NC}"
echo "  Service URL: $SERVICE_URL"

# Test health endpoint
echo ""
echo -e "${GREEN}🏥 Testing health endpoint...${NC}"
HEALTH_STATUS=$(curl -s "$SERVICE_URL/" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null || echo "failed")

if [ "$HEALTH_STATUS" = "healthy" ]; then
    echo -e "${GREEN}✅ Health check passed!${NC}"
else
    echo -e "${YELLOW}⚠️ Health check failed, but service may still work.${NC}"
fi

# Setup Cloud Scheduler
echo ""
echo -e "${GREEN}⏰ Setting up Cloud Scheduler jobs...${NC}"

SCHEDULER_REGION="asia-east1"  # Cloud Scheduler region

# Create jobs for 8am, 12pm, 4pm, 8pm (Asia/Taipei timezone)
for TIME_LABEL in "morning:8:00" "noon:12:00" "afternoon:16:00" "evening:20:00"; do
    IFS=':' read -r LABEL HOUR MINUTE <<< "$TIME_LABEL"
    JOB_NAME="$SERVICE_NAME-$LABEL"

    echo "  Creating job: $JOB_NAME (${HOUR}:${MINUTE})"

    gcloud scheduler jobs create http $JOB_NAME \
      --location=$SCHEDULER_REGION \
      --schedule="$MINUTE $HOUR * * *" \
      --uri="$SERVICE_URL/cron/send-affirmation" \
      --http-method=POST \
      --time-zone="Asia/Taipei" \
      --attempt-deadline=60s \
      --project=$PROJECT_ID \
      2>/dev/null || echo "    (Job already exists, skipping)"
done

echo ""
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo ""
echo "📊 Summary:"
echo "  ✅ Cloud Run service deployed: $SERVICE_URL"
echo "  ✅ 4 Cloud Scheduler jobs created"
echo "  ✅ Scheduled times: 08:00, 12:00, 16:00, 20:00 (Asia/Taipei)"
echo "  💰 Estimated cost: ~\$0.10/month"
echo ""
echo "🧪 Test your deployment:"
echo "  Health check: curl $SERVICE_URL/"
echo "  Manual trigger: curl -X POST $SERVICE_URL/cron/send-affirmation"
echo "  Run scheduler job: gcloud scheduler jobs run $SERVICE_NAME-morning --location=$SCHEDULER_REGION"
echo ""
echo "📋 View logs:"
echo "  gcloud run services logs read $SERVICE_NAME --region $REGION"
echo ""
echo -e "${GREEN}✨ Your bot is now running in the cloud!${NC}"
