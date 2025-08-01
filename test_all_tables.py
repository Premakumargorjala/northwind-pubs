#!/usr/bin/env python3
"""
Test script to verify all tables in the SQL Server database
"""

import pyodbc
import pandas as pd

def test_all_tables():
    """Test all tables in the database"""
    try:
        # SQL Server connection string
        CONN_STR = (
            r'DRIVER={SQL Server};'
            r'SERVER=localhost\\SQLEXPRESS;'
            r'DATABASE=practicedatabase;'
            r'Trusted_Connection=yes;'
        )
        
        # Test connection
        conn = pyodbc.connect(CONN_STR)
        print("✅ Successfully connected to SQL Server")
        
        # List of tables to check
        tables_to_check = ['Customers', 'Orders', 'Products', 'Categories', 'Employees', 'OrderDetails']
        
        cursor = conn.cursor()
        
        print("\n📊 Database Table Summary:")
        print("=" * 60)
        
        for table_name in tables_to_check:
            try:
                # Check if table exists
                cursor.execute(f"""
                    SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME = '{table_name}'
                """)
                
                if cursor.fetchone()[0] > 0:
                    # Get row count
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cursor.fetchone()[0]
                    
                    # Get column count
                    cursor.execute(f"""
                        SELECT COUNT(*) 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = '{table_name}'
                    """)
                    col_count = cursor.fetchone()[0]
                    
                    print(f"✅ {table_name:15} | Records: {row_count:4} | Columns: {col_count:2}")
                    
                    # Show sample data for first 2 rows
                    if row_count > 0:
                        cursor.execute(f"SELECT TOP 2 * FROM {table_name}")
                        sample_data = cursor.fetchall()
                        print(f"   Sample: {sample_data[0][:3]}...")  # Show first 3 columns
                else:
                    print(f"❌ {table_name:15} | Table not found")
                    
            except Exception as e:
                print(f"❌ {table_name:15} | Error: {str(e)}")
        
        print("\n" + "=" * 60)
        
        # Test specific queries for each table
        print("\n🔍 Testing Data Access:")
        print("=" * 60)
        
        for table_name in tables_to_check:
            try:
                cursor.execute(f"SELECT TOP 1 * FROM {table_name}")
                sample = cursor.fetchone()
                if sample:
                    print(f"✅ {table_name}: Data accessible")
                else:
                    print(f"⚠️  {table_name}: Table exists but no data")
            except Exception as e:
                print(f"❌ {table_name}: {str(e)}")
        
        conn.close()
        print("\n✅ All table tests completed!")
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")

if __name__ == "__main__":
    print("🔍 Testing All Database Tables...")
    print("=" * 60)
    test_all_tables() 