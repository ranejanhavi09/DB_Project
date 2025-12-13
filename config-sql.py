"""
MySQL-specific configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

class MySQLConfig:
    """MySQL database configuration"""
    
    # Database connection
    HOST = os.getenv('MYSQL_HOST', 'localhost')
    USER = os.getenv('MYSQL_USER', 'root')
    PASSWORD = os.getenv('MYSQL_PASSWORD', 'mysql123')
    DATABASE = os.getenv('MYSQL_DATABASE', 'ecom-master')
    PORT = int(os.getenv('MYSQL_PORT', 3306))
    
    # Connection pool settings
    POOL_SIZE = int(os.getenv('MYSQL_POOL_SIZE', 5))
    POOL_NAME = os.getenv('MYSQL_POOL_NAME', 'seller_dashboard_pool')
    
    # Query settings
    CHUNK_SIZE = int(os.getenv('MYSQL_CHUNK_SIZE', 1000))
    CONNECT_TIMEOUT = int(os.getenv('MYSQL_CONNECT_TIMEOUT', 10))
    
    # Helper method to get connection parameters
    @property
    def connection_params(self):
        return {
            'host': self.HOST,
            'user': self.USER,
            'password': self.PASSWORD,
            'database': self.DATABASE,
            'port': self.PORT,
            'pool_name': self.POOL_NAME,
            'pool_size': self.POOL_SIZE
        }
    
    # Connection string for SQLAlchemy (if you decide to use ORM later)
    @property
    def sqlalchemy_uri(self):
        return f"mysql+mysqlconnector://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}"