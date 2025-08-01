import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pyodbc
from sqlalchemy import create_engine, text
import numpy as np
from datetime import datetime
from config import get_connection_string

# Page configuration
st.set_page_config(
    page_title="Customer Analytics Dashboard",
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
    }
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    """Load data from SQL Server database"""
    try:
        # Get connection string from config
        CONN_STR = get_connection_string()
        
        # Create SQLAlchemy engine
        engine = create_engine(f'mssql+pyodbc:///?odbc_connect={CONN_STR}')
        
        # Query to get all customers data
        query = """
        SELECT 
            CustomerID,
            CompanyName,
            ContactName,
            ContactTitle,
            Address,
            City,
            Region,
            PostalCode,
            Country,
            Phone,
            Fax
        FROM Customers
        """
        
        # Load data into pandas DataFrame
        df = pd.read_sql(query, engine)
        
        # Clean the data
        df = df.fillna('N/A')
        
        return df
    
    except Exception as e:
        st.error(f"Error connecting to database: {str(e)}")
        return None

def main():
    # Header
    st.markdown('<h1 class="main-header">📊 Customer Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading data from SQL Server..."):
        df = load_data()
    
    if df is None:
        st.error("Failed to load data. Please check your database connection.")
        return
    
    # Sidebar for filters
    st.sidebar.header("🔍 Filters")
    
    # Country filter
    countries = ['All'] + sorted(df['Country'].unique().tolist())
    selected_country = st.sidebar.selectbox("Select Country:", countries)
    
    # City filter (filtered based on selected country)
    if selected_country != 'All':
        cities = ['All'] + sorted(df[df['Country'] == selected_country]['City'].unique().tolist())
    else:
        cities = ['All'] + sorted(df['City'].unique().tolist())
    
    selected_city = st.sidebar.selectbox("Select City:", cities)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_country != 'All':
        filtered_df = filtered_df[filtered_df['Country'] == selected_country]
    if selected_city != 'All':
        filtered_df = filtered_df[filtered_df['City'] == selected_city]
    
    # Key Metrics
    st.header("📈 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Customers</h3>
            <h2>{len(filtered_df):,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Unique Cities</h3>
            <h2>{filtered_df['City'].nunique():,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Unique Countries</h3>
            <h2>{filtered_df['Country'].nunique():,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>With Phone</h3>
            <h2>{len(filtered_df[filtered_df['Phone'] != 'N/A']):,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts Section
    st.header("📊 Data Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Customers by City")
        # Bar chart for customers per city
        city_counts = filtered_df['City'].value_counts().head(10)
        fig_bar = px.bar(
            x=city_counts.values,
            y=city_counts.index,
            orientation='h',
            title="Top 10 Cities by Customer Count",
            labels={'x': 'Number of Customers', 'y': 'City'},
            color=city_counts.values,
            color_continuous_scale='Blues'
        )
        fig_bar.update_layout(height=400)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        st.subheader("Customers by Country")
        # Pie chart for country distribution
        country_counts = filtered_df['Country'].value_counts()
        fig_pie = px.pie(
            values=country_counts.values,
            names=country_counts.index,
            title="Customer Distribution by Country",
            hole=0.3
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Additional insights
    st.markdown("---")
    st.header("🔍 Additional Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Contact Titles Distribution")
        title_counts = filtered_df['ContactTitle'].value_counts().head(8)
        fig_title = px.bar(
            x=title_counts.index,
            y=title_counts.values,
            title="Top Contact Titles",
            labels={'x': 'Contact Title', 'y': 'Count'},
            color=title_counts.values,
            color_continuous_scale='Greens'
        )
        fig_title.update_xaxes(tickangle=45)
        st.plotly_chart(fig_title, use_container_width=True)
    
    with col2:
        st.subheader("Regional Distribution")
        region_counts = filtered_df['Region'].value_counts()
        if len(region_counts) > 1:  # Only show if there are multiple regions
            fig_region = px.pie(
                values=region_counts.values,
                names=region_counts.index,
                title="Customer Distribution by Region",
                hole=0.3
            )
            st.plotly_chart(fig_region, use_container_width=True)
        else:
            st.info("No regional data available or all customers are from the same region.")
    
    # Data Table Section
    st.markdown("---")
    st.header("📋 Customer Data Table")
    
    # Search functionality
    search_term = st.text_input("🔍 Search customers (by name, company, or city):", "")
    
    if search_term:
        search_mask = (
            filtered_df['CompanyName'].str.contains(search_term, case=False, na=False) |
            filtered_df['ContactName'].str.contains(search_term, case=False, na=False) |
            filtered_df['City'].str.contains(search_term, case=False, na=False)
        )
        display_df = filtered_df[search_mask]
    else:
        display_df = filtered_df
    
    # Display the table with pagination
    if len(display_df) > 0:
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "CustomerID": st.column_config.TextColumn("Customer ID", width="medium"),
                "CompanyName": st.column_config.TextColumn("Company Name", width="large"),
                "ContactName": st.column_config.TextColumn("Contact Name", width="medium"),
                "ContactTitle": st.column_config.TextColumn("Contact Title", width="medium"),
                "Address": st.column_config.TextColumn("Address", width="large"),
                "City": st.column_config.TextColumn("City", width="small"),
                "Region": st.column_config.TextColumn("Region", width="small"),
                "PostalCode": st.column_config.TextColumn("Postal Code", width="small"),
                "Country": st.column_config.TextColumn("Country", width="small"),
                "Phone": st.column_config.TextColumn("Phone", width="medium"),
                "Fax": st.column_config.TextColumn("Fax", width="medium")
            }
        )
        
        st.info(f"Showing {len(display_df)} of {len(filtered_df)} customers")
    else:
        st.warning("No customers found matching your search criteria.")
    
    # Download Section
    st.markdown("---")
    st.header("💾 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Download filtered data as CSV
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv_data,
            file_name=f"customers_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            help="Download the currently filtered data as a CSV file"
        )
    
    with col2:
        # Download all data as CSV
        csv_all_data = df.to_csv(index=False)
        st.download_button(
            label="📥 Download All Data (CSV)",
            data=csv_all_data,
            file_name=f"all_customers_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            help="Download all customer data as a CSV file"
        )
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 1rem;'>
            <p>📊 Customer Analytics Dashboard | Powered by Streamlit & SQL Server</p>
            <p>Data last updated: {}</p>
        </div>
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 