#!/usr/bin/env python3
"""
Check what data is being loaded by the multi-page dashboard
"""

import streamlit as st
import pandas as pd
import pyodbc
from sqlalchemy import create_engine
import warnings
warnings.filterwarnings('ignore')

def check_dashboard_data():
    """Check what data the dashboard can load"""
    print("🔍 Checking Dashboard Data Loading...")
    print("=" * 60)
    
    try:
        # SQL Server connection string (working format)
        CONN_STR = (
            r'DRIVER={SQL Server};'
            r'SERVER=localhost\SQLEXPRESS;'
            r'DATABASE=practicedatabase;'
            r'Trusted_Connection=yes;'
        )
        
        # Create SQLAlchemy engine
        engine = create_engine(f'mssql+pyodbc:///?odbc_connect={CONN_STR}')
        
        data = {}
        tables = ['Customers', 'Orders', 'Products', 'Categories', 'Employees', '[Order Details]']
        
        for table in tables:
            try:
                # Handle table names with spaces
                if table == '[Order Details]':
                    query = "SELECT * FROM [Order Details]"
                else:
                    query = f"SELECT * FROM {table}"
                df = pd.read_sql(query, engine)
                data[table.lower()] = df
                print(f"✅ {table:15} | Records: {len(df):4} | Columns: {len(df.columns):2}")
                
                if len(df) > 0:
                    print(f"   Columns: {list(df.columns[:5])}...")  # Show first 5 columns
                    
            except Exception as e:
                print(f"❌ {table:15} | Error: {str(e)}")
                data[table.lower()] = pd.DataFrame()
        
        print("\n" + "=" * 60)
        print("📊 Data Summary:")
        
        for table, df in data.items():
            if not df.empty:
                print(f"✅ {table}: {len(df)} records loaded successfully")
            else:
                print(f"❌ {table}: No data available")
        
        return data
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return None

if __name__ == "__main__":
    data = check_dashboard_data()
    
    if data:
        print("\n🎉 Dashboard data check completed!")
        print("The multi-page dashboard should be working with the available data.")
    else:
        print("\n⚠️  Dashboard data check failed!")
        print("Please check your database connection.") 