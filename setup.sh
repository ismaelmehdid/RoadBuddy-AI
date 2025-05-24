#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to build and start services
start_services() {
    echo "Building and starting services..."
    docker-compose up --build -d
    echo -e "${GREEN}Services are up and running!${NC}"
}

# Function to stop services
stop_services() {
    echo "Stopping services..."
    docker-compose down
    echo -e "${GREEN}Services stopped${NC}"
}

# Main script
case "$1" in
    "start")
        check_docker
        start_services
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        start_services
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac