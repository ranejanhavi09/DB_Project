# Graph Database Schema for Customer Recommendations
## Olist Brazilian E-Commerce Dataset

This document defines the graph database schema optimized for customer recommendation systems using Neo4j, Amazon Neptune, or similar graph databases.

---

## Overview

The graph model enables recommendation algorithms by:
- **Collaborative Filtering**: Find customers with similar purchase patterns
- **Content-Based Filtering**: Recommend products based on customer's past purchases and categories
- **Hybrid Recommendations**: Combine purchase history, sentiment, and seller preferences
- **Path-Based Queries**: Traverse customer → order → product → category relationships

---

## NODES

### 1. Customer Node

**Label**: `Customer`

**Unique Identifier**: `customer_unique_id` (Primary Key)

**Properties**:
```cypher
{
  customer_unique_id: String (unique, indexed)
  customer_zip_code_prefix: String
  customer_city: String
  customer_state: String
  total_orders: Integer (computed)
  total_spent: Float (computed)
  avg_order_value: Float (computed)
  first_order_date: DateTime (computed)
  last_order_date: DateTime (computed)
}
```

**Purpose**: 
- Primary entity for recommendations
- Represents a unique customer across all orders
- Aggregated metrics help identify customer segments

**Cardinality**: ~96,000 unique customers

---

### 2. Order Node

**Label**: `Order`

**Unique Identifier**: `order_id` (Primary Key)

**Properties**:
```cypher
{
  order_id: String (unique, indexed)
  order_status: String (indexed)
  order_purchase_timestamp: DateTime (indexed)
  order_approved_at: DateTime
  order_delivered_carrier_date: DateTime
  order_delivered_customer_date: DateTime
  order_estimated_delivery_date: Date
  total_value: Float (computed: sum of order items)
  item_count: Integer (computed)
}
```

**Purpose**:
- Represents individual purchase transactions
- Links customers to products and sellers
- Order status and dates enable time-based recommendations

**Cardinality**: ~99,441 orders

---

### 3. Product Node

**Label**: `Product`

**Unique Identifier**: `product_id` (Primary Key)

**Properties**:
```cypher
{
  product_id: String (unique, indexed)
  product_name_length: Integer
  product_description_length: Integer
  product_photos_qty: Integer
  product_weight_g: Integer
  product_length_cm: Float
  product_height_cm: Float
  product_width_cm: Float
  total_sales: Integer (computed: count of purchases)
  avg_price: Float (computed)
  avg_rating: Float (computed from reviews)
  total_reviews: Integer (computed)
}
```

**Purpose**:
- Product catalog items
- Physical attributes useful for similarity matching
- Aggregated metrics help identify popular products

**Cardinality**: ~32,951 products

---

### 4. ProductCategory Node

**Label**: `ProductCategory`

**Unique Identifier**: `product_category_name_english` (Primary Key)

**Properties**:
```cypher
{
  product_category_name_english: String (unique, indexed)
  product_category_name_portuguese: String
  total_products: Integer (computed)
  total_sales: Integer (computed)
  avg_price: Float (computed)
  avg_rating: Float (computed)
}
```

**Purpose**:
- Product categories in English (for recommendations)
- Enables category-based recommendations
- Aggregated metrics identify popular categories

**Cardinality**: 72 categories

---

### 5. Seller Node

**Label**: `Seller`

**Unique Identifier**: `seller_id` (Primary Key)

**Properties**:
```cypher
{
  seller_id: String (unique, indexed)
  seller_zip_code_prefix: String
  seller_city: String
  seller_state: String
  total_products_sold: Integer (computed)
  total_revenue: Float (computed)
  avg_rating: Float (computed from reviews)
  total_reviews: Integer (computed)
  avg_shipping_time: Float (computed in days)
}
```

**Purpose**:
- Marketplace sellers
- Seller performance metrics enable seller-based recommendations
- Location data enables geographic recommendations

**Cardinality**: ~3,097 sellers

---

### 6. Review Node

**Label**: `Review`

**Unique Identifier**: `review_id` (Primary Key)

**Properties**:
```cypher
{
  review_id: String (unique, indexed)
  review_score: Integer (indexed: 1-5)
  review_comment_title: String
  review_comment_message: String
  review_text_combined: String
  review_text_english: String
  predicted_sentiment: String (indexed: "POSITIVE" | "NEGATIVE")
  sentiment_confidence: Float (0.0-1.0)
  is_aligned: Boolean
  review_creation_date: DateTime (indexed)
  review_answer_timestamp: DateTime
}
```

**Purpose**:
- Customer feedback and sentiment
- Sentiment values crucial for recommendation quality filtering
- Review scores and sentiment help identify preferred products

**Cardinality**: ~48,195 reviews

---

## RELATIONSHIPS

### 1. Customer → Order Relationship

**Type**: `PLACED_ORDER`

**Direction**: `Customer` → `Order`

**Properties**:
```cypher
{
  order_sequence: Integer (1st, 2nd, 3rd order for this customer)
  days_since_last_order: Integer (computed)
}
```

**Cardinality**: One Customer → Many Orders

**Use Cases**:
- Find all orders for a customer
- Identify repeat customers
- Calculate customer lifetime value
- Time-based recommendations (recent orders weighted higher)

**Example Query**:
```cypher
MATCH (c:Customer {customer_unique_id: $customer_id})-[:PLACED_ORDER]->(o:Order)
RETURN o ORDER BY o.order_purchase_timestamp DESC
```

---

### 2. Order → Product Relationship

**Type**: `CONTAINS_PRODUCT`

**Direction**: `Order` → `Product`

**Properties**:
```cypher
{
  order_item_id: Integer
  price: Float (indexed)
  freight_value: Float
  shipping_limit_date: DateTime
  quantity: Integer (default: 1)
  total_item_value: Float (computed: price + freight_value)
}
```

**Cardinality**: One Order → Many Products

**Use Cases**:
- Find all products in an order
- Calculate order value
- Product co-purchase analysis (products bought together)
- Price-based filtering

**Example Query**:
```cypher
MATCH (o:Order {order_id: $order_id})-[:CONTAINS_PRODUCT]->(p:Product)
RETURN p, o.price as price
```

---

### 3. Product → ProductCategory Relationship

**Type**: `BELONGS_TO_CATEGORY`

**Direction**: `Product` → `ProductCategory`

**Properties**:
```cypher
{
  // No additional properties needed
}
```

**Cardinality**: Many Products → One Category (some products may have NULL category)

**Use Cases**:
- Find all products in a category
- Category-based recommendations
- Cross-category analysis
- Category preference discovery

**Example Query**:
```cypher
MATCH (p:Product)-[:BELONGS_TO_CATEGORY]->(cat:ProductCategory {product_category_name_english: $category})
RETURN p
```

---

### 4. Order → Seller Relationship

**Type**: `PURCHASED_FROM`

**Direction**: `Order` → `Seller`

**Properties**:
```cypher
{
  // Note: This relationship exists through order items
  // Multiple sellers per order possible
  item_count: Integer (number of items from this seller in this order)
  total_value: Float (sum of items from this seller)
}
```

**Cardinality**: One Order → Many Sellers (marketplace model)

**Use Cases**:
- Find sellers for an order
- Seller preference analysis
- Seller-based recommendations
- Multi-seller order analysis

**Note**: This relationship is derived from Order Items. An order can have multiple sellers.

**Example Query**:
```cypher
MATCH (o:Order {order_id: $order_id})-[:PURCHASED_FROM]->(s:Seller)
RETURN s, o.item_count as items_from_seller
```

---

### 5. Product → Seller Relationship

**Type**: `SOLD_BY`

**Direction**: `Product` → `Seller`

**Properties**:
```cypher
{
  times_sold: Integer (computed: count of order items)
  avg_price: Float (computed)
  total_revenue: Float (computed)
  first_sale_date: DateTime
  last_sale_date: DateTime
}
```

**Cardinality**: Many Products → Many Sellers (many-to-many)

**Use Cases**:
- Find all sellers for a product
- Find all products from a seller
- Seller-product performance analysis
- Alternative seller recommendations

**Example Query**:
```cypher
MATCH (p:Product {product_id: $product_id})-[:SOLD_BY]->(s:Seller)
RETURN s ORDER BY s.times_sold DESC
```

---

### 6. Order → Review Relationship

**Type**: `HAS_REVIEW`

**Direction**: `Order` → `Review`

**Properties**:
```cypher
{
  // No additional properties needed
  // Review properties contain all necessary information
}
```

**Cardinality**: One Order → Zero or One Review (not all orders have reviews)

**Use Cases**:
- Find review for an order
- Filter orders by review sentiment
- Sentiment-based product recommendations
- Quality filtering (only recommend products with positive sentiment)

**Example Query**:
```cypher
MATCH (o:Order)-[:HAS_REVIEW]->(r:Review)
WHERE r.predicted_sentiment = "POSITIVE" AND r.review_score >= 4
RETURN o, r
```

---

### 7. Customer → Review Relationship (Indirect)

**Type**: `WROTE_REVIEW`

**Direction**: `Customer` → `Review`

**Properties**:
```cypher
{
  // Derived through: Customer → Order → Review
  // Can be materialized for performance
}
```

**Cardinality**: One Customer → Many Reviews

**Use Cases**:
- Find all reviews by a customer
- Customer sentiment analysis
- Identify customers with similar review patterns
- Sentiment-weighted recommendations

**Example Query**:
```cypher
MATCH (c:Customer {customer_unique_id: $customer_id})-[:PLACED_ORDER]->(o:Order)-[:HAS_REVIEW]->(r:Review)
WHERE r.predicted_sentiment = "POSITIVE"
RETURN r
```

---

### 8. Product → Review Relationship (Indirect)

**Type**: `REVIEWED_IN`

**Direction**: `Product` → `Review`

**Properties**:
```cypher
{
  // Derived through: Product ← Order → Review
  // Can be materialized for performance
  avg_score: Float (computed)
  positive_sentiment_ratio: Float (computed)
}
```

**Cardinality**: One Product → Many Reviews

**Use Cases**:
- Find all reviews for a product
- Product sentiment analysis
- Filter products by sentiment
- Quality-based recommendations

**Example Query**:
```cypher
MATCH (p:Product {product_id: $product_id})<-[:CONTAINS_PRODUCT]-(o:Order)-[:HAS_REVIEW]->(r:Review)
WHERE r.predicted_sentiment = "POSITIVE"
RETURN r, r.review_score as score
```

---

### 9. Seller → Review Relationship (Indirect)

**Type**: `RECEIVED_REVIEW`

**Direction**: `Seller` → `Review`

**Properties**:
```cypher
{
  // Derived through: Seller ← Order → Review
  // Can be materialized for performance
  avg_score: Float (computed)
  positive_sentiment_ratio: Float (computed)
}
```

**Cardinality**: One Seller → Many Reviews

**Use Cases**:
- Find all reviews for a seller
- Seller reputation analysis
- Filter sellers by sentiment
- Quality seller recommendations

**Example Query**:
```cypher
MATCH (s:Seller {seller_id: $seller_id})<-[:PURCHASED_FROM]-(o:Order)-[:HAS_REVIEW]->(r:Review)
WHERE r.predicted_sentiment = "POSITIVE"
RETURN r
```

---

## GRAPH STRUCTURE VISUALIZATION

```
                    ┌─────────────┐
                    │  Customer   │
                    │(unique_id)  │
                    └──────┬──────┘
                           │ PLACED_ORDER
                           │
                    ┌──────▼──────┐
                    │   Order     │
                    │  (order_id) │
                    └──┬──────┬───┘
                       │      │
        CONTAINS_PRODUCT│      │HAS_REVIEW
                       │      │
        ┌──────────────┘      └──────────┐
        │                                 │
┌───────▼──────┐                  ┌───────▼──────┐
│   Product    │                  │   Review     │
│ (product_id) │                  │(review_id)   │
└──┬───────┬───┘                  │sentiment     │
   │       │                      │score         │
   │       │                      └──────────────┘
   │       │
   │       │SOLD_BY
   │       │
   │  ┌────▼──────┐
   │  │  Seller   │
   │  │(seller_id)│
   │  └───────────┘
   │
   │BELONGS_TO_CATEGORY
   │
┌───▼──────────────┐
│ ProductCategory  │
│  (english_name)  │
└──────────────────┘
```

---

## RECOMMENDATION ALGORITHMS ENABLED

### 1. **Collaborative Filtering**
**Query Pattern**: Find customers who bought similar products
```cypher
MATCH (c1:Customer {customer_unique_id: $customer_id})-[:PLACED_ORDER]->(o1:Order)
      -[:CONTAINS_PRODUCT]->(p:Product)<-[:CONTAINS_PRODUCT]-(o2:Order)
      <-[:PLACED_ORDER]-(c2:Customer)
WHERE c1 <> c2
WITH c2, COUNT(DISTINCT p) as common_products
ORDER BY common_products DESC
LIMIT 10
MATCH (c2)-[:PLACED_ORDER]->(o:Order)-[:CONTAINS_PRODUCT]->(rec:Product)
WHERE NOT EXISTS {
  (c1)-[:PLACED_ORDER]->(:Order)-[:CONTAINS_PRODUCT]->(rec)
}
RETURN DISTINCT rec, COUNT(*) as recommendation_score
ORDER BY recommendation_score DESC
```

### 2. **Content-Based Filtering**
**Query Pattern**: Recommend products in categories customer likes
```cypher
MATCH (c:Customer {customer_unique_id: $customer_id})-[:PLACED_ORDER]->(o:Order)
      -[:CONTAINS_PRODUCT]->(p:Product)-[:BELONGS_TO_CATEGORY]->(cat:ProductCategory)
WITH cat, COUNT(*) as purchase_count
ORDER BY purchase_count DESC
LIMIT 5
MATCH (cat)<-[:BELONGS_TO_CATEGORY]-(rec:Product)
WHERE NOT EXISTS {
  (c)-[:PLACED_ORDER]->(:Order)-[:CONTAINS_PRODUCT]->(rec)
}
MATCH (rec)<-[:CONTAINS_PRODUCT]-(o:Order)-[:HAS_REVIEW]->(r:Review)
WHERE r.predicted_sentiment = "POSITIVE" AND r.review_score >= 4
RETURN DISTINCT rec, AVG(r.review_score) as avg_rating
ORDER BY avg_rating DESC
```

### 3. **Sentiment-Based Recommendations**
**Query Pattern**: Recommend products with positive sentiment
```cypher
MATCH (c:Customer {customer_unique_id: $customer_id})-[:PLACED_ORDER]->(o:Order)
      -[:CONTAINS_PRODUCT]->(p:Product)
WITH p, COUNT(*) as times_purchased
MATCH (p)<-[:CONTAINS_PRODUCT]-(o2:Order)-[:HAS_REVIEW]->(r:Review)
WHERE r.predicted_sentiment = "POSITIVE" 
  AND r.sentiment_confidence > 0.8
  AND r.review_score >= 4
WITH p, AVG(r.review_score) as avg_score, COUNT(r) as review_count
WHERE review_count >= 5
RETURN p, avg_score, review_count
ORDER BY avg_score DESC, review_count DESC
```

### 4. **Seller-Based Recommendations**
**Query Pattern**: Recommend products from preferred sellers
```cypher
MATCH (c:Customer {customer_unique_id: $customer_id})-[:PLACED_ORDER]->(o:Order)
      -[:PURCHASED_FROM]->(s:Seller)
WITH s, COUNT(*) as order_count
ORDER BY order_count DESC
LIMIT 3
MATCH (s)<-[:SOLD_BY]-(rec:Product)
WHERE NOT EXISTS {
  (c)-[:PLACED_ORDER]->(:Order)-[:CONTAINS_PRODUCT]->(rec)
}
MATCH (rec)<-[:CONTAINS_PRODUCT]-(o2:Order)-[:HAS_REVIEW]->(r:Review)
WHERE r.predicted_sentiment = "POSITIVE"
RETURN DISTINCT rec, AVG(r.review_score) as avg_rating
ORDER BY avg_rating DESC
```

### 5. **Hybrid Recommendations** (Combining Multiple Signals)
**Query Pattern**: Weighted recommendation score
```cypher
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
WITH rec, category_preference,
     AVG(CASE WHEN r.predicted_sentiment = "POSITIVE" THEN r.review_score ELSE 0 END) as sentiment_score,
     COUNT(r) as review_count
// Calculate recommendation score
WITH rec, 
     category_preference * 0.4 + 
     sentiment_score * 0.4 + 
     (CASE WHEN review_count > 10 THEN 1.0 ELSE review_count/10.0 END) * 0.2 
     as recommendation_score
WHERE sentiment_score >= 3.5 AND review_count >= 3
RETURN rec, recommendation_score
ORDER BY recommendation_score DESC
LIMIT 20
```

---

## INDEXES REQUIRED

For optimal query performance, create indexes on:

```cypher
// Node property indexes
CREATE INDEX customer_unique_id_index FOR (c:Customer) ON (c.customer_unique_id);
CREATE INDEX order_id_index FOR (o:Order) ON (o.order_id);
CREATE INDEX product_id_index FOR (p:Product) ON (p.product_id);
CREATE INDEX seller_id_index FOR (s:Seller) ON (s.seller_id);
CREATE INDEX review_id_index FOR (r:Review) ON (r.review_id);
CREATE INDEX category_name_index FOR (cat:ProductCategory) ON (cat.product_category_name_english);

// Relationship property indexes (if supported)
CREATE INDEX review_sentiment_index FOR (r:Review) ON (r.predicted_sentiment);
CREATE INDEX review_score_index FOR (r:Review) ON (r.review_score);
CREATE INDEX order_timestamp_index FOR (o:Order) ON (o.order_purchase_timestamp);
```

---

## DATA LOADING CONSIDERATIONS

### 1. **Customer Node Creation**
- Group by `customer_unique_id` (not `customer_id`)
- Aggregate metrics: total orders, total spent, etc.
- Use latest location data

### 2. **Order-Product Relationship**
- Create `CONTAINS_PRODUCT` from order_items table
- Include price and freight_value as relationship properties

### 3. **Product-Seller Relationship**
- Create `SOLD_BY` from order_items table
- Aggregate metrics: times_sold, avg_price

### 4. **Sentiment Integration**
- Use `predicted_sentiment` from reviews for filtering
- Use `sentiment_confidence` for quality thresholds
- Filter recommendations by `is_aligned` flag

### 5. **Category Translation**
- Use `product_category_name_english` from translation table
- Handle NULL categories gracefully

---

## METRICS TO TRACK

### Node-Level Metrics
- **Customer**: total_orders, total_spent, avg_order_value, preferred_categories
- **Product**: total_sales, avg_price, avg_rating, positive_sentiment_ratio
- **Seller**: total_products_sold, avg_rating, positive_sentiment_ratio
- **Category**: total_products, total_sales, avg_price, avg_rating

### Relationship-Level Metrics
- **PLACED_ORDER**: order_sequence, recency
- **CONTAINS_PRODUCT**: price, quantity, total_value
- **HAS_REVIEW**: sentiment, score, confidence

---

## RECOMMENDATION QUALITY FILTERS

Use these filters to improve recommendation quality:

1. **Sentiment Filter**: Only recommend products with `predicted_sentiment = "POSITIVE"`
2. **Confidence Filter**: `sentiment_confidence > 0.7`
3. **Score Filter**: `review_score >= 4`
4. **Review Count Filter**: Products with at least 5 reviews
5. **Alignment Filter**: `is_aligned = true` (sentiment matches score)
6. **Recency Filter**: Prefer recent orders (last 6-12 months)

---

*This schema is optimized for graph-based recommendation systems using Neo4j, Amazon Neptune, or similar graph databases.*

