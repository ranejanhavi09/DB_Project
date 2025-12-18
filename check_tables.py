# check_tables.py
import mysql.connector

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mysql123',  # Your actual password
    'database': 'ecom_master',
    'port': 3306
}

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    print("✅ Connected to ecom_master database")
    
    # List all tables
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    
    print(f"📋 Total tables: {len(tables)}")
    print("\n📊 Table list:")
    for i, table in enumerate(tables, 1):
        print(f"{i:2}. {table[0]}")
    
    # Check if we have any seller-related tables
    print("\n🔍 Looking for seller-related tables:")
    cursor.execute("SHOW TABLES LIKE '%seller%'")
    seller_tables = cursor.fetchall()
    for table in seller_tables:
        print(f"  • {table[0]}")
    
    # Check if we have any order-related tables
    print("\n🔍 Looking for order-related tables:")
    cursor.execute("SHOW TABLES LIKE '%order%'")
    order_tables = cursor.fetchall()
    for table in order_tables:
        print(f"  • {table[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")