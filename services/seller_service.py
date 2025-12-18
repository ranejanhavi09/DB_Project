"""
Service layer for seller dashboard business logic
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from repositories.seller_repository import SellerRepository

logger = logging.getLogger(__name__)

class SellerService:
    
    @staticmethod
    def get_default_date_range(days: int = 90) -> tuple:
        """Get default date range for queries"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return start_date, end_date
    
    @staticmethod
    def format_dashboard_data(seller_id: str, days: int = 90) -> Dict[str, Any]:
        """Format comprehensive dashboard data"""
        try:
            start_date, end_date = SellerService.get_default_date_range(days)
            
            # Fetch all data in parallel (you could use threading for performance)
            overview = SellerRepository.get_seller_overview(seller_id, start_date, end_date)
            revenue_trends = SellerRepository.get_revenue_trends(seller_id, start_date, end_date, 'monthly')
            product_performance = SellerRepository.get_product_performance(seller_id, start_date, end_date, 10)
            category_performance = SellerRepository.get_category_performance(seller_id, start_date, end_date)
            delivery_performance = SellerRepository.get_delivery_performance(seller_id, start_date, end_date)
            review_summary = SellerRepository.get_review_summary(seller_id, start_date, end_date)
            recent_orders = SellerRepository.get_recent_orders(seller_id, 10)
            performance_score = SellerRepository.get_performance_score(seller_id, start_date, end_date)
            
            # Format data for frontend
            return {
                'seller_id': seller_id,
                'date_range': {
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'days': days
                },
                'overview': overview,
                'revenue_trends': {
                    'monthly': revenue_trends,
                    'chart_data': SellerService.format_chart_data(revenue_trends, 'period', 'total_gmv')
                },
                'product_performance': product_performance,
                'category_performance': category_performance,
                'delivery_performance': delivery_performance,
                'review_summary': review_summary,
                'recent_orders': recent_orders,
                'performance_score': performance_score,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in format_dashboard_data: {e}")
            raise
    
    @staticmethod
    def format_chart_data(data: List[Dict], label_key: str, value_key: str) -> Dict[str, Any]:
        """Format data for Chart.js visualization"""
        if not data:
            return {'labels': [], 'datasets': []}
        
        labels = [item.get(label_key, '') for item in data]
        values = [float(item.get(value_key, 0)) for item in data]
        
        # Color coding based on values
        colors = []
        if values:
            max_val = max(values)
            for val in values:
                if val >= max_val * 0.8:
                    colors.append('rgba(75, 192, 192, 0.7)')  # Green for high values
                elif val >= max_val * 0.5:
                    colors.append('rgba(255, 206, 86, 0.7)')   # Yellow for medium values
                else:
                    colors.append('rgba(255, 99, 132, 0.7)')   # Red for low values
        
        return {
            'labels': labels,
            'datasets': [{
                'label': value_key.replace('_', ' ').title(),
                'data': values,
                'backgroundColor': colors,
                'borderColor': 'rgba(75, 192, 192, 1)',
                'borderWidth': 2,
                'fill': True
            }]
        }
    
    @staticmethod
    def format_review_distribution(review_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Format review distribution data for pie chart"""
        if not review_summary:
            return {'labels': [], 'datasets': []}
        
        labels = ['5 Stars', '4 Stars', '3 Stars', '2 Stars', '1 Star']
        values = [
            review_summary.get('five_star', 0),
            review_summary.get('four_star', 0),
            review_summary.get('three_star', 0),
            review_summary.get('two_star', 0),
            review_summary.get('one_star', 0)
        ]
        
        colors = [
            'rgba(75, 192, 192, 0.7)',   # 5 stars - Green
            'rgba(54, 162, 235, 0.7)',   # 4 stars - Blue
            'rgba(255, 206, 86, 0.7)',   # 3 stars - Yellow
            'rgba(255, 159, 64, 0.7)',   # 2 stars - Orange
            'rgba(255, 99, 132, 0.7)'    # 1 star - Red
        ]
        
        return {
            'labels': labels,
            'datasets': [{
                'data': values,
                'backgroundColor': colors,
                'borderColor': ['rgba(75, 192, 192, 1)', 'rgba(54, 162, 235, 1)', 
                               'rgba(255, 206, 86, 1)', 'rgba(255, 159, 64, 1)', 
                               'rgba(255, 99, 132, 1)'],
                'borderWidth': 1
            }]
        }
    
    @staticmethod
    def format_sentiment_data(sentiment_analysis: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format sentiment analysis data for chart"""
        if not sentiment_analysis:
            return {'labels': [], 'datasets': []}
        
        labels = [item.get('predicted_sentiment', '').title() for item in sentiment_analysis]
        values = [item.get('review_count', 0) for item in sentiment_analysis]
        
        sentiment_colors = {
            'Positive': 'rgba(75, 192, 192, 0.7)',
            'Negative': 'rgba(255, 99, 132, 0.7)',
            'Neutral': 'rgba(255, 206, 86, 0.7)'
        }
        
        colors = [sentiment_colors.get(label, 'rgba(201, 203, 207, 0.7)') for label in labels]
        
        return {
            'labels': labels,
            'datasets': [{
                'label': 'Sentiment Distribution',
                'data': values,
                'backgroundColor': colors,
                'borderColor': [color.replace('0.7', '1') for color in colors],
                'borderWidth': 2
            }]
        }
    
    @staticmethod
    def format_geographic_data(geographic_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format geographic data for map visualization"""
        if not geographic_data:
            return {'locations': [], 'values': []}
        
        locations = []
        values = []
        
        for item in geographic_data:
            location = item.get('location', 'Unknown')
            value = float(item.get('total_revenue', 0))
            if value > 0:  # Only include locations with revenue
                locations.append(location)
                values.append(value)
        
        return {
            'locations': locations,
            'values': values,
            'max_value': max(values) if values else 0,
            'min_value': min(values) if values else 0
        }
    
    @staticmethod
    def calculate_performance_metrics(overview: Dict[str, Any], 
                                    delivery_performance: Dict[str, Any],
                                    review_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate performance metrics for dashboard cards"""
        metrics = []
        
        # Revenue metric
        if 'total_revenue' in overview:
            metrics.append({
                'title': 'Total Revenue',
                'value': f"R$ {overview.get('total_revenue', 0):,.2f}",
                'icon': 'currency-brl',
                'color': 'success',
                'trend': 'up' if overview.get('total_revenue', 0) > 0 else 'down',
                'subtitle': 'Last 90 days'
            })
        
        # Order count metric
        if 'total_orders' in overview:
            metrics.append({
                'title': 'Total Orders',
                'value': f"{overview.get('total_orders', 0):,}",
                'icon': 'cart-check',
                'color': 'primary',
                'trend': 'up' if overview.get('total_orders', 0) > 0 else 'down',
                'subtitle': f"{overview.get('unique_customers', 0):,} unique customers"
            })
        
        # Average rating metric
        if 'avg_review_score' in overview:
            rating = overview.get('avg_review_score', 0)
            metrics.append({
                'title': 'Average Rating',
                'value': f"{rating:.1f}/5.0",
                'icon': 'star',
                'color': 'warning' if rating >= 4 else 'danger' if rating < 3 else 'info',
                'trend': 'stable',
                'subtitle': f"{overview.get('positive_review_pct', 0):.1f}% positive"
            })
        
        # On-time delivery metric
        if 'on_time_rate_pct' in delivery_performance:
            on_time_rate = delivery_performance.get('on_time_rate_pct', 0)
            metrics.append({
                'title': 'On-Time Delivery',
                'value': f"{on_time_rate:.1f}%",
                'icon': 'truck-delivery',
                'color': 'success' if on_time_rate >= 95 else 'warning' if on_time_rate >= 90 else 'danger',
                'trend': 'up' if on_time_rate >= 95 else 'down',
                'subtitle': f"{delivery_performance.get('avg_delivery_days', 0):.1f} avg days"
            })
        
        # Product diversity metric
        if 'categories_offered' in overview:
            metrics.append({
                'title': 'Product Categories',
                'value': f"{overview.get('categories_offered', 0)}",
                'icon': 'tag',
                'color': 'info',
                'trend': 'up' if overview.get('categories_offered', 0) > 5 else 'stable',
                'subtitle': f"{overview.get('unique_products_sold', 0)} unique products"
            })
        
        # Geographic reach metric
        if 'states_served' in overview:
            metrics.append({
                'title': 'Geographic Reach',
                'value': f"{overview.get('states_served', 0)} states",
                'icon': 'map',
                'color': 'secondary',
                'trend': 'up' if overview.get('states_served', 0) > 5 else 'stable',
                'subtitle': f"{overview.get('cities_served', 0)} cities"
            })
        
        return metrics