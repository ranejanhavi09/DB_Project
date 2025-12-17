"""
Recommendation engine using graph database queries
"""
from database import db
from config import Config

class RecommendationEngine:
    """Graph-based recommendation engine"""
    
    def __init__(self):
        self.db = db
    
    def collaborative_filtering(self, customer_unique_id, limit=Config.MAX_RECOMMENDATIONS):
        """
        Collaborative filtering: Find products bought by similar customers
        """
        query = """
        MATCH (c1:Customer {customer_unique_id: $customer_id})-[:PLACED_ORDER]->(o1:Order)
              -[:CONTAINS_PRODUCT]->(p:Product)<-[:CONTAINS_PRODUCT]-(o2:Order)
              <-[:PLACED_ORDER]-(c2:Customer)
        WHERE c1 <> c2
        WITH c2, COUNT(DISTINCT p) as common_products
        ORDER BY common_products DESC
        LIMIT 10
        MATCH (c2)-[:PLACED_ORDER]->(o:Order)-[:CONTAINS_PRODUCT]->(rec:Product)
        WHERE NOT EXISTS {
            (c1:Customer {customer_unique_id: $customer_id})-[:PLACED_ORDER]->(:Order)
            -[:CONTAINS_PRODUCT]->(rec)
        }
        OPTIONAL MATCH (rec)<-[:CONTAINS_PRODUCT]-(o3:Order)-[:HAS_REVIEW]->(r:Review)
        WHERE r.predicted_sentiment = "POSITIVE" AND r.review_score >= $min_score
        WITH rec, COUNT(DISTINCT c2) as similar_shoppers_count,
             COUNT(DISTINCT o) as purchase_count,
             AVG(r.review_score) as avg_rating,
             COUNT(r) as review_count
        WHERE review_count >= $min_reviews OR review_count = 0
        RETURN rec.product_id as product_id,
               rec.total_sales as total_sales,
               rec.avg_price as avg_price,
               rec.avg_rating as avg_rating,
               purchase_count as recommendation_score,
               review_count,
               similar_shoppers_count as explanation_data
        ORDER BY recommendation_score DESC, avg_rating DESC
        LIMIT $limit
        """
        
        return self.db.execute_query(query, {
            'customer_id': customer_unique_id,
            'limit': limit,
            'min_score': Config.MIN_REVIEW_SCORE,
            'min_reviews': Config.MIN_REVIEW_COUNT
        })
    
    def content_based_filtering(self, customer_unique_id, limit=Config.MAX_RECOMMENDATIONS):
        """
        Content-based filtering: Recommend products in categories customer likes
        """
        query = """
        MATCH (c:Customer {customer_unique_id: $customer_id})-[:PLACED_ORDER]->(o:Order)
              -[:CONTAINS_PRODUCT]->(p:Product)-[:BELONGS_TO_CATEGORY]->(cat:ProductCategory)
        WITH cat, COUNT(*) as purchase_count
        ORDER BY purchase_count DESC
        LIMIT 5
        MATCH (cat)<-[:BELONGS_TO_CATEGORY]-(rec:Product)
        WHERE NOT EXISTS {
            (c:Customer {customer_unique_id: $customer_id})-[:PLACED_ORDER]->(:Order)
            -[:CONTAINS_PRODUCT]->(rec)
        }
        MATCH (c:Customer {customer_unique_id: $customer_id})-[:PLACED_ORDER]->(:Order)
              -[:CONTAINS_PRODUCT]->(related:Product)-[:BELONGS_TO_CATEGORY]->(cat)
        WITH rec, cat, purchase_count, related.product_id as related_product_id
        ORDER BY rec.product_id, related_product_id
        WITH rec, cat, purchase_count, COLLECT(DISTINCT related_product_id)[0] as explanation_data
        OPTIONAL MATCH (rec)<-[:CONTAINS_PRODUCT]-(o2:Order)-[:HAS_REVIEW]->(r:Review)
        WHERE r.predicted_sentiment = "POSITIVE" 
          AND r.sentiment_confidence >= $min_confidence
          AND r.review_score >= $min_score
        WITH rec, cat, purchase_count, explanation_data,
             AVG(r.review_score) as avg_rating,
             COUNT(r) as review_count
        WHERE review_count >= $min_reviews OR review_count = 0
        RETURN rec.product_id as product_id,
               rec.total_sales as total_sales,
               rec.avg_price as avg_price,
               rec.avg_rating as avg_rating,
               cat.product_category_name_english as category,
               purchase_count as category_preference,
               review_count,
               explanation_data
        ORDER BY category_preference DESC, avg_rating DESC
        LIMIT $limit
        """
        
        return self.db.execute_query(query, {
            'customer_id': customer_unique_id,
            'limit': limit,
            'min_score': Config.MIN_REVIEW_SCORE,
            'min_reviews': Config.MIN_REVIEW_COUNT,
            'min_confidence': Config.MIN_SENTIMENT_CONFIDENCE
        })
    
    def sentiment_based_filtering(self, customer_unique_id, limit=Config.MAX_RECOMMENDATIONS):
        """
        Sentiment-based filtering: Recommend products with positive sentiment
        """
        query = """
        MATCH (c:Customer {customer_unique_id: $customer_id})-[:PLACED_ORDER]->(o:Order)
              -[:CONTAINS_PRODUCT]->(p:Product)
        WITH p, COUNT(*) as times_purchased
        MATCH (p)<-[:CONTAINS_PRODUCT]-(o2:Order)-[:HAS_REVIEW]->(r:Review)
        WHERE r.predicted_sentiment = "POSITIVE" 
          AND r.sentiment_confidence >= $min_confidence
          AND r.review_score >= $min_score
        WITH p, times_purchased,
             AVG(r.review_score) as avg_score,
             COUNT(r) as review_count,
             AVG(r.sentiment_confidence) as avg_confidence
        WHERE review_count >= $min_reviews
        RETURN p.product_id as product_id,
               p.total_sales as total_sales,
               p.avg_price as avg_price,
               avg_score as avg_rating,
               review_count,
               avg_confidence as sentiment_confidence,
               times_purchased,
               review_count as explanation_data
        ORDER BY avg_score DESC, review_count DESC, sentiment_confidence DESC
        LIMIT $limit
        """
        
        return self.db.execute_query(query, {
            'customer_id': customer_unique_id,
            'limit': limit,
            'min_score': Config.MIN_REVIEW_SCORE,
            'min_reviews': Config.MIN_REVIEW_COUNT,
            'min_confidence': Config.MIN_SENTIMENT_CONFIDENCE
        })
    
    def seller_based_filtering(self, customer_unique_id, limit=Config.MAX_RECOMMENDATIONS):
        """
        Seller-based filtering: Recommend products from preferred sellers
        """
        query = """
        MATCH (c:Customer {customer_unique_id: $customer_id})-[:PLACED_ORDER]->(o:Order)
              -[:PURCHASED_FROM]->(s:Seller)
        WITH s, COUNT(*) as order_count
        ORDER BY order_count DESC
        LIMIT 3
        MATCH (s)<-[:SOLD_BY]-(rec:Product)
        WHERE NOT EXISTS {
            (c:Customer {customer_unique_id: $customer_id})-[:PLACED_ORDER]->(:Order)
            -[:CONTAINS_PRODUCT]->(rec)
        }
        OPTIONAL MATCH (rec)<-[:CONTAINS_PRODUCT]-(o2:Order)-[:HAS_REVIEW]->(r:Review)
        WHERE r.predicted_sentiment = "POSITIVE"
        WITH rec, s, order_count,
             AVG(r.review_score) as avg_rating,
             COUNT(r) as review_count,
             s.avg_rating as seller_rating
        WHERE review_count >= $min_reviews OR review_count = 0
        RETURN rec.product_id as product_id,
               rec.total_sales as total_sales,
               rec.avg_price as avg_price,
               avg_rating as avg_rating,
               seller_rating,
               s.seller_id as seller_id,
               s.seller_city as seller_city,
               order_count as seller_preference,
               review_count,
               order_count as explanation_data
        ORDER BY seller_preference DESC, seller_rating DESC, avg_rating DESC
        LIMIT $limit
        """
        
        return self.db.execute_query(query, {
            'customer_id': customer_unique_id,
            'limit': limit,
            'min_reviews': Config.MIN_REVIEW_COUNT
        })
    
    def hybrid_recommendations(self, customer_unique_id, limit=Config.MAX_RECOMMENDATIONS):
        """
        Hybrid recommendations: Combine multiple signals with weighted scores
        """
        query = """
        MATCH (c:Customer {customer_unique_id: $customer_id})
        
        // Get customer's preferred categories
        MATCH (c)-[:PLACED_ORDER]->(o1:Order)-[:CONTAINS_PRODUCT]->(p1:Product)
              -[:BELONGS_TO_CATEGORY]->(cat:ProductCategory)
        WITH cat, COUNT(*) as category_preference
        
        // Find products in preferred categories
        MATCH (cat)<-[:BELONGS_TO_CATEGORY]-(rec:Product)
        WHERE NOT EXISTS {
            (c)-[:PLACED_ORDER]->(:Order)-[:CONTAINS_PRODUCT]->(rec)
        }
        
        // Get sentiment scores
        OPTIONAL MATCH (rec)<-[:CONTAINS_PRODUCT]-(o2:Order)-[:HAS_REVIEW]->(r:Review)
        WHERE r.predicted_sentiment = "POSITIVE"
          AND r.sentiment_confidence >= $min_confidence
        
        // Get seller preference
        OPTIONAL MATCH (c)-[:PLACED_ORDER]->(o3:Order)-[:PURCHASED_FROM]->(s:Seller)
        WHERE EXISTS {
            (s)<-[:SOLD_BY]-(rec)
        }
        WITH rec, cat, category_preference,
             AVG(CASE WHEN r.predicted_sentiment = "POSITIVE" THEN r.review_score ELSE 0 END) as sentiment_score,
             COUNT(DISTINCT r) as review_count,
             COUNT(DISTINCT s) as preferred_seller_count,
             rec.total_sales as total_sales,
             rec.avg_price as avg_price
        
        // Calculate recommendation score
        WITH rec, cat, category_preference,
             sentiment_score,
             review_count,
             preferred_seller_count,
             total_sales,
             avg_price,
             (category_preference * 0.4 + 
              sentiment_score * 0.4 + 
              (CASE WHEN review_count > 10 THEN 1.0 ELSE review_count/10.0 END) * 0.1 +
              (CASE WHEN preferred_seller_count > 0 THEN 0.1 ELSE 0.0 END)) as recommendation_score
        
        WHERE sentiment_score >= $min_score AND review_count >= $min_reviews
        
        RETURN rec.product_id as product_id,
               rec.total_sales as total_sales,
               rec.avg_price as avg_price,
               sentiment_score as avg_rating,
               cat.product_category_name_english as category,
               review_count,
               recommendation_score
        
        ORDER BY recommendation_score DESC
        LIMIT $limit
        """
        
        return self.db.execute_query(query, {
            'customer_id': customer_unique_id,
            'limit': limit,
            'min_score': Config.MIN_REVIEW_SCORE,
            'min_reviews': Config.MIN_REVIEW_COUNT,
            'min_confidence': Config.MIN_SENTIMENT_CONFIDENCE
        })
    
    def get_customer_info(self, customer_unique_id):
        """Get customer information and purchase history"""
        query = """
        MATCH (c:Customer {customer_unique_id: $customer_id})
        OPTIONAL MATCH (c)-[:PLACED_ORDER]->(o:Order)
        OPTIONAL MATCH (o)-[:CONTAINS_PRODUCT]->(p:Product)
        OPTIONAL MATCH (o)-[:HAS_REVIEW]->(r:Review)
        
        RETURN c.customer_unique_id as customer_unique_id,
               c.customer_city as city,
               c.customer_state as state,
               c.total_orders as total_orders,
               c.first_order_date as first_order_date,
               c.last_order_date as last_order_date,
               COUNT(DISTINCT o) as order_count,
               COUNT(DISTINCT p) as product_count,
               AVG(r.review_score) as avg_review_score
        """
        
        result = self.db.execute_query(query, {'customer_id': customer_unique_id})
        return result[0] if result else None
    
    def get_product_details(self, product_id):
        """Get detailed product information"""
        query = """
        MATCH (p:Product {product_id: $product_id})
        OPTIONAL MATCH (p)-[:BELONGS_TO_CATEGORY]->(cat:ProductCategory)
        OPTIONAL MATCH (p)<-[:CONTAINS_PRODUCT]-(o:Order)-[:HAS_REVIEW]->(r:Review)
        OPTIONAL MATCH (p)-[:SOLD_BY]->(s:Seller)
        
        RETURN p.product_id as product_id,
               p.product_weight_g as weight_g,
               p.product_length_cm as length_cm,
               p.product_height_cm as height_cm,
               p.product_width_cm as width_cm,
               p.total_sales as total_sales,
               p.avg_price as avg_price,
               p.avg_rating as avg_rating,
               p.total_reviews as total_reviews,
               COLLECT(DISTINCT cat.product_category_name_english) as categories,
               COUNT(DISTINCT s) as seller_count,
               AVG(r.review_score) as review_avg_score,
               COUNT(CASE WHEN r.predicted_sentiment = "POSITIVE" THEN 1 END) as positive_reviews,
               COUNT(CASE WHEN r.predicted_sentiment = "NEGATIVE" THEN 1 END) as negative_reviews
        """
        
        result = self.db.execute_query(query, {'product_id': product_id})
        return result[0] if result else None

