# Get all deployed Cloud Run service URLs
$REGION = "us-central1"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Cloud Run Service URLs" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

$PLOT_URL = gcloud run services describe plot-service --region=$REGION --format="value(status.url)" 2>$null
$CALC_URL = gcloud run services describe calculator --region=$REGION --format="value(status.url)" 2>$null
$PDF_URL = gcloud run services describe pdf-parser --region=$REGION --format="value(status.url)" 2>$null

Write-Host "plot-service:" -ForegroundColor Yellow -NoNewline
Write-Host " $PLOT_URL/mcp/plot"

Write-Host "calculator:  " -ForegroundColor Yellow -NoNewline
Write-Host " $CALC_URL/mcp/calculate"

Write-Host "pdf-parser:  " -ForegroundColor Yellow -NoNewline
Write-Host " $PDF_URL/mcp/parse"

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Add to your .env file:" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "PLOT_SERVICE_URL=$PLOT_URL/mcp/plot"
Write-Host "CALCULATOR_URL=$CALC_URL/mcp/calculate"
Write-Host "PDF_PARSER_URL=$PDF_URL/mcp/parse"
