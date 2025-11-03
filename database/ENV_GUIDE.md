# Environment Variable Configuration Guide

This guide explains how to use environment variables for flexible database configuration in your PostgreSQL setup.

## 🔧 **Quick Start**

### Switch Between Environments
```bash
# Switch to development environment
./switch-env.sh development

# Switch to production environment  
./switch-env.sh production

# Switch to testing environment
./switch-env.sh testing
```

### Manual Environment Loading
```bash
# Load specific environment
cp .env.development .env
docker compose down && docker compose up -d

# Test connection
cd ../scripts && python3 check_postgres.py
```

## 📁 **Environment Files**

| File | Purpose | Use Case |
|------|---------|----------|
| `.env` | Active configuration | Current environment settings |
| `.env.development` | Development settings | Local development work |
| `.env.production` | Production settings | Production deployment |
| `.env.testing` | Testing settings | Automated testing |

## 🔑 **Environment Variables**

### Core Database Settings
```bash
POSTGRES_DB=cats_db                    # Database name
POSTGRES_USER=cats_user                # Database user
POSTGRES_PASSWORD=secure_password      # Database password
POSTGRES_HOST=localhost                # Database host
POSTGRES_PORT=5432                     # Database port
```

### Security Settings
```bash
POSTGRES_SSL_MODE=require              # SSL mode (disable/allow/prefer/require)
POSTGRES_SSL_CERT=/path/to/cert.pem    # SSL certificate path
POSTGRES_SSL_KEY=/path/to/key.pem      # SSL key path
POSTGRES_SSL_ROOT_CERT=/path/to/ca.pem # SSL root certificate
```

### Performance Settings
```bash
POSTGRES_MAX_CONNECTIONS=100           # Maximum connections
POSTGRES_SHARED_BUFFERS=256MB          # Shared buffers size
POSTGRES_CONNECT_TIMEOUT=10            # Connection timeout (seconds)
```

### Container Settings
```bash
POSTGRES_CONTAINER_NAME=cats_database  # Container name
POSTGRES_VOLUME_NAME=cats_data         # Volume name
POSTGRES_NETWORK_NAME=cats_network     # Network name
```

### Application Settings
```bash
ENVIRONMENT=development                # Environment type
POSTGRES_APPLICATION_NAME=cats_app     # Application identifier
```

### Health Check Settings
```bash
POSTGRES_HEALTH_CHECK_INTERVAL=30s     # Health check interval
POSTGRES_HEALTH_CHECK_TIMEOUT=10s      # Health check timeout
POSTGRES_HEALTH_CHECK_RETRIES=3        # Health check retries
```

## 🚀 **Usage Examples**

### 1. Development Setup
```bash
# Use development environment
./switch-env.sh development

# Or manually
cp .env.development .env
docker compose up -d
```

### 2. Production Deployment
```bash
# Use production environment
./switch-env.sh production

# Verify security settings
grep SSL .env
```

### 3. Testing Configuration
```bash
# Use testing environment for CI/CD
./switch-env.sh testing

# Run tests
cd ../scripts && python3 check_postgres.py
```

### 4. Custom Configuration
```bash
# Create custom environment file
cp .env.development .env.custom
# Edit .env.custom with your settings
vim .env.custom

# Use custom configuration
cp .env.custom .env
docker compose down && docker compose up -d
```

## 🐍 **Python Integration**

The Python scripts automatically read environment variables:

```python
from decouple import config

# Database connection using environment variables
db_config = {
    'host': config('POSTGRES_HOST', default='localhost'),
    'port': config('POSTGRES_PORT', default=5432, cast=int),
    'database': config('POSTGRES_DB', default='cats_db'),
    'user': config('POSTGRES_USER', default='cats_user'),
    'password': config('POSTGRES_PASSWORD')
}
```

### Environment Variable Priority
1. Command line arguments (highest priority)
2. Environment variables
3. `.env` file values
4. Default values (lowest priority)

## 🔐 **Security Best Practices**

### 1. Never Commit Sensitive Data
```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo ".env.production" >> .gitignore
echo ".env.backup.*" >> .gitignore
```

### 2. Use Strong Passwords
```bash
# Generate secure password
openssl rand -base64 32

# Or use pwgen
pwgen 32 1
```

### 3. Separate Environments
- Development: Relaxed security, detailed logging
- Testing: Fast operations, minimal logging
- Production: Strong security, optimized performance

### 4. SSL in Production
```bash
# Production SSL settings
POSTGRES_SSL_MODE=require
POSTGRES_SSL_CERT=/etc/ssl/certs/postgresql.crt
POSTGRES_SSL_KEY=/etc/ssl/private/postgresql.key
```

## 🧪 **Testing Configuration**

### Verify Environment Loading
```bash
# Check current configuration
grep -E "^POSTGRES_" .env

# Test database connection
cd ../scripts && python3 check_postgres.py

# Check container status
docker compose ps
```

### Validate Environment Files
```bash
# Check all environment files exist
ls -la .env.*

# Validate syntax
bash -n switch-env.sh
```

## 🔧 **Troubleshooting**

### Connection Issues
```bash
# Check environment variables
printenv | grep POSTGRES

# Test connection manually
psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB

# Check container logs
docker compose logs cats_postgres
```

### Environment Switching Issues
```bash
# Check current environment
cat .env | head -5

# List available environments
ls .env.*

# Restore from backup
cp .env.backup.* .env
```

### Permission Issues
```bash
# Fix script permissions
chmod +x switch-env.sh

# Fix file ownership
sudo chown $USER:$USER .env*
```

## 📚 **Integration Examples**

### Django Settings
```python
# settings.py
from decouple import config

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB'),
        'USER': config('POSTGRES_USER'),
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': config('POSTGRES_HOST'),
        'PORT': config('POSTGRES_PORT'),
        'OPTIONS': {
            'sslmode': config('POSTGRES_SSL_MODE', default='prefer'),
        }
    }
}
```

### Docker Compose Override
```yaml
# docker-compose.override.yml
version: '3.8'
services:
  cats_postgres:
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD_OVERRIDE}
    ports:
      - "${CUSTOM_PORT}:5432"
```

### CI/CD Pipeline
```yaml
# .github/workflows/test.yml
env:
  POSTGRES_DB: cats_test_db
  POSTGRES_USER: test_user
  POSTGRES_PASSWORD: test_password
  POSTGRES_HOST: localhost
  POSTGRES_PORT: 5432
```

## 🏗️ **Advanced Usage**

### External Configuration Management
```bash
# AWS Secrets Manager
export POSTGRES_PASSWORD=$(aws secretsmanager get-secret-value --secret-id prod/postgres/password --query SecretString --output text)

# HashiCorp Vault
export POSTGRES_PASSWORD=$(vault kv get -field=password secret/postgres)

# Kubernetes Secrets
kubectl get secret postgres-secret -o jsonpath="{.data.password}" | base64 --decode
```

### Multiple Database Support
```bash
# Primary database
POSTGRES_DB_PRIMARY=cats_main
POSTGRES_HOST_PRIMARY=db1.company.com

# Replica database
POSTGRES_DB_REPLICA=cats_replica
POSTGRES_HOST_REPLICA=db2.company.com
```

This comprehensive environment variable system provides flexibility, security, and maintainability for your PostgreSQL database configuration across different deployment scenarios.