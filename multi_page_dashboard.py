import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pyodbc
from sqlalchemy import create_engine, text
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Business Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_all_data():
    """Load all data from SQL Server database"""
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
        
        # Load Customers
        try:
            customers_query = "SELECT * FROM Customers"
            data['customers'] = pd.read_sql(customers_query, engine)
            # Handle NaN values properly for string columns
            string_columns = data['customers'].select_dtypes(include=['object']).columns
            data['customers'][string_columns] = data['customers'][string_columns].fillna('N/A')
        except Exception as e:
            st.warning(f"Could not load Customers table: {str(e)}")
            data['customers'] = pd.DataFrame()
        
        # Load Orders
        try:
            orders_query = "SELECT * FROM Orders"
            data['orders'] = pd.read_sql(orders_query, engine)
            # Handle date columns properly
            date_columns = ['OrderDate', 'RequiredDate', 'ShippedDate']
            for col in date_columns:
                if col in data['orders'].columns:
                    data['orders'][col] = pd.to_datetime(data['orders'][col], errors='coerce')
            
            # Handle string columns
            string_columns = data['orders'].select_dtypes(include=['object']).columns
            data['orders'][string_columns] = data['orders'][string_columns].fillna('N/A')
        except Exception as e:
            st.warning(f"Could not load Orders table: {str(e)}")
            data['orders'] = pd.DataFrame()
        
        # Load Products
        try:
            products_query = "SELECT * FROM Products"
            data['products'] = pd.read_sql(products_query, engine)
            # Handle numeric columns properly
            numeric_columns = data['products'].select_dtypes(include=[np.number]).columns
            data['products'][numeric_columns] = data['products'][numeric_columns].fillna(0)
            
            # Handle string columns
            string_columns = data['products'].select_dtypes(include=['object']).columns
            data['products'][string_columns] = data['products'][string_columns].fillna('N/A')
        except Exception as e:
            st.warning(f"Could not load Products table: {str(e)}")
            data['products'] = pd.DataFrame()
        
        # Load Categories
        try:
            categories_query = "SELECT * FROM Categories"
            data['categories'] = pd.read_sql(categories_query, engine)
            # Handle string columns
            string_columns = data['categories'].select_dtypes(include=['object']).columns
            data['categories'][string_columns] = data['categories'][string_columns].fillna('N/A')
        except Exception as e:
            st.warning(f"Could not load Categories table: {str(e)}")
            data['categories'] = pd.DataFrame()
        
        # Load Employees
        try:
            employees_query = "SELECT * FROM Employees"
            data['employees'] = pd.read_sql(employees_query, engine)
            # Handle ReportsTo column properly (it's numeric but can be null)
            if 'ReportsTo' in data['employees'].columns:
                data['employees']['ReportsTo'] = pd.to_numeric(data['employees']['ReportsTo'], errors='coerce')
                data['employees']['ReportsTo'] = data['employees']['ReportsTo'].fillna(0).astype(int)
            
            # Handle date columns
            date_columns = ['BirthDate', 'HireDate']
            for col in date_columns:
                if col in data['employees'].columns:
                    data['employees'][col] = pd.to_datetime(data['employees'][col], errors='coerce')
            
            # Handle string columns
            string_columns = data['employees'].select_dtypes(include=['object']).columns
            data['employees'][string_columns] = data['employees'][string_columns].fillna('N/A')
        except Exception as e:
            st.warning(f"Could not load Employees table: {str(e)}")
            data['employees'] = pd.DataFrame()
        
        # Load Order Details (table name has a space)
        try:
            orderdetails_query = "SELECT * FROM [Order Details]"
            data['orderdetails'] = pd.read_sql(orderdetails_query, engine)
            # Handle numeric columns properly
            numeric_columns = data['orderdetails'].select_dtypes(include=[np.number]).columns
            data['orderdetails'][numeric_columns] = data['orderdetails'][numeric_columns].fillna(0)
        except Exception as e:
            st.warning(f"Could not load Order Details table: {str(e)}")
            data['orderdetails'] = pd.DataFrame()
        
        return data
    
    except Exception as e:
        st.error(f"Error connecting to database: {str(e)}")
        return None

def customer_insights_page(data):
    """Customer Insights Dashboard"""
    st.markdown('<h1 class="main-header">👥 Customer Insights</h1>', unsafe_allow_html=True)
    
    if data['customers'].empty:
        st.error("No customer data available")
        return
    
    customers_df = data['customers']
    
    # Sidebar filters
    st.sidebar.header("🔍 Customer Filters")
    
    # Country filter
    countries = ['All'] + sorted(customers_df['Country'].unique().tolist())
    selected_country = st.sidebar.selectbox("Select Country:", countries)
    
    # City filter (filtered based on selected country)
    if selected_country != 'All':
        cities = ['All'] + sorted(customers_df[customers_df['Country'] == selected_country]['City'].unique().tolist())
    else:
        cities = ['All'] + sorted(customers_df['City'].unique().tolist())
    
    selected_city = st.sidebar.selectbox("Select City:", cities)
    
    # Apply filters
    filtered_customers = customers_df.copy()
    if selected_country != 'All':
        filtered_customers = filtered_customers[filtered_customers['Country'] == selected_country]
    if selected_city != 'All':
        filtered_customers = filtered_customers[filtered_customers['City'] == selected_city]
    
    # Key Metrics
    st.header("📈 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Customers</h3>
            <h2>{len(filtered_customers):,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Unique Cities</h3>
            <h2>{filtered_customers['City'].nunique():,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Unique Countries</h3>
            <h2>{filtered_customers['Country'].nunique():,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>With Phone</h3>
            <h2>{len(filtered_customers[filtered_customers['Phone'] != 'N/A']):,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts
    st.header("📊 Customer Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Customers by Country")
        country_counts = filtered_customers['Country'].value_counts()
        fig_country = px.pie(
            values=country_counts.values,
            names=country_counts.index,
            title="Customer Distribution by Country",
            hole=0.3
        )
        fig_country.update_layout(height=400)
        st.plotly_chart(fig_country, use_container_width=True)
    
    with col2:
        st.subheader("Top Cities by Customer Count")
        city_counts = filtered_customers['City'].value_counts().head(10)
        # Create DataFrame for plotting
        city_df = pd.DataFrame({
            'City': city_counts.index,
            'Count': city_counts.values
        })
        fig_city = px.bar(
            city_df,
            x='Count',
            y='City',
            orientation='h',
            title="Top 10 Cities by Customer Count",
            labels={'Count': 'Number of Customers', 'City': 'City'},
            color='Count',
            color_continuous_scale='Blues'
        )
        fig_city.update_layout(height=400)
        st.plotly_chart(fig_city, use_container_width=True)
    
    # Contact Titles Distribution
    st.subheader("Contact Titles Distribution")
    title_counts = filtered_customers['ContactTitle'].value_counts().head(8)
    # Create DataFrame for plotting
    title_df = pd.DataFrame({
        'Title': title_counts.index,
        'Count': title_counts.values
    })
    fig_title = px.bar(
        title_df,
        x='Title',
        y='Count',
        title="Top Contact Titles",
        labels={'Title': 'Contact Title', 'Count': 'Count'},
        color='Count',
        color_continuous_scale='Greens'
    )
    fig_title.update_xaxes(tickangle=45)
    st.plotly_chart(fig_title, use_container_width=True)
    
    # Download section
    st.markdown("---")
    st.header("💾 Export Customer Data")
    
    csv_data = filtered_customers.to_csv(index=False)
    st.download_button(
        label="📥 Download Customer Data (CSV)",
        data=csv_data,
        file_name=f"customer_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def orders_overview_page(data):
    """Orders Overview Dashboard"""
    st.markdown('<h1 class="main-header">📦 Orders Overview</h1>', unsafe_allow_html=True)
    
    if data['orders'].empty:
        st.error("No orders data available")
        return
    
    orders_df = data['orders']
    
    # Convert date columns if they exist
    date_columns = ['OrderDate', 'RequiredDate', 'ShippedDate']
    for col in date_columns:
        if col in orders_df.columns:
            orders_df[col] = pd.to_datetime(orders_df[col], errors='coerce')
    
    # Sidebar filters
    st.sidebar.header("🔍 Order Filters")
    
    # Date filter
    if 'OrderDate' in orders_df.columns:
        min_date = orders_df['OrderDate'].min()
        max_date = orders_df['OrderDate'].max()
        
        if pd.notna(min_date) and pd.notna(max_date):
            date_range = st.sidebar.date_input(
                "Select Date Range:",
                value=(min_date.date(), max_date.date()),
                min_value=min_date.date(),
                max_value=max_date.date()
            )
            
            if len(date_range) == 2:
                start_date, end_date = date_range
                filtered_orders = orders_df[
                    (orders_df['OrderDate'].dt.date >= start_date) &
                    (orders_df['OrderDate'].dt.date <= end_date)
                ]
            else:
                filtered_orders = orders_df
        else:
            filtered_orders = orders_df
    else:
        filtered_orders = orders_df
    
    # Status filter (if available)
    if 'ShipCountry' in filtered_orders.columns:
        countries = ['All'] + sorted(filtered_orders['ShipCountry'].unique().tolist())
        selected_country = st.sidebar.selectbox("Ship Country:", countries)
        
        if selected_country != 'All':
            filtered_orders = filtered_orders[filtered_orders['ShipCountry'] == selected_country]
    
    # Key Metrics
    st.header("📈 Order Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Orders</h3>
            <h2>{len(filtered_orders):,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        recent_orders = len(filtered_orders) if 'OrderDate' not in filtered_orders.columns else len(
            filtered_orders[filtered_orders['OrderDate'] >= (datetime.now() - timedelta(days=30))]
        )
        st.markdown(f"""
        <div class="metric-card">
            <h3>Recent Orders (30d)</h3>
            <h2>{recent_orders:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        unique_customers = filtered_orders['CustomerID'].nunique() if 'CustomerID' in filtered_orders.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>Unique Customers</h3>
            <h2>{unique_customers:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        unique_countries = filtered_orders['ShipCountry'].nunique() if 'ShipCountry' in filtered_orders.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>Ship Countries</h3>
            <h2>{unique_countries:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts
    st.header("📊 Order Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'OrderDate' in filtered_orders.columns:
            st.subheader("Orders Over Time")
            orders_by_date = filtered_orders.groupby(filtered_orders['OrderDate'].dt.date).size().reset_index(name='count')
            fig_time = px.line(
                x=orders_by_date['OrderDate'],
                y=orders_by_date['count'],
                title="Orders Over Time",
                labels={'x': 'Date', 'y': 'Number of Orders'}
            )
            fig_time.update_layout(height=400)
            st.plotly_chart(fig_time, use_container_width=True)
    
    with col2:
        if 'ShipCountry' in filtered_orders.columns:
            st.subheader("Orders by Country")
            country_counts = filtered_orders['ShipCountry'].value_counts().head(10)
            fig_country = px.bar(
                x=country_counts.index,
                y=country_counts.values,
                title="Top 10 Countries by Orders",
                labels={'x': 'Country', 'y': 'Number of Orders'},
                color=country_counts.values,
                color_continuous_scale='Reds'
            )
            fig_country.update_xaxes(tickangle=45)
            fig_country.update_layout(height=400)
            st.plotly_chart(fig_country, use_container_width=True)
    
    # Top Customers
    if 'CustomerID' in filtered_orders.columns:
        st.subheader("Top Customers by Orders")
        customer_counts = filtered_orders['CustomerID'].value_counts().head(10)
        fig_customers = px.bar(
            x=customer_counts.index,
            y=customer_counts.values,
            title="Top 10 Customers by Order Count",
            labels={'x': 'Customer ID', 'y': 'Number of Orders'},
            color=customer_counts.values,
            color_continuous_scale='Purples'
        )
        fig_customers.update_xaxes(tickangle=45)
        st.plotly_chart(fig_customers, use_container_width=True)
    
    # Download section
    st.markdown("---")
    st.header("💾 Export Order Data")
    
    csv_data = filtered_orders.to_csv(index=False)
    st.download_button(
        label="📥 Download Order Data (CSV)",
        data=csv_data,
        file_name=f"order_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def sales_products_page(data):
    """Sales & Products Dashboard"""
    st.markdown('<h1 class="main-header">💰 Sales & Products</h1>', unsafe_allow_html=True)
    
    # Check if we have the necessary tables
    if data['orderdetails'].empty or data['products'].empty:
        st.error("OrderDetails or Products data not available")
        return
    
    # Create sales data by joining tables
    try:
        # Join OrderDetails with Products
        sales_df = data['orderdetails'].merge(
            data['products'], 
            left_on='ProductID', 
            right_on='ProductID', 
            how='left',
            suffixes=('_order', '_product')
        )
        
        # Join with Categories if available
        if not data['categories'].empty:
            sales_df = sales_df.merge(
                data['categories'],
                left_on='CategoryID',
                right_on='CategoryID',
                how='left'
            )
        
        # Calculate revenue - use the UnitPrice from OrderDetails (UnitPrice_order)
        if 'UnitPrice_order' in sales_df.columns and 'Quantity' in sales_df.columns:
            sales_df['Revenue'] = sales_df['UnitPrice_order'] * sales_df['Quantity']
        elif 'UnitPrice' in sales_df.columns and 'Quantity' in sales_df.columns:
            sales_df['Revenue'] = sales_df['UnitPrice'] * sales_df['Quantity']
        else:
            st.error("Required columns for revenue calculation not found")
            return
        
        # Join with Orders for date information
        if not data['orders'].empty:
            sales_df = sales_df.merge(
                data['orders'][['OrderID', 'OrderDate', 'ShipCountry']],
                left_on='OrderID',
                right_on='OrderID',
                how='left'
            )
            
            if 'OrderDate' in sales_df.columns:
                sales_df['OrderDate'] = pd.to_datetime(sales_df['OrderDate'], errors='coerce')
        
    except Exception as e:
        st.error(f"Error creating sales data: {str(e)}")
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Sales Filters")
    
    # Category filter
    if 'CategoryName' in sales_df.columns:
        categories = ['All'] + sorted(sales_df['CategoryName'].unique().tolist())
        selected_category = st.sidebar.selectbox("Select Category:", categories)
        
        if selected_category != 'All':
            sales_df = sales_df[sales_df['CategoryName'] == selected_category]
    
    # Date filter
    if 'OrderDate' in sales_df.columns:
        min_date = sales_df['OrderDate'].min()
        max_date = sales_df['OrderDate'].max()
        
        if pd.notna(min_date) and pd.notna(max_date):
            date_range = st.sidebar.date_input(
                "Select Date Range:",
                value=(min_date.date(), max_date.date()),
                min_value=min_date.date(),
                max_value=max_date.date()
            )
            
            if len(date_range) == 2:
                start_date, end_date = date_range
                sales_df = sales_df[
                    (sales_df['OrderDate'].dt.date >= start_date) &
                    (sales_df['OrderDate'].dt.date <= end_date)
                ]
    
    # Key Metrics
    st.header("📈 Sales Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = sales_df['Revenue'].sum() if 'Revenue' in sales_df.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Revenue</h3>
            <h2>${total_revenue:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_orders = sales_df['OrderID'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Orders</h3>
            <h2>{total_orders:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_products = sales_df['ProductID'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <h3>Products Sold</h3>
            <h2>{total_products:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>Avg Order Value</h3>
            <h2>${avg_order_value:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts
    st.header("📊 Sales Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'CategoryName' in sales_df.columns:
            st.subheader("Revenue by Category")
            category_revenue = sales_df.groupby('CategoryName')['Revenue'].sum().sort_values(ascending=False)
            fig_category = px.pie(
                values=category_revenue.values,
                names=category_revenue.index,
                title="Revenue Distribution by Category",
                hole=0.3
            )
            fig_category.update_layout(height=400)
            st.plotly_chart(fig_category, use_container_width=True)
    
    with col2:
        if 'ProductName' in sales_df.columns:
            st.subheader("Best Selling Products")
            product_sales = sales_df.groupby('ProductName')['Quantity'].sum().sort_values(ascending=False).head(10)
            # Create DataFrame for plotting
            product_df = pd.DataFrame({
                'Product': product_sales.index,
                'Quantity': product_sales.values
            })
            fig_products = px.bar(
                product_df,
                x='Quantity',
                y='Product',
                orientation='h',
                title="Top 10 Products by Quantity Sold",
                labels={'Quantity': 'Quantity Sold', 'Product': 'Product'},
                color='Quantity',
                color_continuous_scale='Greens'
            )
            fig_products.update_layout(height=400)
            st.plotly_chart(fig_products, use_container_width=True)
    
    # Revenue over time
    if 'OrderDate' in sales_df.columns:
        st.subheader("Revenue Over Time")
        daily_revenue = sales_df.groupby(sales_df['OrderDate'].dt.date)['Revenue'].sum().reset_index()
        fig_revenue = px.line(
            x=daily_revenue['OrderDate'],
            y=daily_revenue['Revenue'],
            title="Daily Revenue",
            labels={'x': 'Date', 'y': 'Revenue ($)'}
        )
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    # Download section
    st.markdown("---")
    st.header("💾 Export Sales Data")
    
    csv_data = sales_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Sales Data (CSV)",
        data=csv_data,
        file_name=f"sales_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def employees_page(data):
    """Employees Dashboard"""
    st.markdown('<h1 class="main-header">👨‍💼 Employee Analytics</h1>', unsafe_allow_html=True)
    
    if data['employees'].empty:
        st.error("No employee data available")
        return
    
    employees_df = data['employees']
    
    # Sidebar filters
    st.sidebar.header("🔍 Employee Filters")
    
    # Title filter
    if 'Title' in employees_df.columns:
        titles = ['All'] + sorted(employees_df['Title'].unique().tolist())
        selected_title = st.sidebar.selectbox("Select Title:", titles)
        
        if selected_title != 'All':
            employees_df = employees_df[employees_df['Title'] == selected_title]
    
    # Country filter
    if 'Country' in employees_df.columns:
        countries = ['All'] + sorted(employees_df['Country'].unique().tolist())
        selected_country = st.sidebar.selectbox("Select Country:", countries)
        
        if selected_country != 'All':
            employees_df = employees_df[employees_df['Country'] == selected_country]
    
    # Key Metrics
    st.header("📈 Employee Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Employees</h3>
            <h2>{len(employees_df):,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        unique_titles = employees_df['Title'].nunique() if 'Title' in employees_df.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>Job Titles</h3>
            <h2>{unique_titles:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        unique_countries = employees_df['Country'].nunique() if 'Country' in employees_df.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>Countries</h3>
            <h2>{unique_countries:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        unique_cities = employees_df['City'].nunique() if 'City' in employees_df.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>Cities</h3>
            <h2>{unique_cities:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts
    st.header("📊 Employee Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Title' in employees_df.columns:
            st.subheader("Employees by Title")
            title_counts = employees_df['Title'].value_counts()
            fig_title = px.pie(
                values=title_counts.values,
                names=title_counts.index,
                title="Employee Distribution by Title",
                hole=0.3
            )
            fig_title.update_layout(height=400)
            st.plotly_chart(fig_title, use_container_width=True)
    
    with col2:
        if 'Country' in employees_df.columns:
            st.subheader("Employees by Country")
            country_counts = employees_df['Country'].value_counts()
            # Create DataFrame for plotting
            country_df = pd.DataFrame({
                'Country': country_counts.index,
                'Count': country_counts.values
            })
            fig_country = px.bar(
                country_df,
                x='Country',
                y='Count',
                title="Employees by Country",
                labels={'Country': 'Country', 'Count': 'Number of Employees'},
                color='Count',
                color_continuous_scale='Blues'
            )
            fig_country.update_xaxes(tickangle=45)
            fig_country.update_layout(height=400)
            st.plotly_chart(fig_country, use_container_width=True)
    
    # Employee performance (if orders data available)
    if not data['orders'].empty and 'EmployeeID' in data['orders'].columns:
        st.subheader("Employee Performance")
        
        # Count orders per employee
        employee_orders = data['orders']['EmployeeID'].value_counts()
        
        # Merge with employee names if available
        if 'EmployeeID' in employees_df.columns and 'FirstName' in employees_df.columns and 'LastName' in employees_df.columns:
            employees_df['FullName'] = employees_df['FirstName'] + ' ' + employees_df['LastName']
            employee_performance = employee_orders.reset_index()
            employee_performance.columns = ['EmployeeID', 'OrderCount']
            employee_performance = employee_performance.merge(
                employees_df[['EmployeeID', 'FullName']], 
                on='EmployeeID', 
                how='left'
            )
            
            fig_performance = px.bar(
                employee_performance,
                x='FullName',
                y='OrderCount',
                title="Orders Handled by Employee",
                labels={'FullName': 'Employee', 'OrderCount': 'Number of Orders'},
                color='OrderCount',
                color_continuous_scale='Purples'
            )
            fig_performance.update_xaxes(tickangle=45)
            st.plotly_chart(fig_performance, use_container_width=True)
    
    # Download section
    st.markdown("---")
    st.header("💾 Export Employee Data")
    
    csv_data = employees_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Employee Data (CSV)",
        data=csv_data,
        file_name=f"employee_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def all_data_tables_page(data):
    """All Data Tables Page"""
    st.markdown('<h1 class="main-header">📋 All Data Tables</h1>', unsafe_allow_html=True)
    
    # Create tabs for each table
    table_names = ['Customers', 'Orders', 'Products', 'Categories', 'Employees', 'OrderDetails']
    table_data = {
        'Customers': data['customers'],
        'Orders': data['orders'],
        'Products': data['products'],
        'Categories': data['categories'],
        'Employees': data['employees'],
        'OrderDetails': data['orderdetails']
    }
    
    tabs = st.tabs(table_names)
    
    for i, (tab, table_name) in enumerate(zip(tabs, table_names)):
        with tab:
            df = table_data[table_name]
            
            if df.empty:
                st.warning(f"No data available for {table_name} table")
                continue
            
            st.subheader(f"{table_name} Table")
            st.write(f"**Total Records:** {len(df):,}")
            
            # Search functionality
            search_term = st.text_input(f"🔍 Search in {table_name}:", key=f"search_{table_name}")
            
            if search_term:
                # Search in all string columns
                search_mask = pd.DataFrame([df[col].astype(str).str.contains(search_term, case=False, na=False) 
                                          for col in df.select_dtypes(include=['object']).columns]).any()
                display_df = df[search_mask]
            else:
                display_df = df
            
            # Display the table
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Download button for this table
            csv_data = display_df.to_csv(index=False)
            st.download_button(
                label=f"📥 Download {table_name} Data (CSV)",
                data=csv_data,
                file_name=f"{table_name.lower()}_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key=f"download_{table_name}"
            )

def main():
    # Load data
    with st.spinner("Loading data from SQL Server..."):
        data = load_all_data()
    
    if data is None:
        st.error("Failed to load data. Please check your database connection.")
        return
    
    # Sidebar navigation
    st.sidebar.title("📊 Dashboard Navigation")
    
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Customer Insights", "Orders Overview", "Sales & Products", "Employees", "All Data Tables"]
    )
    
    # Display selected page
    if page == "Customer Insights":
        customer_insights_page(data)
    elif page == "Orders Overview":
        orders_overview_page(data)
    elif page == "Sales & Products":
        sales_products_page(data)
    elif page == "Employees":
        employees_page(data)
    elif page == "All Data Tables":
        all_data_tables_page(data)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 1rem;'>
            <p>📊 Business Analytics Dashboard | Powered by Streamlit & SQL Server</p>
            <p>Data last updated: {}</p>
        </div>
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 