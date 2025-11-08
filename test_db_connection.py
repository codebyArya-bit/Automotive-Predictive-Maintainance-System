#!/usr/bin/env python3
"""
Test database connectivity
"""
import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager
from sqlalchemy import text


async def test_database_connection():
    """Test database connection and initialization"""
    try:
        print("Testing database connection...")
        dm = DatabaseManager()
        await dm.initialize()
        print("✓ Database initialized successfully")

        # Test basic query using the proper session method
        try:
            with dm.get_session() as session:
                result = session.execute(text("SELECT 1 as test"))
                row = result.fetchone()
                if row and row[0] == 1:
                    print("✓ Database query test successful")
                else:
                    print("✗ Database query test failed")
        except Exception as e:
            print(f"✗ Database query failed: {e}")

        # Test if we can query actual tables
        try:
            with dm.get_session() as session:
                result = session.execute(text("SELECT COUNT(*) FROM vehicles"))
                count = result.fetchone()[0]
                print(f"✓ Found {count} vehicles in database")
        except Exception as e:
            print(f"✗ Vehicle table query failed: {e}")

        await dm.shutdown()
        print("✓ Database connection test completed")
        return True

    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_database_connection())
    sys.exit(0 if success else 1)
