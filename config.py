"""
Configuration file for the recommendation engine
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Neo4j Configuration
    NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')

     # MySQL Configuration for Seller Dashboard
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'mysql123')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'ecom_master')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_POOL_SIZE = int(os.getenv('MYSQL_POOL_SIZE', 5))
    MYSQL_POOL_NAME = os.getenv('MYSQL_POOL_NAME', 'seller_dashboard_pool')
    
    # Flask Configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5001))
    
    # Dataset Paths
    DATASETS_PATH = os.getenv('DATASETS_PATH', './Datasets')
    
    # Recommendation Settings
    MAX_RECOMMENDATIONS = 20
    MIN_REVIEW_COUNT = 3
    MIN_SENTIMENT_CONFIDENCE = 0.7
    MIN_REVIEW_SCORE = 4

    # Dashboard Settings
    DASHBOARD_TIMEZONE = os.getenv('DASHBOARD_TIMEZONE', 'UTC')
    
    # Helper method to get MySQL config as dict
    @property
    def mysql_config(self):
        return {
            'host': self.MYSQL_HOST,
            'user': self.MYSQL_USER,
            'password': self.MYSQL_PASSWORD,
            'database': self.MYSQL_DATABASE,
            'port': self.MYSQL_PORT,
            'pool_name': self.MYSQL_POOL_NAME,
            'pool_size': self.MYSQL_POOL_SIZE
        }