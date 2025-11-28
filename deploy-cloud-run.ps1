# Deploy all MCP tools to Google Cloud Run
#
# Prerequisites:
# 1. Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install
# 2. Run: gcloud auth login
# 3. Run: gcloud config set project YOUR_PROJECT_ID
# 4. Enable required APIs:
#    gcloud services enable run.googleapis.com
#    gcloud services enable cloudbuild.googleapis.com

$ErrorActionPreference = "Stop"  # Exit on error

# Configuration
$PROJECT_ID = gcloud config get-value project 2>$null
$REGION = "us-central1"  # Change to your preferred region

if ([string]::IsNullOrEmpty($PROJECT_ID)) {
    Write-Host "Error: No GCP project configured. Run: gcloud config set project YOUR_PROJECT_ID" -ForegroundColor Red
    exit 1
}

Write-Host "Deploying to project: $PROJECT_ID" -ForegroundColor Green
Write-Host "Region: $REGION" -ForegroundColor Green
Write-Host ""

# Function to deploy a service
function Deploy-Service {
    param(
        [string]$ServiceName,
        [string]$ServiceDir,
        [string]$EndpointPath
    )

    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "Deploying $ServiceName..." -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan

    Push-Location "tools\$ServiceDir"

    # Build and deploy to Cloud Run
    gcloud run deploy $ServiceName `
        --source . `
        --platform managed `
        --region $REGION `
        --allow-unauthenticated `
        --memory 512Mi `
        --cpu 1 `
        --timeout 60 `
        --max-instances 10 `
        --min-instances 0

    # Get service URL
    $SERVICE_URL = gcloud run services describe $ServiceName `
        --region=$REGION `
        --format="value(status.url)"

    Write-Host ""
    Write-Host "✅ $ServiceName deployed successfully!" -ForegroundColor Green
    Write-Host "📍 URL: $SERVICE_URL$EndpointPath" -ForegroundColor Yellow
    Write-Host ""

    Pop-Location
}

# Deploy each service
Deploy-Service -ServiceName "plot-service" -ServiceDir "plot-service" -EndpointPath "/mcp/plot"
Deploy-Service -ServiceName "calculator" -ServiceDir "calculator" -EndpointPath "/mcp/calculate"
Deploy-Service -ServiceName "pdf-parser" -ServiceDir "pdf-parser" -EndpointPath "/mcp/parse"

Write-Host "==========================================" -ForegroundColor Green
Write-Host "🎉 All services deployed successfully!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Service URLs:" -ForegroundColor Cyan
Write-Host "-------------" -ForegroundColor Cyan

$PLOT_URL = gcloud run services describe plot-service --region=$REGION --format="value(status.url)"
$CALC_URL = gcloud run services describe calculator --region=$REGION --format="value(status.url)"
$PDF_URL = gcloud run services describe pdf-parser --region=$REGION --format="value(status.url)"

Write-Host "plot-service: $PLOT_URL/mcp/plot" -ForegroundColor Yellow
Write-Host "calculator:   $CALC_URL/mcp/calculate" -ForegroundColor Yellow
Write-Host "pdf-parser:   $PDF_URL/mcp/parse" -ForegroundColor Yellow
Write-Host ""
Write-Host "To update your agent configuration, add to your .env file:" -ForegroundColor Cyan
Write-Host "PLOT_SERVICE_URL=$PLOT_URL/mcp/plot"
Write-Host "CALCULATOR_URL=$CALC_URL/mcp/calculate"
Write-Host "PDF_PARSER_URL=$PDF_URL/mcp/parse"
