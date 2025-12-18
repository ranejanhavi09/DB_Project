import mysql.connector
import pandas as pd

def get_all_table_ddl():
    # Replace with your connection details
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='mysql123',
        database='ecom_master'
    )
    
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    
    ddl_statements = []
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SHOW CREATE TABLE {table_name}")
        result = cursor.fetchone()
        if result:
            ddl_statements.append(result[1])
            ddl_statements.append("\n" + "-"*50 + "\n")
    
    cursor.close()
    conn.close()
    
    # Save to file
    with open('database_ddl.sql', 'w') as f:
        f.write('\n'.join(ddl_statements))
    
    return ddl_statements

# Run the function
ddl = get_all_table_ddl()
for statement in ddl:
    print(statement)