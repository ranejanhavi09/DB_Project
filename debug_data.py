import mysql.connector
import pandas as pd

# Your MySQL configuration
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mysql123',  # Your password here
    'database': 'ecom_master'
}

def test_all_queries():
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    print("🔍 Testing Dashboard Queries\n" + "="*50)
    
    # Test 1: Check basic table counts
    print("\n1. 📊 TABLE COUNTS:")
    tables = ['sellers', 'orders', 'customers', 'products', 'order_items']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
        count = cursor.fetchone()['count']
        print(f"   {table:15} → {count:,} rows")
    
    # Test 2: Check sellers data
    print("\n2. 🏪 SELLERS DATA:")
    cursor.execute("SELECT * FROM sellers LIMIT 3")
    sellers = cursor.fetchall()
    if sellers:
        print(f"   Found {len(sellers)} sellers (sample):")
        for seller in sellers:
            print(f"   • {seller}")
    else:
        print("   ❌ No sellers found!")
    
    # Test 3: Check orders data
    print("\n3. 📦 ORDERS DATA:")
    cursor.execute("""
        SELECT order_status, COUNT(*) as count 
        FROM orders 
        GROUP BY order_status 
        LIMIT 5
    """)
    order_status = cursor.fetchall()
    if order_status:
        print(f"   Order status distribution:")
        for status in order_status:
            print(f"   • {status['order_status']}: {status['count']:,}")
    else:
        print("   ❌ No orders found!")
    
    # Test 4: Check order_items (connects sellers, products, orders)
    print("\n4. 🔗 ORDER_ITEMS (Critical for relationships):")
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT seller_id) as unique_sellers,
            COUNT(DISTINCT product_id) as unique_products,
            COUNT(DISTINCT order_id) as unique_orders,
            SUM(price) as total_revenue
        FROM order_items
    """)
    order_items_stats = cursor.fetchone()
    print(f"   Unique sellers in order_items: {order_items_stats['unique_sellers']:,}")
    print(f"   Unique products in order_items: {order_items_stats['unique_products']:,}")
    print(f"   Unique orders in order_items: {order_items_stats['unique_orders']:,}")
    print(f"   Total revenue in order_items: ${order_items_stats['total_revenue'] or 0:,.2f}")
    
    # Test 5: Check if JOINs work
    print("\n5. 🔄 TESTING JOINS:")
    
    # Test seller-orders join
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM sellers s 
        JOIN order_items oi ON s.seller_id = oi.seller_id
    """)
    join_count = cursor.fetchone()['count']
    print(f"   Sellers with orders: {join_count:,}")
    
    if join_count == 0:
        print("   ⚠️  WARNING: No matching records between sellers and order_items!")
        print("   This explains empty charts!")
    
    # Test 6: Sample revenue query
    print("\n6. 💰 REVENUE QUERY TEST:")
    cursor.execute("""
        SELECT 
            DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') as month,
            COUNT(DISTINCT o.order_id) as orders,
            SUM(oi.price) as revenue
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_purchase_timestamp IS NOT NULL
        GROUP BY DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m')
        ORDER BY month DESC
        LIMIT 3
    """)
    revenue_data = cursor.fetchall()
    if revenue_data:
        print(f"   Recent revenue data:")
        for row in revenue_data:
            print(f"   • {row['month']}: {row['orders']} orders, ${row['revenue'] or 0:,.2f}")
    else:
        print("   ❌ No revenue data!")
        print("   Checking if order_purchase_timestamp has data...")
        cursor.execute("SELECT COUNT(*) as count FROM orders WHERE order_purchase_timestamp IS NOT NULL")
        ts_count = cursor.fetchone()['count']
        print(f"   Orders with timestamps: {ts_count:,}")
    
    # Test 7: Check column names
    print("\n7. 📋 COLUMN NAMES CHECK:")
    tables_to_check = ['sellers', 'orders', 'order_items', 'products']
    for table in tables_to_check:
        cursor.execute(f"DESCRIBE {table}")
        columns = [col[0] for col in cursor.fetchall()]
        print(f"   {table}: {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*50)
    print("✅ Debug complete!")

def fix_data_issues():
    """If data is missing, create sample data"""
    print("\n🛠️  Creating sample data if needed...")
    
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    # Check if we have any seller-order relationships
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM sellers s 
        JOIN order_items oi ON s.seller_id = oi.seller_id
    """)
    join_count = cursor.fetchone()['count']
    
    if join_count == 0:
        print("⚠️  No seller-order relationships found!")
        print("Creating sample relationships...")
        
        # Get some sample sellers and orders
        cursor.execute("SELECT seller_id FROM sellers LIMIT 5")
        sellers = [row['seller_id'] for row in cursor.fetchall()]
        
        cursor.execute("SELECT order_id FROM orders LIMIT 10")
        orders = [row['order_id'] for row in cursor.fetchall()]
        
        cursor.execute("SELECT product_id FROM products LIMIT 10")
        products = [row['product_id'] for row in cursor.fetchall()]
        
        if sellers and orders and products:
            # Create sample order_items
            sample_data = []
            for i in range(min(100, len(orders))):
                import random
                sample_data.append((
                    orders[i % len(orders)],
                    random.randint(1, 10),
                    products[i % len(products)],
                    sellers[i % len(sellers)],
                    round(random.uniform(10, 500), 2),
                    round(random.uniform(5, 50), 2)
                ))
            
            # Insert sample order_items
            insert_query = """
                INSERT INTO order_items 
                (order_id, order_item_id, product_id, seller_id, price, freight_value)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE price = VALUES(price)
            """
            
            cursor.executemany(insert_query, sample_data)
            conn.commit()
            print(f"✅ Created {cursor.rowcount} sample order_items records")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    test_all_queries()
    fix_data_issues()