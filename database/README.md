# PostgreSQL Cats Database

This directory contains the configuration for a PostgreSQL database with sample cat data.

## 🐱 Database Structure

### Cats Table
- **id**: Primary key (auto-increment)
- **name**: Cat's name (VARCHAR 100)
- **breed**: Cat breed (VARCHAR 100)
- **age**: Age in years (INTEGER)
- **color**: Cat's color (VARCHAR 50)
- **weight**: Weight in kg (DECIMAL 4,2)
- **is_neutered**: Neutered status (BOOLEAN)
- **owner_name**: Owner's name (VARCHAR 100)
- **adoption_date**: Date of adoption (DATE)
- **description**: Cat description (TEXT)
- **created_at**: Record creation timestamp

## 🚀 Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Navigate to database directory
cd database

# Start the PostgreSQL container
docker-compose up -d

# Check container status
docker-compose ps

# View logs
docker-compose logs cats_postgres
```

### Option 2: Using Docker directly

```bash
# Navigate to database directory
cd database

# Build the Docker image
docker build -t cats-postgres .

# Run the container
docker run -d \
  --name cats_database \
  -p 5432:5432 \
  -e POSTGRES_DB=cats_db \
  -e POSTGRES_USER=cats_user \
  -e POSTGRES_PASSWORD=cats_password \
  cats-postgres
```

## 🔗 Connection Details

- **Host**: localhost
- **Port**: 5432
- **Database**: cats_db
- **Username**: cats_user
- **Password**: cats_password

### Connection String
```
postgresql://cats_user:cats_password@localhost:5432/cats_db
```

## 📊 Sample Queries

### Connect to the database
```bash
# Using psql
docker exec -it cats_database psql -U cats_user -d cats_db

# Or using docker-compose
docker-compose exec cats_postgres psql -U cats_user -d cats_db
```

### Basic queries
```sql
-- View all cats
SELECT * FROM cats;

-- Count cats by breed
SELECT breed, COUNT(*) as count 
FROM cats 
GROUP BY breed 
ORDER BY count DESC;

-- Find cats older than 3 years
SELECT name, breed, age 
FROM cats 
WHERE age > 3 
ORDER BY age DESC;

-- Search cats by color
SELECT name, breed, color, weight 
FROM cats 
WHERE color ILIKE '%black%';

-- Get neutered cats with their owners
SELECT name, breed, owner_name, adoption_date 
FROM cats 
WHERE is_neutered = TRUE 
ORDER BY adoption_date;
```

## 🛠️ Management Commands

```bash
# Stop the database
docker-compose down

# Stop and remove volumes (WARNING: This deletes all data)
docker-compose down -v

# View container logs
docker-compose logs -f cats_postgres

# Backup database
docker exec cats_database pg_dump -U cats_user cats_db > backup.sql

# Restore database
cat backup.sql | docker exec -i cats_database psql -U cats_user -d cats_db
```

## 🐛 Troubleshooting

### Container won't start
```bash
# Check if port 5432 is already in use
sudo netstat -tlnp | grep 5432

# Stop any existing PostgreSQL service
sudo systemctl stop postgresql

# Check Docker logs
docker-compose logs cats_postgres
```

### Connection refused
```bash
# Wait for container to be ready
docker-compose exec cats_postgres pg_isready -U cats_user -d cats_db

# Check container health
docker-compose ps
```

### Reset database
```bash
# Stop and remove everything
docker-compose down -v

# Start fresh
docker-compose up -d
```

## 📁 Files

- `Dockerfile`: PostgreSQL container configuration
- `docker-compose.yml`: Service orchestration
- `create-data.sql`: Database schema and sample data
- `README.md`: This documentation

## 🔗 Integration with Django

To use this database with your Django backend:

```python
# In backend/.env
DATABASE_URL=postgresql://cats_user:cats_password@localhost:5432/cats_db

# In settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cats_db',
        'USER': 'cats_user',
        'PASSWORD': 'cats_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```