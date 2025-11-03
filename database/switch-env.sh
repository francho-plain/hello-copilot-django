#!/bin/bash
# switch-env.sh - Environment switcher for PostgreSQL configurations

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_DIR="$SCRIPT_DIR"

# Available environments
ENVIRONMENTS=("development" "testing" "production")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

usage() {
    echo "🔄 PostgreSQL Environment Switcher"
    echo "=================================="
    echo ""
    echo "Usage: $0 <environment>"
    echo ""
    echo "Available environments:"
    for env in "${ENVIRONMENTS[@]}"; do
        echo "  - $env"
    done
    echo ""
    echo "Examples:"
    echo "  $0 development    # Switch to development environment"
    echo "  $0 production     # Switch to production environment"
    echo "  $0 testing        # Switch to testing environment"
    echo ""
    echo "This script will:"
    echo "  1. Copy the appropriate .env.<environment> file to .env"
    echo "  2. Stop current containers"
    echo "  3. Start containers with new configuration"
}

check_environment() {
    local env="$1"
    local env_file="$ENV_DIR/.env.$env"
    
    if [[ ! " ${ENVIRONMENTS[@]} " =~ " ${env} " ]]; then
        echo -e "${RED}❌ Error: Invalid environment '$env'${NC}"
        echo -e "${YELLOW}Available environments: ${ENVIRONMENTS[*]}${NC}"
        return 1
    fi
    
    if [[ ! -f "$env_file" ]]; then
        echo -e "${RED}❌ Error: Environment file '$env_file' not found${NC}"
        return 1
    fi
    
    return 0
}

backup_current_env() {
    local backup_file="$ENV_DIR/.env.backup.$(date +%Y%m%d_%H%M%S)"
    
    if [[ -f "$ENV_DIR/.env" ]]; then
        echo -e "${BLUE}📦 Backing up current .env to $(basename "$backup_file")${NC}"
        cp "$ENV_DIR/.env" "$backup_file"
    fi
}

switch_environment() {
    local env="$1"
    local env_file="$ENV_DIR/.env.$env"
    local target_file="$ENV_DIR/.env"
    
    echo -e "${BLUE}🔄 Switching to $env environment...${NC}"
    
    # Copy environment file
    cp "$env_file" "$target_file"
    echo -e "${GREEN}✅ Environment file copied${NC}"
    
    # Show configuration summary
    echo -e "${BLUE}📋 Configuration Summary:${NC}"
    echo "  Database: $(grep POSTGRES_DB= "$target_file" | cut -d'=' -f2)"
    echo "  Host: $(grep POSTGRES_HOST= "$target_file" | cut -d'=' -f2)"
    echo "  Port: $(grep POSTGRES_PORT= "$target_file" | cut -d'=' -f2)"
    echo "  User: $(grep POSTGRES_USER= "$target_file" | cut -d'=' -f2)"
    echo "  Environment: $(grep ENVIRONMENT= "$target_file" | cut -d'=' -f2)"
}

restart_containers() {
    echo -e "${BLUE}🐳 Restarting Docker containers...${NC}"
    
    # Stop existing containers
    if docker compose ps -q > /dev/null 2>&1; then
        echo "  Stopping existing containers..."
        docker compose down
    fi
    
    # Start with new configuration
    echo "  Starting containers with new configuration..."
    docker compose up -d
    
    # Wait for health check
    echo "  Waiting for database to be ready..."
    sleep 5
    
    # Check status
    if docker compose ps | grep -q "healthy\|Up"; then
        echo -e "${GREEN}✅ Containers started successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  Containers started, checking status...${NC}"
        docker compose ps
    fi
}

test_connection() {
    local env="$1"
    
    echo -e "${BLUE}🔍 Testing database connection...${NC}"
    
    # Source the environment file to get variables
    source "$ENV_DIR/.env"
    
    # Test connection using the Python script
    cd "$SCRIPT_DIR/../scripts"
    if python3 check_postgres.py > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Database connection successful${NC}"
    else
        echo -e "${YELLOW}⚠️  Database connection test failed. This might be normal if containers are still starting.${NC}"
        echo -e "${YELLOW}   Try running: cd ../scripts && python3 check_postgres.py${NC}"
    fi
}

show_next_steps() {
    local env="$1"
    
    echo ""
    echo -e "${GREEN}🎉 Environment switched to $env successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Check container status: docker compose ps"
    echo "  2. View logs: docker compose logs -f"
    echo "  3. Test connection: cd ../scripts && python3 check_postgres.py"
    echo "  4. Connect manually: psql -h localhost -p \$POSTGRES_PORT -U \$POSTGRES_USER -d \$POSTGRES_DB"
    echo ""
    echo "Environment files:"
    echo "  Current: .env"
    echo "  Source: .env.$env"
    echo "  Backup: .env.backup.*"
}

main() {
    local environment="$1"
    
    # Show usage if no argument provided
    if [[ -z "$environment" ]]; then
        usage
        exit 1
    fi
    
    # Show usage for help flags
    if [[ "$environment" == "-h" || "$environment" == "--help" ]]; then
        usage
        exit 0
    fi
    
    # Change to script directory
    cd "$SCRIPT_DIR"
    
    echo -e "${BLUE}🔄 PostgreSQL Environment Switcher${NC}"
    echo "=================================="
    
    # Validate environment
    if ! check_environment "$environment"; then
        exit 1
    fi
    
    # Backup current environment
    backup_current_env
    
    # Switch environment
    switch_environment "$environment"
    
    # Ask for confirmation before restarting containers
    echo ""
    read -p "🐳 Restart Docker containers with new configuration? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        restart_containers
        test_connection "$environment"
    else
        echo -e "${YELLOW}⚠️  Skipped container restart. Remember to restart manually:${NC}"
        echo "   docker compose down && docker compose up -d"
    fi
    
    show_next_steps "$environment"
}

# Run main function with all arguments
main "$@"