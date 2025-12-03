# Deployment Guide - Cloud Run + Cloud Scheduler

## 💰 Cost: ~$0.10/month

This deployment uses:
- **Cloud Run** (min-instances=0, scales to zero when not in use)
- **Cloud Scheduler** (4 jobs: first 3 free, 4th = $0.10/month)

## 📋 Prerequisites

1. Google Cloud Platform account
2. `gcloud` CLI installed and configured
3. Docker installed (for building container)

## 🚀 Deployment Steps

### 1. Build and Deploy to Cloud Run

```bash
# Set your project ID
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Build and deploy
gcloud run deploy jar-of-awesome \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 1 \
  --memory 512Mi \
  --timeout 60s \
  --set-env-vars RUN_MODE=http \
  --set-env-vars TELEGRAM_BOT_TOKEN="your-bot-token" \
  --set-env-vars TELEGRAM_USER_ID="your-user-id" \
  --set-env-vars USE_PREGENERATED=1 \
  --set-env-vars DEBUG=0 \
  --project $PROJECT_ID
```

**Important**: Replace `your-bot-token` and `your-user-id` with actual values!

### 2. Get Service URL

```bash
# Get your Cloud Run service URL
gcloud run services describe jar-of-awesome \
  --platform managed \
  --region $REGION \
  --format 'value(status.url)' \
  --project $PROJECT_ID
```

Copy this URL (e.g., `https://jar-of-awesome-xxx.a.run.app`)

### 3. Setup Cloud Scheduler

```bash
# Edit setup-cloud-scheduler.sh with your values
nano setup-cloud-scheduler.sh

# Update these lines:
# PROJECT_ID="your-project-id"
# SERVICE_URL="https://your-cloud-run-url"

# Run the setup script
./setup-cloud-scheduler.sh
```

### 4. Test the Setup

```bash
# Test health endpoint
curl https://your-cloud-run-url/

# Manually trigger milestone (for testing)
curl -X POST https://your-cloud-run-url/cron/send-milestone

# Test a scheduled job
gcloud scheduler jobs run jar-of-awesome-morning \
  --location $REGION \
  --project $PROJECT_ID
```

## 📊 Verify Deployment

### Check Cloud Run logs
```bash
gcloud run services logs read jar-of-awesome \
  --region $REGION \
  --project $PROJECT_ID
```

### Check Cloud Scheduler jobs
```bash
gcloud scheduler jobs list \
  --location $REGION \
  --project $PROJECT_ID
```

### View Scheduler execution history
```bash
gcloud logging read \
  "resource.type=cloud_scheduler_job" \
  --limit 10 \
  --project $PROJECT_ID
```

## 🔧 Local Testing (Before Deployment)

### Test HTTP mode locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run in HTTP mode
RUN_MODE=http python -m src.main
```

Visit `http://localhost:8080/` for health check
Test trigger: `curl -X POST http://localhost:8080/cron/send-milestone`

### Test Bot mode locally (current behavior)
```bash
# Run normally (keeps bot running with APScheduler)
python -m src.main
```

## 📅 Schedule Times

The bot will send milestones at:
- 🌅 8:00 AM (Asia/Taipei)
- ☀️ 12:00 PM (Asia/Taipei)
- 🌤️ 4:00 PM (Asia/Taipei)
- 🌙 8:00 PM (Asia/Taipei)

To change times, edit `setup-cloud-scheduler.sh` and update the `--schedule` parameters.

## 💸 Cost Breakdown

| Service | Usage | Cost |
|---------|-------|------|
| Cloud Run | 4 requests/day × 30 days = 120 requests | Free tier (2M requests/month) |
| Cloud Run | ~5 seconds per invocation | Free tier (360,000 vCPU-seconds/month) |
| Cloud Scheduler | 4 jobs | First 3 free, 4th = **$0.10/month** |
| **Total** | | **~$0.10/month** |

## 🔄 Update Deployment

To update milestones or code:

```bash
# Update files locally, then redeploy
gcloud run deploy jar-of-awesome \
  --source . \
  --region $REGION \
  --project $PROJECT_ID
```

Cloud Scheduler jobs don't need to be recreated unless you change the schedule times.

## 🐛 Troubleshooting

### Bot not sending messages
1. Check Cloud Run logs: `gcloud run services logs read jar-of-awesome`
2. Verify env vars are set correctly
3. Test manually: `curl -X POST https://your-url/cron/send-milestone`

### Scheduler jobs not running
1. Check job status: `gcloud scheduler jobs list`
2. View scheduler logs: `gcloud logging read "resource.type=cloud_scheduler_job"`
3. Manually run job to test: `gcloud scheduler jobs run jar-of-awesome-morning`

### Cost higher than expected
- Verify `min-instances` is set to 0
- Check that you're not getting extra traffic
- View billing: https://console.cloud.google.com/billing
