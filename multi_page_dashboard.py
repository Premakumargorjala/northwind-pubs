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

def data_relationships_page(data):
    """Enhanced Data Relationships Page with comprehensive sidebar filters and detailed data display"""
    st.markdown('<h1 class="main-header">🔗 Advanced Data Relationships Dashboard</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background-color: #f0f8ff; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem;'>
        <h3>🔍 Interactive Data Exploration:</h3>
        <ul>
            <li>Select any filter to see detailed related information across all tables</li>
            <li>View customer details, orders, products, and employee information</li>
            <li>Interactive charts and analytics for your selected criteria</li>
            <li>Export filtered data for further analysis</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Filters
    st.sidebar.header("🔍 Sidebar Filters")
    
    # Get unique values for filters
    order_ids = ['All'] + sorted(data['orders']['OrderID'].unique().tolist()) if not data['orders'].empty else ['All']
    customer_ids = ['All'] + sorted(data['customers']['CustomerID'].unique().tolist()) if not data['customers'].empty else ['All']
    employee_ids = ['All'] + sorted(data['employees']['EmployeeID'].unique().tolist()) if not data['employees'].empty else ['All']
    product_ids = ['All'] + sorted(data['products']['ProductID'].unique().tolist()) if not data['products'].empty else ['All']
    category_ids = ['All'] + sorted(data['categories']['CategoryID'].unique().tolist()) if not data['categories'].empty else ['All']
    
    # Filter dropdowns
    selected_order = st.sidebar.selectbox("📦 OrderID (from Orders):", order_ids)
    selected_customer = st.sidebar.selectbox("👤 CustomerID (from Customers):", customer_ids)
    selected_employee = st.sidebar.selectbox("👨‍💼 EmployeeID (from Employees):", employee_ids)
    selected_product = st.sidebar.selectbox("📦 ProductID (from Products):", product_ids)
    selected_category = st.sidebar.selectbox("🏷️ CategoryID (from Categories):", category_ids)
    
    # Date Range Filter
    if not data['orders'].empty and 'OrderDate' in data['orders'].columns:
        data['orders']['OrderDate'] = pd.to_datetime(data['orders']['OrderDate'], errors='coerce')
        min_date = data['orders']['OrderDate'].min()
        max_date = data['orders']['OrderDate'].max()
        
        if pd.notna(min_date) and pd.notna(max_date):
            date_range = st.sidebar.date_input(
                "📅 Date Range (OrderDate):",
                value=(min_date.date(), max_date.date()),
                min_value=min_date.date(),
                max_value=max_date.date()
            )
        else:
            date_range = None
    else:
        date_range = None
    
    # Determine which filter is active and show detailed information
    active_filter = None
    if selected_order != 'All':
        active_filter = 'OrderID'
        filter_value = selected_order
    elif selected_customer != 'All':
        active_filter = 'CustomerID'
        filter_value = selected_customer
    elif selected_employee != 'All':
        active_filter = 'EmployeeID'
        filter_value = selected_employee
    elif selected_product != 'All':
        active_filter = 'ProductID'
        filter_value = selected_product
    elif selected_category != 'All':
        active_filter = 'CategoryID'
        filter_value = selected_category
    elif date_range and len(date_range) == 2:
        active_filter = 'DateRange'
        filter_value = date_range
    
    # Main content area
    if active_filter:
        st.header(f"📊 Detailed Analysis for {active_filter}: {filter_value}")
        
        # Create tabs for organized display
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Related Data", "📈 Analytics", "📊 Charts", "💾 Export"])
        
        with tab1:
            st.subheader("🔗 Related Information")
            
            if active_filter == 'CustomerID':
                show_customer_detailed_relationships(data, filter_value)
            elif active_filter == 'OrderID':
                show_order_detailed_relationships(data, filter_value)
            elif active_filter == 'EmployeeID':
                show_employee_detailed_relationships(data, filter_value)
            elif active_filter == 'ProductID':
                show_product_detailed_relationships(data, filter_value)
            elif active_filter == 'CategoryID':
                show_category_detailed_relationships(data, filter_value)
            elif active_filter == 'DateRange':
                show_date_range_relationships(data, filter_value)
        
        with tab2:
            st.subheader("📈 Key Metrics & Analytics")
            show_analytics_for_filter(data, active_filter, filter_value)
        
        with tab3:
            st.subheader("📊 Interactive Charts")
            show_charts_for_filter(data, active_filter, filter_value)
        
        with tab4:
            st.subheader("💾 Export Data")
            show_export_options(data, active_filter, filter_value)
    
    else:
        # Show overview when no filter is selected
        st.header("📋 Data Overview")
        st.info("👈 Select a filter from the sidebar to explore detailed relationships")
        
        # Show summary statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Orders", len(data['orders']) if not data['orders'].empty else 0)
            st.metric("Total Customers", len(data['customers']) if not data['customers'].empty else 0)
        
        with col2:
            st.metric("Total Products", len(data['products']) if not data['products'].empty else 0)
            st.metric("Total Employees", len(data['employees']) if not data['employees'].empty else 0)
        
        with col3:
            st.metric("Total Categories", len(data['categories']) if not data['categories'].empty else 0)
            st.metric("Order Details", len(data['orderdetails']) if not data['orderdetails'].empty else 0)
        
        # Show sample data from each table
        st.subheader("📋 Sample Data from Each Table")
        
        tables = ['customers', 'orders', 'products', 'categories', 'employees', 'orderdetails']
        for table in tables:
            if not data[table].empty:
                with st.expander(f"📊 {table.title()} (First 5 rows)"):
                    st.dataframe(data[table].head(), use_container_width=True)

def create_comprehensive_dataset(data):
    """Create comprehensive dataset using your exact SQL query logic"""
    try:
        # Start with Orders and Order Details (RIGHT JOIN)
        if data['orders'].empty or data['orderdetails'].empty:
            return pd.DataFrame()
        
        # RIGHT JOIN Orders with Order Details
        comprehensive = data['orderdetails'].merge(
            data['orders'],
            left_on='OrderID',
            right_on='OrderID',
            how='right'
        )
        
        # LEFT JOIN with Products
        if not data['products'].empty:
            comprehensive = comprehensive.merge(
                data['products'],
                left_on='ProductID',
                right_on='ProductID',
                how='left'
            )
        
        # JOIN with Customers
        if not data['customers'].empty:
            comprehensive = comprehensive.merge(
                data['customers'],
                left_on='CustomerID',
                right_on='CustomerID',
                how='inner'
            )
        
        # JOIN with Categories
        if not data['categories'].empty and 'CategoryID' in comprehensive.columns:
            comprehensive = comprehensive.merge(
                data['categories'],
                left_on='CategoryID',
                right_on='CategoryID',
                how='inner'
            )
        
        # JOIN with Employees
        if not data['employees'].empty:
            comprehensive = comprehensive.merge(
                data['employees'],
                left_on='EmployeeID',
                right_on='EmployeeID',
                how='inner'
            )
        
        # Select and rename columns to match your exact SQL query
        columns_to_keep = [
            'OrderID', 'ShippedDate', 'ShipName', 'ProductID', 'UnitPrice', 
            'Quantity', 'Discount', 'CompanyName', 'CategoryName', 'ProductName', 
            'CustomerID', 'EmployeeID', 'FirstName', 'LastName'
        ]
        
        # Keep only columns that exist and rename CompanyName to CustomerCompany
        available_columns = [col for col in columns_to_keep if col in comprehensive.columns]
        comprehensive = comprehensive[available_columns]
        
        # Rename CompanyName to CustomerCompany to match your query
        if 'CompanyName' in comprehensive.columns:
            comprehensive = comprehensive.rename(columns={'CompanyName': 'CustomerCompany'})
        
        return comprehensive
        
    except Exception as e:
        st.error(f"Error in create_comprehensive_dataset: {str(e)}")
        return pd.DataFrame()

def show_customer_relationships(data, customer_id):
    """Show all data related to a specific customer"""
    st.markdown("### 📊 Customer Relationships")
    
    # Customer details
    customer = data['customers'][data['customers']['CustomerID'] == customer_id]
    if not customer.empty:
        st.markdown("**Customer Information:**")
        st.json(customer.iloc[0].to_dict())
    
    # Customer's orders
    customer_orders = data['orders'][data['orders']['CustomerID'] == customer_id]
    if not customer_orders.empty:
        st.markdown(f"**Orders ({len(customer_orders)}):**")
        st.dataframe(customer_orders, use_container_width=True, hide_index=True)
        
        # Order details for this customer
        order_ids = customer_orders['OrderID'].tolist()
        if order_ids and not data['orderdetails'].empty:
            customer_order_details = data['orderdetails'][data['orderdetails']['OrderID'].isin(order_ids)]
            if not customer_order_details.empty:
                st.markdown(f"**Order Details ({len(customer_order_details)}):**")
                st.dataframe(customer_order_details, use_container_width=True, hide_index=True)

def show_order_relationships(data, order_id):
    """Show all data related to a specific order"""
    st.markdown("### 📊 Order Relationships")
    
    # Order details
    order = data['orders'][data['orders']['OrderID'] == order_id]
    if not order.empty:
        st.markdown("**Order Information:**")
        st.json(order.iloc[0].to_dict())
    
    # Customer who placed the order
    if not order.empty and 'CustomerID' in order.columns:
        customer_id = order.iloc[0]['CustomerID']
        customer = data['customers'][data['customers']['CustomerID'] == customer_id]
        if not customer.empty:
            st.markdown("**Customer Information:**")
            st.json(customer.iloc[0].to_dict())
    
    # Employee who handled the order
    if not order.empty and 'EmployeeID' in order.columns:
        employee_id = order.iloc[0]['EmployeeID']
        employee = data['employees'][data['employees']['EmployeeID'] == employee_id]
        if not employee.empty:
            st.markdown("**Employee Information:**")
            st.json(employee.iloc[0].to_dict())
    
    # Order details
    order_details = data['orderdetails'][data['orderdetails']['OrderID'] == order_id]
    if not order_details.empty:
        st.markdown(f"**Order Details ({len(order_details)}):**")
        st.dataframe(order_details, use_container_width=True, hide_index=True)
        
        # Product information for order details
        product_ids = order_details['ProductID'].tolist()
        if product_ids and not data['products'].empty:
            products = data['products'][data['products']['ProductID'].isin(product_ids)]
            if not products.empty:
                st.markdown("**Products in this Order:**")
                st.dataframe(products, use_container_width=True, hide_index=True)

def show_product_relationships(data, product_id):
    """Show all data related to a specific product"""
    st.markdown("### 📊 Product Relationships")
    
    # Product details
    product = data['products'][data['products']['ProductID'] == product_id]
    if not product.empty:
        st.markdown("**Product Information:**")
        st.json(product.iloc[0].to_dict())
    
    # Category information
    if not product.empty and 'CategoryID' in product.columns:
        category_id = product.iloc[0]['CategoryID']
        category = data['categories'][data['categories']['CategoryID'] == category_id]
        if not category.empty:
            st.markdown("**Category Information:**")
            st.json(category.iloc[0].to_dict())
    
    # Order details for this product
    product_order_details = data['orderdetails'][data['orderdetails']['ProductID'] == product_id]
    if not product_order_details.empty:
        st.markdown(f"**Order Details ({len(product_order_details)}):**")
        st.dataframe(product_order_details, use_container_width=True, hide_index=True)
        
        # Orders that contain this product
        order_ids = product_order_details['OrderID'].tolist()
        if order_ids and not data['orders'].empty:
            orders = data['orders'][data['orders']['OrderID'].isin(order_ids)]
            if not orders.empty:
                st.markdown("**Orders containing this Product:**")
                st.dataframe(orders, use_container_width=True, hide_index=True)

def show_category_relationships(data, category_id):
    """Show all data related to a specific category"""
    st.markdown("### 📊 Category Relationships")
    
    # Category details
    category = data['categories'][data['categories']['CategoryID'] == category_id]
    if not category.empty:
        st.markdown("**Category Information:**")
        st.json(category.iloc[0].to_dict())
    
    # Products in this category
    category_products = data['products'][data['products']['CategoryID'] == category_id]
    if not category_products.empty:
        st.markdown(f"**Products in this Category ({len(category_products)}):**")
        st.dataframe(category_products, use_container_width=True, hide_index=True)
        
        # Order details for products in this category
        product_ids = category_products['ProductID'].tolist()
        if product_ids and not data['orderdetails'].empty:
            category_order_details = data['orderdetails'][data['orderdetails']['ProductID'].isin(product_ids)]
            if not category_order_details.empty:
                st.markdown(f"**Order Details for Products in this Category ({len(category_order_details)}):**")
                st.dataframe(category_order_details, use_container_width=True, hide_index=True)

def show_employee_relationships(data, employee_id):
    """Show all data related to a specific employee"""
    st.markdown("### 📊 Employee Relationships")
    
    # Employee details
    employee = data['employees'][data['employees']['EmployeeID'] == employee_id]
    if not employee.empty:
        st.markdown("**Employee Information:**")
        st.json(employee.iloc[0].to_dict())
    
    # Orders handled by this employee
    employee_orders = data['orders'][data['orders']['EmployeeID'] == employee_id]
    if not employee_orders.empty:
        st.markdown(f"**Orders Handled ({len(employee_orders)}):**")
        st.dataframe(employee_orders, use_container_width=True, hide_index=True)
        
        # Customers served by this employee
        customer_ids = employee_orders['CustomerID'].dropna().unique()
        if len(customer_ids) > 0 and not data['customers'].empty:
            customers = data['customers'][data['customers']['CustomerID'].isin(customer_ids)]
            if not customers.empty:
                st.markdown(f"**Customers Served ({len(customers)}):**")
                st.dataframe(customers, use_container_width=True, hide_index=True)

# Enhanced Data Relationships Helper Functions
def show_customer_detailed_relationships(data, customer_id):
    """Show detailed customer relationships with expandable sections"""
    customer = data['customers'][data['customers']['CustomerID'] == customer_id]
    
    if not customer.empty:
        with st.expander("👤 Customer Details", expanded=True):
            st.json(customer.iloc[0].to_dict())
    
    # Customer's orders
    customer_orders = data['orders'][data['orders']['CustomerID'] == customer_id]
    if not customer_orders.empty:
        with st.expander(f"📦 Orders ({len(customer_orders)})", expanded=True):
            st.dataframe(customer_orders, use_container_width=True, hide_index=True)
            
            # Order details for this customer
            order_ids = customer_orders['OrderID'].tolist()
            if order_ids and not data['orderdetails'].empty:
                customer_order_details = data['orderdetails'][data['orderdetails']['OrderID'].isin(order_ids)]
                if not customer_order_details.empty:
                    st.subheader("Order Details")
                    st.dataframe(customer_order_details, use_container_width=True, hide_index=True)
                    
                    # Products purchased by this customer
                    product_ids = customer_order_details['ProductID'].unique()
                    if len(product_ids) > 0 and not data['products'].empty:
                        products = data['products'][data['products']['ProductID'].isin(product_ids)]
                        if not products.empty:
                            st.subheader("Products Purchased")
                            st.dataframe(products, use_container_width=True, hide_index=True)

def show_order_detailed_relationships(data, order_id):
    """Show detailed order relationships with expandable sections"""
    order = data['orders'][data['orders']['OrderID'] == order_id]
    
    if not order.empty:
        with st.expander("📦 Order Details", expanded=True):
            st.json(order.iloc[0].to_dict())
        
        # Customer who placed the order
        if 'CustomerID' in order.columns:
            customer_id = order.iloc[0]['CustomerID']
            customer = data['customers'][data['customers']['CustomerID'] == customer_id]
            if not customer.empty:
                with st.expander("👤 Customer Information", expanded=True):
                    st.json(customer.iloc[0].to_dict())
        
        # Employee who handled the order
        if 'EmployeeID' in order.columns:
            employee_id = order.iloc[0]['EmployeeID']
            employee = data['employees'][data['employees']['EmployeeID'] == employee_id]
            if not employee.empty:
                with st.expander("👨‍💼 Employee Information", expanded=True):
                    st.json(employee.iloc[0].to_dict())
        
        # Order details
        order_details = data['orderdetails'][data['orderdetails']['OrderID'] == order_id]
        if not order_details.empty:
            with st.expander(f"📋 Order Details ({len(order_details)})", expanded=True):
                st.dataframe(order_details, use_container_width=True, hide_index=True)
                
                # Product information for order details
                product_ids = order_details['ProductID'].tolist()
                if product_ids and not data['products'].empty:
                    products = data['products'][data['products']['ProductID'].isin(product_ids)]
                    if not products.empty:
                        st.subheader("Products in this Order")
                        st.dataframe(products, use_container_width=True, hide_index=True)

def show_employee_detailed_relationships(data, employee_id):
    """Show detailed employee relationships with expandable sections"""
    employee = data['employees'][data['employees']['EmployeeID'] == employee_id]
    
    if not employee.empty:
        with st.expander("👨‍💼 Employee Details", expanded=True):
            st.json(employee.iloc[0].to_dict())
    
    # Orders handled by this employee
    employee_orders = data['orders'][data['orders']['EmployeeID'] == employee_id]
    if not employee_orders.empty:
        with st.expander(f"📦 Orders Handled ({len(employee_orders)})", expanded=True):
            st.dataframe(employee_orders, use_container_width=True, hide_index=True)
            
            # Customers served by this employee
            customer_ids = employee_orders['CustomerID'].dropna().unique()
            if len(customer_ids) > 0 and not data['customers'].empty:
                customers = data['customers'][data['customers']['CustomerID'].isin(customer_ids)]
                if not customers.empty:
                    st.subheader("Customers Served")
                    st.dataframe(customers, use_container_width=True, hide_index=True)
            
            # Products sold by this employee
            order_ids = employee_orders['OrderID'].tolist()
            if order_ids and not data['orderdetails'].empty:
                employee_order_details = data['orderdetails'][data['orderdetails']['OrderID'].isin(order_ids)]
                if not employee_order_details.empty:
                    st.subheader("Order Details")
                    st.dataframe(employee_order_details, use_container_width=True, hide_index=True)
                    
                    product_ids = employee_order_details['ProductID'].unique()
                    if len(product_ids) > 0 and not data['products'].empty:
                        products = data['products'][data['products']['ProductID'].isin(product_ids)]
                        if not products.empty:
                            st.subheader("Products Sold")
                            st.dataframe(products, use_container_width=True, hide_index=True)

def show_product_detailed_relationships(data, product_id):
    """Show detailed product relationships with expandable sections"""
    product = data['products'][data['products']['ProductID'] == product_id]
    
    if not product.empty:
        with st.expander("📦 Product Details", expanded=True):
            st.json(product.iloc[0].to_dict())
        
        # Category information
        if 'CategoryID' in product.columns:
            category_id = product.iloc[0]['CategoryID']
            category = data['categories'][data['categories']['CategoryID'] == category_id]
            if not category.empty:
                with st.expander("🏷️ Category Information", expanded=True):
                    st.json(category.iloc[0].to_dict())
        
        # Order details for this product
        product_order_details = data['orderdetails'][data['orderdetails']['ProductID'] == product_id]
        if not product_order_details.empty:
            with st.expander(f"📋 Order Details ({len(product_order_details)})", expanded=True):
                st.dataframe(product_order_details, use_container_width=True, hide_index=True)
                
                # Orders that contain this product
                order_ids = product_order_details['OrderID'].tolist()
                if order_ids and not data['orders'].empty:
                    orders = data['orders'][data['orders']['OrderID'].isin(order_ids)]
                    if not orders.empty:
                        st.subheader("Orders containing this Product")
                        st.dataframe(orders, use_container_width=True, hide_index=True)
                        
                        # Customers who bought this product
                        customer_ids = orders['CustomerID'].dropna().unique()
                        if len(customer_ids) > 0 and not data['customers'].empty:
                            customers = data['customers'][data['customers']['CustomerID'].isin(customer_ids)]
                            if not customers.empty:
                                st.subheader("Customers who bought this Product")
                                st.dataframe(customers, use_container_width=True, hide_index=True)

def show_category_detailed_relationships(data, category_id):
    """Show detailed category relationships with expandable sections"""
    category = data['categories'][data['categories']['CategoryID'] == category_id]
    
    if not category.empty:
        with st.expander("🏷️ Category Details", expanded=True):
            st.json(category.iloc[0].to_dict())
    
    # Products in this category
    category_products = data['products'][data['products']['CategoryID'] == category_id]
    if not category_products.empty:
        with st.expander(f"📦 Products in Category ({len(category_products)})", expanded=True):
            st.dataframe(category_products, use_container_width=True, hide_index=True)
            
            # Order details for products in this category
            product_ids = category_products['ProductID'].tolist()
            if product_ids and not data['orderdetails'].empty:
                category_order_details = data['orderdetails'][data['orderdetails']['ProductID'].isin(product_ids)]
                if not category_order_details.empty:
                    st.subheader("Order Details for Products in this Category")
                    st.dataframe(category_order_details, use_container_width=True, hide_index=True)
                    
                    # Orders involving products in this category
                    order_ids = category_order_details['OrderID'].unique()
                    if len(order_ids) > 0 and not data['orders'].empty:
                        orders = data['orders'][data['orders']['OrderID'].isin(order_ids)]
                        if not orders.empty:
                            st.subheader("Orders involving Products in this Category")
                            st.dataframe(orders, use_container_width=True, hide_index=True)

def show_date_range_relationships(data, date_range):
    """Show relationships for a specific date range"""
    start_date, end_date = date_range
    
    # Filter orders by date range
    if not data['orders'].empty and 'OrderDate' in data['orders'].columns:
        data['orders']['OrderDate'] = pd.to_datetime(data['orders']['OrderDate'], errors='coerce')
        date_filtered_orders = data['orders'][
            (data['orders']['OrderDate'].dt.date >= start_date) &
            (data['orders']['OrderDate'].dt.date <= end_date)
        ]
        
        if not date_filtered_orders.empty:
            with st.expander(f"📦 Orders in Date Range ({len(date_filtered_orders)})", expanded=True):
                st.dataframe(date_filtered_orders, use_container_width=True, hide_index=True)
                
                # Order details for this date range
                order_ids = date_filtered_orders['OrderID'].tolist()
                if order_ids and not data['orderdetails'].empty:
                    date_order_details = data['orderdetails'][data['orderdetails']['OrderID'].isin(order_ids)]
                    if not date_order_details.empty:
                        st.subheader("Order Details in Date Range")
                        st.dataframe(date_order_details, use_container_width=True, hide_index=True)
                        
                        # Products sold in this date range
                        product_ids = date_order_details['ProductID'].unique()
                        if len(product_ids) > 0 and not data['products'].empty:
                            products = data['products'][data['products']['ProductID'].isin(product_ids)]
                            if not products.empty:
                                st.subheader("Products Sold in Date Range")
                                st.dataframe(products, use_container_width=True, hide_index=True)
                        
                        # Customers who ordered in this date range
                        customer_ids = date_filtered_orders['CustomerID'].dropna().unique()
                        if len(customer_ids) > 0 and not data['customers'].empty:
                            customers = data['customers'][data['customers']['CustomerID'].isin(customer_ids)]
                            if not customers.empty:
                                st.subheader("Customers who Ordered in Date Range")
                                st.dataframe(customers, use_container_width=True, hide_index=True)

def show_analytics_for_filter(data, active_filter, filter_value):
    """Show analytics and metrics for the selected filter"""
    if active_filter == 'CustomerID':
        # Customer analytics
        customer_orders = data['orders'][data['orders']['CustomerID'] == filter_value]
        if not customer_orders.empty:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Orders", len(customer_orders))
            with col2:
                st.metric("Total Revenue", f"${customer_orders.get('Freight', 0).sum():,.2f}")
            with col3:
                st.metric("Countries Shipped To", customer_orders['ShipCountry'].nunique())
            with col4:
                st.metric("Cities Shipped To", customer_orders['ShipCity'].nunique())
    
    elif active_filter == 'OrderID':
        # Order analytics
        order = data['orders'][data['orders']['OrderID'] == filter_value]
        if not order.empty:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Order Value", f"${order.iloc[0].get('Freight', 0):,.2f}")
            with col2:
                st.metric("Ship Country", order.iloc[0].get('ShipCountry', 'N/A'))
            with col3:
                st.metric("Ship City", order.iloc[0].get('ShipCity', 'N/A'))
            with col4:
                st.metric("Order Date", order.iloc[0].get('OrderDate', 'N/A'))
    
    elif active_filter == 'EmployeeID':
        # Employee analytics
        employee_orders = data['orders'][data['orders']['EmployeeID'] == filter_value]
        if not employee_orders.empty:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Orders Handled", len(employee_orders))
            with col2:
                st.metric("Total Revenue", f"${employee_orders.get('Freight', 0).sum():,.2f}")
            with col3:
                st.metric("Customers Served", employee_orders['CustomerID'].nunique())
            with col4:
                st.metric("Countries Served", employee_orders['ShipCountry'].nunique())
    
    elif active_filter == 'ProductID':
        # Product analytics
        product_orders = data['orderdetails'][data['orderdetails']['ProductID'] == filter_value]
        if not product_orders.empty:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Quantity Sold", product_orders['Quantity'].sum())
            with col2:
                st.metric("Total Revenue", f"${(product_orders['UnitPrice'] * product_orders['Quantity']).sum():,.2f}")
            with col3:
                st.metric("Orders Containing Product", product_orders['OrderID'].nunique())
            with col4:
                st.metric("Average Discount", f"{product_orders['Discount'].mean():.2%}")
    
    elif active_filter == 'CategoryID':
        # Category analytics
        category_products = data['products'][data['products']['CategoryID'] == filter_value]
        if not category_products.empty:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Products in Category", len(category_products))
            with col2:
                st.metric("Average Unit Price", f"${category_products['UnitPrice'].mean():,.2f}")
            with col3:
                st.metric("Total Stock", category_products['UnitsInStock'].sum())
            with col4:
                st.metric("Discontinued Products", len(category_products[category_products['Discontinued'] == True]))

def show_charts_for_filter(data, active_filter, filter_value):
    """Show interactive charts for the selected filter"""
    if active_filter == 'CustomerID':
        # Customer charts
        customer_orders = data['orders'][data['orders']['CustomerID'] == filter_value]
        if not customer_orders.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Orders over time
                if 'OrderDate' in customer_orders.columns:
                    customer_orders['OrderDate'] = pd.to_datetime(customer_orders['OrderDate'], errors='coerce')
                    orders_by_date = customer_orders.groupby(customer_orders['OrderDate'].dt.date).size().reset_index(name='count')
                    fig = px.line(orders_by_date, x='OrderDate', y='count', title="Orders Over Time")
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Orders by ship country
                country_counts = customer_orders['ShipCountry'].value_counts()
                fig = px.pie(values=country_counts.values, names=country_counts.index, title="Orders by Ship Country")
                st.plotly_chart(fig, use_container_width=True)
    
    elif active_filter == 'EmployeeID':
        # Employee charts
        employee_orders = data['orders'][data['orders']['EmployeeID'] == filter_value]
        if not employee_orders.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Orders by customer
                customer_counts = employee_orders['CustomerID'].value_counts().head(10)
                fig = px.bar(x=customer_counts.index, y=customer_counts.values, title="Top 10 Customers")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Orders by ship country
                country_counts = employee_orders['ShipCountry'].value_counts()
                fig = px.pie(values=country_counts.values, names=country_counts.index, title="Orders by Ship Country")
                st.plotly_chart(fig, use_container_width=True)
    
    elif active_filter == 'ProductID':
        # Product charts
        product_orders = data['orderdetails'][data['orderdetails']['ProductID'] == filter_value]
        if not product_orders.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Quantity sold over time (if order dates available)
                if not data['orders'].empty:
                    order_dates = data['orders'][['OrderID', 'OrderDate']]
                    product_with_dates = product_orders.merge(order_dates, on='OrderID', how='left')
                    if 'OrderDate' in product_with_dates.columns:
                        product_with_dates['OrderDate'] = pd.to_datetime(product_with_dates['OrderDate'], errors='coerce')
                        quantity_by_date = product_with_dates.groupby(product_with_dates['OrderDate'].dt.date)['Quantity'].sum().reset_index()
                        fig = px.line(quantity_by_date, x='OrderDate', y='Quantity', title="Quantity Sold Over Time")
                        st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Revenue by order
                product_orders['Revenue'] = product_orders['UnitPrice'] * product_orders['Quantity']
                revenue_by_order = product_orders.groupby('OrderID')['Revenue'].sum().sort_values(ascending=False).head(10)
                fig = px.bar(x=revenue_by_order.index, y=revenue_by_order.values, title="Top 10 Orders by Revenue")
                st.plotly_chart(fig, use_container_width=True)

def show_export_options(data, active_filter, filter_value):
    """Show export options for the filtered data"""
    st.subheader("📊 Export Filtered Data")
    
    if active_filter == 'CustomerID':
        # Export customer-related data
        customer_orders = data['orders'][data['orders']['CustomerID'] == filter_value]
        if not customer_orders.empty:
            csv_data = customer_orders.to_csv(index=False)
            st.download_button(
                label="📥 Download Customer Orders (CSV)",
                data=csv_data,
                file_name=f"customer_{filter_value}_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    elif active_filter == 'OrderID':
        # Export order-related data
        order_details = data['orderdetails'][data['orderdetails']['OrderID'] == filter_value]
        if not order_details.empty:
            csv_data = order_details.to_csv(index=False)
            st.download_button(
                label="📥 Download Order Details (CSV)",
                data=csv_data,
                file_name=f"order_{filter_value}_details_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    elif active_filter == 'EmployeeID':
        # Export employee-related data
        employee_orders = data['orders'][data['orders']['EmployeeID'] == filter_value]
        if not employee_orders.empty:
            csv_data = employee_orders.to_csv(index=False)
            st.download_button(
                label="📥 Download Employee Orders (CSV)",
                data=csv_data,
                file_name=f"employee_{filter_value}_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    elif active_filter == 'ProductID':
        # Export product-related data
        product_orders = data['orderdetails'][data['orderdetails']['ProductID'] == filter_value]
        if not product_orders.empty:
            csv_data = product_orders.to_csv(index=False)
            st.download_button(
                label="📥 Download Product Orders (CSV)",
                data=csv_data,
                file_name=f"product_{filter_value}_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    elif active_filter == 'CategoryID':
        # Export category-related data
        category_products = data['products'][data['products']['CategoryID'] == filter_value]
        if not category_products.empty:
            csv_data = category_products.to_csv(index=False)
            st.download_button(
                label="📥 Download Category Products (CSV)",
                data=csv_data,
                file_name=f"category_{filter_value}_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    elif active_filter == 'DateRange':
        # Export date range data
        start_date, end_date = filter_value
        if not data['orders'].empty and 'OrderDate' in data['orders'].columns:
            data['orders']['OrderDate'] = pd.to_datetime(data['orders']['OrderDate'], errors='coerce')
            date_filtered_orders = data['orders'][
                (data['orders']['OrderDate'].dt.date >= start_date) &
                (data['orders']['OrderDate'].dt.date <= end_date)
            ]
            if not date_filtered_orders.empty:
                csv_data = date_filtered_orders.to_csv(index=False)
                st.download_button(
                    label="📥 Download Date Range Orders (CSV)",
                    data=csv_data,
                    file_name=f"orders_{start_date}_to_{end_date}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
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
        ["Customer Insights", "Orders Overview", "Sales & Products", "Employees", "Data Relationships", "All Data Tables"]
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
    elif page == "Data Relationships":
        data_relationships_page(data)
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