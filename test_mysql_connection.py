import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '3306'),
    'user': os.getenv('DB_USERNAME', 'root'),
    'password': os.getenv('DB_PASSWORD', 'mysql123'),
    'database': os.getenv('DB_DATABASE', 'ecom_master')
}

print('Testing with config:', {k: v for k, v in config.items() if k != 'password'})

try:
    connection = mysql.connector.connect(**config)
    print('✅ SUCCESS! Connected to MySQL')
    connection.close()
except mysql.connector.Error as err:
    print(f'❌ FAILED: {err}')
