# Customer Analytics Dashboard

A comprehensive Streamlit application that connects to SQL Server and provides interactive analytics for customer data.

## 🚀 Features

- **Database Integration**: Connects to SQL Server using pyodbc and SQLAlchemy
- **Interactive Dashboard**: Clean, responsive, and presentation-ready interface
- **Key Metrics**: Total customers, unique cities, unique countries, and phone coverage
- **Advanced Filtering**: Filter by country and city using dropdown menus
- **Data Visualizations**:
  - Bar chart showing customers per city (top 10)
  - Pie chart showing customer distribution by country
  - Contact titles distribution chart
  - Regional distribution chart
- **Searchable Table**: Search and sort customer data by name, company, or city
- **Data Export**: Download filtered or all data as CSV files
- **Real-time Updates**: Data is cached for performance with hourly refresh

## 📋 Prerequisites

- Python 3.8 or higher
- SQL Server with SQL Server Express (SQLEXPRESS)
- SQL Server ODBC Driver
- Access to a database named `practicedatabase` with a `Customers` table

## 🛠️ Installation

1. **Clone or download this repository**

2. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install SQL Server ODBC Driver** (if not already installed):
   - Download from Microsoft's website: [SQL Server ODBC Driver](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
   - Or install via package manager:
     ```bash
     # For Windows (using chocolatey)
     choco install msodbcsql17
     
     # For Ubuntu/Debian
     sudo apt-get install unixodbc-dev
     ```

## 🗄️ Database Setup

Ensure your SQL Server database has a `Customers` table with the following columns:

```sql
CREATE TABLE Customers (
    CustomerID VARCHAR(50) PRIMARY KEY,
    CompanyName VARCHAR(100),
    ContactName VARCHAR(100),
    ContactTitle VARCHAR(100),
    Address VARCHAR(200),
    City VARCHAR(100),
    Region VARCHAR(100),
    PostalCode VARCHAR(20),
    Country VARCHAR(100),
    Phone VARCHAR(50),
    Fax VARCHAR(50)
);
```

## 🚀 Running the Application

1. **Start the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** and navigate to the URL shown in the terminal (typically `http://localhost:8501`)

## 📊 Dashboard Sections

### 1. Key Metrics
- Total number of customers
- Number of unique cities
- Number of unique countries
- Customers with phone numbers

### 2. Data Visualizations
- **Customers by City**: Horizontal bar chart showing top 10 cities
- **Customers by Country**: Donut chart showing country distribution
- **Contact Titles**: Bar chart of most common contact titles
- **Regional Distribution**: Pie chart of regional distribution

### 3. Interactive Table
- Searchable and sortable customer data
- All customer information displayed in a clean table format
- Real-time filtering based on search terms

### 4. Data Export
- Download filtered data as CSV
- Download all data as CSV
- Timestamped file names for easy organization

## 🔧 Configuration

The application uses the following connection string by default:
```python
CONN_STR = (
    r'DRIVER={SQL Server};'
    r'SERVER=localhost\\SQLEXPRESS;'
    r'DATABASE=practicedatabase;'
    r'Trusted_Connection=yes;'
)
```

To modify the connection:
1. Edit the `CONN_STR` variable in `app.py`
2. Update server name, database name, or authentication method as needed

## 🎨 Customization

### Styling
The dashboard uses custom CSS for styling. You can modify the styles in the `st.markdown()` section at the top of the `app.py` file.

### Charts
All charts are created using Plotly Express. You can customize colors, layouts, and chart types by modifying the chart creation code.

### Metrics
Add or modify key metrics by editing the metrics section in the `main()` function.

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Verify SQL Server is running
   - Check the connection string
   - Ensure the database and table exist
   - Verify Windows Authentication is enabled

2. **ODBC Driver Not Found**:
   - Install the appropriate SQL Server ODBC Driver
   - Verify the driver name in the connection string

3. **Permission Issues**:
   - Ensure your Windows account has access to the database
   - Check SQL Server permissions

### Error Messages

- **"Error connecting to database"**: Check database connection and credentials
- **"No customers found"**: Verify the Customers table has data
- **"Failed to load data"**: Check SQL Server status and network connectivity

## 📈 Performance Tips

- The application caches data for 1 hour to improve performance
- Large datasets are handled efficiently with pagination
- Charts are optimized for interactive viewing

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve this dashboard.

## 📄 License

This project is open source and available under the MIT License.

---

**Note**: Make sure your SQL Server instance is running and accessible before starting the application. 