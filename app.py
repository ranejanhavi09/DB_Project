"""
Flask API for the recommendation engine
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from recommendation_engine import RecommendationEngine
from database import db
from config import Config

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize recommendation engine
recommendation_engine = RecommendationEngine()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.execute_query("RETURN 1 as test")
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
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

if __name__ == '__main__':
    print(f"Starting Flask server on port {Config.FLASK_PORT}")
    print(f"Neo4j URI: {Config.NEO4J_URI}")
    app.run(host='0.0.0.0', port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG)

