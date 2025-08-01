import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Business Analytics Dashboard - Demo",
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
def load_sample_data():
    """Load sample data for demonstration"""
    
    # Sample Customers data
    customers_data = {
        'CustomerID': ['ALFKI', 'ANATR', 'ANTON', 'AROUT', 'BERGS', 'BLAUS', 'BLONP', 'BOLID', 'BONAP', 'BOTTM'],
        'CompanyName': ['Alfreds Futterkiste', 'Ana Trujillo Emparedados', 'Antonio Moreno Taquería', 'Around the Horn', 'Berglunds snabbköp', 'Blauer See Delikatessen', 'Blondel père et fils', 'Bólido Comidas preparadas', 'Bon app\'', 'Bottom-Dollar Markets'],
        'ContactName': ['Maria Anders', 'Ana Trujillo', 'Antonio Moreno', 'Thomas Hardy', 'Christina Berglund', 'Hanna Moos', 'Frédérique Citeaux', 'Martín Sommer', 'Laurence Lebihans', 'Elizabeth Lincoln'],
        'ContactTitle': ['Sales Representative', 'Owner', 'Owner', 'Sales Representative', 'Order Administrator', 'Sales Representative', 'Marketing Manager', 'Owner', 'Owner', 'Accounting Manager'],
        'Country': ['Germany', 'Mexico', 'Mexico', 'UK', 'Sweden', 'Germany', 'France', 'Spain', 'France', 'Canada'],
        'City': ['Berlin', 'México D.F.', 'México D.F.', 'London', 'Luleå', 'Mannheim', 'Strasbourg', 'Madrid', 'Marseille', 'Tsawassen'],
        'Phone': ['030-0074321', '(5) 555-4729', '(5) 555-3932', '(171) 555-7788', '0921-12 34 65', '0621-08460', '88.60.15.31', '(91) 555 22 82', '91.24.45.40', '(604) 555-4729']
    }
    
    # Sample Orders data
    orders_data = {
        'OrderID': [10248, 10249, 10250, 10251, 10252, 10253, 10254, 10255, 10256, 10257],
        'CustomerID': ['VINET', 'TOMSP', 'HANAR', 'VICTE', 'SUPRD', 'HANAR', 'CHOPS', 'RICSU', 'WELLI', 'HILAA'],
        'OrderDate': ['1996-07-04', '1996-07-05', '1996-07-08', '1996-07-08', '1996-07-09', '1996-07-10', '1996-07-11', '1996-07-12', '1996-07-15', '1996-07-16'],
        'ShipCountry': ['France', 'Germany', 'Brazil', 'France', 'Belgium', 'Brazil', 'Switzerland', 'Switzerland', 'Brazil', 'Venezuela'],
        'EmployeeID': [5, 6, 4, 3, 4, 3, 5, 9, 3, 4]
    }
    
    # Sample Products data
    products_data = {
        'ProductID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'ProductName': ['Chai', 'Chang', 'Aniseed Syrup', 'Chef Anton\'s Cajun Seasoning', 'Chef Anton\'s Gumbo Mix', 'Grandma\'s Boysenberry Spread', 'Uncle Bob\'s Organic Dried Pears', 'Northwoods Cranberry Sauce', 'Mishi Kobe Niku', 'Ikura'],
        'CategoryID': [1, 1, 2, 2, 2, 2, 7, 2, 6, 8],
        'UnitPrice': [18.00, 19.00, 10.00, 22.00, 21.35, 25.00, 30.00, 40.00, 97.00, 31.00]
    }
    
    # Sample Categories data
    categories_data = {
        'CategoryID': [1, 2, 3, 4, 5, 6, 7, 8],
        'CategoryName': ['Beverages', 'Condiments', 'Confections', 'Dairy Products', 'Grains/Cereals', 'Meat/Poultry', 'Produce', 'Seafood'],
        'Description': ['Soft drinks, coffees, teas, beers, and ales', 'Sweet and savory sauces, relishes, spreads, and seasonings', 'Desserts, candies, and sweet breads', 'Cheeses', 'Breads, crackers, pasta, and cereal', 'Prepared meats', 'Dried fruit and bean curd', 'Seaweed and fish']
    }
    
    # Sample Employees data
    employees_data = {
        'EmployeeID': [1, 2, 3, 4, 5, 6, 7, 8, 9],
        'FirstName': ['Nancy', 'Andrew', 'Janet', 'Margaret', 'Steven', 'Michael', 'Robert', 'Laura', 'Anne'],
        'LastName': ['Davolio', 'Fuller', 'Leverling', 'Peacock', 'Buchanan', 'Suyama', 'King', 'Callahan', 'Dodsworth'],
        'Title': ['Sales Representative', 'Vice President, Sales', 'Sales Representative', 'Sales Representative', 'Sales Manager', 'Sales Representative', 'Sales Representative', 'Inside Sales Coordinator', 'Sales Representative'],
        'Country': ['USA', 'USA', 'USA', 'UK', 'UK', 'UK', 'UK', 'USA', 'UK'],
        'City': ['Seattle', 'Tacoma', 'Kirkland', 'London', 'London', 'London', 'London', 'Seattle', 'London']
    }
    
    # Sample OrderDetails data
    orderdetails_data = {
        'OrderID': [10248, 10248, 10249, 10250, 10250, 10251, 10251, 10252, 10252, 10253],
        'ProductID': [11, 42, 72, 14, 51, 41, 51, 22, 65, 20],
        'UnitPrice': [14.00, 9.80, 34.80, 18.60, 42.40, 7.70, 42.40, 16.80, 16.80, 64.80],
        'Quantity': [12, 10, 5, 9, 40, 10, 35, 6, 15, 40]
    }
    
    data = {
        'customers': pd.DataFrame(customers_data),
        'orders': pd.DataFrame(orders_data),
        'products': pd.DataFrame(products_data),
        'categories': pd.DataFrame(categories_data),
        'employees': pd.DataFrame(employees_data),
        'orderdetails': pd.DataFrame(orderdetails_data)
    }
    
    # Convert date columns
    data['orders']['OrderDate'] = pd.to_datetime(data['orders']['OrderDate'])
    
    return data

def customer_insights_page(data):
    """Customer Insights Dashboard"""
    st.markdown('<h1 class="main-header">👥 Customer Insights</h1>', unsafe_allow_html=True)
    
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
            <h3>Contact Titles</h3>
            <h2>{filtered_customers['ContactTitle'].nunique():,}</h2>
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
            title="Top Cities by Customer Count",
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
    
    orders_df = data['orders']
    
    # Sidebar filters
    st.sidebar.header("🔍 Order Filters")
    
    # Date filter
    min_date = orders_df['OrderDate'].min()
    max_date = orders_df['OrderDate'].max()
    
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
    
    # Country filter
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
        recent_orders = len(filtered_orders[filtered_orders['OrderDate'] >= (datetime.now() - timedelta(days=30))])
        st.markdown(f"""
        <div class="metric-card">
            <h3>Recent Orders (30d)</h3>
            <h2>{recent_orders:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        unique_customers = filtered_orders['CustomerID'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <h3>Unique Customers</h3>
            <h2>{unique_customers:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        unique_countries = filtered_orders['ShipCountry'].nunique()
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
        st.subheader("Orders by Country")
        country_counts = filtered_orders['ShipCountry'].value_counts().head(10)
        fig_country = px.bar(
            x=country_counts.index,
            y=country_counts.values,
            title="Top Countries by Orders",
            labels={'x': 'Country', 'y': 'Number of Orders'},
            color_continuous_scale='Reds'
        )
        fig_country.update_xaxes(tickangle=45)
        fig_country.update_layout(height=400)
        st.plotly_chart(fig_country, use_container_width=True)
    
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
    
    # Create sales data by joining tables
    sales_df = data['orderdetails'].merge(
        data['products'], 
        left_on='ProductID', 
        right_on='ProductID', 
        how='left',
        suffixes=('_order', '_product')
    )
    
    # Join with Categories
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
    sales_df = sales_df.merge(
        data['orders'][['OrderID', 'OrderDate', 'ShipCountry']],
        left_on='OrderID',
        right_on='OrderID',
        how='left'
    )
    
    # Sidebar filters
    st.sidebar.header("🔍 Sales Filters")
    
    # Category filter
    categories = ['All'] + sorted(sales_df['CategoryName'].unique().tolist())
    selected_category = st.sidebar.selectbox("Select Category:", categories)
    
    if selected_category != 'All':
        sales_df = sales_df[sales_df['CategoryName'] == selected_category]
    
    # Key Metrics
    st.header("📈 Sales Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = sales_df['Revenue'].sum()
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
    
    employees_df = data['employees']
    
    # Sidebar filters
    st.sidebar.header("🔍 Employee Filters")
    
    # Title filter
    titles = ['All'] + sorted(employees_df['Title'].unique().tolist())
    selected_title = st.sidebar.selectbox("Select Title:", titles)
    
    if selected_title != 'All':
        employees_df = employees_df[employees_df['Title'] == selected_title]
    
    # Country filter
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
        unique_titles = employees_df['Title'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <h3>Job Titles</h3>
            <h2>{unique_titles:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        unique_countries = employees_df['Country'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <h3>Countries</h3>
            <h2>{unique_countries:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        unique_cities = employees_df['City'].nunique()
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
    # Load sample data
    with st.spinner("Loading sample data..."):
        data = load_sample_data()
    
    # Add a notice about demo data
    st.info("🎯 **Demo Mode**: This dashboard is running with sample data. The actual multi-page dashboard connects to your SQL Server database.")
    
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
            <p>📊 Business Analytics Dashboard - Demo | Powered by Streamlit</p>
            <p>Data last updated: {}</p>
        </div>
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 