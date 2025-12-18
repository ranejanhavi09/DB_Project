"""
Flask routes for seller dashboard
"""
from flask import Blueprint, render_template, jsonify, request, session
from datetime import datetime, timedelta
import logging
from services.seller_service import SellerService
from repositories.seller_repository import SellerRepository

logger = logging.getLogger(__name__)

seller_bp = Blueprint('seller', __name__, url_prefix='/seller')

@seller_bp.route('/dashboard')
def dashboard():
    """Render seller dashboard page"""
    seller_id = request.args.get('seller_id', '')
    days = request.args.get('days', 90, type=int)
    
    if not seller_id:
        # Get list of sellers for testing/demo
        sellers = SellerRepository.get_all_sellers(limit=20)
        return render_template('seller_dashboard/select_seller.html', 
                             sellers=sellers)
    
    return render_template('seller_dashboard/dashboard.html', 
                         seller_id=seller_id, 
                         days=days)

@seller_bp.route('/api/dashboard-data')
def get_dashboard_data():
    """API endpoint for comprehensive dashboard data"""
    try:
        seller_id = request.args.get('seller_id', '')
        days = request.args.get('days', 90, type=int)
        
        if not seller_id:
            return jsonify({
                'success': False,
                'error': 'Seller ID is required'
            }), 400
        
        # Get comprehensive dashboard data
        dashboard_data = SellerService.format_dashboard_data(seller_id, days)
        
        # Get additional data for charts
        start_date, end_date = SellerService.get_default_date_range(days)
        
        # Geographic data
        geographic_data = SellerRepository.get_geographic_distribution(
            seller_id, start_date, end_date, 'state'
        )
        
        # Sentiment analysis
        sentiment_analysis = SellerRepository.get_sentiment_analysis(
            seller_id, start_date, end_date
        )
        
        # Top cities
        top_cities = SellerRepository.get_top_customer_cities(
            seller_id, start_date, end_date, 10
        )
        
        # Format chart data
        dashboard_data['review_chart'] = SellerService.format_review_distribution(
            dashboard_data['review_summary']
        )
        
        dashboard_data['sentiment_chart'] = SellerService.format_sentiment_data(
            sentiment_analysis
        )
        
        dashboard_data['geographic_data'] = SellerService.format_geographic_data(
            geographic_data
        )
        
        dashboard_data['top_cities'] = top_cities
        
        # Performance metrics for cards
        dashboard_data['performance_metrics'] = SellerService.calculate_performance_metrics(
            dashboard_data['overview'],
            dashboard_data['delivery_performance'],
            dashboard_data['review_summary']
        )
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
        
    except Exception as e:
        logger.error(f"Error in get_dashboard_data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@seller_bp.route('/api/revenue-trends')
def get_revenue_trends():
    """API endpoint for revenue trends"""
    try:
        seller_id = request.args.get('seller_id', '')
        days = request.args.get('days', 90, type=int)
        granularity = request.args.get('granularity', 'monthly')
        
        if not seller_id:
            return jsonify({
                'success': False,
                'error': 'Seller ID is required'
            }), 400
        
        start_date, end_date = SellerService.get_default_date_range(days)
        
        revenue_data = SellerRepository.get_revenue_trends(
            seller_id, start_date, end_date, granularity
        )
        
        chart_data = SellerService.format_chart_data(
            revenue_data, 'period', 'total_gmv'
        )
        
        return jsonify({
            'success': True,
            'data': {
                'trends': revenue_data,
                'chart': chart_data,
                'granularity': granularity
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_revenue_trends: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@seller_bp.route('/api/product-performance')
def get_product_performance():
    """API endpoint for product performance"""
    try:
        seller_id = request.args.get('seller_id', '')
        days = request.args.get('days', 90, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        if not seller_id:
            return jsonify({
                'success': False,
                'error': 'Seller ID is required'
            }), 400
        
        start_date, end_date = SellerService.get_default_date_range(days)
        
        products = SellerRepository.get_product_performance(
            seller_id, start_date, end_date, limit
        )
        
        return jsonify({
            'success': True,
            'data': products
        })
        
    except Exception as e:
        logger.error(f"Error in get_product_performance: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@seller_bp.route('/api/review-details')
def get_review_details():
    """API endpoint for review details"""
    try:
        seller_id = request.args.get('seller_id', '')
        days = request.args.get('days', 90, type=int)
        min_score = request.args.get('min_score', 1, type=int)
        max_score = request.args.get('max_score', 5, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        if not seller_id:
            return jsonify({
                'success': False,
                'error': 'Seller ID is required'
            }), 400
        
        start_date, end_date = SellerService.get_default_date_range(days)
        
        reviews = SellerRepository.get_review_details(
            seller_id, start_date, end_date, min_score, max_score, limit
        )
        
        return jsonify({
            'success': True,
            'data': reviews
        })
        
    except Exception as e:
        logger.error(f"Error in get_review_details: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@seller_bp.route('/api/competitor-comparison')
def get_competitor_comparison():
    """API endpoint for competitor comparison"""
    try:
        seller_id = request.args.get('seller_id', '')
        days = request.args.get('days', 180, type=int)
        comparison_type = request.args.get('type', 'state')
        
        if not seller_id:
            return jsonify({
                'success': False,
                'error': 'Seller ID is required'
            }), 400
        
        start_date, end_date = SellerService.get_default_date_range(days)
        
        competitors = SellerRepository.get_competitor_comparison(
            seller_id, comparison_type, start_date, end_date
        )
        
        return jsonify({
            'success': True,
            'data': competitors
        })
        
    except Exception as e:
        logger.error(f"Error in get_competitor_comparison: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@seller_bp.route('/api/customer-retention')
def get_customer_retention():
    """API endpoint for customer retention"""
    try:
        seller_id = request.args.get('seller_id', '')
        days = request.args.get('days', 180, type=int)
        
        if not seller_id:
            return jsonify({
                'success': False,
                'error': 'Seller ID is required'
            }), 400
        
        start_date, end_date = SellerService.get_default_date_range(days)
        
        retention = SellerRepository.get_customer_retention(
            seller_id, start_date, end_date
        )
        
        return jsonify({
            'success': True,
            'data': retention
        })
        
    except Exception as e:
        logger.error(f"Error in get_customer_retention: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@seller_bp.route('/api/all-sellers')
def get_all_sellers():
    """API endpoint to get all sellers for testing"""
    try:
        limit = request.args.get('limit', 100, type=int)
        
        sellers = SellerRepository.get_all_sellers(limit)
        
        return jsonify({
            'success': True,
            'data': sellers
        })
        
    except Exception as e:
        logger.error(f"Error in get_all_sellers: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500