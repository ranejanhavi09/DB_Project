"""
Seller Dashboard with Correct Table Names
"""
from flask import Flask, jsonify, render_template_string
import mysql.connector
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# MySQL Configuration - UPDATE WITH YOUR CREDENTIALS
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mysql123',  # CHANGE THIS
    'database': 'ecom_master',
    'port': 3306
}

def get_mysql_connection():
    """Get MySQL connection"""
    return mysql.connector.connect(**MYSQL_CONFIG)

@app.route('/')
def home():
    """Homepage for seller dashboard"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Seller Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: #28a745; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .card { 
                border: 1px solid #ddd; 
                border-radius: 8px; 
                padding: 20px; 
                margin: 10px; 
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                display: inline-block;
                width: 30%;
                vertical-align: top;
            }
            .btn { 
                display: inline-block; 
                padding: 10px 20px; 
                background: #28a745; 
                color: white; 
                text-decoration: none; 
                border-radius: 5px; 
                margin: 5px;
            }
            .btn:hover { background: #218838; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background: #f2f2f2; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Seller Dashboard</h1>
                <p>MySQL-based analytics platform for sellers</p>
                <p><strong>Database:</strong> ecom_master | <strong>Tables found:</strong> 9</p>
            </div>
            
            <div class="card">
                <h3>📈 Seller Statistics</h3>
                <p>Get overview of seller performance</p>
                <a href="/api/sellers" class="btn">View Sellers</a>
                <a href="/api/top-sellers" class="btn">Top Sellers</a>
            </div>
            
            <div class="card">
                <h3>📊 Orders Analysis</h3>
                <p>Orders statistics and trends</p>
                <a href="/api/orders-summary" class="btn">Orders Summary</a>
                <a href="/api/revenue-trends" class="btn">Revenue Trends</a>
            </div>
            
            <div class="card">
                <h3>📦 Products & Customers</h3>
                <p>Products and customer analytics</p>
                <a href="/api/products-summary" class="btn">Products Summary</a>
                <a href="/api/customer-stats" class="btn">Customer Stats</a>
            </div>
            
            <div style="margin-top: 30px;">
                <h3>Database Tables:</h3>
                <ul>
                    <li><code>sellers</code> - Seller information</li>
                    <li><code>orders</code> - Order information</li>
                    <li><code>customers</code> - Customer information</li>
                    <li><code>products</code> - Product information</li>
                    <li><code>order_items</code> - Order items (connects orders, products, sellers)</li>
                    <li><code>order_payments</code> - Payment information</li>
                    <li><code>order_reviews</code> - Customer reviews</li>
                    <li><code>product_category</code> - Product categories</li>
                    <li><code>geolocation</code> - Geographic data</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/api/health')
def health():
    """Health check endpoint"""
    try:
        conn = get_mysql_connection()
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return jsonify({
                'status': 'healthy',
                'database': 'mysql',
                'connection': 'connected',
                'timestamp': datetime.now().isoformat()
            }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'mysql',
            'connection': 'disconnected',
            'error': str(e)
        }), 500

@app.route('/api/db-info')
def db_info():
    """Get database information"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()[0]
        
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        # Get row counts for main tables
        row_counts = {}
        for table in ['sellers', 'orders', 'customers', 'products']:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_counts[table] = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'database': db_name,
            'mysql_version': version,
            'tables_count': len(tables),
            'tables': tables,
            'row_counts': row_counts
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/sellers')
def get_sellers():
    """Get all sellers"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                seller_id,
                seller_city,
                seller_state,
                seller_zip_code_prefix
            FROM sellers
            ORDER BY seller_id
            LIMIT 100
        """)
        
        sellers = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            'count': len(sellers),
            'sellers': sellers
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/top-sellers')
def top_sellers():
    """Get top sellers by order count"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                s.seller_id,
                s.seller_city,
                s.seller_state,
                COUNT(DISTINCT oi.order_id) as order_count,
                SUM(oi.price) as total_revenue,
                AVG(oi.price) as avg_order_value
            FROM sellers s
            JOIN order_items oi ON s.seller_id = oi.seller_id
            GROUP BY s.seller_id, s.seller_city, s.seller_state
            ORDER BY total_revenue DESC
            LIMIT 10
        """)
        
        top_sellers = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            'top_sellers': top_sellers
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/orders-summary')
def orders_summary():
    """Get orders summary"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Total orders
        cursor.execute("SELECT COUNT(*) as total_orders FROM orders")
        total_orders = cursor.fetchone()
        
        # Orders by status
        cursor.execute("""
            SELECT 
                order_status,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders), 2) as percentage
            FROM orders
            GROUP BY order_status
            ORDER BY count DESC
        """)
        by_status = cursor.fetchall()
        
        # Monthly orders
        cursor.execute("""
            SELECT 
                DATE_FORMAT(order_purchase_timestamp, '%Y-%m') as month,
                COUNT(*) as order_count
            FROM orders
            WHERE order_purchase_timestamp IS NOT NULL
            GROUP BY DATE_FORMAT(order_purchase_timestamp, '%Y-%m')
            ORDER BY month DESC
            LIMIT 6
        """)
        monthly = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'total_orders': total_orders['total_orders'],
            'by_status': by_status,
            'monthly_trend': monthly
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/products-summary')
def products_summary():
    """Get products summary"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Total products
        cursor.execute("SELECT COUNT(*) as total_products FROM products")
        total = cursor.fetchone()
        
        # Products by category
        cursor.execute("""
            SELECT 
                product_category_name,
                COUNT(*) as product_count
            FROM products
            WHERE product_category_name IS NOT NULL
            GROUP BY product_category_name
            ORDER BY product_count DESC
            LIMIT 10
        """)
        by_category = cursor.fetchall()
        
        # Price distribution
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN price <= 10 THEN '0-10'
                    WHEN price <= 50 THEN '11-50'
                    WHEN price <= 100 THEN '51-100'
                    WHEN price <= 200 THEN '101-200'
                    ELSE '200+'
                END as price_range,
                COUNT(*) as product_count
            FROM (
                SELECT p.product_id, oi.price
                FROM products p
                JOIN order_items oi ON p.product_id = oi.product_id
                WHERE oi.price IS NOT NULL
                GROUP BY p.product_id, oi.price
            ) as product_prices
            GROUP BY price_range
            ORDER BY MIN(price)
        """)
        price_ranges = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'total_products': total['total_products'],
            'top_categories': by_category,
            'price_distribution': price_ranges
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/revenue-trends')
def revenue_trends():
    """Get revenue trends"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') as month,
                COUNT(DISTINCT o.order_id) as order_count,
                SUM(oi.price) as total_revenue,
                AVG(oi.price) as avg_order_value
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.order_purchase_timestamp IS NOT NULL
            GROUP BY DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m')
            ORDER BY month DESC
            LIMIT 12
        """)
        
        trends = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'revenue_trends': trends
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/customer-stats')
def customer_stats():
    """Get customer statistics"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Total customers
        cursor.execute("SELECT COUNT(DISTINCT customer_unique_id) as total_customers FROM customers")
        total = cursor.fetchone()
        
        # Customers by state
        cursor.execute("""
            SELECT 
                customer_state,
                COUNT(*) as customer_count
            FROM customers
            GROUP BY customer_state
            ORDER BY customer_count DESC
            LIMIT 10
        """)
        by_state = cursor.fetchall()
        
        # Repeat customers
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN order_count = 1 THEN 'One-time'
                    WHEN order_count = 2 THEN 'Repeat (2)'
                    WHEN order_count BETWEEN 3 AND 5 THEN 'Repeat (3-5)'
                    ELSE 'Frequent (5+)'
                END as customer_type,
                COUNT(*) as count
            FROM (
                SELECT 
                    c.customer_unique_id,
                    COUNT(DISTINCT o.order_id) as order_count
                FROM customers c
                JOIN orders o ON c.customer_id = o.customer_id
                GROUP BY c.customer_unique_id
            ) as customer_orders
            GROUP BY customer_type
        """)
        customer_types = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'total_customers': total['total_customers'],
            'customers_by_state': by_state,
            'customer_types': customer_types
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/seller-stats/<seller_id>')
def seller_stats(seller_id):
    """Get detailed stats for a specific seller"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Seller basic info
        cursor.execute("""
            SELECT * FROM sellers 
            WHERE seller_id = %s
        """, (seller_id,))
        seller_info = cursor.fetchone()
        
        if not seller_info:
            return jsonify({'error': 'Seller not found'}), 404
        
        # Sales summary
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT oi.order_id) as total_orders,
                SUM(oi.price) as total_revenue,
                AVG(oi.price) as avg_order_value,
                COUNT(DISTINCT oi.product_id) as unique_products_sold
            FROM order_items oi
            WHERE oi.seller_id = %s
        """, (seller_id,))
        sales_summary = cursor.fetchone()
        
        # Monthly performance
        cursor.execute("""
            SELECT 
                DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') as month,
                COUNT(DISTINCT oi.order_id) as order_count,
                SUM(oi.price) as monthly_revenue
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE oi.seller_id = %s
            AND o.order_purchase_timestamp IS NOT NULL
            GROUP BY DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m')
            ORDER BY month DESC
            LIMIT 6
        """, (seller_id,))
        monthly_performance = cursor.fetchall()
        
        # Top products
        cursor.execute("""
            SELECT 
                p.product_id,
                p.product_category_name,
                COUNT(*) as units_sold,
                SUM(oi.price) as revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.seller_id = %s
            GROUP BY p.product_id, p.product_category_name
            ORDER BY revenue DESC
            LIMIT 10
        """, (seller_id,))
        top_products = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'seller_info': seller_info,
            'sales_summary': sales_summary,
            'monthly_performance': monthly_performance,
            'top_products': top_products
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/sample-seller')
def sample_seller():
    """Get a sample seller ID for testing"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT seller_id FROM sellers LIMIT 1")
        seller = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if seller:
            return jsonify({
                'sample_seller_id': seller['seller_id'],
                'test_url': f"/api/seller-stats/{seller['seller_id']}"
            }), 200
        else:
            return jsonify({'error': 'No sellers found'}), 404
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    PORT = 5001
    print("🚀 Starting Seller Dashboard (MySQL Only)")
    print("📊 No Neo4j dependencies")
    print(f"🔗 MySQL Database: {MYSQL_CONFIG['database']}")
    print(f"📋 Tables: sellers, orders, customers, products, order_items, etc.")
    print(f"🌐 Server: http://localhost:{PORT}")
    print("📋 API Endpoints:")
    print("   /api/health - Health check")
    print("   /api/sellers - List all sellers")
    print("   /api/top-sellers - Top 10 sellers")
    print("   /api/orders-summary - Orders statistics")
    print("   /api/seller-stats/<seller_id> - Detailed seller stats")
    print("   /api/sample-seller - Get a sample seller ID")
    app.run(host='0.0.0.0', port=PORT, debug=True)