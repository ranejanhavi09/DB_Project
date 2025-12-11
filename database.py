"""
Neo4j database connection and utilities
"""
from neo4j import GraphDatabase
from config import Config

class Neo4jConnection:
    """Neo4j database connection manager"""
    
    def __init__(self):
        self.driver = GraphDatabase.driver(
            Config.NEO4J_URI,
            auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD)
        )
    
    def close(self):
        """Close the database connection"""
        self.driver.close()
    
    def get_session(self):
        """Get a database session"""
        return self.driver.session()
    
    def execute_query(self, query, parameters=None):
        """Execute a Cypher query and return results"""
        from neo4j.time import DateTime, Date

        def convert_neo4j_types(obj):
            """Convert Neo4j datetime types to strings"""
            if isinstance(obj, (DateTime, Date)):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: convert_neo4j_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_neo4j_types(item) for item in obj]
            return obj

        with self.get_session() as session:
            result = session.run(query, parameters or {})
            return [convert_neo4j_types(record.data()) for record in result]
    
    def execute_write(self, query, parameters=None):
        """Execute a write query"""
        with self.get_session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

# Global database connection instance
db = Neo4jConnection()

