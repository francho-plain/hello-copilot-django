# PostgreSQL Database Scripts

This directory contains Python scripts for interacting with the local PostgreSQL database.

## Files

- `check_postgres.py` - Main script to connect and display data from PostgreSQL
- `setup.sh` - Setup script to install dependencies and prepare the environment
- `requirements.txt` - Python dependencies for the scripts

## Quick Start

### 1. Make sure PostgreSQL is running

```bash
cd ../database
docker compose up -d
```

### 2. Install dependencies

```bash
# Option 1: Use the setup script
./setup.sh

# Option 2: Manual installation
pip3 install -r requirements.txt
```

### 3. Run the PostgreSQL checker

```bash
python3 check_postgres.py
```

## What the Script Does

The `check_postgres.py` script provides comprehensive PostgreSQL database inspection:

### 🔍 **Database Information**
- Connection status and database details
- PostgreSQL version and database size
- Current user and database name

### 📋 **Table Structure Analysis**
- Verifies cats table exists
- Displays complete table schema
- Shows column types, constraints, and defaults
- Reports total record count

### 🐱 **Data Display**
- Lists all cats with detailed information
- Shows adoption status, breed, age, weight
- Displays neuter status and owner information
- Includes descriptions and creation dates

### 📊 **Statistical Analysis**
- **Adoption Statistics**: Total, adopted, and available cats
- **Age Distribution**: Youngest, oldest, and average age
- **Neuter Status**: Count of neutered vs intact cats
- **Breed Distribution**: Top breeds in the database

## Features

### ✅ **Robust Error Handling**
- Graceful connection failure handling
- Clear error messages with troubleshooting tips
- Transaction rollback on errors

### 🎨 **Rich Output Formatting**
- Emoji indicators for different statuses
- Formatted tables and statistics
- Color-coded information display

### 🔧 **Easy Configuration**
- Connection parameters can be easily modified
- Customizable output limits
- Extensible for additional queries

## Database Connection Details

The script connects to PostgreSQL with these default settings:
- **Host**: localhost
- **Port**: 5432
- **Database**: cats_db
- **User**: cats_user
- **Password**: cats_password

These match the configuration in `../database/docker-compose.yml`.

## Troubleshooting

### Connection Issues
```bash
# Check if PostgreSQL container is running
docker compose ps

# Check if port 5432 is accessible
telnet localhost 5432

# View PostgreSQL logs
docker compose logs cats_postgres
```

### Python Issues
```bash
# Verify Python version (should be 3.6+)
python3 --version

# Check if psycopg2 is installed
python3 -c "import psycopg2; print('psycopg2 installed successfully')"

# Reinstall dependencies if needed
pip3 install --force-reinstall -r requirements.txt
```

### Database Issues
```bash
# Reset the database
cd ../database
docker compose down
docker compose up -d

# Check database logs
docker compose logs -f cats_postgres
```

## Extending the Script

The script is designed to be easily extensible. You can add new functions by:

1. **Adding new query methods** to the `PostgreSQLChecker` class
2. **Extending the statistics section** with additional metrics
3. **Modifying the display format** to show different information
4. **Adding command-line arguments** for different operation modes

### Example: Adding a search function

```python
def search_cats_by_breed(self, breed: str) -> List[Dict[str, Any]]:
    """Search cats by breed."""
    with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("""
            SELECT * FROM cats 
            WHERE breed ILIKE %s 
            ORDER BY name;
        """, (f"%{breed}%",))
        return cursor.fetchall()
```

## Requirements

- **Python**: 3.6 or higher
- **psycopg2-binary**: 2.9.0 or higher
- **PostgreSQL**: Running container with cats database

## License

This script is part of the Django + React workshop project and follows the same license terms.