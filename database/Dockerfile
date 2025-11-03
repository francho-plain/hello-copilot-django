FROM postgres:15

# Set environment variables
ENV POSTGRES_DB=cats_db
ENV POSTGRES_USER=cats_user
ENV POSTGRES_PASSWORD=cats_password

# Copy initialization script
COPY create-data.sql /docker-entrypoint-initdb.d/

# Expose PostgreSQL port
EXPOSE 5432

# The postgres image automatically runs scripts in /docker-entrypoint-initdb.d/
# when the container is first started