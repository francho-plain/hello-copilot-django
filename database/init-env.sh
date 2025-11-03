#!/bin/bash
# init-env.sh - Environment variable initialization script for PostgreSQL

set -e

echo "🔧 Initializing PostgreSQL with environment variables..."

# Display environment information (without sensitive data)
echo "📊 Database Configuration:"
echo "  Database: ${POSTGRES_DB}"
echo "  User: ${POSTGRES_USER}"
echo "  Max Connections: ${POSTGRES_MAX_CONNECTIONS}"
echo "  Shared Buffers: ${POSTGRES_SHARED_BUFFERS}"
echo "  Environment: ${ENVIRONMENT:-development}"

# Configure PostgreSQL based on environment
if [ "$ENVIRONMENT" = "production" ]; then
    echo "🔒 Applying production configuration..."
    
    # Production-specific settings
    cat >> ${PGDATA}/postgresql.conf <<EOF

# Production Configuration
max_connections = ${POSTGRES_MAX_CONNECTIONS}
shared_buffers = ${POSTGRES_SHARED_BUFFERS}
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# Logging
log_statement = 'all'
log_duration = on
log_min_duration_statement = 1000

# Security
ssl = on
password_encryption = scram-sha-256

# Performance
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
EOF

    echo "✅ Production configuration applied"
    
elif [ "$ENVIRONMENT" = "development" ]; then
    echo "🛠️ Applying development configuration..."
    
    # Development-specific settings
    cat >> ${PGDATA}/postgresql.conf <<EOF

# Development Configuration
max_connections = ${POSTGRES_MAX_CONNECTIONS}
shared_buffers = ${POSTGRES_SHARED_BUFFERS}

# Enhanced logging for development
log_statement = 'all'
log_duration = on
log_min_duration_statement = 0
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '

# Development conveniences
shared_preload_libraries = 'pg_stat_statements'
track_activity_query_size = 2048
EOF

    echo "✅ Development configuration applied"
fi

# Validate required environment variables
required_vars=("POSTGRES_DB" "POSTGRES_USER" "POSTGRES_PASSWORD")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: Required environment variable $var is not set"
        exit 1
    fi
done

# Create connection URL for reference (without password)
export POSTGRES_URL_NO_PASS="postgresql://${POSTGRES_USER}@${POSTGRES_HOST:-localhost}:${POSTGRES_PORT:-5432}/${POSTGRES_DB}"

echo "🔗 Connection URL: ${POSTGRES_URL_NO_PASS}"
echo "✅ Environment initialization complete!"

# Create a status file
echo "Environment initialized at $(date)" > /var/lib/postgresql/data/env_status.txt