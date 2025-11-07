#!/bin/bash

# DigitalOcean MCP Server Docker Wrapper Script
# This script helps build and run the DigitalOcean MCP server Docker container

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
IMAGE_NAME="digitalocean-mcp-server"
CONTAINER_NAME="digitalocean-mcp-server"
API_TOKEN="${DIGITALOCEAN_API_TOKEN}"

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to display help message
show_help() {
    cat << EOF
DigitalOcean MCP Server Docker Wrapper

USAGE:
    $0 [OPTIONS] [COMMAND]

COMMANDS:
    build               Build the Docker image
    run                 Run the Docker container
    build-run           Build and then run the container
    stop                Stop the running container
    logs                View container logs
    clean               Remove the Docker image and container
    help                Show this help message

OPTIONS:
    -t, --token TOKEN   Set DigitalOcean API token
    -i, --image NAME    Docker image name (default: digitalocean-mcp-server)
    -c, --container NAME Container name (default: digitalocean-mcp-server)
    -h, --help          Show this help message

ENVIRONMENT VARIABLES:
    DIGITALOCEAN_API_TOKEN    DigitalOcean API token (can be set instead of -t option)

EXAMPLES:
    # Build the image
    $0 build

    # Run with token from environment variable
    export DIGITALOCEAN_API_TOKEN="your-token"
    $0 run

    # Run with token as option
    $0 run --token "your-token"

    # Build and run in one command
    $0 build-run --token "your-token"

    # View logs
    $0 logs

    # Stop the container
    $0 stop

    # Clean up (remove image and container)
    $0 clean

NOTES:
    - The API token can be provided via the -t/--token option or the DIGITALOCEAN_API_TOKEN environment variable
    - If using docker-compose, use: docker-compose up
    - The container runs in interactive mode for MCP stdio communication

EOF
}

# Function to check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
}

# Function to check if API token is set
check_token() {
    if [ -z "$API_TOKEN" ]; then
        print_error "DigitalOcean API token is required"
        echo ""
        echo "Set it using one of these methods:"
        echo "  1. Use -t/--token option: $0 run --token 'your-token'"
        echo "  2. Set environment variable: export DIGITALOCEAN_API_TOKEN='your-token'"
        echo "  3. Create a .env file with: DIGITALOCEAN_API_TOKEN=your-token"
        exit 1
    fi
}

# Function to build the Docker image
build_image() {
    print_info "Building Docker image: $IMAGE_NAME"
    docker build -t "$IMAGE_NAME" .
    
    if [ $? -eq 0 ]; then
        print_success "Image '$IMAGE_NAME' built successfully"
    else
        print_error "Failed to build image"
        exit 1
    fi
}

# Function to run the container
run_container() {
    check_token
    
    # Check if container is already running
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_warning "Container '$CONTAINER_NAME' is already running"
        echo "Use '$0 stop' to stop it first, or use '$0 logs' to view logs"
        exit 1
    fi
    
    # Remove stopped container if it exists
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_info "Removing existing stopped container"
        docker rm "$CONTAINER_NAME" > /dev/null 2>&1 || true
    fi
    
    print_info "Running container: $CONTAINER_NAME"
    print_info "Using API token: ${API_TOKEN:0:10}..." # Show first 10 chars for verification
    
    docker run -it --rm \
        --name "$CONTAINER_NAME" \
        -e DIGITALOCEAN_API_TOKEN="$API_TOKEN" \
        "$IMAGE_NAME"
}

# Function to stop the container
stop_container() {
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_info "Stopping container: $CONTAINER_NAME"
        docker stop "$CONTAINER_NAME"
        print_success "Container stopped"
    else
        print_warning "Container '$CONTAINER_NAME' is not running"
    fi
}

# Function to view logs
view_logs() {
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_info "Viewing logs for: $CONTAINER_NAME"
        docker logs -f "$CONTAINER_NAME"
    else
        print_warning "Container '$CONTAINER_NAME' does not exist"
    fi
}

# Function to clean up
clean_up() {
    print_info "Cleaning up Docker resources..."
    
    # Stop and remove container if running
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_info "Stopping container: $CONTAINER_NAME"
        docker stop "$CONTAINER_NAME" > /dev/null 2>&1 || true
    fi
    
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_info "Removing container: $CONTAINER_NAME"
        docker rm "$CONTAINER_NAME" > /dev/null 2>&1 || true
    fi
    
    # Remove image if it exists
    if docker images --format '{{.Repository}}' | grep -q "^${IMAGE_NAME}$"; then
        print_info "Removing image: $IMAGE_NAME"
        docker rmi "$IMAGE_NAME" > /dev/null 2>&1 || true
    fi
    
    print_success "Cleanup complete"
}

# Function to build and run
build_and_run() {
    build_image
    echo ""
    run_container
}

# Parse command line arguments
COMMAND=""
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--token)
            API_TOKEN="$2"
            shift 2
            ;;
        -i|--image)
            IMAGE_NAME="$2"
            shift 2
            ;;
        -c|--container)
            CONTAINER_NAME="$2"
            shift 2
            ;;
        -h|--help|help)
            show_help
            exit 0
            ;;
        build|run|build-run|stop|logs|clean)
            COMMAND="$1"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
done

# If no command provided, show help
if [ -z "$COMMAND" ]; then
    print_warning "No command specified"
    echo ""
    show_help
    exit 1
fi

# Check Docker availability
check_docker

# Execute the command
case $COMMAND in
    build)
        build_image
        ;;
    run)
        run_container
        ;;
    build-run)
        build_and_run
        ;;
    stop)
        stop_container
        ;;
    logs)
        view_logs
        ;;
    clean)
        clean_up
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac

