#!/bin/bash

# High-performance Quiz System Docker deployment script
# Usage: ./deploy.sh [dev|prod] [--build] [--logs]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT=${1:-prod}
BUILD_FLAG=""
LOGS_FLAG=""

# Parse arguments
for arg in "$@"; do
    case $arg in
        --build)
            BUILD_FLAG="--build"
            shift
            ;;
        --logs)
            LOGS_FLAG="true"
            shift
            ;;
    esac
done

echo -e "${BLUE}🚀 Quiz System Docker Deployment${NC}"
echo -e "Environment: ${YELLOW}$ENVIRONMENT${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Pre-deployment checks
echo -e "\n${BLUE}📋 Pre-deployment checks...${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi
print_status "Docker is running"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed. Please install it and try again."
    exit 1
fi
print_status "docker-compose is available"

# Check for environment file
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        print_warning "No .env file found. Copying from .env.example"
        cp .env.example .env
        print_warning "Please edit .env file with your actual configuration before running again"
        exit 1
    else
        print_error "No .env file found. Please create one based on .env.example"
        exit 1
    fi
fi
print_status "Environment file exists"

# Create necessary directories
echo -e "\n${BLUE}📁 Creating directories...${NC}"
mkdir -p img quiz result tmp
print_status "Directories created"

# Initialize database if it doesn't exist
if [ ! -f data.sqlite ]; then
    print_warning "Database file not found. Will be created on first run."
fi

# Set up environment-specific configuration
if [ "$ENVIRONMENT" = "dev" ]; then
    export FLASK_ENV=development
    export COMPOSE_FILE=docker-compose.yml:docker-compose.dev.yml
    echo -e "${YELLOW}📝 Using development configuration${NC}"
else
    export FLASK_ENV=production
    export COMPOSE_FILE=docker-compose.yml
    echo -e "${GREEN}🏭 Using production configuration${NC}"
fi

# Build and deploy
echo -e "\n${BLUE}🏗️ Building and deploying...${NC}"

if [ "$BUILD_FLAG" = "--build" ]; then
    print_status "Building images..."
    docker-compose build --no-cache
fi

print_status "Starting services..."
docker-compose up -d $BUILD_FLAG

# Wait for services to be healthy
echo -e "\n${BLUE}⏳ Waiting for services to be ready...${NC}"

# Function to check service health
check_health() {
    local service=$1
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps $service | grep -q "healthy\|Up"; then
            print_status "$service is ready"
            return 0
        fi

        if [ $attempt -eq $max_attempts ]; then
            print_error "$service failed to start properly"
            return 1
        fi

        echo -e "${YELLOW}⏳${NC} Waiting for $service... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
}

# Check each service
check_health quiz-app
check_health nginx

# Display deployment information
echo -e "\n${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "\n${BLUE}📊 Service Information:${NC}"
docker-compose ps

echo -e "\n${BLUE}🌐 Access URLs:${NC}"
echo -e "  Main Application: ${GREEN}http://localhost${NC}"
echo -e "  Health Check:     ${GREEN}http://localhost/health${NC}"
echo -e "  Admin Login:      ${GREEN}http://localhost/admin_login${NC}"

if docker-compose ps grafana 2>/dev/null | grep -q "Up"; then
    echo -e "  Grafana:          ${GREEN}http://localhost:3000${NC}"
fi

if docker-compose ps prometheus 2>/dev/null | grep -q "Up"; then
    echo -e "  Prometheus:       ${GREEN}http://localhost:9090${NC}"
fi

# Display resource usage
echo -e "\n${BLUE}💾 Resource Usage:${NC}"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" $(docker-compose ps -q)

# Show logs if requested
if [ "$LOGS_FLAG" = "true" ]; then
    echo -e "\n${BLUE}📜 Service Logs:${NC}"
    docker-compose logs --tail=50
fi

echo -e "\n${BLUE}🔧 Useful Commands:${NC}"
echo -e "  View logs:        ${YELLOW}docker-compose logs -f${NC}"
echo -e "  Scale app:        ${YELLOW}docker-compose up -d --scale quiz-app=3${NC}"
echo -e "  Stop services:    ${YELLOW}docker-compose down${NC}"
echo -e "  Restart service:  ${YELLOW}docker-compose restart quiz-app${NC}"
echo -e "  Shell access:     ${YELLOW}docker-compose exec quiz-app /bin/bash${NC}"

echo -e "\n${GREEN}✨ Quiz System is now running in $ENVIRONMENT mode!${NC}"