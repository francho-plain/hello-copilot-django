#!/usr/bin/env python3
"""
PostgreSQL Database Checker Script

This script connects to the local PostgreSQL database and prints data from the cats table.
Requirements: psycopg2-binary

Usage:
    python check_postgres.py
"""

import sys
import traceback
import os
from typing import List, Dict, Any, Optional
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("❌ Error: psycopg2-binary not installed")
    print("Install with: pip install psycopg2-binary")
    sys.exit(1)

try:
    from decouple import config
    USE_DECOUPLE = True
except ImportError:
    USE_DECOUPLE = False
    print("⚠️  Warning: python-decouple not found, using os.environ fallback")
    
def get_env(key: str, default: Any = None, cast: type = str) -> Any:
    """Get environment variable with fallback support."""
    if USE_DECOUPLE:
        return config(key, default=default, cast=cast)
    else:
        value = os.environ.get(key, default)
        if cast and value is not None and cast != str:
            try:
                return cast(value)
            except (ValueError, TypeError):
                return default
        return value


class PostgreSQLChecker:
    """PostgreSQL database connection and query handler."""
    
    def __init__(self, 
                 host: Optional[str] = None,
                 port: Optional[int] = None,
                 database: Optional[str] = None,
                 user: Optional[str] = None,
                 password: Optional[str] = None):
        """Initialize database connection parameters from environment variables."""
        
        # Load from environment variables with fallbacks
        self.connection_params = {
            'host': host or get_env('POSTGRES_HOST', 'localhost'),
            'port': port or get_env('POSTGRES_PORT', 5432, int),
            'database': database or get_env('POSTGRES_DB', 'cats_db'),
            'user': user or get_env('POSTGRES_USER', 'cats_user'),
            'password': password or get_env('POSTGRES_PASSWORD', 'cats_password')
        }
        
        # Additional connection parameters from environment
        self.ssl_mode = get_env('POSTGRES_SSL_MODE', 'prefer')
        self.connect_timeout = get_env('POSTGRES_CONNECT_TIMEOUT', 10, int)
        self.application_name = get_env('POSTGRES_APPLICATION_NAME', 'cats_checker')
        
        self.connection: Optional[psycopg2.extensions.connection] = None
        
        # Display configuration (without password)
        print(f"🔧 Database Configuration:")
        print(f"  Host: {self.connection_params['host']}")
        print(f"  Port: {self.connection_params['port']}")
        print(f"  Database: {self.connection_params['database']}")
        print(f"  User: {self.connection_params['user']}")
        print(f"  SSL Mode: {self.ssl_mode}")
        print(f"  Application: {self.application_name}")
        print()
    
    def connect(self) -> bool:
        """Establish connection to PostgreSQL database."""
        try:
            print(f"🔌 Connecting to PostgreSQL at {self.connection_params['host']}:{self.connection_params['port']}")
            
            # Build connection parameters with additional settings
            conn_params = self.connection_params.copy()
            conn_params.update({
                'sslmode': self.ssl_mode,
                'connect_timeout': self.connect_timeout,
                'application_name': self.application_name
            })
            
            self.connection = psycopg2.connect(**conn_params)
            print("✅ Successfully connected to PostgreSQL!")
            
            # Show additional connection info
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT inet_server_addr(), inet_server_port();")
                server_info = cursor.fetchone()
                if server_info[0]:  # If we have server address info
                    print(f"📡 Connected to server: {server_info[0]}:{server_info[1]}")
                    
            return True
        except psycopg2.OperationalError as e:
            print(f"❌ Connection failed: {e}")
            print("\n🔧 Troubleshooting tips:")
            print("1. Make sure PostgreSQL container is running: docker compose ps")
            print("2. Check if port is accessible: telnet {host} {port}".format(**self.connection_params))
            print("3. Verify database credentials in .env file")
            print("4. Check environment variables:")
            print(f"   POSTGRES_HOST={get_env('POSTGRES_HOST', 'not set')}")
            print(f"   POSTGRES_PORT={get_env('POSTGRES_PORT', 'not set')}")
            print(f"   POSTGRES_DB={get_env('POSTGRES_DB', 'not set')}")
            print(f"   POSTGRES_USER={get_env('POSTGRES_USER', 'not set')}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get basic database information."""
        if not self.connection:
            return {}
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get PostgreSQL version
                cursor.execute("SELECT version();")
                version = cursor.fetchone()['version']
                
                # Get current database name
                cursor.execute("SELECT current_database();")
                current_db = cursor.fetchone()['current_database']
                
                # Get current user
                cursor.execute("SELECT current_user;")
                current_user = cursor.fetchone()['current_user']
                
                # Get database size
                cursor.execute("""
                    SELECT pg_size_pretty(pg_database_size(current_database())) as size;
                """)
                db_size = cursor.fetchone()['size']
                
                return {
                    'version': version,
                    'database': current_db,
                    'user': current_user,
                    'size': db_size
                }
        except Exception as e:
            print(f"❌ Error getting database info: {e}")
            return {}
    
    def check_cats_table(self) -> bool:
        """Check if the cats table exists and get its structure."""
        if not self.connection:
            return False
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Check if table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'cats'
                    );
                """)
                table_exists = cursor.fetchone()['exists']
                
                if not table_exists:
                    print("❌ Cats table does not exist!")
                    return False
                
                print("✅ Cats table exists!")
                
                # Get table structure
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'cats' 
                    ORDER BY ordinal_position;
                """)
                columns = cursor.fetchall()
                
                print("\n📋 Table Structure:")
                print("=" * 60)
                for col in columns:
                    nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                    default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                    print(f"  {col['column_name']:<15} | {col['data_type']:<20} | {nullable}{default}")
                
                # Get row count
                cursor.execute("SELECT COUNT(*) as count FROM cats;")
                row_count = cursor.fetchone()['count']
                print(f"\n📊 Total records: {row_count}")
                
                return True
                
        except Exception as e:
            print(f"❌ Error checking cats table: {e}")
            return False
    
    def get_cats_data(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve and display cats data."""
        if not self.connection:
            return []
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(f"""
                    SELECT 
                        id, name, breed, color, age, weight, 
                        is_neutered, owner_name, adoption_date, description, created_at
                    FROM cats 
                    ORDER BY id 
                    LIMIT {limit};
                """)
                cats = cursor.fetchall()
                
                if not cats:
                    print("🐱 No cats found in the database!")
                    return []
                
                print(f"\n🐱 Displaying {len(cats)} cats:")
                print("=" * 80)
                
                for cat in cats:
                    adopted = "🏠 Adopted" if cat['adoption_date'] else "🔍 Available"
                    neutered = "✂️ Neutered" if cat['is_neutered'] else "🐾 Intact"
                    
                    print(f"""
ID: {cat['id']} | Name: {cat['name']} | {adopted}
Breed: {cat['breed']} | Color: {cat['color']}
Age: {cat['age']} years | Weight: {cat['weight']} kg
Status: {neutered} | Owner: {cat['owner_name'] or 'No owner'}
Adoption Date: {cat['adoption_date'] or 'Not adopted'}
Description: {cat['description']}
Created: {cat['created_at']}
{'-' * 40}""")
                
                return cats
                
        except Exception as e:
            print(f"❌ Error retrieving cats data: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get interesting statistics about the cats."""
        if not self.connection:
            return {}
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                stats = {}
                
                # Adoption statistics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(*) FILTER (WHERE adoption_date IS NOT NULL) as adopted,
                        COUNT(*) FILTER (WHERE adoption_date IS NULL) as available
                    FROM cats;
                """)
                adoption_stats = cursor.fetchone()
                stats['adoption'] = adoption_stats
                
                # Breed distribution
                cursor.execute("""
                    SELECT breed, COUNT(*) as count 
                    FROM cats 
                    GROUP BY breed 
                    ORDER BY count DESC;
                """)
                breed_stats = cursor.fetchall()
                stats['breeds'] = breed_stats
                
                # Age statistics
                cursor.execute("""
                    SELECT 
                        MIN(age) as youngest,
                        MAX(age) as oldest,
                        ROUND(AVG(age), 1) as average_age
                    FROM cats;
                """)
                age_stats = cursor.fetchone()
                stats['age'] = age_stats
                
                # Neutered vs Intact
                cursor.execute("""
                    SELECT 
                        COUNT(*) FILTER (WHERE is_neutered = true) as neutered,
                        COUNT(*) FILTER (WHERE is_neutered = false) as intact
                    FROM cats;
                """)
                neuter_stats = cursor.fetchone()
                stats['neuter'] = neuter_stats
                
                return stats
                
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {}
    
    def display_statistics(self, stats: Dict[str, Any]) -> None:
        """Display formatted statistics."""
        if not stats:
            return
        
        print("\n📊 Database Statistics:")
        print("=" * 50)
        
        # Adoption stats
        if 'adoption' in stats:
            adoption = stats['adoption']
            total = adoption['total']
            adopted = adoption['adopted']
            available = adoption['available']
            adoption_rate = (adopted / total * 100) if total > 0 else 0
            
            print(f"\n🏠 Adoption Status:")
            print(f"  Total cats: {total}")
            print(f"  Adopted: {adopted} ({adoption_rate:.1f}%)")
            print(f"  Available: {available}")
        
        # Age statistics
        if 'age' in stats:
            age = stats['age']
            print(f"\n🎂 Age Distribution:")
            print(f"  Youngest: {age['youngest']} years")
            print(f"  Oldest: {age['oldest']} years")
            print(f"  Average: {age['average_age']} years")
        
        # Lifestyle stats
        if 'neuter' in stats:
            neuter = stats['neuter']
            print(f"\n✂️ Neuter Status:")
            print(f"  Neutered cats: {neuter['neutered']}")
            print(f"  Intact cats: {neuter['intact']}")
        
        # Breed distribution
        if 'breeds' in stats:
            print(f"\n🐱 Breed Distribution:")
            for breed in stats['breeds'][:5]:  # Top 5 breeds
                print(f"  {breed['breed']}: {breed['count']} cats")
    
    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print("\n🔌 Database connection closed.")


def main():
    """Main execution function."""
    print("🐱 PostgreSQL Cats Database Checker")
    print("=" * 40)
    
    # Initialize checker
    db_checker = PostgreSQLChecker()
    
    try:
        # Connect to database
        if not db_checker.connect():
            return
        
        # Get database info
        print("\n🔍 Database Information:")
        print("-" * 30)
        db_info = db_checker.get_database_info()
        if db_info:
            print(f"Database: {db_info.get('database', 'Unknown')}")
            print(f"User: {db_info.get('user', 'Unknown')}")
            print(f"Size: {db_info.get('size', 'Unknown')}")
            print(f"Version: {db_info.get('version', 'Unknown')[:50]}...")
        
        # Check cats table
        if not db_checker.check_cats_table():
            print("\n💡 Tip: Run the database setup first:")
            print("cd database && docker compose up -d")
            return
        
        # Get cats data
        cats_data = db_checker.get_cats_data(limit=15)
        
        # Get and display statistics
        stats = db_checker.get_statistics()
        db_checker.display_statistics(stats)
        
        print(f"\n✅ Successfully checked PostgreSQL database!")
        print(f"Found {len(cats_data)} cats in the database.")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Script interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Full traceback:")
        traceback.print_exc()
    finally:
        db_checker.close()


if __name__ == "__main__":
    main()