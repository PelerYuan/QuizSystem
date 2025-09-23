#!/bin/bash

# Quiz System Docker Maintenance Script
# Usage: ./maintenance.sh [backup|restore|update|logs|stats|clean]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ACTION=${1:-help}

print_status() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
print_info() { echo -e "${BLUE}ℹ${NC} $1"; }

case $ACTION in
    backup)
        echo -e "${BLUE}💾 Creating backup...${NC}"

        # Create backup directory
        BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
        mkdir -p $BACKUP_DIR

        # Backup database
        if [ -f data.sqlite ]; then
            cp data.sqlite $BACKUP_DIR/
            print_status "Database backed up"
        fi

        # Backup uploaded files
        if [ -d img ]; then
            cp -r img $BACKUP_DIR/
            print_status "Images backed up"
        fi

        # Backup quiz files
        if [ -d quiz ]; then
            cp -r quiz $BACKUP_DIR/
            print_status "Quiz files backed up"
        fi

        # Backup configuration
        if [ -f configure.json ]; then
            cp configure.json $BACKUP_DIR/
            print_status "Configuration backed up"
        fi

        # Create archive
        tar -czf $BACKUP_DIR.tar.gz -C backups $(basename $BACKUP_DIR)
        rm -rf $BACKUP_DIR

        print_status "Backup created: $BACKUP_DIR.tar.gz"
        ;;

    restore)
        echo -e "${BLUE}🔄 Restoring from backup...${NC}"

        if [ -z "$2" ]; then
            print_error "Please specify backup file: ./maintenance.sh restore backup_file.tar.gz"
            exit 1
        fi

        if [ ! -f "$2" ]; then
            print_error "Backup file not found: $2"
            exit 1
        fi

        # Extract backup
        tar -xzf "$2" -C .
        print_status "Backup restored from $2"

        # Restart services
        docker-compose restart
        print_status "Services restarted"
        ;;

    update)
        echo -e "${BLUE}🔄 Updating Quiz System...${NC}"

        # Pull latest images
        docker-compose pull
        print_status "Images updated"

        # Rebuild and restart
        docker-compose up -d --build
        print_status "Services updated and restarted"

        # Check health
        sleep 10
        if curl -f http://localhost/health > /dev/null 2>&1; then
            print_status "Health check passed"
        else
            print_warning "Health check failed - check logs"
        fi
        ;;

    logs)
        echo -e "${BLUE}📜 Showing service logs...${NC}"

        if [ -n "$2" ]; then
            docker-compose logs -f "$2"
        else
            docker-compose logs -f --tail=100
        fi
        ;;

    stats)
        echo -e "${BLUE}📊 System Statistics${NC}\n"

        echo -e "${YELLOW}Container Status:${NC}"
        docker-compose ps

        echo -e "\n${YELLOW}Resource Usage:${NC}"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.PIDs}}"

        echo -e "\n${YELLOW}Disk Usage:${NC}"
        docker system df

        echo -e "\n${YELLOW}Volume Information:${NC}"
        docker volume ls | grep quiz
        ;;

    clean)
        echo -e "${BLUE}🧹 Cleaning up Docker resources...${NC}"

        # Stop services
        docker-compose down
        print_status "Services stopped"

        # Remove unused containers, networks, images
        docker system prune -f
        print_status "Unused resources cleaned"

        # Remove dangling volumes (optional - commented for safety)
        # docker volume prune -f
        # print_status "Unused volumes cleaned"

        # Restart services
        docker-compose up -d
        print_status "Services restarted"
        ;;

    health)
        echo -e "${BLUE}🏥 Health Check...${NC}"

        # Check main application
        if curl -f http://localhost/health > /dev/null 2>&1; then
            print_status "Application is healthy"
        else
            print_error "Application health check failed"
        fi

        # Check individual services
        echo -e "\n${YELLOW}Service Health:${NC}"
        docker-compose ps
        ;;

    scale)
        if [ -z "$2" ]; then
            print_error "Please specify scale number: ./maintenance.sh scale 3"
            exit 1
        fi

        echo -e "${BLUE}⚖️ Scaling application to $2 instances...${NC}"
        docker-compose up -d --scale quiz-app=$2
        print_status "Application scaled to $2 instances"
        ;;

    help|*)
        echo -e "${BLUE}🛠️ Quiz System Maintenance Script${NC}\n"
        echo -e "Usage: ${YELLOW}./maintenance.sh [command] [options]${NC}\n"
        echo -e "Commands:"
        echo -e "  ${GREEN}backup${NC}           Create full system backup"
        echo -e "  ${GREEN}restore${NC} <file>   Restore from backup file"
        echo -e "  ${GREEN}update${NC}            Update and restart all services"
        echo -e "  ${GREEN}logs${NC} [service]   Show logs (optionally for specific service)"
        echo -e "  ${GREEN}stats${NC}             Show system statistics and resource usage"
        echo -e "  ${GREEN}clean${NC}             Clean up Docker resources"
        echo -e "  ${GREEN}health${NC}            Check system health"
        echo -e "  ${GREEN}scale${NC} <number>   Scale application instances"
        echo -e "  ${GREEN}help${NC}              Show this help message"
        echo -e "\nExamples:"
        echo -e "  ${YELLOW}./maintenance.sh backup${NC}"
        echo -e "  ${YELLOW}./maintenance.sh restore backups/20231201_120000.tar.gz${NC}"
        echo -e "  ${YELLOW}./maintenance.sh logs quiz-app${NC}"
        echo -e "  ${YELLOW}./maintenance.sh scale 3${NC}"
        ;;
esac