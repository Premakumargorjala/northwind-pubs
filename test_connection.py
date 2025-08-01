#!/usr/bin/env python3
"""
Test script to verify SQL Server connection and Customers table structure
"""

import pyodbc
from config import get_connection_string
import pandas as pd

def test_connection():
    """Test the database connection and verify table structure"""
    try:
        # Get connection string
        conn_str = get_connection_string()
        print("✅ Connection string generated successfully")
        print(f"Connection string: {conn_str}")
        
        # Test connection
        conn = pyodbc.connect(conn_str)
        print("✅ Successfully connected to SQL Server")
        
        # Test query to get table structure
        cursor = conn.cursor()
        
        # Check if Customers table exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'Customers'
        """)
        
        if cursor.fetchone()[0] > 0:
            print("✅ Customers table found")
            
            # Get table structure
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'Customers'
                ORDER BY ORDINAL_POSITION
            """)
            
            columns = cursor.fetchall()
            print("\n📋 Table Structure:")
            print("Column Name".ljust(20) + "Data Type".ljust(15) + "Nullable")
            print("-" * 50)
            for col in columns:
                print(f"{col[0].ljust(20)} {col[1].ljust(15)} {col[2]}")
            
            # Get row count
            cursor.execute("SELECT COUNT(*) FROM Customers")
            row_count = cursor.fetchone()[0]
            print(f"\n📊 Total rows in Customers table: {row_count}")
            
            # Get sample data
            if row_count > 0:
                cursor.execute("SELECT TOP 3 * FROM Customers")
                sample_data = cursor.fetchall()
                print("\n📄 Sample data (first 3 rows):")
                print("-" * 80)
                for row in sample_data:
                    print(row)
            
        else:
            print("❌ Customers table not found")
            print("Please ensure the table exists in your database")
        
        conn.close()
        print("\n✅ Connection test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Ensure SQL Server is running")
        print("2. Verify the server name and database name")
        print("3. Check Windows Authentication is enabled")
        print("4. Install SQL Server ODBC Driver if not already installed")
        return False

if __name__ == "__main__":
    print("🔍 Testing SQL Server Connection...")
    print("=" * 50)
    success = test_connection()
    
    if success:
        print("\n🎉 All tests passed! You can now run the Streamlit app.")
        print("Run: streamlit run app.py")
    else:
        print("\n⚠️  Please fix the connection issues before running the app.") 