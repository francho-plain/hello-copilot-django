FROM postgres:15

# Install additional tools for environment variable handling
RUN apt-get update && apt-get install -y \
    gettext-base \
    && rm -rf /var/lib/apt/lists/*

# Create directory for custom configuration
RUN mkdir -p /docker-entrypoint-initdb.d/config

# Copy initialization script
COPY create-data.sql /docker-entrypoint-initdb.d/

# Copy environment-aware configuration script
COPY init-env.sh /docker-entrypoint-initdb.d/00-init-env.sh
RUN chmod +x /docker-entrypoint-initdb.d/00-init-env.sh

# Set default environment variables (can be overridden)
ENV POSTGRES_DB=${POSTGRES_DB:-cats_db}
ENV POSTGRES_USER=${POSTGRES_USER:-cats_user}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-changeme}
ENV POSTGRES_INITDB_ARGS=${POSTGRES_INITDB_ARGS:---encoding=UTF-8}
ENV POSTGRES_MAX_CONNECTIONS=${POSTGRES_MAX_CONNECTIONS:-100}
ENV POSTGRES_SHARED_BUFFERS=${POSTGRES_SHARED_BUFFERS:-256MB}

# Expose PostgreSQL port
EXPOSE 5432

# The postgres image automatically runs scripts in /docker-entrypoint-initdb.d/
# Scripts are executed in alphabetical order