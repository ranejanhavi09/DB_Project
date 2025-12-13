"""
MySQL database connection utilities
"""
import mysql.connector
from mysql.connector import Error, pooling
from config import Config
import logging

logger = logging.getLogger(__name__)

class MySQLConnectionManager:
    """Manages MySQL connection pool"""
    
    _connection_pool = None
    
    @classmethod
    def initialize_pool(cls):
        """Initialize the MySQL connection pool"""
        try:
            config = Config()
            
            cls._connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name=config.mysql_config.get('pool_name', 'seller_dashboard_pool'),
                pool_size=config.mysql_config.get('pool_size', 5),
                host=config.mysql_config['host'],
                user=config.mysql_config['user'],
                password=config.mysql_config['password'],
                database=config.mysql_config['database'],
                port=config.mysql_config['port'],
                autocommit=True,
                buffered=True
            )
            logger.info(f"MySQL connection pool initialized with {config.mysql_config.get('pool_size', 5)} connections")
            return True
            
        except Error as e:
            logger.error(f"Error initializing MySQL connection pool: {e}")
            raise
    
    @classmethod
    def get_connection(cls):
        """Get a connection from the pool"""
        if cls._connection_pool is None:
            cls.initialize_pool()
        
        try:
            connection = cls._connection_pool.get_connection()
            return connection
        except Error as e:
            logger.error(f"Error getting MySQL connection: {e}")
            raise
    
    @staticmethod
    def close_connection(connection, cursor=None):
        """Close connection and cursor"""
        try:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
        except Error as e:
            logger.error(f"Error closing MySQL connection: {e}")
    
    @classmethod
    def execute_query(cls, query, params=None, fetch=True, dictionary=True):
        """
        Execute a SQL query
        
        Args:
            query: SQL query string
            params: Query parameters (tuple or dict)
            fetch: Whether to fetch results
            dictionary: Return results as dictionary
            
        Returns:
            Query results or last row ID for INSERT
        """
        connection = None
        cursor = None
        try:
            connection = cls.get_connection()
            cursor = connection.cursor(dictionary=dictionary)
            
            cursor.execute(query, params or ())
            
            if fetch:
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                elif query.strip().upper().startswith('CALL'):
                    # Handle stored procedures
                    results = []
                    for result in cursor.stored_results():
                        results.append(result.fetchall())
                    return results
                else:
                    connection.commit()
                    return cursor.lastrowid
            else:
                connection.commit()
                return cursor.rowcount
                
        except Error as e:
            logger.error(f"MySQL query error: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
        finally:
            cls.close_connection(connection, cursor)
    
    @classmethod
    def test_connection(cls):
        """Test the database connection"""
        connection = None
        try:
            connection = cls.get_connection()
            if connection.is_connected():
                db_info = connection.get_server_info()
                logger.info(f"Connected to MySQL Server version {db_info}")
                return True
            return False
        except Error as e:
            logger.error(f"MySQL connection test failed: {e}")
            return False
        finally:
            cls.close_connection(connection)