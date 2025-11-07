# DigitalOcean MCP Server Docker Wrapper Script (PowerShell)
# This script helps build and run the DigitalOcean MCP server Docker container

param(
    [Parameter(Position=0)]
    [ValidateSet("build", "run", "build-run", "stop", "logs", "clean", "help")]
    [string]$Command = "help",
    
    [Parameter()]
    [string]$Token = $env:DIGITALOCEAN_API_TOKEN,
    
    [Parameter()]
    [string]$Image = "digitalocean-mcp-server",
    
    [Parameter()]
    [string]$Container = "digitalocean-mcp-server",
    
    [Parameter()]
    [switch]$Help
)

# Default values
$ErrorActionPreference = "Stop"

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Show-Help {
    Write-Host @"
DigitalOcean MCP Server Docker Wrapper (PowerShell)

USAGE:
    .\docker-run.ps1 [COMMAND] [OPTIONS]

COMMANDS:
    build               Build the Docker image
    run                 Run the Docker container
    build-run           Build and then run the container
    stop                Stop the running container
    logs                View container logs
    clean               Remove the Docker image and container
    help                Show this help message

OPTIONS:
    -Token TOKEN        Set DigitalOcean API token
    -Image NAME         Docker image name (default: digitalocean-mcp-server)
    -Container NAME     Container name (default: digitalocean-mcp-server)
    -Help               Show this help message

ENVIRONMENT VARIABLES:
    DIGITALOCEAN_API_TOKEN    DigitalOcean API token (can be set instead of -Token option)

EXAMPLES:
    # Build the image
    .\docker-run.ps1 build

    # Run with token from environment variable
    `$env:DIGITALOCEAN_API_TOKEN = "your-token"
    .\docker-run.ps1 run

    # Run with token as parameter
    .\docker-run.ps1 run -Token "your-token"

    # Build and run in one command
    .\docker-run.ps1 build-run -Token "your-token"

    # View logs
    .\docker-run.ps1 logs

    # Stop the container
    .\docker-run.ps1 stop

    # Clean up (remove image and container)
    .\docker-run.ps1 clean

NOTES:
    - The API token can be provided via the -Token parameter or the DIGITALOCEAN_API_TOKEN environment variable
    - If using docker-compose, use: docker-compose up
    - The container runs in interactive mode for MCP stdio communication

"@
}

function Test-Docker {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "Docker is not installed or not in PATH"
        exit 1
    }
}

function Test-Token {
    if ([string]::IsNullOrEmpty($Token)) {
        Write-Error "DigitalOcean API token is required"
        Write-Host ""
        Write-Host "Set it using one of these methods:"
        Write-Host "  1. Use -Token parameter: .\docker-run.ps1 run -Token 'your-token'"
        Write-Host "  2. Set environment variable: `$env:DIGITALOCEAN_API_TOKEN = 'your-token'"
        Write-Host "  3. Create a .env file with: DIGITALOCEAN_API_TOKEN=your-token"
        exit 1
    }
}

function Build-Image {
    Write-Info "Building Docker image: $Image"
    docker build -t $Image .
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Image '$Image' built successfully"
    } else {
        Write-Error "Failed to build image"
        exit 1
    }
}

function Run-Container {
    Test-Token
    
    # Check if container is already running
    $running = docker ps --format '{{.Names}}' | Select-String -Pattern "^$Container$"
    if ($running) {
        Write-Warning "Container '$Container' is already running"
        Write-Host "Use '.\docker-run.ps1 stop' to stop it first, or use '.\docker-run.ps1 logs' to view logs"
        exit 1
    }
    
    # Remove stopped container if it exists
    $exists = docker ps -a --format '{{.Names}}' | Select-String -Pattern "^$Container$"
    if ($exists) {
        Write-Info "Removing existing stopped container"
        docker rm $Container 2>&1 | Out-Null
    }
    
    Write-Info "Running container: $Container"
    $tokenPreview = if ($Token.Length -gt 10) { $Token.Substring(0, 10) + "..." } else { $Token }
    Write-Info "Using API token: $tokenPreview"
    
    docker run -it --rm `
        --name $Container `
        -e DIGITALOCEAN_API_TOKEN=$Token `
        $Image
}

function Stop-Container {
    $running = docker ps --format '{{.Names}}' | Select-String -Pattern "^$Container$"
    if ($running) {
        Write-Info "Stopping container: $Container"
        docker stop $Container
        Write-Success "Container stopped"
    } else {
        Write-Warning "Container '$Container' is not running"
    }
}

function View-Logs {
    $exists = docker ps -a --format '{{.Names}}' | Select-String -Pattern "^$Container$"
    if ($exists) {
        Write-Info "Viewing logs for: $Container"
        docker logs -f $Container
    } else {
        Write-Warning "Container '$Container' does not exist"
    }
}

function Clean-Up {
    Write-Info "Cleaning up Docker resources..."
    
    # Stop and remove container if running
    $running = docker ps --format '{{.Names}}' | Select-String -Pattern "^$Container$"
    if ($running) {
        Write-Info "Stopping container: $Container"
        docker stop $Container 2>&1 | Out-Null
    }
    
    $exists = docker ps -a --format '{{.Names}}' | Select-String -Pattern "^$Container$"
    if ($exists) {
        Write-Info "Removing container: $Container"
        docker rm $Container 2>&1 | Out-Null
    }
    
    # Remove image if it exists
    $imageExists = docker images --format '{{.Repository}}' | Select-String -Pattern "^$Image$"
    if ($imageExists) {
        Write-Info "Removing image: $Image"
        docker rmi $Image 2>&1 | Out-Null
    }
    
    Write-Success "Cleanup complete"
}

function Build-And-Run {
    Build-Image
    Write-Host ""
    Run-Container
}

# Show help if requested
if ($Help -or $Command -eq "help") {
    Show-Help
    exit 0
}

# Check Docker availability
Test-Docker

# Execute the command
switch ($Command) {
    "build" {
        Build-Image
    }
    "run" {
        Run-Container
    }
    "build-run" {
        Build-And-Run
    }
    "stop" {
        Stop-Container
    }
    "logs" {
        View-Logs
    }
    "clean" {
        Clean-Up
    }
    default {
        Show-Help
        exit 1
    }
}

