"""
Quick test for seller dashboard MySQL queries
"""
import mysql.connector

# Update these with your credentials
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mysql123',
    'database': 'ecom_master'
}

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=True)
    
    print("✅ Connected to MySQL")
    
    # Test 1: Check sellers table
    cursor.execute("SELECT COUNT(*) as count FROM sellers_dataset")
    sellers_count = cursor.fetchone()
    print(f"📊 Sellers in database: {sellers_count['count']:,}")
    
    # Test 2: Check orders table  
    cursor.execute("SELECT COUNT(*) as count FROM orders_dataset")
    orders_count = cursor.fetchone()
    print(f"📦 Orders in database: {orders_count['count']:,}")
    
    # Test 3: Check products table
    cursor.execute("SELECT COUNT(*) as count FROM products_dataset")
    products_count = cursor.fetchone()
    print(f"🎯 Products in database: {products_count['count']:,}")
    
    # Test 4: Sample seller stats
    cursor.execute("""
        SELECT 
            s.seller_id,
            s.seller_city,
            s.seller_state,
            COUNT(DISTINCT oi.order_id) as order_count,
            SUM(oi.price) as total_revenue
        FROM sellers_dataset s
        LEFT JOIN order_items_dataset oi ON s.seller_id = oi.seller_id
        GROUP BY s.seller_id, s.seller_city, s.seller_state
        ORDER BY total_revenue DESC NULLS LAST
        LIMIT 5
    """)
    
    top_sellers = cursor.fetchall()
    print("\n🏆 Top 5 sellers by revenue:")
    for seller in top_sellers:
        print(f"  {seller['seller_id']}: {seller['seller_city']}, {seller['seller_state']} - "
              f"${seller['total_revenue'] or 0:.2f} ({seller['order_count'] or 0} orders)")
    
    cursor.close()
    conn.close()
    
    print("\n✅ All MySQL queries successful!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()