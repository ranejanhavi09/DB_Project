
-- =====================================================

DELIMITER $

-- =====================================================
-- 1. GET SELLER OVERVIEW METRICS
-- Returns key performance indicators for a specific seller
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_seller_overview$
CREATE PROCEDURE sp_get_seller_overview(
    IN p_seller_id TEXT,
    IN p_start_date DATETIME,
    IN p_end_date DATETIME
)
BEGIN
    SELECT 
        s.seller_id,
        s.seller_city,
        s.seller_state,
        COUNT(DISTINCT oi.order_id) AS total_orders,
        COUNT(DISTINCT oi.product_id) AS unique_products_sold,
        COUNT(DISTINCT p.product_category_name) AS categories_offered,
        ROUND(SUM(oi.price), 2) AS total_revenue,
        ROUND(AVG(oi.price), 2) AS avg_item_price,
        ROUND(SUM(oi.freight_value), 2) AS total_freight_revenue,
        ROUND(SUM(oi.price + oi.freight_value), 2) AS total_gmv,
        COUNT(DISTINCT o.customer_id) AS unique_customers,
        COUNT(DISTINCT c.customer_state) AS states_served,
        COUNT(DISTINCT c.customer_city) AS cities_served,
        COUNT(DISTINCT r.review_id) AS total_reviews,
        ROUND(AVG(r.review_score), 2) AS avg_review_score,
        ROUND(100.0 * SUM(CASE WHEN r.review_score >= 4 THEN 1 ELSE 0 END) / 
              NULLIF(COUNT(DISTINCT r.review_id), 0), 2) AS positive_review_pct,
        ROUND(AVG(DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp)), 1) AS avg_delivery_days
    FROM sellers s
    JOIN order_items oi ON s.seller_id = oi.seller_id
    JOIN orders o ON oi.order_id = o.order_id
    JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN customers c ON o.customer_id = c.customer_id
    LEFT JOIN order_reviews r ON o.order_id = r.order_id
    WHERE s.seller_id = p_seller_id
      AND o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
      AND o.order_status = 'delivered'
    GROUP BY s.seller_id, s.seller_city, s.seller_state;
END$

-- =====================================================
-- 2. GET SELLER REVENUE TRENDS
-- Returns daily/monthly revenue trends for visualization
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_seller_revenue_trends$
CREATE PROCEDURE sp_get_seller_revenue_trends(
    IN p_seller_id TEXT,
    IN p_start_date DATETIME,
    IN p_end_date DATETIME,
    IN p_granularity VARCHAR(10) -- 'daily' or 'monthly'
)
BEGIN
    IF p_granularity = 'monthly' THEN
        SELECT 
            DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') AS period,
            COUNT(DISTINCT oi.order_id) AS order_count,
            ROUND(SUM(oi.price), 2) AS revenue,
            ROUND(SUM(oi.freight_value), 2) AS freight_revenue,
            ROUND(SUM(oi.price + oi.freight_value), 2) AS total_gmv,
            ROUND(AVG(oi.price), 2) AS avg_order_value,
            COUNT(DISTINCT o.customer_id) AS unique_customers
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        WHERE oi.seller_id = p_seller_id
          AND o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
          AND o.order_status = 'delivered'
        GROUP BY DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m')
        ORDER BY period;
    ELSE
        SELECT 
            DATE(o.order_purchase_timestamp) AS period,
            COUNT(DISTINCT oi.order_id) AS order_count,
            ROUND(SUM(oi.price), 2) AS revenue,
            ROUND(SUM(oi.freight_value), 2) AS freight_revenue,
            ROUND(SUM(oi.price + oi.freight_value), 2) AS total_gmv,
            ROUND(AVG(oi.price), 2) AS avg_order_value,
            COUNT(DISTINCT o.customer_id) AS unique_customers
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        WHERE oi.seller_id = p_seller_id
          AND o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
          AND o.order_status = 'delivered'
        GROUP BY DATE(o.order_purchase_timestamp)
        ORDER BY period;
    END IF;
END$

-- =====================================================
-- 3. GET SELLER PRODUCT PERFORMANCE
-- Returns performance metrics for each product sold
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_seller_product_performance$
CREATE PROCEDURE sp_get_seller_product_performance(
    IN p_seller_id TEXT,
    IN p_start_date DATETIME,
    IN p_end_date DATETIME,
    IN p_limit INT
)
BEGIN
    SELECT 
        p.product_id,
        p.product_category_name,
        pct.product_category_name_english,
        COUNT(DISTINCT oi.order_id) AS orders_count,
        COUNT(oi.order_item_id) AS units_sold,
        ROUND(SUM(oi.price), 2) AS total_revenue,
        ROUND(AVG(oi.price), 2) AS avg_price,
        ROUND(SUM(oi.freight_value), 2) AS total_freight,
        ROUND(AVG(oi.freight_value), 2) AS avg_freight,
        COUNT(DISTINCT r.review_id) AS review_count,
        ROUND(AVG(r.review_score), 2) AS avg_rating,
        SUM(CASE WHEN r.review_score >= 4 THEN 1 ELSE 0 END) AS positive_reviews,
        SUM(CASE WHEN r.review_score <= 2 THEN 1 ELSE 0 END) AS negative_reviews,
        p.product_weight_g,
        p.product_length_cm,
        p.product_height_cm,
        p.product_width_cm
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN product_category pct ON p.product_category_name = pct.product_category_name
    LEFT JOIN order_reviews r ON o.order_id = r.order_id
    WHERE oi.seller_id = p_seller_id
      AND o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
      AND o.order_status = 'delivered'
    GROUP BY p.product_id, p.product_category_name, pct.product_category_name_english,
             p.product_weight_g, p.product_length_cm, p.product_height_cm, p.product_width_cm
    ORDER BY total_revenue DESC
    LIMIT p_limit;
END$

-- =====================================================
-- 4. GET SELLER CATEGORY PERFORMANCE
-- Returns aggregated metrics by product category
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_seller_category_performance$
CREATE PROCEDURE sp_get_seller_category_performance(
    IN p_seller_id TEXT,
    IN p_start_date DATETIME,
    IN p_end_date DATETIME
)
BEGIN
    SELECT 
        COALESCE(pct.product_category_name_english, 'Uncategorized') AS category,
        COUNT(DISTINCT oi.order_id) AS order_count,
        COUNT(DISTINCT oi.product_id) AS product_count,
        ROUND(SUM(oi.price), 2) AS total_revenue,
        ROUND(AVG(oi.price), 2) AS avg_item_price,
        ROUND(SUM(oi.freight_value), 2) AS total_freight,
        ROUND(AVG(oi.freight_value), 2) AS avg_freight,
        COUNT(DISTINCT r.review_id) AS review_count,
        ROUND(AVG(r.review_score), 2) AS avg_rating,
        ROUND(100.0 * SUM(CASE WHEN r.review_score >= 4 THEN 1 ELSE 0 END) / 
              NULLIF(COUNT(DISTINCT r.review_id), 0), 2) AS positive_review_pct
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN product_category pct ON p.product_category_name = pct.product_category_name
    LEFT JOIN order_reviews r ON o.order_id = r.order_id
    WHERE oi.seller_id = p_seller_id
      AND o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
      AND o.order_status = 'delivered'
    GROUP BY category
    ORDER BY total_revenue DESC;
END$

-- =====================================================
-- 5. GET SELLER DELIVERY PERFORMANCE
-- Returns delivery metrics and on-time performance
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_seller_delivery_performance$
CREATE PROCEDURE sp_get_seller_delivery_performance(
    IN p_seller_id TEXT,
    IN p_start_date DATETIME,
    IN p_end_date DATETIME
)
BEGIN
    SELECT 
        COUNT(DISTINCT o.order_id) AS total_delivered_orders,
        ROUND(AVG(DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp)), 1) AS avg_delivery_days,
        ROUND(AVG(DATEDIFF(o.order_estimated_delivery_date, o.order_purchase_timestamp)), 1) AS avg_estimated_days,
        ROUND(AVG(DATEDIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date)), 1) AS avg_vs_estimate,
        SUM(CASE WHEN o.order_delivered_customer_date < o.order_estimated_delivery_date THEN 1 ELSE 0 END) AS early_deliveries,
        SUM(CASE WHEN DATE(o.order_delivered_customer_date) = DATE(o.order_estimated_delivery_date) THEN 1 ELSE 0 END) AS on_time_deliveries,
        SUM(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 ELSE 0 END) AS late_deliveries,
        ROUND(100.0 * SUM(CASE WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date THEN 1 ELSE 0 END) / 
              COUNT(*), 2) AS on_time_rate_pct,
        ROUND(AVG(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date 
                       THEN DATEDIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date) END), 1) AS avg_delay_when_late,
        ROUND(AVG(r.review_score), 2) AS avg_review_score_all,
        ROUND(AVG(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date 
                       THEN r.review_score END), 2) AS avg_review_score_late,
        ROUND(AVG(CASE WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date 
                       THEN r.review_score END), 2) AS avg_review_score_on_time
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    LEFT JOIN order_reviews r ON o.order_id = r.order_id
    WHERE oi.seller_id = p_seller_id
      AND o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
      AND o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL;
END$

-- =====================================================
-- 6. GET SELLER GEOGRAPHIC DISTRIBUTION
-- Returns customer distribution by state and city
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_seller_geographic_distribution$
CREATE PROCEDURE sp_get_seller_geographic_distribution(
    IN p_seller_id TEXT,
    IN p_start_date DATETIME,
    IN p_end_date DATETIME,
    IN p_group_by VARCHAR(10) -- 'state' or 'city'
)
BEGIN
    IF p_group_by = 'state' THEN
        SELECT 
            c.customer_state AS location,
            COUNT(DISTINCT o.order_id) AS order_count,
            COUNT(DISTINCT o.customer_id) AS customer_count,
            ROUND(SUM(oi.price), 2) AS total_revenue,
            ROUND(AVG(oi.price), 2) AS avg_order_value,
            ROUND(AVG(DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp)), 1) AS avg_delivery_days,
            ROUND(AVG(r.review_score), 2) AS avg_rating
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        LEFT JOIN order_reviews r ON o.order_id = r.order_id
        WHERE oi.seller_id = p_seller_id
          AND o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
          AND o.order_status = 'delivered'
        GROUP BY c.customer_state
        ORDER BY total_revenue DESC;
    ELSE
        SELECT 
            c.customer_city AS location,
            c.customer_state AS state,
            COUNT(DISTINCT o.order_id) AS order_count,
            COUNT(DISTINCT o.customer_id) AS customer_count,
            ROUND(SUM(oi.price), 2) AS total_revenue,
            ROUND(AVG(oi.price), 2) AS avg_order_value,
            ROUND(AVG(DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp)), 1) AS avg_delivery_days,
            ROUND(AVG(r.review_score), 2) AS avg_rating
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        LEFT JOIN order_reviews r ON o.order_id = r.order_id
        WHERE oi.seller_id = p_seller_id
          AND o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
          AND o.order_status = 'delivered'
        GROUP BY c.customer_city, c.customer_state
        HAVING order_count >= 3
        ORDER BY total_revenue DESC
        LIMIT 50;
    END IF;
END$

-- =====================================================
-- 7. GET SELLER REVIEW DETAILS
-- Returns detailed review information with sentiment
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_seller_review_details$
CREATE PROCEDURE sp_get_seller_review_details(
    IN p_seller_id TEXT,
    IN p_start_date DATETIME,
    IN p_end_date DATETIME,
    IN p_min_score INT,
    IN p_max_score INT,
    IN p_limit INT
)
BEGIN
    SELECT 
        r.review_id,
        r.order_id,
        o.order_purchase_timestamp,
        r.review_score,
        r.review_comment_title,
        r.review_comment_message,
        r.review_text_english,
        r.predicted_sentiment,
        r.sentiment_confidence,
        r.is_aligned,
        r.review_creation_date,
        r.review_answer_timestamp,
        c.customer_city,
        c.customer_state,
        p.product_category_name,
        pct.product_category_name_english,
        oi.price AS item_price,
        DATEDIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date) AS delivery_vs_estimate,
        CASE 
            WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 'Late'
            WHEN o.order_delivered_customer_date < o.order_estimated_delivery_date THEN 'Early'
            ELSE 'On Time'
        END AS delivery_status
    FROM order_reviews r
    JOIN orders o ON r.order_id = o.order_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN product_category pct ON p.product_category_name = pct.product_category_name
    WHERE oi.seller_id = p_seller_id
      AND o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
      AND r.review_score BETWEEN p_min_score AND p_max_score
      AND o.order_status = 'delivered'
    ORDER BY r.review_creation_date DESC
    LIMIT p_limit;
END$

-- =====================================================
-- 8. GET SELLER REVIEW SUMMARY
-- Returns review distribution and trends
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_seller_review_summary$
CREATE PROCEDURE sp_get_seller_review_summary(
    IN p_seller_id TEXT,
    IN p_start_date DATETIME,
    IN p_end_date DATETIME
)
BEGIN
    SELECT 
        COUNT(DISTINCT r.review_id) AS total_reviews,
        ROUND(AVG(r.review_score), 2) AS avg_score,
        SUM(CASE WHEN r.review_score = 5 THEN 1 ELSE 0 END) AS five_star,
        SUM(CASE WHEN r.review_score = 4 THEN 1 ELSE 0 END) AS four_star,
        SUM(CASE WHEN r.review_score = 3 THEN 1 ELSE 0 END) AS three_star,
        SUM(CASE WHEN r.review_score = 2 THEN 1 ELSE 0 END) AS two_star,
        SUM(CASE WHEN r.review_score = 1 THEN 1 ELSE 0 END) AS one_star,
        ROUND(100.0 * SUM(CASE WHEN r.review_score = 5 THEN 1 ELSE 0 END) / COUNT(*), 2) AS five_star_pct,
        ROUND(100.0 * SUM(CASE WHEN r.review_score >= 4 THEN 1 ELSE 0 END) / COUNT(*), 2) AS positive_pct,
        ROUND(100.0 * SUM(CASE WHEN r.review_score <= 2 THEN 1 ELSE 0 END) / COUNT(*), 2) AS negative_pct,
        SUM(CASE WHEN r.review_comment_message IS NOT NULL AND r.review_comment_message != '' THEN 1 ELSE 0 END) AS reviews_with_comments,
        ROUND(100.0 * SUM(CASE WHEN r.review_comment_message IS NOT NULL AND r.review_comment_message != '' THEN 1 ELSE 0 END) / 
              COUNT(*), 2) AS comment_rate_pct,
        SUM(CASE WHEN r.predicted_sentiment = 'positive' THEN 1 ELSE 0 END) AS positive_sentiment_count,
        SUM(CASE WHEN r.predicted_sentiment = 'negative' THEN 1 ELSE 0 END) AS negative_sentiment_count,
        SUM(CASE WHEN r.predicted_sentiment = 'neutral' THEN 1 ELSE 0 END) AS neutral_sentiment_count,
        ROUND(AVG(r.sentiment_confidence), 2) AS avg_sentiment_confidence
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN order_reviews r ON o.order_id = r.order_id
    WHERE oi.seller_id = p_seller_id
      AND o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
      AND o.order_status = 'delivered';
END$

-- =====================================================
-- 9. GET SELLER COMPETITOR COMPARISON
-- Compares seller with others in same state/category
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_seller_competitor_comparison$
CREATE PROCEDURE sp_get_seller_competitor_comparison(
    IN p_seller_id TEXT,
    IN p_comparison_type VARCHAR(20), -- 'state' or 'category'
    IN p_start_date DATETIME,
    IN p_end_date DATETIME
)
BEGIN
    -- Get seller's state and primary category
    DECLARE v_seller_state TEXT;
    DECLARE v_primary_category TEXT;
    
    SELECT seller_state INTO v_seller_state
    FROM sellers WHERE seller_id = p_seller_id;
    
    SELECT p.product_category_name INTO v_primary_category
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    WHERE oi.seller_id = p_seller_id
    GROUP BY p.product_category_name
    ORDER BY COUNT(*) DESC
    LIMIT 1;
    
    IF p_comparison_type = 'state' THEN
        SELECT 
            s.seller_id,
            s.seller_city,
            CASE WHEN s.seller_id = p_seller_id THEN 'YOU' ELSE '' END AS is_current_seller,
            COUNT(DISTINCT oi.order_id) AS order_count,
            ROUND(SUM(oi.price), 2) AS total_revenue,
            ROUND(AVG(r.review_score), 2) AS avg_rating,
            ROUND(AVG(DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp)), 1) AS avg_delivery_days,
            COUNT(DISTINCT c.customer_state) AS states_served
        FROM sellers s
        JOIN order_items oi ON s.seller_id = oi.seller_id
        JOIN orders o ON oi.order_id = o.order_id
        LEFT JOIN order_reviews r ON o.order_id = r.order_id
        LEFT JOIN customers c ON o.customer_id = c.customer_id
        WHERE s.seller_state = v_seller_state
          AND o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
          AND o.order_status = 'delivered'
        GROUP BY s.seller_id, s.seller_city
        HAVING order_count >= 5
        ORDER BY total_revenue DESC
        LIMIT 20;
    ELSE
        SELECT 
            s.seller_id,
            s.seller_city,
            s.seller_state,
            CASE WHEN s.seller_id = p_seller_id THEN 'YOU' ELSE '' END AS is_current_seller,
            COUNT(DISTINCT oi.order_id) AS order_count,
            ROUND(SUM(oi.price), 2) AS total_revenue,
            ROUND(AVG(r.review_score), 2) AS avg_rating,
            ROUND(AVG(DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp)), 1) AS avg_delivery_days
        FROM sellers s
        JOIN order_items oi ON s.seller_id = oi.seller_id
        JOIN orders o ON oi.order_id = o.order_id
        JOIN products p ON oi.product_id = p.product_id
        LEFT JOIN order_reviews r ON o.order_id = r.order_id
        WHERE p.product_category_name = v_primary_category
          AND o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
          AND o.order_status = 'delivered'
        GROUP BY s.seller_id, s.seller_city, s.seller_state
        HAVING order_count >= 5
        ORDER BY total_revenue DESC
        LIMIT 20;
    END IF;
END$

-- =====================================================
-- 10. GET SELLER CUSTOMER RETENTION
-- Analyzes repeat customer behavior
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_seller_customer_retention$
CREATE PROCEDURE sp_get_seller_customer_retention(
    IN p_seller_id TEXT,
    IN p_start_date DATETIME,
    IN p_end_date DATETIME
)
BEGIN
    WITH CustomerPurchases AS (
        SELECT 
            o.customer_id,
            COUNT(DISTINCT o.order_id) AS purchase_count,
            MIN(o.order_purchase_timestamp) AS first_purchase,
            MAX(o.order_purchase_timestamp) AS last_purchase,
            SUM(oi.price) AS total_spent
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        WHERE oi.seller_id = p_seller_id
          AND o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
          AND o.order_status = 'delivered'
        GROUP BY o.customer_id
    )
    SELECT 
        COUNT(*) AS total_customers,
        SUM(CASE WHEN purchase_count = 1 THEN 1 ELSE 0 END) AS one_time_customers,
        SUM(CASE WHEN purchase_count >= 2 THEN 1 ELSE 0 END) AS repeat_customers,
        ROUND(100.0 * SUM(CASE WHEN purchase_count >= 2 THEN 1 ELSE 0 END) / COUNT(*), 2) AS repeat_customer_rate,
        ROUND(AVG(purchase_count), 2) AS avg_purchases_per_customer,
        ROUND(AVG(total_spent), 2) AS avg_customer_lifetime_value,
        ROUND(AVG(CASE WHEN purchase_count >= 2 THEN DATEDIFF(last_purchase, first_purchase) END), 1) AS avg_days_between_purchases
    FROM CustomerPurchases;
END$

-- =====================================================
-- 11. GET SELLER RECENT ORDERS
-- Returns recent order details for monitoring
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_seller_recent_orders$
CREATE PROCEDURE sp_get_seller_recent_orders(
    IN p_seller_id TEXT,
    IN p_limit INT
)
BEGIN
    SELECT 
        o.order_id,
        o.order_purchase_timestamp,
        o.order_status,
        c.customer_city,
        c.customer_state,
        COUNT(oi.order_item_id) AS items_count,
        ROUND(SUM(oi.price), 2) AS order_value,
        ROUND(SUM(oi.freight_value), 2) AS freight_value,
        MAX(oi.shipping_limit_date) AS shipping_limit_date,
        o.order_estimated_delivery_date,
        o.order_delivered_customer_date,
        r.review_score,
        CASE 
            WHEN o.order_delivered_customer_date IS NULL AND o.order_estimated_delivery_date < NOW() THEN 'OVERDUE'
            WHEN o.order_delivered_customer_date IS NULL THEN 'IN TRANSIT'
            WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 'DELIVERED LATE'
            ELSE 'DELIVERED ON TIME'
        END AS delivery_status
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN customers c ON o.customer_id = c.customer_id
    LEFT JOIN order_reviews r ON o.order_id = r.order_id
    WHERE oi.seller_id = p_seller_id
    GROUP BY o.order_id, o.order_purchase_timestamp, o.order_status, 
             c.customer_city, c.customer_state,
             o.order_estimated_delivery_date, o.order_delivered_customer_date, r.review_score
    ORDER BY o.order_purchase_timestamp DESC
    LIMIT p_limit;
END$

-- =====================================================
-- 12. GET SELLER PAYMENT METHODS ANALYSIS
-- Analyzes payment method preferences
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_seller_payment_analysis$
CREATE PROCEDURE sp_get_seller_payment_analysis(
    IN p_seller_id TEXT,
    IN p_start_date DATETIME,
    IN p_end_date DATETIME
)
BEGIN
    SELECT 
        op.payment_type,
        COUNT(DISTINCT o.order_id) AS order_count,
        ROUND(AVG(op.payment_installments), 1) AS avg_installments,
        ROUND(SUM(op.payment_value), 2) AS total_payment_value,
        ROUND(AVG(op.payment_value), 2) AS avg_payment_value,
        ROUND(100.0 * COUNT(DISTINCT o.order_id) / 
              (SELECT COUNT(DISTINCT o2.order_id) 
               FROM order_items oi2 
               JOIN orders o2 ON oi2.order_id = o2.order_id
               WHERE oi2.seller_id = p_seller_id
                 AND o2.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
                 AND o2.order_status = 'delivered'), 2) AS payment_method_pct
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN order_payments op ON o.order_id = op.order_id
    WHERE oi.seller_id = p_seller_id
      AND o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
      AND o.order_status = 'delivered'
    GROUP BY op.payment_type
    ORDER BY order_count DESC;
END$

-- =====================================================
-- 13. GET SELLER SENTIMENT ANALYSIS
-- Analyzes sentiment from review comments
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_seller_sentiment_analysis$
CREATE PROCEDURE sp_get_seller_sentiment_analysis(
    IN p_seller_id TEXT,
    IN p_start_date DATETIME,
    IN p_end_date DATETIME
)
BEGIN
    SELECT 
        r.predicted_sentiment,
        COUNT(DISTINCT r.review_id) AS review_count,
        ROUND(AVG(r.review_score), 2) AS avg_review_score,
        ROUND(AVG(r.sentiment_confidence), 2) AS avg_confidence,
        ROUND(100.0 * COUNT(DISTINCT r.review_id) / 
              (SELECT COUNT(DISTINCT r2.review_id)
               FROM order_items oi2
               JOIN orders o2 ON oi2.order_id = o2.order_id
               JOIN order_reviews r2 ON o2.order_id = r2.order_id
               WHERE oi2.seller_id = p_seller_id
                 AND o2.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
                 AND o2.order_status = 'delivered'
                 AND r2.predicted_sentiment IS NOT NULL), 2) AS sentiment_pct,
        SUM(CASE WHEN r.is_aligned = 'yes' THEN 1 ELSE 0 END) AS aligned_count,
        ROUND(100.0 * SUM(CASE WHEN r.is_aligned = 'yes' THEN 1 ELSE 0 END) / 
              COUNT(*), 2) AS alignment_rate_pct
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN order_reviews r ON o.order_id = r.order_id
    WHERE oi.seller_id = p_seller_id
      AND o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
      AND o.order_status = 'delivered'
      AND r.predicted_sentiment IS NOT NULL
    GROUP BY r.predicted_sentiment
    ORDER BY review_count DESC;
END$

-- =====================================================
-- 14. GET SELLER TOP CUSTOMER CITIES
-- Returns top cities by revenue and order volume
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_seller_top_customer_cities$
CREATE PROCEDURE sp_get_seller_top_customer_cities(
    IN p_seller_id TEXT,
    IN p_start_date DATETIME,
    IN p_end_date DATETIME,
    IN p_limit INT
)
BEGIN
    SELECT 
        c.customer_city,
        c.customer_state,
        COUNT(DISTINCT o.order_id) AS order_count,
        COUNT(DISTINCT o.customer_id) AS customer_count,
        ROUND(SUM(oi.price), 2) AS total_revenue,
        ROUND(AVG(oi.price), 2) AS avg_order_value,
        ROUND(SUM(oi.freight_value), 2) AS total_freight,
        ROUND(AVG(r.review_score), 2) AS avg_rating,
        ROUND(AVG(DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp)), 1) AS avg_delivery_days,
        SUM(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 ELSE 0 END) AS late_deliveries,
        ROUND(100.0 * SUM(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 ELSE 0 END) / 
              COUNT(DISTINCT o.order_id), 2) AS late_delivery_pct
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN customers c ON o.customer_id = c.customer_id
    LEFT JOIN order_reviews r ON o.order_id = r.order_id
    WHERE oi.seller_id = p_seller_id
      AND o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
      AND o.order_status = 'delivered'
    GROUP BY c.customer_city, c.customer_state
    ORDER BY total_revenue DESC
    LIMIT p_limit;
END$

-- =====================================================
-- 15. GET SELLER PERFORMANCE SCORE
-- Calculates comprehensive performance score
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_seller_performance_score$
CREATE PROCEDURE sp_get_seller_performance_score(
    IN p_seller_id TEXT,
    IN p_start_date DATETIME,
    IN p_end_date DATETIME
)
BEGIN
    WITH SellerMetrics AS (
        SELECT 
            COUNT(DISTINCT o.order_id) AS total_orders,
            ROUND(AVG(r.review_score), 2) AS avg_rating,
            ROUND(100.0 * SUM(CASE WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date THEN 1 ELSE 0 END) / 
                  NULLIF(COUNT(DISTINCT CASE WHEN o.order_delivered_customer_date IS NOT NULL THEN o.order_id END), 0), 2) AS on_time_pct,
            COUNT(DISTINCT p.product_category_name) AS category_diversity,
            ROUND(SUM(oi.price), 2) AS total_revenue
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN products p ON oi.product_id = p.product_id
        LEFT JOIN order_reviews r ON o.order_id = r.order_id
        WHERE oi.seller_id = p_seller_id
          AND o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
          AND o.order_status = 'delivered'
    )
    SELECT 
        total_orders,
        avg_rating,
        on_time_pct,
        category_diversity,
        total_revenue,
        -- Composite performance score (0-100)
        ROUND(
            (COALESCE(avg_rating, 3) / 5.0) * 40 +                    -- 40% weight on customer satisfaction
            (COALESCE(on_time_pct, 50) / 100.0) * 30 +                -- 30% weight on delivery performance
            LEAST(total_orders / 100.0, 1) * 20 +                     -- 20% weight on volume
            LEAST(category_diversity / 10.0, 1) * 10,                 -- 10% weight on diversity
        2) AS performance_score,
        CASE 
            WHEN (COALESCE(avg_rating, 3) / 5.0) * 40 + (COALESCE(on_time_pct, 50) / 100.0) * 30 + 
                 LEAST(total_orders / 100.0, 1) * 20 + LEAST(category_diversity / 10.0, 1) * 10 >= 80 THEN 'Excellent'
            WHEN (COALESCE(avg_rating, 3) / 5.0) * 40 + (COALESCE(on_time_pct, 50) / 100.0) * 30 + 
                 LEAST(total_orders / 100.0, 1) * 20 + LEAST(category_diversity / 10.0, 1) * 10 >= 60 THEN 'Good'
            WHEN (COALESCE(avg_rating, 3) / 5.0) * 40 + (COALESCE(on_time_pct, 50) / 100.0) * 30 + 
                 LEAST(total_orders / 100.0, 1) * 20 + LEAST(category_diversity / 10.0, 1) * 10 >= 40 THEN 'Average'
            ELSE 'Needs Improvement'
        END AS performance_grade
    FROM SellerMetrics;
END$

-- =====================================================
-- 16. GET CUSTOMER GEOGRAPHIC DISTRIBUTION
-- Answers Question 1: Distribution of customers across Brazilian states
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_customer_geographic_distribution$
CREATE PROCEDURE sp_get_customer_geographic_distribution(
    IN p_start_date DATETIME,
    IN p_end_date DATETIME
)
BEGIN
    -- State-level distribution
    SELECT 
        c.customer_state AS state,
        COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
        COUNT(DISTINCT c.customer_id) AS customer_records,
        COUNT(DISTINCT o.order_id) AS total_orders,
        ROUND(COUNT(DISTINCT o.order_id) * 1.0 / 
              NULLIF(COUNT(DISTINCT c.customer_unique_id), 0), 2) AS orders_per_customer,
        ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue,
        ROUND(AVG(oi.price + oi.freight_value), 2) AS avg_order_value,
        COUNT(DISTINCT c.customer_city) AS cities_count,
        ROUND(AVG(r.review_score), 2) AS avg_satisfaction_score
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    LEFT JOIN order_items oi ON o.order_id = oi.order_id
    LEFT JOIN order_reviews r ON o.order_id = r.order_id
    WHERE o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
      AND o.order_status = 'delivered'
    GROUP BY c.customer_state
    ORDER BY total_orders DESC;
END$

-- =====================================================
-- 17. GET_TOP_CITIES_BY_ORDER_VOLUME
-- Returns top cities with highest concentration of orders
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_top_cities_by_order_volume$
CREATE PROCEDURE sp_get_top_cities_by_order_volume(
    IN p_start_date DATETIME,
    IN p_end_date DATETIME,
    IN p_limit INT
)
BEGIN
    SELECT
        c.customer_city AS city,
        c.customer_state AS state,
        COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
        COUNT(DISTINCT o.order_id) AS total_orders,
        ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue,
        ROUND(AVG(oi.price + oi.freight_value), 2) AS avg_order_value,
        ROUND(AVG(r.review_score), 2) AS avg_satisfaction_score,
        ROUND(AVG(DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp)), 1) AS avg_delivery_days
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    LEFT JOIN order_items oi ON o.order_id = oi.order_id
    LEFT JOIN order_reviews r ON o.order_id = r.order_id
    WHERE o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
      AND o.order_status = 'delivered'
    GROUP BY c.customer_city, c.customer_state
    HAVING total_orders >= 10
    ORDER BY total_orders DESC
    LIMIT p_limit;
END$

-- =====================================================
-- 18. GET_CUSTOMER_LIFETIME_VALUE_ANALYSIS
-- Answers Question 2: Customer lifetime value segmentation
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_customer_lifetime_value_analysis$
CREATE PROCEDURE sp_get_customer_lifetime_value_analysis(
    IN p_start_date DATETIME,
    IN p_end_date DATETIME
)
BEGIN
    WITH CustomerMetrics AS (
        SELECT
            c.customer_unique_id,
            c.customer_state,
            COUNT(DISTINCT o.order_id) AS total_orders,
            MIN(o.order_purchase_timestamp) AS first_purchase,
            MAX(o.order_purchase_timestamp) AS last_purchase,
            DATEDIFF(MAX(o.order_purchase_timestamp), MIN(o.order_purchase_timestamp)) AS lifespan_days,
            ROUND(SUM(oi.price + oi.freight_value), 2) AS lifetime_value,
            ROUND(AVG(oi.price + oi.freight_value), 2) AS avg_order_value,
            ROUND(AVG(r.review_score), 2) AS avg_review_score
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        LEFT JOIN order_reviews r ON o.order_id = r.order_id
        WHERE o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
          AND o.order_status = 'delivered'
        GROUP BY c.customer_unique_id, c.customer_state
    )
    SELECT
        CASE
            WHEN total_orders = 1 THEN 'One-time buyer'
            WHEN total_orders BETWEEN 2 AND 3 THEN 'Occasional buyer'
            WHEN total_orders >= 4 THEN 'Loyal customer'
            ELSE 'Unknown'
        END AS customer_segment,
        COUNT(*) AS customer_count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM CustomerMetrics), 2) AS segment_pct,
        ROUND(AVG(lifetime_value), 2) AS avg_lifetime_value,
        ROUND(AVG(avg_order_value), 2) AS avg_order_value,
        ROUND(AVG(total_orders), 2) AS avg_orders_per_customer,
        ROUND(AVG(lifespan_days), 1) AS avg_lifespan_days,
        ROUND(AVG(avg_review_score), 2) AS avg_satisfaction_score
    FROM CustomerMetrics
    GROUP BY customer_segment
    ORDER BY avg_lifetime_value DESC;
END$

-- =====================================================
-- 19. GET_TOP_CUSTOMERS_BY_LIFETIME_VALUE
-- Returns top customers by lifetime value
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_top_customers_by_lifetime_value$
CREATE PROCEDURE sp_get_top_customers_by_lifetime_value(
    IN p_start_date DATETIME,
    IN p_end_date DATETIME,
    IN p_limit INT
)
BEGIN
    SELECT
        c.customer_unique_id,
        c.customer_state,
        c.customer_city,
        COUNT(DISTINCT o.order_id) AS total_orders,
        ROUND(SUM(oi.price + oi.freight_value), 2) AS lifetime_value,
        ROUND(AVG(oi.price + oi.freight_value), 2) AS avg_order_value,
        MIN(o.order_purchase_timestamp) AS first_purchase,
        MAX(o.order_purchase_timestamp) AS last_purchase,
        ROUND(AVG(r.review_score), 2) AS avg_review_score,
        ROUND(AVG(DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp)), 1) AS avg_delivery_days
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    LEFT JOIN order_reviews r ON o.order_id = r.order_id
    WHERE o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
      AND o.order_status = 'delivered'
    GROUP BY c.customer_unique_id, c.customer_state, c.customer_city
    ORDER BY lifetime_value DESC
    LIMIT p_limit;
END$

-- =====================================================
-- 20. GET_REPEAT_PURCHASE_ANALYSIS
-- Answers Question 3: Repeat purchase analysis
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_repeat_purchase_analysis$
CREATE PROCEDURE sp_get_repeat_purchase_analysis(
    IN p_start_date DATETIME,
    IN p_end_date DATETIME
)
BEGIN
    WITH CustomerPurchases AS (
        SELECT
            c.customer_unique_id,
            c.customer_state,
            o.order_id,
            o.order_purchase_timestamp,
            ROW_NUMBER() OVER (
                PARTITION BY c.customer_unique_id
                ORDER BY o.order_purchase_timestamp
            ) AS purchase_number
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        WHERE o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
          AND o.order_status IN ('delivered', 'shipped', 'invoiced')
    ),
    FirstTwoOrders AS (
        SELECT
            cp1.customer_unique_id,
            cp1.customer_state,
            cp1.order_purchase_timestamp AS first_purchase,
            cp2.order_purchase_timestamp AS second_purchase,
            DATEDIFF(cp2.order_purchase_timestamp, cp1.order_purchase_timestamp) AS days_between
        FROM CustomerPurchases cp1
        LEFT JOIN CustomerPurchases cp2
            ON cp1.customer_unique_id = cp2.customer_unique_id
            AND cp2.purchase_number = 2
        WHERE cp1.purchase_number = 1
    )
    SELECT
        'Overall' AS segment,
        COUNT(*) AS total_customers,
        SUM(CASE WHEN second_purchase IS NOT NULL THEN 1 ELSE 0 END) AS repeat_customers,
        ROUND(100.0 * SUM(CASE WHEN second_purchase IS NOT NULL THEN 1 ELSE 0 END) / 
              COUNT(*), 2) AS repeat_purchase_rate_pct,
        ROUND(AVG(days_between), 1) AS avg_days_to_second_purchase,
        MIN(days_between) AS min_days_between,
        MAX(days_between) AS max_days_between
    FROM FirstTwoOrders
    UNION ALL
    SELECT
        customer_state AS segment,
        COUNT(*) AS total_customers,
        SUM(CASE WHEN second_purchase IS NOT NULL THEN 1 ELSE 0 END) AS repeat_customers,
        ROUND(100.0 * SUM(CASE WHEN second_purchase IS NOT NULL THEN 1 ELSE 0 END) / 
              COUNT(*), 2) AS repeat_purchase_rate_pct,
        ROUND(AVG(days_between), 1) AS avg_days_to_second_purchase,
        MIN(days_between) AS min_days_between,
        MAX(days_between) AS max_days_between
    FROM FirstTwoOrders
    WHERE customer_state IS NOT NULL
    GROUP BY customer_state
    HAVING total_customers >= 50
    ORDER BY repeat_purchase_rate_pct DESC;
END$

-- =====================================================
-- 21. GET_CUSTOMER_SATISFACTION_BY_STATE
-- Answers Question 4: Customer satisfaction by state
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_customer_satisfaction_by_state$
CREATE PROCEDURE sp_get_customer_satisfaction_by_state(
    IN p_start_date DATETIME,
    IN p_end_date DATETIME
)
BEGIN
    SELECT
        c.customer_state AS state,
        COUNT(DISTINCT o.order_id) AS total_orders_with_reviews,
        COUNT(DISTINCT c.customer_unique_id) AS customers_who_reviewed,
        ROUND(AVG(r.review_score), 2) AS avg_review_score,
        SUM(CASE WHEN r.review_score = 5 THEN 1 ELSE 0 END) AS five_star_reviews,
        SUM(CASE WHEN r.review_score <= 2 THEN 1 ELSE 0 END) AS poor_reviews,
        ROUND(100.0 * SUM(CASE WHEN r.review_score = 5 THEN 1 ELSE 0 END) / 
              COUNT(*), 2) AS pct_five_star,
        ROUND(100.0 * SUM(CASE WHEN r.review_score <= 2 THEN 1 ELSE 0 END) / 
              COUNT(*), 2) AS pct_poor_reviews,
        ROUND(AVG(DATEDIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date)), 1) AS avg_delivery_delay_days,
        SUM(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 ELSE 0 END) AS late_deliveries,
        ROUND(100.0 * SUM(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 ELSE 0 END) / 
              COUNT(*), 2) AS pct_late_deliveries
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_reviews r ON o.order_id = r.order_id
    WHERE o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
      AND o.order_status = 'delivered'
    GROUP BY c.customer_state
    HAVING total_orders_with_reviews >= 50
    ORDER BY avg_review_score DESC;
END$

-- =====================================================
-- 22. GET_PURCHASE_FREQUENCY_PATTERNS
-- Answers Question 5: Purchase frequency patterns by city size
-- Fixed for MySQL compatibility (no PERCENTILE_CONT)
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_purchase_frequency_patterns$
CREATE PROCEDURE sp_get_purchase_frequency_patterns(
    IN p_start_date DATETIME,
    IN p_end_date DATETIME
)
BEGIN
    WITH RepeatCustomers AS (
        SELECT
            c.customer_unique_id,
            c.customer_city,
            c.customer_state,
            COUNT(DISTINCT o.order_id) AS purchase_count,
            CASE 
                WHEN c.customer_city IN ('sao paulo', 'rio de janeiro', 'brasilia', 
                                         'salvador', 'fortaleza', 'belo horizonte',
                                         'curitiba', 'manaus', 'recife', 'porto alegre',
                                         'belem', 'goiania', 'guarulhos', 'campinas') 
                THEN 'Metro City'
                ELSE 'Smaller City'
            END AS city_size_category
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        WHERE o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
          AND o.order_status = 'delivered'
        GROUP BY c.customer_unique_id, c.customer_city, c.customer_state
        HAVING purchase_count >= 2
    ),
    OrderSequences AS (
        SELECT
            c.customer_unique_id,
            o.order_id,
            o.order_purchase_timestamp,
            rc.city_size_category,
            LAG(o.order_purchase_timestamp) OVER (
                PARTITION BY c.customer_unique_id 
                ORDER BY o.order_purchase_timestamp
            ) AS previous_order_date
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN RepeatCustomers rc ON c.customer_unique_id = rc.customer_unique_id
        WHERE o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
          AND o.order_status = 'delivered'
    ),
    DaysBetweenOrders AS (
        SELECT
            city_size_category,
            DATEDIFF(order_purchase_timestamp, previous_order_date) AS days_between
        FROM OrderSequences
        WHERE previous_order_date IS NOT NULL
    ),
    RankedDays AS (
        SELECT
            city_size_category,
            days_between,
            ROW_NUMBER() OVER (PARTITION BY city_size_category ORDER BY days_between) AS row_num,
            COUNT(*) OVER (PARTITION BY city_size_category) AS total_count
        FROM DaysBetweenOrders
    )
    SELECT
        d.city_size_category,
        COUNT(DISTINCT os.customer_unique_id) AS repeat_customers,
        ROUND(AVG(d.days_between), 1) AS avg_days_between_orders,
        MIN(d.days_between) AS min_days_between,
        MAX(d.days_between) AS max_days_between,
        AVG(CASE 
            WHEN r.row_num IN (FLOOR((r.total_count + 1) / 2), CEIL((r.total_count + 1) / 2)) 
            THEN r.days_between 
        END) AS median_days_between
    FROM DaysBetweenOrders d
    JOIN OrderSequences os ON d.city_size_category = os.city_size_category
    JOIN RankedDays r ON d.city_size_category = r.city_size_category AND d.days_between = r.days_between
    GROUP BY d.city_size_category
    ORDER BY avg_days_between_orders;
END$

-- =====================================================
-- 23. GET_TOP_SELLERS_BY_MULTIPLE_METRICS
-- Answers Question 6: Top performing sellers
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_top_sellers_by_multiple_metrics$
CREATE PROCEDURE sp_get_top_sellers_by_multiple_metrics(
    IN p_start_date DATETIME,
    IN p_end_date DATETIME,
    IN p_metric VARCHAR(20), -- 'revenue', 'orders', 'rating', 'performance'
    IN p_limit INT
)
BEGIN
    IF p_metric = 'revenue' THEN
        SELECT 
            s.seller_id,
            s.seller_city,
            s.seller_state,
            COUNT(DISTINCT oi.order_id) AS total_orders,
            COUNT(DISTINCT oi.product_id) AS unique_products,
            COUNT(DISTINCT p.product_category_name) AS categories_offered,
            ROUND(SUM(oi.price), 2) AS total_revenue,
            ROUND(AVG(oi.price), 2) AS avg_item_price,
            ROUND(SUM(oi.freight_value), 2) AS total_freight_charged,
            ROUND(SUM(oi.price + oi.freight_value), 2) AS total_gmv,
            COUNT(r.review_id) AS reviews_received,
            ROUND(AVG(r.review_score), 2) AS avg_review_score,
            COUNT(DISTINCT c.customer_state) AS customer_states_served,
            ROUND(AVG(DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp)), 1) AS avg_delivery_days
        FROM sellers s
        JOIN order_items oi ON s.seller_id = oi.seller_id
        JOIN orders o ON oi.order_id = o.order_id
        JOIN products p ON oi.product_id = p.product_id
        LEFT JOIN order_reviews r ON o.order_id = r.order_id
        LEFT JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
          AND o.order_status = 'delivered'
        GROUP BY s.seller_id, s.seller_city, s.seller_state
        HAVING total_orders >= 10
        ORDER BY total_revenue DESC
        LIMIT p_limit;
        
    ELSEIF p_metric = 'orders' THEN
        SELECT 
            s.seller_id,
            s.seller_city,
            s.seller_state,
            COUNT(DISTINCT oi.order_id) AS total_orders,
            COUNT(DISTINCT oi.product_id) AS unique_products,
            ROUND(SUM(oi.price), 2) AS total_revenue,
            ROUND(AVG(r.review_score), 2) AS avg_review_score,
            COUNT(DISTINCT c.customer_state) AS customer_states_served
        FROM sellers s
        JOIN order_items oi ON s.seller_id = oi.seller_id
        JOIN orders o ON oi.order_id = o.order_id
        LEFT JOIN order_reviews r ON o.order_id = r.order_id
        LEFT JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
          AND o.order_status = 'delivered'
        GROUP BY s.seller_id, s.seller_city, s.seller_state
        HAVING total_orders >= 10
        ORDER BY total_orders DESC
        LIMIT p_limit;
        
    ELSEIF p_metric = 'rating' THEN
        SELECT 
            s.seller_id,
            s.seller_city,
            s.seller_state,
            COUNT(DISTINCT oi.order_id) AS total_orders,
            ROUND(AVG(r.review_score), 2) AS avg_review_score,
            COUNT(r.review_id) AS reviews_received,
            SUM(CASE WHEN r.review_score = 5 THEN 1 ELSE 0 END) AS five_star_count,
            SUM(CASE WHEN r.review_score <= 2 THEN 1 ELSE 0 END) AS poor_review_count,
            ROUND(100.0 * SUM(CASE WHEN r.review_score = 5 THEN 1 ELSE 0 END) / 
                  NULLIF(COUNT(r.review_id), 0), 2) AS pct_five_star,
            ROUND(SUM(oi.price), 2) AS total_revenue
        FROM sellers s
        JOIN order_items oi ON s.seller_id = oi.seller_id
        JOIN orders o ON oi.order_id = o.order_id
        LEFT JOIN order_reviews r ON o.order_id = r.order_id
        WHERE o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
          AND o.order_status = 'delivered'
          AND r.review_score IS NOT NULL
        GROUP BY s.seller_id, s.seller_city, s.seller_state
        HAVING reviews_received >= 5
        ORDER BY avg_review_score DESC, reviews_received DESC
        LIMIT p_limit;
        
    ELSE -- performance (composite score)
        SELECT 
            s.seller_id,
            s.seller_city,
            s.seller_state,
            COUNT(DISTINCT oi.order_id) AS total_orders,
            ROUND(SUM(oi.price), 2) AS total_revenue,
            ROUND(AVG(r.review_score), 2) AS avg_review_score,
            COUNT(DISTINCT p.product_category_name) AS categories_offered,
            COUNT(DISTINCT c.customer_state) AS customer_states_served,
            ROUND(AVG(DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp)), 1) AS avg_delivery_days,
            ROUND(100.0 * SUM(CASE WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date THEN 1 ELSE 0 END) / 
                  NULLIF(COUNT(DISTINCT CASE WHEN o.order_delivered_customer_date IS NOT NULL THEN o.order_id END), 0), 2) AS on_time_rate_pct,
            -- Composite performance score
            ROUND(
                (COALESCE(AVG(r.review_score), 3) / 5.0) * 40 + -- 40% weight on satisfaction
                (COALESCE(100.0 * SUM(CASE WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date THEN 1 ELSE 0 END) / 
                  NULLIF(COUNT(DISTINCT CASE WHEN o.order_delivered_customer_date IS NOT NULL THEN o.order_id END), 0), 50) / 100.0) * 30 + -- 30% weight on delivery
                LEAST(COUNT(DISTINCT oi.order_id) / 100.0, 1) * 20 + -- 20% weight on volume
                LEAST(COUNT(DISTINCT p.product_category_name) / 10.0, 1) * 10, -- 10% weight on diversity
            2) AS performance_score
        FROM sellers s
        JOIN order_items oi ON s.seller_id = oi.seller_id
        JOIN orders o ON oi.order_id = o.order_id
        JOIN products p ON oi.product_id = p.product_id
        LEFT JOIN order_reviews r ON o.order_id = r.order_id
        LEFT JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
          AND o.order_status = 'delivered'
        GROUP BY s.seller_id, s.seller_city, s.seller_state
        HAVING total_orders >= 10
        ORDER BY performance_score DESC, total_revenue DESC
        LIMIT p_limit;
    END IF;
END$

-- =====================================================
-- 24. GET_SELLER_GEOGRAPHIC_COVERAGE
-- Answers Question 7: Seller geographic coverage
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_seller_geographic_coverage$
CREATE PROCEDURE sp_get_seller_geographic_coverage(
    IN p_start_date DATETIME,
    IN p_end_date DATETIME,
    IN p_limit INT
)
BEGIN
    SELECT 
        s.seller_id,
        s.seller_city,
        s.seller_state,
        COUNT(DISTINCT c.customer_state) AS states_served,
        COUNT(DISTINCT c.customer_city) AS cities_served,
        COUNT(DISTINCT o.order_id) AS total_orders,
        COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
        ROUND(SUM(oi.price), 2) AS total_revenue,
        ROUND(AVG(r.review_score), 2) AS avg_rating,
        GROUP_CONCAT(DISTINCT c.customer_state ORDER BY c.customer_state SEPARATOR ', ') AS states_list
    FROM sellers s
    JOIN order_items oi ON s.seller_id = oi.seller_id
    JOIN orders o ON oi.order_id = o.order_id
    JOIN customers c ON o.customer_id = c.customer_id
    LEFT JOIN order_reviews r ON o.order_id = r.order_id
    WHERE o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
      AND o.order_status = 'delivered'
    GROUP BY s.seller_id, s.seller_city, s.seller_state
    ORDER BY states_served DESC, total_revenue DESC
    LIMIT p_limit;
END$

-- =====================================================
-- 25. GET_PRODUCT_REVENUE_BY_CATEGORY
-- Answers Question 11: Product revenue by category
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_product_revenue_by_category$
CREATE PROCEDURE sp_get_product_revenue_by_category(
    IN p_start_date DATETIME,
    IN p_end_date DATETIME
)
BEGIN
    SELECT
        COALESCE(pct.product_category_name_english, p.product_category_name) AS category_name,
        COUNT(DISTINCT oi.order_id) AS total_orders,
        COUNT(DISTINCT oi.product_id) AS unique_products,
        SUM(oi.price) AS total_revenue,
        ROUND(SUM(oi.price) / NULLIF(COUNT(DISTINCT oi.order_id), 0), 2) AS avg_revenue_per_order,
        SUM(oi.freight_value) AS total_freight_cost,
        COUNT(DISTINCT oi.seller_id) AS unique_sellers,
        COUNT(DISTINCT o.customer_id) AS unique_customers
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN product_category_translation pct ON p.product_category_name = pct.product_category_name
    WHERE o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
      AND o.order_status = 'delivered'
    GROUP BY COALESCE(pct.product_category_name_english, p.product_category_name)
    ORDER BY total_revenue DESC;
END$

-- =====================================================
-- 26. GET_PRODUCT_DELIVERY_EFFICIENCY
-- Answers Question 12: Product delivery efficiency
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_product_delivery_efficiency$
CREATE PROCEDURE sp_get_product_delivery_efficiency(
    IN p_start_date DATETIME,
    IN p_end_date DATETIME
)
BEGIN
    SELECT
        COALESCE(pct.product_category_name_english, p.product_category_name) AS category_name,
        COUNT(DISTINCT oi.order_id) AS total_orders,
        ROUND(AVG(DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp)), 1) AS avg_delivery_days,
        ROUND(AVG(DATEDIFF(o.order_estimated_delivery_date, o.order_purchase_timestamp)), 1) AS avg_estimated_days,
        ROUND(AVG(DATEDIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date)), 1) AS avg_delivery_variance,
        SUM(CASE WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date THEN 1 ELSE 0 END) AS on_time_deliveries,
        SUM(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 ELSE 0 END) AS late_deliveries,
        ROUND(100.0 * SUM(CASE WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date THEN 1 ELSE 0 END) / 
              COUNT(*), 2) AS on_time_rate_pct,
        AVG(p.product_weight_g) AS avg_product_weight_g,
        AVG(oi.freight_value) AS avg_freight_cost
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN product_category_translation pct ON p.product_category_name = pct.product_category_name
    WHERE o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
      AND o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
    GROUP BY COALESCE(pct.product_category_name_english, p.product_category_name)
    HAVING total_orders >= 10
    ORDER BY avg_delivery_days;
END$

-- =====================================================
-- 27. GET_PRODUCT_FREIGHT_COST_ANALYSIS
-- Answers Question 13: Product freight cost analysis
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_product_freight_cost_analysis$
CREATE PROCEDURE sp_get_product_freight_cost_analysis(
    IN p_start_date DATETIME,
    IN p_end_date DATETIME
)
BEGIN
    SELECT
        COALESCE(pct.product_category_name_english, p.product_category_name) AS category_name,
        COUNT(DISTINCT oi.order_id) AS total_orders,
        ROUND(AVG(oi.freight_value), 2) AS avg_freight_cost,
        ROUND(AVG(oi.price), 2) AS avg_product_price,
        ROUND(AVG(oi.freight_value) / NULLIF(AVG(oi.price), 0) * 100, 2) AS freight_as_pct_of_price,
        ROUND(AVG(p.product_weight_g), 1) AS avg_product_weight_g,
        ROUND(AVG(p.product_length_cm * p.product_height_cm * p.product_width_cm), 1) AS avg_product_volume_cm3,
        ROUND(AVG(DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp)), 1) AS avg_delivery_days,
        COUNT(DISTINCT oi.seller_id) AS unique_sellers
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN product_category_translation pct ON p.product_category_name = pct.product_category_name
    WHERE o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
      AND o.order_status = 'delivered'
    GROUP BY COALESCE(pct.product_category_name_english, p.product_category_name)
    HAVING total_orders >= 10
    ORDER BY avg_freight_cost DESC;
END$

-- =====================================================
-- 28. GET_PRODUCT_SALES_VOLUME_RANKING
-- Answers Question 14: Product sales volume ranking
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_product_sales_volume_ranking$
CREATE PROCEDURE sp_get_product_sales_volume_ranking(
    IN p_start_date DATETIME,
    IN p_end_date DATETIME,
    IN p_limit INT
)
BEGIN
    SELECT
        p.product_id,
        COALESCE(pct.product_category_name_english, p.product_category_name) AS category_name,
        COUNT(DISTINCT oi.order_id) AS order_count,
        COUNT(oi.order_item_id) AS units_sold,
        ROUND(SUM(oi.price), 2) AS total_revenue,
        ROUND(AVG(oi.price), 2) AS avg_price,
        ROUND(AVG(oi.freight_value), 2) AS avg_freight_cost,
        COUNT(DISTINCT r.review_id) AS review_count,
        ROUND(AVG(r.review_score), 2) AS avg_rating,
        COUNT(DISTINCT oi.seller_id) AS unique_sellers,
        COUNT(DISTINCT o.customer_id) AS unique_customers
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN product_category_translation pct ON p.product_category_name = pct.product_category_name
    LEFT JOIN order_reviews r ON o.order_id = r.order_id
    WHERE o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
      AND o.order_status = 'delivered'
    GROUP BY p.product_id, COALESCE(pct.product_category_name_english, p.product_category_name)
    ORDER BY units_sold DESC
    LIMIT p_limit;
END$

-- =====================================================
-- 29. GET_PRODUCT_REVIEW_QUALITY
-- Answers Question 15: Product review quality by category
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_product_review_quality$
CREATE PROCEDURE sp_get_product_review_quality(
    IN p_start_date DATETIME,
    IN p_end_date DATETIME
)
BEGIN
    SELECT
        COALESCE(pct.product_category_name_english, p.product_category_name) AS category_name,
        COUNT(DISTINCT r.review_id) AS total_reviews,
        ROUND(AVG(r.review_score), 2) AS avg_review_score,
        SUM(CASE WHEN r.review_score = 5 THEN 1 ELSE 0 END) AS five_star_reviews,
        SUM(CASE WHEN r.review_score = 4 THEN 1 ELSE 0 END) AS four_star_reviews,
        SUM(CASE WHEN r.review_score = 3 THEN 1 ELSE 0 END) AS three_star_reviews,
        SUM(CASE WHEN r.review_score = 2 THEN 1 ELSE 0 END) AS two_star_reviews,
        SUM(CASE WHEN r.review_score = 1 THEN 1 ELSE 0 END) AS one_star_reviews,
        ROUND(100.0 * SUM(CASE WHEN r.review_score >= 4 THEN 1 ELSE 0 END) / 
              COUNT(*), 2) AS positive_review_pct,
        ROUND(100.0 * SUM(CASE WHEN r.review_score <= 2 THEN 1 ELSE 0 END) / 
              COUNT(*), 2) AS negative_review_pct,
        COUNT(DISTINCT oi.product_id) AS unique_products,
        COUNT(DISTINCT oi.order_id) AS total_orders,
        SUM(CASE WHEN r.review_comment_message IS NOT NULL AND r.review_comment_message != '' THEN 1 ELSE 0 END) AS reviews_with_comments
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN products p ON oi.product_id = p.product_id
    JOIN order_reviews r ON o.order_id = r.order_id
    LEFT JOIN product_category_translation pct ON p.product_category_name = pct.product_category_name
    WHERE o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
      AND o.order_status = 'delivered'
    GROUP BY COALESCE(pct.product_category_name_english, p.product_category_name)
    HAVING total_reviews >= 20
    ORDER BY avg_review_score DESC;
END$

-- =====================================================
-- 30. GET_SELLER_PRODUCT_DIVERSIFICATION
-- Answers Question 9: Seller product diversification
-- =====================================================
DROP PROCEDURE IF EXISTS sp_get_seller_product_diversification$
CREATE PROCEDURE sp_get_seller_product_diversification(
    IN p_start_date DATETIME,
    IN p_end_date DATETIME,
    IN p_limit INT
)
BEGIN
    SELECT 
        s.seller_id,
        s.seller_city,
        s.seller_state,
        COUNT(DISTINCT p.product_category_name) AS categories_count,
        COUNT(DISTINCT p.product_id) AS unique_products,
        COUNT(DISTINCT o.order_id) AS total_orders,
        ROUND(SUM(oi.price), 2) AS total_revenue,
        ROUND(AVG(r.review_score), 2) AS avg_rating,
        GROUP_CONCAT(DISTINCT COALESCE(pct.product_category_name_english, p.product_category_name) 
                     ORDER BY COALESCE(pct.product_category_name_english, p.product_category_name) 
                     SEPARATOR ', ') AS categories_sold,
        CASE 
            WHEN COUNT(DISTINCT p.product_category_name) = 1 THEN 'Specialist'
            WHEN COUNT(DISTINCT p.product_category_name) BETWEEN 2 AND 3 THEN 'Diversified (Light)'
            WHEN COUNT(DISTINCT p.product_category_name) BETWEEN 4 AND 6 THEN 'Diversified (Medium)'
            ELSE 'Highly Diversified'
        END AS diversification_level
    FROM sellers s
    JOIN order_items oi ON s.seller_id = oi.seller_id
    JOIN orders o ON oi.order_id = o.order_id
    JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN product_category_translation pct ON p.product_category_name = pct.product_category_name
    LEFT JOIN order_reviews r ON o.order_id = r.order_id
    WHERE o.order_purchase_timestamp BETWEEN p_start_date AND p_end_date
      AND o.order_status = 'delivered'
    GROUP BY s.seller_id, s.seller_city, s.seller_state
    HAVING total_orders >= 10
    ORDER BY categories_count DESC, total_revenue DESC
    LIMIT p_limit;
END$

DELIMITER ;