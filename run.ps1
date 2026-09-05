<#
.SYNOPSIS
    Setup and run the AI Global Pulse Dashboard.
    
.DESCRIPTION
    This script automates the setup and execution of the Docker environment for the dashboard.
    It builds the containers and starts them up. If the -Mock switch is used, it injects
    synthetic data to bypass external API calls.
    
.PARAMETER Mock
    Runs the pipeline using synthetic data instead of live external API calls.
    
.EXAMPLE
    .\run.ps1
    Starts the environment with live data fetching (requires API keys in .env).

.EXAMPLE
    .\run.ps1 -Mock
    Starts the environment with mock data for testing/demo purposes.
#>

param (
    [switch]$Mock = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AI Global Pulse Dashboard Setup    " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
docker info > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Docker is not running or not installed. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Building and starting Docker containers..." -ForegroundColor Green
docker compose up --build -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to start Docker containers." -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Containers are up and running!" -ForegroundColor Green

if ($Mock) {
    Write-Host "[INFO] Waiting 5 seconds for containers to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    Write-Host "[INFO] Running pipeline in Mock mode (synthetic data)..." -ForegroundColor Magenta
    docker compose run --rm pipeline_worker python sentiment_pipeline.py --mock
} else {
    Write-Host "[INFO] Running in Live mode." -ForegroundColor Yellow
    Write-Host "[!] Ensure you have configured your .env file or docker-compose.yml with valid NEWS_API_KEY and LLM_API_KEY." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 Dashboard is now available at: http://localhost:3000" -ForegroundColor Green
Write-Host "🛑 To stop the application, run: docker compose down" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
