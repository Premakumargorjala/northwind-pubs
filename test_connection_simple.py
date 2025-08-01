import pyodbc
import pandas as pd
from sqlalchemy import create_engine
import urllib.parse

def test_connection_methods():
    """Test different connection methods to SQL Server"""
    
    # Method 1: Direct pyodbc connection
    print("=== Testing Method 1: Direct pyodbc ===")
    try:
        conn_str = (
            r'DRIVER={SQL Server};'
            r'SERVER=localhost\SQLEXPRESS;'
            r'DATABASE=practicedatabase;'
            r'Trusted_Connection=yes;'
        )
        conn = pyodbc.connect(conn_str)
        print("✅ Direct pyodbc connection successful!")
        
        # Test query
        df = pd.read_sql("SELECT COUNT(*) as count FROM Customers", conn)
        print(f"Customers count: {df['count'].iloc[0]}")
        conn.close()
        
    except Exception as e:
        print(f"❌ Direct pyodbc failed: {e}")
    
    # Method 2: SQLAlchemy with pyodbc
    print("\n=== Testing Method 2: SQLAlchemy with pyodbc ===")
    try:
        conn_str = (
            r'mssql+pyodbc://localhost\SQLEXPRESS/practicedatabase?'
            r'driver=SQL+Server&'
            r'trusted_connection=yes'
        )
        engine = create_engine(conn_str)
        df = pd.read_sql("SELECT COUNT(*) as count FROM Customers", engine)
        print("✅ SQLAlchemy connection successful!")
        print(f"Customers count: {df['count'].iloc[0]}")
        engine.dispose()
        
    except Exception as e:
        print(f"❌ SQLAlchemy failed: {e}")
    
    # Method 3: Alternative server name format
    print("\n=== Testing Method 3: Alternative server format ===")
    try:
        conn_str = (
            r'DRIVER={SQL Server};'
            r'SERVER=(local)\SQLEXPRESS;'
            r'DATABASE=practicedatabase;'
            r'Trusted_Connection=yes;'
        )
        conn = pyodbc.connect(conn_str)
        print("✅ Alternative server format successful!")
        df = pd.read_sql("SELECT COUNT(*) as count FROM Customers", conn)
        print(f"Customers count: {df['count'].iloc[0]}")
        conn.close()
        
    except Exception as e:
        print(f"❌ Alternative server format failed: {e}")
    
    # Method 4: Check available drivers
    print("\n=== Available ODBC Drivers ===")
    drivers = pyodbc.drivers()
    for driver in drivers:
        print(f"  - {driver}")

if __name__ == "__main__":
    test_connection_methods() 