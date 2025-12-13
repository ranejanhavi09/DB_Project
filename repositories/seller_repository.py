"""
Repository for seller-related database operations using stored procedures
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from db.mysql_connection import MySQLConnectionManager

logger = logging.getLogger(__name__)

class SellerRepository:
    
    @staticmethod
    def get_seller_overview(seller_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get seller overview metrics using stored procedure"""
        try:
            connection = MySQLConnectionManager.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.callproc('sp_get_seller_overview', (seller_id, start_date, end_date))
            
            result = None
            for result_set in cursor.stored_results():
                result = result_set.fetchone()
                break
            
            cursor.close()
            connection.close()
            
            return result or {}
            
        except Exception as e:
            logger.error(f"Error in get_seller_overview: {e}")
            raise
    
    @staticmethod
    def get_revenue_trends(seller_id: str, start_date: datetime, end_date: datetime, 
                          granularity: str = 'monthly') -> List[Dict[str, Any]]:
        """Get revenue trends using stored procedure"""
        try:
            connection = MySQLConnectionManager.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.callproc('sp_get_seller_revenue_trends', 
                          (seller_id, start_date, end_date, granularity))
            
            results = []
            for result_set in cursor.stored_results():
                results = result_set.fetchall()
                break
            
            cursor.close()
            connection.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Error in get_revenue_trends: {e}")
            raise
    
    @staticmethod
    def get_product_performance(seller_id: str, start_date: datetime, 
                               end_date: datetime, limit: int = 20) -> List[Dict[str, Any]]:
        """Get product performance using stored procedure"""
        try:
            connection = MySQLConnectionManager.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.callproc('sp_get_seller_product_performance', 
                          (seller_id, start_date, end_date, limit))
            
            results = []
            for result_set in cursor.stored_results():
                results = result_set.fetchall()
                break
            
            cursor.close()
            connection.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Error in get_product_performance: {e}")
            raise
    
    @staticmethod
    def get_category_performance(seller_id: str, start_date: datetime, 
                                end_date: datetime) -> List[Dict[str, Any]]:
        """Get category performance using stored procedure"""
        try:
            connection = MySQLConnectionManager.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.callproc('sp_get_seller_category_performance', 
                          (seller_id, start_date, end_date))
            
            results = []
            for result_set in cursor.stored_results():
                results = result_set.fetchall()
                break
            
            cursor.close()
            connection.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Error in get_category_performance: {e}")
            raise
    
    @staticmethod
    def get_delivery_performance(seller_id: str, start_date: datetime, 
                                end_date: datetime) -> Dict[str, Any]:
        """Get delivery performance using stored procedure"""
        try:
            connection = MySQLConnectionManager.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.callproc('sp_get_seller_delivery_performance', 
                          (seller_id, start_date, end_date))
            
            result = None
            for result_set in cursor.stored_results():
                result = result_set.fetchone()
                break
            
            cursor.close()
            connection.close()
            
            return result or {}
            
        except Exception as e:
            logger.error(f"Error in get_delivery_performance: {e}")
            raise
    
    @staticmethod
    def get_geographic_distribution(seller_id: str, start_date: datetime, 
                                   end_date: datetime, group_by: str = 'state') -> List[Dict[str, Any]]:
        """Get geographic distribution using stored procedure"""
        try:
            connection = MySQLConnectionManager.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.callproc('sp_get_seller_geographic_distribution', 
                          (seller_id, start_date, end_date, group_by))
            
            results = []
            for result_set in cursor.stored_results():
                results = result_set.fetchall()
                break
            
            cursor.close()
            connection.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Error in get_geographic_distribution: {e}")
            raise
    
    @staticmethod
    def get_review_summary(seller_id: str, start_date: datetime, 
                          end_date: datetime) -> Dict[str, Any]:
        """Get review summary using stored procedure"""
        try:
            connection = MySQLConnectionManager.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.callproc('sp_get_seller_review_summary', 
                          (seller_id, start_date, end_date))
            
            result = None
            for result_set in cursor.stored_results():
                result = result_set.fetchone()
                break
            
            cursor.close()
            connection.close()
            
            return result or {}
            
        except Exception as e:
            logger.error(f"Error in get_review_summary: {e}")
            raise
    
    @staticmethod
    def get_review_details(seller_id: str, start_date: datetime, end_date: datetime, 
                          min_score: int = 1, max_score: int = 5, limit: int = 50) -> List[Dict[str, Any]]:
        """Get review details using stored procedure"""
        try:
            connection = MySQLConnectionManager.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.callproc('sp_get_seller_review_details', 
                          (seller_id, start_date, end_date, min_score, max_score, limit))
            
            results = []
            for result_set in cursor.stored_results():
                results = result_set.fetchall()
                break
            
            cursor.close()
            connection.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Error in get_review_details: {e}")
            raise
    
    @staticmethod
    def get_competitor_comparison(seller_id: str, comparison_type: str, 
                                 start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get competitor comparison using stored procedure"""
        try:
            connection = MySQLConnectionManager.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.callproc('sp_get_seller_competitor_comparison', 
                          (seller_id, comparison_type, start_date, end_date))
            
            results = []
            for result_set in cursor.stored_results():
                results = result_set.fetchall()
                break
            
            cursor.close()
            connection.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Error in get_competitor_comparison: {e}")
            raise
    
    @staticmethod
    def get_customer_retention(seller_id: str, start_date: datetime, 
                              end_date: datetime) -> Dict[str, Any]:
        """Get customer retention using stored procedure"""
        try:
            connection = MySQLConnectionManager.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.callproc('sp_get_seller_customer_retention', 
                          (seller_id, start_date, end_date))
            
            result = None
            for result_set in cursor.stored_results():
                result = result_set.fetchone()
                break
            
            cursor.close()
            connection.close()
            
            return result or {}
            
        except Exception as e:
            logger.error(f"Error in get_customer_retention: {e}")
            raise
    
    @staticmethod
    def get_recent_orders(seller_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent orders using stored procedure"""
        try:
            connection = MySQLConnectionManager.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.callproc('sp_get_seller_recent_orders', (seller_id, limit))
            
            results = []
            for result_set in cursor.stored_results():
                results = result_set.fetchall()
                break
            
            cursor.close()
            connection.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Error in get_recent_orders: {e}")
            raise
    
    @staticmethod
    def get_payment_analysis(seller_id: str, start_date: datetime, 
                            end_date: datetime) -> List[Dict[str, Any]]:
        """Get payment analysis using stored procedure"""
        try:
            connection = MySQLConnectionManager.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.callproc('sp_get_seller_payment_analysis', 
                          (seller_id, start_date, end_date))
            
            results = []
            for result_set in cursor.stored_results():
                results = result_set.fetchall()
                break
            
            cursor.close()
            connection.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Error in get_payment_analysis: {e}")
            raise
    
    @staticmethod
    def get_sentiment_analysis(seller_id: str, start_date: datetime, 
                              end_date: datetime) -> List[Dict[str, Any]]:
        """Get sentiment analysis using stored procedure"""
        try:
            connection = MySQLConnectionManager.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.callproc('sp_get_seller_sentiment_analysis', 
                          (seller_id, start_date, end_date))
            
            results = []
            for result_set in cursor.stored_results():
                results = result_set.fetchall()
                break
            
            cursor.close()
            connection.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Error in get_sentiment_analysis: {e}")
            raise
    
    @staticmethod
    def get_top_customer_cities(seller_id: str, start_date: datetime, 
                               end_date: datetime, limit: int = 20) -> List[Dict[str, Any]]:
        """Get top customer cities using stored procedure"""
        try:
            connection = MySQLConnectionManager.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.callproc('sp_get_seller_top_customer_cities', 
                          (seller_id, start_date, end_date, limit))
            
            results = []
            for result_set in cursor.stored_results():
                results = result_set.fetchall()
                break
            
            cursor.close()
            connection.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Error in get_top_customer_cities: {e}")
            raise
    
    @staticmethod
    def get_performance_score(seller_id: str, start_date: datetime, 
                             end_date: datetime) -> Dict[str, Any]:
        """Get performance score using stored procedure"""
        try:
            connection = MySQLConnectionManager.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.callproc('sp_get_seller_performance_score', 
                          (seller_id, start_date, end_date))
            
            result = None
            for result_set in cursor.stored_results():
                result = result_set.fetchone()
                break
            
            cursor.close()
            connection.close()
            
            return result or {}
            
        except Exception as e:
            logger.error(f"Error in get_performance_score: {e}")
            raise
    
    @staticmethod
    def get_all_sellers(limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of all sellers for testing"""
        try:
            query = """
            SELECT seller_id, seller_city, seller_state 
            FROM sellers 
            WHERE seller_id IN (
                SELECT DISTINCT seller_id 
                FROM order_items 
                GROUP BY seller_id 
                HAVING COUNT(*) > 10
            )
            LIMIT %s
            """
            
            result = MySQLConnectionManager.execute_query(query, (limit,))
            return result
            
        except Exception as e:
            logger.error(f"Error in get_all_sellers: {e}")
            raise