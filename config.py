# Database Configuration
DB_CONFIG = {
    'driver': 'SQL Server',
    'server': 'localhost\\SQLEXPRESS',
    'database': 'practicedatabase',
    'trusted_connection': 'yes'
}

# Build connection string
def get_connection_string():
    """Build the SQL Server connection string from configuration"""
    return (
        f"DRIVER={{{DB_CONFIG['driver']}}};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"Trusted_Connection={DB_CONFIG['trusted_connection']};"
    )

# Alternative connection string for SQL Server Authentication
# Uncomment and modify if using SQL Server Authentication instead of Windows Authentication
# DB_CONFIG_AUTH = {
#     'driver': 'SQL Server',
#     'server': 'localhost\\SQLEXPRESS',
#     'database': 'practicedatabase',
#     'uid': 'your_username',
#     'pwd': 'your_password'
# }

# def get_connection_string_auth():
#     """Build the SQL Server connection string with authentication"""
#     return (
#         f"DRIVER={{{DB_CONFIG_AUTH['driver']}}};"
#         f"SERVER={DB_CONFIG_AUTH['server']};"
#         f"DATABASE={DB_CONFIG_AUTH['database']};"
#         f"UID={DB_CONFIG_AUTH['uid']};"
#         f"PWD={DB_CONFIG_AUTH['pwd']};"
#     ) 