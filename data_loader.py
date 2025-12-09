"""
Data loading script to import CSV data into Neo4j graph database
"""
import pandas as pd
import os
from datetime import datetime
from database import db
from config import Config

def iso_dt(x):
    if pd.isna(x) or x is None:
        return ''
    s = str(x).strip()
    if s.lower() == 'nan' or s == '':
        return ''
    return s.replace(' ', 'T')  # Neo4j expects ISO-8601

def iso_date(x):
    if pd.isna(x) or x is None:
        return ''
    s = str(x).strip()
    if s.lower() == 'nan' or s == '':
        return ''
    return s[:10]  # keep YYYY-MM-DD


def load_customers():
    """Load customers into graph database"""
    print("Loading customers...")
    df = pd.read_csv(os.path.join(Config.DATASETS_PATH, 'olist_customers_dataset.csv'))
    
    query = """
    UNWIND $customers AS customer
    MERGE (c:Customer {customer_unique_id: customer.customer_unique_id})
    SET c.customer_zip_code_prefix = customer.customer_zip_code_prefix,
        c.customer_city = customer.customer_city,
        c.customer_state = customer.customer_state
    """
    
    customers = df.to_dict('records')
    batch_size = 1000
    
    for i in range(0, len(customers), batch_size):
        batch = customers[i:i+batch_size]
        db.execute_write(query, {'customers': batch})
        print(f"Loaded {min(i+batch_size, len(customers))}/{len(customers)} customers")
    
    print("Customers loaded successfully!")

def load_products():
    """Load products into graph database"""
    print("Loading products...")
    df = pd.read_csv(os.path.join(Config.DATASETS_PATH, 'olist_products_dataset.csv'))
    
    query = """
    UNWIND $products AS product
    MERGE (p:Product {product_id: product.product_id})
    SET p.product_name_length = product.product_name_lenght,
        p.product_description_length = product.product_description_lenght,
        p.product_photos_qty = product.product_photos_qty,
        p.product_weight_g = product.product_weight_g,
        p.product_length_cm = product.product_length_cm,
        p.product_height_cm = product.product_height_cm,
        p.product_width_cm = product.product_width_cm
    """
    
    products = df.to_dict('records')
    batch_size = 1000
    
    for i in range(0, len(products), batch_size):
        batch = products[i:i+batch_size]
        db.execute_write(query, {'products': batch})
        print(f"Loaded {min(i+batch_size, len(products))}/{len(products)} products")
    
    print("Products loaded successfully!")

def load_product_categories():
    """Load product categories and link to products"""
    print("Loading product categories...")
    
    # Load translation table
    translation_df = pd.read_csv(os.path.join(Config.DATASETS_PATH, 'product_category_name_translation.csv'))
    translation_dict = dict(zip(
        translation_df['product_category_name'],
        translation_df['product_category_name_english']
    ))
    
    # Load products
    products_df = pd.read_csv(os.path.join(Config.DATASETS_PATH, 'olist_products_dataset.csv'))
    
    # Create categories
    query_create = """
    UNWIND $categories AS cat
    MERGE (pc:ProductCategory {product_category_name_english: cat.english_name})
    SET pc.product_category_name_portuguese = cat.portuguese_name
    """
    
    categories = [
        {'english_name': eng, 'portuguese_name': por}
        for por, eng in translation_dict.items()
    ]
    db.execute_write(query_create, {'categories': categories})
    
    # Link products to categories
    query_link = """
    UNWIND $links AS link
    MATCH (p:Product {product_id: link.product_id})
    MATCH (pc:ProductCategory {product_category_name_english: link.category_english})
    MERGE (p)-[:BELONGS_TO_CATEGORY]->(pc)
    """
    
    links = []
    for _, row in products_df.iterrows():
        if pd.notna(row['product_category_name']):
            category_eng = translation_dict.get(row['product_category_name'])
            if category_eng:
                links.append({
                    'product_id': row['product_id'],
                    'category_english': category_eng
                })
    
    batch_size = 1000
    for i in range(0, len(links), batch_size):
        batch = links[i:i+batch_size]
        db.execute_write(query_link, {'links': batch})
        print(f"Linked {min(i+batch_size, len(links))}/{len(links)} products to categories")
    
    print("Product categories loaded successfully!")

def load_sellers():
    """Load sellers into graph database"""
    print("Loading sellers...")
    df = pd.read_csv(os.path.join(Config.DATASETS_PATH, 'olist_sellers_dataset.csv'))
    
    query = """
    UNWIND $sellers AS seller
    MERGE (s:Seller {seller_id: seller.seller_id})
    SET s.seller_zip_code_prefix = seller.seller_zip_code_prefix,
        s.seller_city = seller.seller_city,
        s.seller_state = seller.seller_state
    """
    
    sellers = df.to_dict('records')
    batch_size = 1000
    
    for i in range(0, len(sellers), batch_size):
        batch = sellers[i:i+batch_size]
        db.execute_write(query, {'sellers': batch})
        print(f"Loaded {min(i+batch_size, len(sellers))}/{len(sellers)} sellers")
    
    print("Sellers loaded successfully!")

def load_orders():
    """Load orders and link to customers"""
    print("Loading orders...")
    df = pd.read_csv(os.path.join(Config.DATASETS_PATH, 'olist_orders_dataset.csv'))
    
    # Load customer mapping first
    customers_df = pd.read_csv(os.path.join(Config.DATASETS_PATH, 'olist_customers_dataset.csv'))
    customer_map = dict(zip(customers_df['customer_id'], customers_df['customer_unique_id']))
    
    # Prepare orders with customer_unique_id
    orders_data = []
    for _, row in df.iterrows():
        customer_unique_id = customer_map.get(row['customer_id'])
        if customer_unique_id:
            order_data = {
                'order_id': str(row['order_id']),
                'order_status': str(row['order_status']),
                'order_purchase_timestamp': iso_dt(row['order_purchase_timestamp']),
                'order_approved_at': iso_dt(row.get('order_approved_at')),
                'order_delivered_carrier_date': iso_dt(row.get('order_delivered_carrier_date')),
                'order_delivered_customer_date': iso_dt(row.get('order_delivered_customer_date')),
                'order_estimated_delivery_date': iso_date(row.get('order_estimated_delivery_date')),
                'customer_unique_id': str(customer_unique_id)
            }
            orders_data.append(order_data)
    
    # Create orders and link to customers in one query
    query_create = """
    UNWIND $orders AS order
    MERGE (o:Order {order_id: order.order_id})
    SET o.order_status = order.order_status,
        o.order_purchase_timestamp = datetime(order.order_purchase_timestamp),
        o.order_approved_at = CASE WHEN order.order_approved_at <> '' AND order.order_approved_at IS NOT NULL 
            THEN datetime(order.order_approved_at) ELSE NULL END,
        o.order_delivered_carrier_date = CASE WHEN order.order_delivered_carrier_date <> '' AND order.order_delivered_carrier_date IS NOT NULL 
            THEN datetime(order.order_delivered_carrier_date) ELSE NULL END,
        o.order_delivered_customer_date = CASE WHEN order.order_delivered_customer_date <> '' AND order.order_delivered_customer_date IS NOT NULL 
            THEN datetime(order.order_delivered_customer_date) ELSE NULL END,
        o.order_estimated_delivery_date = CASE WHEN order.order_estimated_delivery_date <> '' AND order.order_estimated_delivery_date IS NOT NULL 
            THEN date(order.order_estimated_delivery_date) ELSE NULL END
    WITH o, order
    MATCH (c:Customer {customer_unique_id: order.customer_unique_id})
    MERGE (c)-[:PLACED_ORDER]->(o)
    """
    
    batch_size = 1000
    for i in range(0, len(orders_data), batch_size):
        batch = orders_data[i:i+batch_size]
        db.execute_write(query_create, {'orders': batch})
        print(f"Created and linked {min(i+batch_size, len(orders_data))}/{len(orders_data)} orders")
    
    print("Orders loaded successfully!")

def load_order_items():
    """Load order items and create relationships"""
    print("Loading order items...")
    df = pd.read_csv(os.path.join(Config.DATASETS_PATH, 'olist_order_items_dataset.csv'))

    df["shipping_limit_date"] = df["shipping_limit_date"].apply(iso_dt)

    
    # Link orders to products
    query_order_product = """
    UNWIND $items AS item
    MATCH (o:Order {order_id: item.order_id})
    MATCH (p:Product {product_id: item.product_id})
    MERGE (o)-[r:CONTAINS_PRODUCT]->(p)
    SET r.order_item_id = toInteger(item.order_item_id),
        r.price = toFloat(item.price),
        r.freight_value = toFloat(item.freight_value),
        r.shipping_limit_date = CASE WHEN item.shipping_limit_date <> '' AND item.shipping_limit_date IS NOT NULL 
            THEN datetime(item.shipping_limit_date) ELSE NULL END,
        r.total_item_value = toFloat(item.price) + toFloat(item.freight_value)
    """
    
    # Link orders to sellers
    query_order_seller = """
    UNWIND $items AS item
    MATCH (o:Order {order_id: item.order_id})
    MATCH (s:Seller {seller_id: item.seller_id})
    MERGE (o)-[r:PURCHASED_FROM]->(s)
    ON CREATE SET r.item_count = 1, r.total_value = toFloat(item.price) + toFloat(item.freight_value)
    ON MATCH SET r.item_count = r.item_count + 1, 
                 r.total_value = r.total_value + toFloat(item.price) + toFloat(item.freight_value)
    """
    
    # Link products to sellers
    query_product_seller = """
    UNWIND $items AS item
    MATCH (p:Product {product_id: item.product_id})
    MATCH (s:Seller {seller_id: item.seller_id})
    MERGE (p)-[r:SOLD_BY]->(s)
    ON CREATE SET r.times_sold = 1, r.avg_price = toFloat(item.price)
    ON MATCH SET r.times_sold = r.times_sold + 1,
                 r.avg_price = (r.avg_price * (r.times_sold - 1) + toFloat(item.price)) / r.times_sold
    """
    
    items = df.to_dict('records')
    batch_size = 1000
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        db.execute_write(query_order_product, {'items': batch})
        db.execute_write(query_order_seller, {'items': batch})
        db.execute_write(query_product_seller, {'items': batch})
        print(f"Processed {min(i+batch_size, len(items))}/{len(items)} order items")
    
    print("Order items loaded successfully!")

def load_reviews():
    """Load reviews and link to orders"""
    print("Loading reviews...")
    df = pd.read_csv(os.path.join(Config.DATASETS_PATH, 'olist_order_reviews_cleaned.csv'))
    df["review_creation_date"] = df["review_creation_date"].apply(iso_dt)
    df["review_answer_timestamp"] = df["review_answer_timestamp"].apply(iso_dt)
    
    # Create reviews
    query_create = """
    UNWIND $reviews AS review
    MERGE (r:Review {review_id: review.review_id})
    SET r.review_score = toInteger(review.review_score),
        r.review_comment_title = CASE WHEN review.review_comment_title IS NOT NULL THEN review.review_comment_title ELSE '' END,
        r.review_comment_message = CASE WHEN review.review_comment_message IS NOT NULL THEN review.review_comment_message ELSE '' END,
        r.review_text_combined = CASE WHEN review.review_text_combined IS NOT NULL THEN review.review_text_combined ELSE '' END,
        r.review_text_english = CASE WHEN review.review_text_english IS NOT NULL THEN review.review_text_english ELSE '' END,
        r.predicted_sentiment = review.predicted_sentiment,
        r.sentiment_confidence = toFloat(review.sentiment_confidence),
        r.is_aligned = CASE WHEN review.is_aligned = 'True' OR review.is_aligned = true THEN true ELSE false END,
        r.review_creation_date = datetime(review.review_creation_date),
        r.review_answer_timestamp = CASE WHEN review.review_answer_timestamp <> '' AND review.review_answer_timestamp IS NOT NULL 
            THEN datetime(review.review_answer_timestamp) ELSE NULL END
    """
    
    reviews = df.to_dict('records')
    batch_size = 1000
    
    for i in range(0, len(reviews), batch_size):
        batch = reviews[i:i+batch_size]
        db.execute_write(query_create, {'reviews': batch})
        print(f"Created {min(i+batch_size, len(reviews))}/{len(reviews)} reviews")
    
    # Link reviews to orders
    query_link = """
    UNWIND $links AS link
    MATCH (o:Order {order_id: link.order_id})
    MATCH (r:Review {review_id: link.review_id})
    MERGE (o)-[:HAS_REVIEW]->(r)
    """
    
    links = []
    for _, row in df.iterrows():
        if pd.notna(row.get('order_id')) and pd.notna(row.get('review_id')):
            links.append({
                'order_id': str(row['order_id']),
                'review_id': str(row['review_id'])
            })
    
    batch_size = 1000
    for i in range(0, len(links), batch_size):
        batch = links[i:i+batch_size]
        db.execute_write(query_link, {'links': batch})
        print(f"Linked {min(i+batch_size, len(links))}/{len(links)} reviews to orders")
    
    print("Reviews loaded successfully!")

def create_indexes():
    """Create indexes for better query performance"""
    print("Creating indexes...")
    
    indexes = [
        "CREATE INDEX customer_unique_id_index IF NOT EXISTS FOR (c:Customer) ON (c.customer_unique_id)",
        "CREATE INDEX order_id_index IF NOT EXISTS FOR (o:Order) ON (o.order_id)",
        "CREATE INDEX product_id_index IF NOT EXISTS FOR (p:Product) ON (p.product_id)",
        "CREATE INDEX seller_id_index IF NOT EXISTS FOR (s:Seller) ON (s.seller_id)",
        "CREATE INDEX review_id_index IF NOT EXISTS FOR (r:Review) ON (r.review_id)",
        "CREATE INDEX category_name_index IF NOT EXISTS FOR (cat:ProductCategory) ON (cat.product_category_name_english)",
        "CREATE INDEX review_sentiment_index IF NOT EXISTS FOR (r:Review) ON (r.predicted_sentiment)",
        "CREATE INDEX review_score_index IF NOT EXISTS FOR (r:Review) ON (r.review_score)",
    ]
    
    for index_query in indexes:
        try:
            db.execute_write(index_query)
        except Exception as e:
            print(f"Index creation note: {e}")
    
    print("Indexes created successfully!")

def compute_aggregated_metrics():
    """Compute aggregated metrics for nodes"""
    print("Computing aggregated metrics...")
    
    # Customer metrics
    query_customer = """
    MATCH (c:Customer)-[:PLACED_ORDER]->(o:Order)
    WHERE o.order_purchase_timestamp IS NOT NULL
    WITH c,
         min(o.order_purchase_timestamp) AS first_order_date,
         max(o.order_purchase_timestamp) AS last_order_date,
         count(o) AS total_orders
    SET  c.first_order_date = first_order_date,
         c.last_order_date  = last_order_date,
         c.total_orders     = total_orders
    """

    db.execute_write(query_customer)
    
    # Product metrics
    query_product = """
    MATCH (p:Product)<-[:CONTAINS_PRODUCT]-(o:Order)
    WITH p, COUNT(o) as total_sales,
         AVG([(o)-[r:CONTAINS_PRODUCT]->(p) | r.price][0]) as avg_price
    SET p.total_sales = total_sales,
        p.avg_price = avg_price
    """
    db.execute_write(query_product)
    
    # Product ratings
    query_product_rating = """
    MATCH (p:Product)<-[:CONTAINS_PRODUCT]-(o:Order)-[:HAS_REVIEW]->(r:Review)
    WITH p, AVG(r.review_score) as avg_rating, COUNT(r) as total_reviews
    SET p.avg_rating = avg_rating,
        p.total_reviews = total_reviews
    """
    db.execute_write(query_product_rating)
    
    # Seller metrics
    query_seller = """
    MATCH (s:Seller)<-[:PURCHASED_FROM]-(o:Order)
    WITH s, COUNT(DISTINCT o) as total_orders
    SET s.total_products_sold = total_orders
    """
    db.execute_write(query_seller)
    
    # Seller ratings
    query_seller_rating = """
    MATCH (s:Seller)<-[:PURCHASED_FROM]-(o:Order)-[:HAS_REVIEW]->(r:Review)
    WITH s, AVG(r.review_score) as avg_rating, COUNT(r) as total_reviews
    SET s.avg_rating = avg_rating,
        s.total_reviews = total_reviews
    """
    db.execute_write(query_seller_rating)
    
    print("Aggregated metrics computed successfully!")

def main():
    """Main function to load all data"""
    print("Starting data loading process...")
    print("=" * 50)
    
    try:
        # Create indexes first
        create_indexes()
        
        # Load nodes
        load_customers()
        load_products()
        load_product_categories()
        load_sellers()
        load_orders()
        
        # Load relationships
        load_order_items()
        load_reviews()
        
        # Compute aggregated metrics
        compute_aggregated_metrics()
        
        print("=" * 50)
        print("Data loading completed successfully!")
        
    except Exception as e:
        print(f"Error during data loading: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()

