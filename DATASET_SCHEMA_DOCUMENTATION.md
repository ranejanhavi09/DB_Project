# Olist Brazilian E-Commerce Dataset - Schema Documentation

## Overview
This dataset contains information about orders made at Olist Store, a Brazilian e-commerce marketplace. The dataset includes multiple interconnected tables that capture the complete e-commerce transaction lifecycle from customer orders to product delivery and reviews.

---

## Table 1: Customers (`olist_customers_dataset.csv`)

### Purpose
Stores customer demographic and location information.

### Fields
- **`customer_id`** (VARCHAR/STRING, Primary Key)
  - Unique identifier for each customer order instance
  - Note: A single customer can have multiple `customer_id` values if they place multiple orders
  
- **`customer_unique_id`** (VARCHAR/STRING)
  - Unique identifier for each distinct customer across all orders
  - Used to track repeat customers
  - Multiple `customer_id` values can map to the same `customer_unique_id`
  
- **`customer_zip_code_prefix`** (VARCHAR/STRING)
  - First 5 digits of the customer's postal code
  - Links to geolocation data
  
- **`customer_city`** (VARCHAR/STRING)
  - City where the customer is located
  
- **`customer_state`** (VARCHAR/STRING)
  - Brazilian state abbreviation (e.g., SP, RJ, MG)

### Relationships
- **One-to-Many** with `olist_orders_dataset`: `customer_id` → `customer_id` in orders table
- **Many-to-One** with `olist_geolocation_dataset`: `customer_zip_code_prefix` → `geolocation_zip_code_prefix`

### Key Insights
- Total records: ~99,443 customers
- `customer_unique_id` allows tracking customer lifetime value and repeat purchase behavior

---

## Table 2: Orders (`olist_orders_dataset.csv`)

### Purpose
Central table tracking order lifecycle and status.

### Fields
- **`order_id`** (VARCHAR/STRING, Primary Key)
  - Unique identifier for each order
  
- **`customer_id`** (VARCHAR/STRING, Foreign Key)
  - References `customer_id` in customers table
  - Links order to customer
  
- **`order_status`** (VARCHAR/STRING)
  - Current status of the order
  - Possible values: `delivered`, `shipped`, `canceled`, `invoiced`, `processing`, `unavailable`, `approved`, `created`
  
- **`order_purchase_timestamp`** (DATETIME)
  - When the customer placed the order
  
- **`order_approved_at`** (DATETIME, nullable)
  - When payment was approved
  - Can be NULL if order was canceled before approval
  
- **`order_delivered_carrier_date`** (DATETIME, nullable)
  - When order was handed over to shipping carrier
  - NULL if order not yet shipped
  
- **`order_delivered_customer_date`** (DATETIME, nullable)
  - Actual delivery date to customer
  - NULL if order not yet delivered
  
- **`order_estimated_delivery_date`** (DATE)
  - Estimated delivery date promised to customer

### Relationships
- **Many-to-One** with Customers: `customer_id` → `customer_id`
- **One-to-Many** with Order Items: `order_id` → `order_id`
- **One-to-Many** with Order Payments: `order_id` → `order_id`
- **One-to-Many** with Order Reviews: `order_id` → `order_id`

### Key Insights
- Total records: ~99,441 orders
- Order status progression: created → approved → invoiced → shipped → delivered
- Can calculate delivery time: `order_delivered_customer_date` - `order_delivered_carrier_date`
- Can calculate fulfillment time: `order_delivered_customer_date` - `order_purchase_timestamp`

---

## Table 3: Order Items (`olist_order_items_dataset.csv`)

### Purpose
Stores individual products within each order. An order can contain multiple items.

### Fields
- **`order_id`** (VARCHAR/STRING, Foreign Key)
  - References `order_id` in orders table
  
- **`order_item_id`** (INTEGER)
  - Sequential number identifying items within the same order
  - Starts at 1 for each order
  - Used when an order contains multiple products
  
- **`product_id`** (VARCHAR/STRING, Foreign Key)
  - References `product_id` in products table
  
- **`seller_id`** (VARCHAR/STRING, Foreign Key)
  - References `seller_id` in sellers table
  
- **`shipping_limit_date`** (DATETIME)
  - Deadline for seller to ship the product to carrier
  
- **`price`** (DECIMAL/FLOAT)
  - Product price (in Brazilian Reais)
  
- **`freight_value`** (DECIMAL/FLOAT)
  - Shipping cost for this specific item (in Brazilian Reais)

### Relationships
- **Many-to-One** with Orders: `order_id` → `order_id`
- **Many-to-One** with Products: `product_id` → `product_id`
- **Many-to-One** with Sellers: `seller_id` → `seller_id`

### Key Insights
- Total records: ~112,650 order items
- Order total value = sum of (`price` + `freight_value`) for all items in an order
- Multiple sellers can be involved in a single order (marketplace model)
- `shipping_limit_date` helps track seller performance

---

## Table 4: Products (`olist_products_dataset.csv`)

### Purpose
Contains product catalog information including dimensions, weight, and category.

### Fields
- **`product_id`** (VARCHAR/STRING, Primary Key)
  - Unique identifier for each product
  
- **`product_category_name`** (VARCHAR/STRING, nullable)
  - Product category in Portuguese
  - Can be NULL for some products
  - Links to translation table
  
- **`product_name_lenght`** (INTEGER, nullable)
  - Length of product name (number of characters)
  - Note: Field name has typo "lenght" instead of "length"
  
- **`product_description_lenght`** (INTEGER, nullable)
  - Length of product description (number of characters)
  - Note: Field name has typo "lenght" instead of "length"
  
- **`product_photos_qty`** (INTEGER, nullable)
  - Number of product photos/images
  
- **`product_weight_g`** (INTEGER, nullable)
  - Product weight in grams
  
- **`product_length_cm`** (DECIMAL/FLOAT, nullable)
  - Product length in centimeters
  
- **`product_height_cm`** (DECIMAL/FLOAT, nullable)
  - Product height in centimeters
  
- **`product_width_cm`** (DECIMAL/FLOAT, nullable)
  - Product width in centimeters

### Relationships
- **One-to-Many** with Order Items: `product_id` → `product_id`
- **Many-to-One** with Product Category Translation: `product_category_name` → `product_category_name`

### Key Insights
- Total records: ~32,951 products
- Many fields are nullable, indicating incomplete product data
- Dimensions and weight are crucial for shipping cost calculation
- Product catalog completeness varies (some products missing dimensions/descriptions)

---

## Table 5: Sellers (`olist_sellers_dataset.csv`)

### Purpose
Stores seller location and identification information.

### Fields
- **`seller_id`** (VARCHAR/STRING, Primary Key)
  - Unique identifier for each seller
  
- **`seller_zip_code_prefix`** (VARCHAR/STRING)
  - First 5 digits of seller's postal code
  - Links to geolocation data
  
- **`seller_city`** (VARCHAR/STRING)
  - City where seller is located
  
- **`seller_state`** (VARCHAR/STRING)
  - Brazilian state abbreviation

### Relationships
- **One-to-Many** with Order Items: `seller_id` → `seller_id`
- **Many-to-One** with Geolocation: `seller_zip_code_prefix` → `geolocation_zip_code_prefix`

### Key Insights
- Total records: ~3,097 sellers
- Marketplace model: multiple sellers can sell the same product
- Seller location affects shipping costs and delivery times
- Can analyze seller performance and geographic distribution

---

## Table 6: Order Payments (`olist_order_payments_dataset.csv`)

### Purpose
Tracks payment information for orders. An order can have multiple payment transactions.

### Fields
- **`order_id`** (VARCHAR/STRING, Foreign Key)
  - References `order_id` in orders table
  
- **`payment_sequential`** (INTEGER)
  - Sequential number for multiple payments on the same order
  - Starts at 1
  - Used when customer splits payment across multiple methods
  
- **`payment_type`** (VARCHAR/STRING)
  - Payment method used
  - Common values: `credit_card`, `boleto`, `voucher`, `debit_card`, `not_defined`
  
- **`payment_installments`** (INTEGER)
  - Number of installments for payment
  - 1 = single payment, >1 = installment plan
  
- **`payment_value`** (DECIMAL/FLOAT)
  - Payment amount for this transaction (in Brazilian Reais)
  - Sum of all `payment_value` for an order equals total order value

### Relationships
- **Many-to-One** with Orders: `order_id` → `order_id`

### Key Insights
- Total records: ~103,886 payment records
- Orders can have multiple payment methods (e.g., partial credit card + voucher)
- Payment type distribution shows customer payment preferences
- Installment analysis reveals financing patterns

---

## Table 7: Order Reviews (`olist_order_reviews_cleaned.csv`)

### Purpose
Contains customer reviews and ratings for orders. This appears to be a cleaned/enhanced version with sentiment analysis.

### Fields
- **`review_id`** (VARCHAR/STRING, Primary Key)
  - Unique identifier for each review
  
- **`order_id`** (VARCHAR/STRING, Foreign Key)
  - References `order_id` in orders table
  
- **`review_score`** (INTEGER)
  - Customer rating from 1 to 5
  - 1 = worst, 5 = best
  
- **`review_comment_title`** (TEXT, nullable)
  - Title of the review comment
  
- **`review_comment_message`** (TEXT, nullable)
  - Full review text in Portuguese
  
- **`review_text_combined`** (TEXT, nullable)
  - Combined review text (title + message)
  
- **`review_text_english`** (TEXT, nullable)
  - English translation of review text
  
- **`predicted_sentiment`** (VARCHAR/STRING)
  - Machine learning predicted sentiment
  - Values: `POSITIVE`, `NEGATIVE`
  
- **`sentiment_confidence`** (DECIMAL/FLOAT)
  - Confidence score for sentiment prediction (0 to 1)
  
- **`is_aligned`** (BOOLEAN)
  - Whether sentiment aligns with review score
  - True if positive sentiment with score 4-5, or negative sentiment with score 1-2
  
- **`review_creation_date`** (DATETIME)
  - When the review was created
  
- **`review_answer_timestamp`** (DATETIME, nullable)
  - When seller responded to the review
  - NULL if no response

### Relationships
- **Many-to-One** with Orders: `order_id` → `order_id`

### Key Insights
- Total records: ~48,195 reviews
- Not all orders have reviews (review rate < 50%)
- Sentiment analysis provides additional insights beyond numeric scores
- Review response time can indicate seller engagement
- `is_aligned` flag helps identify reviews where sentiment doesn't match score

---

## Table 8: Geolocation (`olist_geolocation_dataset.csv`)

### Purpose
Provides geographic coordinates (latitude/longitude) for Brazilian zip code prefixes.

### Fields
- **`geolocation_zip_code_prefix`** (VARCHAR/STRING)
  - First 5 digits of postal code
  - Not unique (multiple coordinates per prefix)
  
- **`geolocation_lat`** (DECIMAL/FLOAT)
  - Latitude coordinate
  
- **`geolocation_lng`** (DECIMAL/FLOAT)
  - Longitude coordinate
  
- **`geolocation_city`** (VARCHAR/STRING)
  - City name
  
- **`geolocation_state`** (VARCHAR/STRING)
  - State abbreviation

### Relationships
- **Many-to-Many** with Customers: `geolocation_zip_code_prefix` → `customer_zip_code_prefix`
- **Many-to-Many** with Sellers: `geolocation_zip_code_prefix` → `seller_zip_code_prefix`

### Key Insights
- Total records: ~1,000,165 geolocation points
- Multiple coordinates per zip code prefix (granular location data)
- Enables distance calculations between customers and sellers
- Useful for logistics and shipping cost analysis
- Can map customer and seller locations on maps

---

## Table 9: Product Category Translation (`product_category_name_translation.csv`)

### Purpose
Translation table mapping Portuguese product category names to English.

### Fields
- **`product_category_name`** (VARCHAR/STRING, Primary Key)
  - Original category name in Portuguese
  
- **`product_category_name_english`** (VARCHAR/STRING)
  - English translation of category name

### Relationships
- **One-to-Many** with Products: `product_category_name` → `product_category_name`

### Key Insights
- Total records: 72 category translations
- Categories include: `beleza_saude` → `health_beauty`, `informatica_acessorios` → `computers_accessories`, etc.
- Some categories may not have translations (NULL in products table)
- Essential for international analysis and reporting

---

## Entity Relationship Diagram (ERD) Summary

```
Customers (1) ──< (Many) Orders (1) ──< (Many) Order Items
                                                      │
                                                      ├──> (Many) Products
                                                      │
                                                      └──> (Many) Sellers

Orders (1) ──< (Many) Order Payments
Orders (1) ──< (Many) Order Reviews

Customers ──> Geolocation (via zip_code_prefix)
Sellers ──> Geolocation (via zip_code_prefix)

Products ──> Product Category Translation (via product_category_name)
```

---

## Key Business Insights Enabled by Schema

### 1. **Customer Analytics**
- Track repeat customers via `customer_unique_id`
- Analyze customer geographic distribution
- Calculate customer lifetime value

### 2. **Order Fulfillment**
- Measure order-to-delivery time
- Track order status progression
- Identify bottlenecks in fulfillment process

### 3. **Product Performance**
- Analyze product sales by category
- Track product dimensions/weight impact on shipping
- Identify best-selling products

### 4. **Seller Performance**
- Evaluate seller shipping compliance (`shipping_limit_date`)
- Analyze seller geographic distribution
- Track seller ratings and reviews

### 5. **Financial Analysis**
- Calculate order values (price + freight)
- Analyze payment method preferences
- Track installment payment patterns

### 6. **Customer Satisfaction**
- Review scores and sentiment analysis
- Review response rates
- Identify satisfaction drivers

### 7. **Logistics & Shipping**
- Calculate shipping distances (customer ↔ seller)
- Analyze freight costs
- Optimize delivery routes

---

## Data Quality Notes

1. **Missing Values**: Many fields are nullable, especially in products table
2. **Field Name Typos**: `product_name_lenght` and `product_description_lenght` have typos
3. **Review Coverage**: Not all orders have reviews (~48% review rate)
4. **Geolocation Granularity**: Multiple coordinates per zip code prefix
5. **Customer ID vs Unique ID**: Important distinction for customer analysis
6. **Multiple Payments**: Orders can have multiple payment transactions
7. **Multiple Items**: Orders can contain multiple products from different sellers

---

## Common Query Patterns

### Calculate Order Total Value
```sql
SELECT 
    o.order_id,
    SUM(oi.price + oi.freight_value) as total_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_id
```

### Find Repeat Customers
```sql
SELECT 
    customer_unique_id,
    COUNT(DISTINCT customer_id) as order_count
FROM customers
GROUP BY customer_unique_id
HAVING COUNT(DISTINCT customer_id) > 1
```

### Calculate Delivery Time
```sql
SELECT 
    order_id,
    DATEDIFF(order_delivered_customer_date, order_delivered_carrier_date) as delivery_days
FROM orders
WHERE order_delivered_customer_date IS NOT NULL
```

### Seller Performance by Reviews
```sql
SELECT 
    s.seller_id,
    AVG(r.review_score) as avg_rating,
    COUNT(r.review_id) as review_count
FROM sellers s
JOIN order_items oi ON s.seller_id = oi.seller_id
JOIN orders o ON oi.order_id = o.order_id
JOIN order_reviews r ON o.order_id = r.order_id
GROUP BY s.seller_id
```

---

## Dataset Statistics Summary

| Table | Approximate Records | Key Purpose |
|-------|-------------------|-------------|
| Customers | ~99,443 | Customer demographics |
| Orders | ~99,441 | Order lifecycle tracking |
| Order Items | ~112,650 | Product-line details |
| Products | ~32,951 | Product catalog |
| Sellers | ~3,097 | Seller information |
| Order Payments | ~103,886 | Payment transactions |
| Order Reviews | ~48,195 | Customer feedback |
| Geolocation | ~1,000,165 | Geographic coordinates |
| Category Translation | 72 | Category translations |

---

*Documentation created based on dataset analysis and Kaggle dataset schema information*

