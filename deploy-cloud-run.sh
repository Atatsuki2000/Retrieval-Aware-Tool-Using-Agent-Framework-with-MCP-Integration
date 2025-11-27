#!/bin/bash
# Deploy all MCP tools to Google Cloud Run
#
# Prerequisites:
# 1. Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install
# 2. Run: gcloud auth login
# 3. Run: gcloud config set project YOUR_PROJECT_ID
# 4. Enable required APIs:
#    gcloud services enable run.googleapis.com
#    gcloud services enable cloudbuild.googleapis.com

set -e  # Exit on error

# Configuration
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"  # Change to your preferred region

if [ -z "$PROJECT_ID" ]; then
    echo "Error: No GCP project configured. Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "Deploying to project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Function to deploy a service
deploy_service() {
    SERVICE_NAME=$1
    SERVICE_DIR=$2
    ENDPOINT_PATH=$3

    echo "=========================================="
    echo "Deploying $SERVICE_NAME..."
    echo "=========================================="

    cd "tools/$SERVICE_DIR"

    # Build and deploy to Cloud Run
    gcloud run deploy "$SERVICE_NAME" \
        --source . \
        --platform managed \
        --region "$REGION" \
        --allow-unauthenticated \
        --memory 512Mi \
        --cpu 1 \
        --timeout 60 \
        --max-instances 10 \
        --min-instances 0

    # Get service URL
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
        --region="$REGION" \
        --format="value(status.url)")

    echo ""
    echo "✅ $SERVICE_NAME deployed successfully!"
    echo "📍 URL: $SERVICE_URL$ENDPOINT_PATH"
    echo ""

    cd ../..
}

# Deploy each service
deploy_service "plot-service" "plot-service" "/mcp/plot"
deploy_service "calculator" "calculator" "/mcp/calculate"
deploy_service "pdf-parser" "pdf-parser" "/mcp/parse"

echo "=========================================="
echo "🎉 All services deployed successfully!"
echo "=========================================="
echo ""
echo "Service URLs:"
echo "-------------"
PLOT_URL=$(gcloud run services describe plot-service --region="$REGION" --format="value(status.url)")
CALC_URL=$(gcloud run services describe calculator --region="$REGION" --format="value(status.url)")
PDF_URL=$(gcloud run services describe pdf-parser --region="$REGION" --format="value(status.url)")

echo "plot-service: $PLOT_URL/mcp/plot"
echo "calculator:   $CALC_URL/mcp/calculate"
echo "pdf-parser:   $PDF_URL/mcp/parse"
echo ""
echo "To update your agent configuration, run:"
echo "export PLOT_SERVICE_URL=\"$PLOT_URL/mcp/plot\""
echo "export CALCULATOR_URL=\"$CALC_URL/mcp/calculate\""
echo "export PDF_PARSER_URL=\"$PDF_URL/mcp/parse\""
echo ""
echo "Or add to your .env file:"
echo "PLOT_SERVICE_URL=$PLOT_URL/mcp/plot"
echo "CALCULATOR_URL=$CALC_URL/mcp/calculate"
echo "PDF_PARSER_URL=$PDF_URL/mcp/parse"
