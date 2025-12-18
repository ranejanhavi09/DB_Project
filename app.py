"""
Flask API for the recommendation engine
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from recommendation_engine import RecommendationEngine
from database import db
from config import Config

#ap - sql database addition: Import MySQL connection and seller dashboard components
import logging
from db.mysql_connection import MySQLConnectionManager
from routes.seller_routes import seller_bp

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize recommendation engine
recommendation_engine = RecommendationEngine()

#ap - sql database addition: Configure logging for seller dashboard
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

#ap - sql database addition: Initialize MySQL connection pool for seller dashboard
try:
    MySQLConnectionManager.initialize_pool()
    print("✅ Seller Dashboard: MySQL connection pool initialized successfully")
except Exception as e:
    print(f"❌ Seller Dashboard: Failed to initialize MySQL connection pool: {e}")

#ap - sql database addition: Register seller dashboard blueprint
app.register_blueprint(seller_bp)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.execute_query("RETURN 1 as test")
        
        #ap - sql database addition: Add MySQL health check
        mysql_status = "unknown"
        try:
            from db.mysql_connection import MySQLConnectionManager
            if MySQLConnectionManager.test_connection():
                mysql_status = "connected"
            else:
                mysql_status = "disconnected"
        except Exception as mysql_e:
            mysql_status = f"error: {str(mysql_e)}"
        
        return jsonify({
            'status': 'healthy',
            'neo4j': 'connected',
            'mysql': mysql_status,  #ap - sql database addition
            'services': {
                'recommendation_engine': 'active',
                'seller_dashboard': 'active'  #ap - sql database addition
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500

#ap - sql database addition: New health endpoint specifically for seller dashboard
@app.route('/api/health/seller-dashboard', methods=['GET'])
def health_check_seller_dashboard():
    """Health check for seller dashboard MySQL database"""
    try:
        from db.mysql_connection import MySQLConnectionManager
        if MySQLConnectionManager.test_connection():
            return jsonify({
                'status': 'healthy',
                'service': 'seller_dashboard',
                'database': 'mysql',
                'connection': 'connected'
            }), 200
        else:
            return jsonify({
                'status': 'unhealthy',
                'service': 'seller_dashboard',
                'database': 'mysql',
                'connection': 'disconnected'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'service': 'seller_dashboard',
            'database': 'mysql',
            'error': str(e)
        }), 500

@app.route('/api/customers', methods=['GET'])
def get_customers():
    """Get list of customers"""
    try:
        query = """
        MATCH (c:Customer)
        RETURN c.customer_unique_id as customer_unique_id,
               c.customer_city as city,
               c.customer_state as state,
               c.total_orders as total_orders
        ORDER BY c.total_orders DESC
        LIMIT 100
        """
        customers = db.execute_query(query)
        return jsonify({
            'success': True,
            'customers': customers,
            'count': len(customers)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/customers/<customer_unique_id>', methods=['GET'])
def get_customer_info(customer_unique_id):
    """Get customer information"""
    try:
        customer_info = recommendation_engine.get_customer_info(customer_unique_id)
        if customer_info:
            return jsonify({
                'success': True,
                'customer': customer_info
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Customer not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/customers/<customer_unique_id>/recommendations', methods=['GET'])
def get_recommendations(customer_unique_id):
    """Get recommendations for a customer"""
    try:
        algorithm = request.args.get('algorithm', 'hybrid')
        limit = int(request.args.get('limit', Config.MAX_RECOMMENDATIONS))
        
        if algorithm == 'collaborative':
            recommendations = recommendation_engine.collaborative_filtering(customer_unique_id, limit)
        elif algorithm == 'content':
            recommendations = recommendation_engine.content_based_filtering(customer_unique_id, limit)
        elif algorithm == 'sentiment':
            recommendations = recommendation_engine.sentiment_based_filtering(customer_unique_id, limit)
        elif algorithm == 'seller':
            recommendations = recommendation_engine.seller_based_filtering(customer_unique_id, limit)
        else:  # hybrid (default)
            recommendations = recommendation_engine.hybrid_recommendations(customer_unique_id, limit)
        
        return jsonify({
            'success': True,
            'algorithm': algorithm,
            'customer_id': customer_unique_id,
            'recommendations': recommendations,
            'count': len(recommendations)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/products/<product_id>', methods=['GET'])
def get_product_details(product_id):
    """Get product details"""
    try:
        product = recommendation_engine.get_product_details(product_id)
        if product:
            return jsonify({
                'success': True,
                'product': product
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get list of product categories"""
    try:
        query = """
        MATCH (cat:ProductCategory)
        RETURN cat.product_category_name_english as category_name,
               cat.product_category_name_portuguese as category_name_pt,
               cat.total_products as total_products
        ORDER BY cat.total_products DESC
        """
        categories = db.execute_query(query)
        return jsonify({
            'success': True,
            'categories': categories,
            'count': len(categories)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        query = """
        MATCH (c:Customer)
        WITH COUNT(c) as customer_count
        MATCH (o:Order)
        WITH customer_count, COUNT(o) as order_count
        MATCH (p:Product)
        WITH customer_count, order_count, COUNT(p) as product_count
        MATCH (s:Seller)
        WITH customer_count, order_count, product_count, COUNT(s) as seller_count
        MATCH (r:Review)
        WITH customer_count, order_count, product_count, seller_count, COUNT(r) as review_count
        MATCH (cat:ProductCategory)
        RETURN customer_count, order_count, product_count, seller_count, review_count, COUNT(cat) as category_count
        """
        stats = db.execute_query(query)
        return jsonify({
            'success': True,
            'stats': stats[0] if stats else {}
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

#ap - sql database addition: New endpoint to get seller stats from MySQL
@app.route('/api/seller-stats', methods=['GET'])
def get_seller_stats():
    """Get seller dashboard statistics from MySQL"""
    try:
        from repositories.seller_repository import SellerRepository
        
        # Get sample seller for demo
        sellers = SellerRepository.get_all_sellers(limit=1)
        if sellers:
            seller_id = sellers[0]['seller_id']
            from datetime import datetime, timedelta
            start_date = datetime.now() - timedelta(days=90)
            end_date = datetime.now()
            
            overview = SellerRepository.get_seller_overview(seller_id, start_date, end_date)
            
            return jsonify({
                'success': True,
                'sample_seller_id': seller_id,
                'overview': overview,
                'note': 'This is sample data from MySQL seller dashboard'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No sellers found in MySQL database'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'note': 'Make sure seller dashboard components are properly configured'
        }), 500

#ap - sql database addition: New endpoint to test MySQL connection
@app.route('/api/test-mysql', methods=['GET'])
def test_mysql():
    """Test MySQL connection and show basic info"""
    try:
        from db.mysql_connection import MySQLConnectionManager
        
        connection = MySQLConnectionManager.get_connection()
        if connection.is_connected():
            db_info = connection.get_server_info()
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()[0]
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            cursor.close()
            connection.close()
            
            return jsonify({
                'success': True,
                'mysql_status': 'connected',
                'server_version': db_info,
                'database': db_name,
                'tables_count': len(tables),
                'tables': tables[:10]  # Show first 10 tables
            }), 200
        else:
            return jsonify({
                'success': False,
                'mysql_status': 'disconnected'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'mysql_status': 'error',
            'error': str(e)
        }), 500

#ap - sql database addition: Homepage with links to both services
@app.route('/')
def home():
    """Homepage with links to both services"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>E-Commerce Analytics Platform</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .header { background: #4a6fa5; color: white; padding: 20px; border-radius: 10px; }
            .service-card { 
                border: 1px solid #ddd; 
                border-radius: 8px; 
                padding: 20px; 
                margin: 20px 0; 
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .service-card h3 { margin-top: 0; color: #333; }
            .btn { 
                display: inline-block; 
                padding: 10px 20px; 
                background: #4a6fa5; 
                color: white; 
                text-decoration: none; 
                border-radius: 5px; 
                margin: 5px;
            }
            .btn:hover { background: #3a5a85; }
            .btn-mysql { background: #28a745; }
            .btn-mysql:hover { background: #218838; }
            .btn-neo4j { background: #6f42c1; }
            .btn-neo4j:hover { background: #5a32a3; }
            .status { padding: 5px 10px; border-radius: 3px; font-size: 0.9em; }
            .status-healthy { background: #d4edda; color: #155724; }
            .status-unhealthy { background: #f8d7da; color: #721c24; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 E-Commerce Analytics Platform</h1>
                <p>Unified platform for recommendations and seller analytics</p>
            </div>
            
            <div class="service-card">
                <h3>📊 Seller Dashboard (MySQL)</h3>
                <p>Advanced analytics for sellers with interactive visualizations</p>
                <a href="/seller/dashboard" class="btn btn-mysql">Go to Seller Dashboard</a>
                <a href="/api/health/seller-dashboard" class="btn">Check MySQL Health</a>
                <a href="/api/test-mysql" class="btn">Test MySQL Connection</a>
            </div>
            
            <div class="service-card">
                <h3>🎯 Recommendation Engine (Neo4j)</h3>
                <p>Personalized product recommendations using graph algorithms</p>
                <a href="/api/health" class="btn">Check System Health</a>
                <a href="/api/customers" class="btn">View Customers</a>
                <a href="/api/categories" class="btn">View Categories</a>
                <a href="/api/stats" class="btn">View Stats</a>
            </div>
            
            <div class="service-card">
                <h3>🔧 API Endpoints</h3>
                <p><strong>Recommendation Engine:</strong></p>
                <ul>
                    <li><code>/api/customers</code> - List customers</li>
                    <li><code>/api/customers/{id}/recommendations</code> - Get recommendations</li>
                    <li><code>/api/products/{id}</code> - Get product details</li>
                </ul>
                <p><strong>Seller Dashboard:</strong></p>
                <ul>
                    <li><code>/seller/dashboard</code> - Main dashboard UI</li>
                    <li><code>/seller/api/dashboard-data</code> - Dashboard data API</li>
                    <li><code>/seller/api/revenue-trends</code> - Revenue trends API</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print(f"Starting Flask server on port {Config.FLASK_PORT}")
    print(f"Neo4j URI: {Config.NEO4J_URI}")
    print(f"MySQL Database: {Config().mysql_config['database'] if hasattr(Config(), 'mysql_config') else 'Not configured'}")
    print(f"Seller Dashboard: http://localhost:{Config.FLASK_PORT}/seller/dashboard")
    print(f"Homepage: http://localhost:{Config.FLASK_PORT}/")
    app.run(host='0.0.0.0', port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG)