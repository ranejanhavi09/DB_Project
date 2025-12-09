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
    
    # Flask Configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # Dataset Paths
    DATASETS_PATH = os.getenv('DATASETS_PATH', './Datasets')
    
    # Recommendation Settings
    MAX_RECOMMENDATIONS = 20
    MIN_REVIEW_COUNT = 3
    MIN_SENTIMENT_CONFIDENCE = 0.7
    MIN_REVIEW_SCORE = 4

