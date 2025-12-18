# check_columns.py
import mysql.connector

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mysql123',  # Your password
    'database': 'ecom_master'
}

conn = mysql.connector.connect(**config)
cursor = conn.cursor(dictionary=True)

print("🔍 Checking actual column names in each table:\n")

tables = ['sellers', 'orders', 'order_items', 'products', 'customers']

for table in tables:
    print(f"📋 {table.upper()} table columns:")
    cursor.execute(f"DESCRIBE {table}")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  • {col['Field']} ({col['Type']})")
    print()

cursor.close()
conn.close()