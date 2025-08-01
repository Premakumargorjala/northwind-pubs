import streamlit as st
import pandas as pd
import pyodbc
from sqlalchemy import create_engine
import warnings
warnings.filterwarnings('ignore')

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_relationship_data():
    """Load data with proper table relationships for dropdowns"""
    try:
        # SQL Server connection string
        CONN_STR = (
            r'DRIVER={SQL Server};'
            r'SERVER=localhost\SQLEXPRESS;'
            r'DATABASE=practicedatabase;'
            r'Trusted_Connection=yes;'
        )
        
        # Create SQLAlchemy engine
        engine = create_engine(f'mssql+pyodbc:///?odbc_connect={CONN_STR}')
        
        relationship_data = {}
        
        # Query 1: Orders with Customer and Employee information
        try:
            orders_query = """
            SELECT 
                o.OrderID,
                o.OrderDate,
                o.ShipName,
                c.CompanyName AS CustomerName,
                c.CustomerID,
                e.FirstName + ' ' + e.LastName AS EmployeeName,
                e.EmployeeID
            FROM Orders o
            LEFT JOIN Customers c ON o.CustomerID = c.CustomerID
            LEFT JOIN Employees e ON o.EmployeeID = e.EmployeeID
            ORDER BY o.OrderDate DESC
            """
            relationship_data['orders_with_details'] = pd.read_sql(orders_query, engine)
            print(f"✅ Loaded {len(relationship_data['orders_with_details'])} orders with details")
        except Exception as e:
            print(f"❌ Could not load Orders with details: {str(e)}")
            relationship_data['orders_with_details'] = pd.DataFrame()
        
        # Query 2: Products with Category information
        try:
            products_query = """
            SELECT 
                p.ProductID,
                p.ProductName,
                p.UnitPrice,
                p.UnitsInStock,
                c.CategoryName,
                c.CategoryID
            FROM Products p
            LEFT JOIN Categories c ON p.CategoryID = c.CategoryID
            ORDER BY p.ProductName
            """
            relationship_data['products_with_categories'] = pd.read_sql(products_query, engine)
            print(f"✅ Loaded {len(relationship_data['products_with_categories'])} products with categories")
        except Exception as e:
            print(f"❌ Could not load Products with categories: {str(e)}")
            relationship_data['products_with_categories'] = pd.DataFrame()
        
        # Query 3: Order Details with Product and Order information
        try:
            orderdetails_query = """
            SELECT 
                od.OrderID,
                od.ProductID,
                od.UnitPrice,
                od.Quantity,
                od.Discount,
                p.ProductName,
                o.OrderDate,
                c.CompanyName AS CustomerName
            FROM [Order Details] od
            LEFT JOIN Products p ON od.ProductID = p.ProductID
            LEFT JOIN Orders o ON od.OrderID = o.OrderID
            LEFT JOIN Customers c ON o.CustomerID = c.CustomerID
            ORDER BY o.OrderDate DESC
            """
            relationship_data['orderdetails_with_details'] = pd.read_sql(orderdetails_query, engine)
            print(f"✅ Loaded {len(relationship_data['orderdetails_with_details'])} order details with details")
        except Exception as e:
            print(f"❌ Could not load Order Details with details: {str(e)}")
            relationship_data['orderdetails_with_details'] = pd.DataFrame()
        
        # Query 4: Employees with their order count
        try:
            employees_query = """
            SELECT 
                e.EmployeeID,
                e.FirstName,
                e.LastName,
                e.Title,
                e.City,
                COUNT(o.OrderID) AS OrderCount
            FROM Employees e
            LEFT JOIN Orders o ON e.EmployeeID = o.EmployeeID
            GROUP BY e.EmployeeID, e.FirstName, e.LastName, e.Title, e.City
            ORDER BY OrderCount DESC
            """
            relationship_data['employees_with_orders'] = pd.read_sql(employees_query, engine)
            print(f"✅ Loaded {len(relationship_data['employees_with_orders'])} employees with orders")
        except Exception as e:
            print(f"❌ Could not load Employees with orders: {str(e)}")
            relationship_data['employees_with_orders'] = pd.DataFrame()
        
        # Query 5: Categories with product count and revenue
        try:
            categories_query = """
            SELECT 
                c.CategoryID,
                c.CategoryName,
                COUNT(p.ProductID) AS ProductCount,
                SUM(od.UnitPrice * od.Quantity) AS TotalRevenue
            FROM Categories c
            LEFT JOIN Products p ON c.CategoryID = p.CategoryID
            LEFT JOIN [Order Details] od ON p.ProductID = od.ProductID
            GROUP BY c.CategoryID, c.CategoryName
            ORDER BY TotalRevenue DESC
            """
            relationship_data['categories_with_stats'] = pd.read_sql(categories_query, engine)
            print(f"✅ Loaded {len(relationship_data['categories_with_stats'])} categories with stats")
        except Exception as e:
            print(f"❌ Could not load Categories with stats: {str(e)}")
            relationship_data['categories_with_stats'] = pd.DataFrame()
        
        return relationship_data
        
    except Exception as e:
        print(f"❌ Error loading relationship data: {str(e)}")
        return None

if __name__ == "__main__":
    print("🔍 Testing Relationship Data Loading...")
    print("=" * 50)
    
    relationship_data = load_relationship_data()
    
    if relationship_data:
        print("\n📊 Relationship Data Summary:")
        print("=" * 30)
        
        for key, df in relationship_data.items():
            if not df.empty:
                print(f"✅ {key}: {len(df)} rows")
                print(f"   Columns: {list(df.columns)}")
                if len(df) > 0:
                    print(f"   Sample data:")
                    print(df.head(2).to_string())
                print()
            else:
                print(f"❌ {key}: No data")
                print()
    else:
        print("❌ Failed to load relationship data") 