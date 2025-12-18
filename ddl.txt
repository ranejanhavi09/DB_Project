CREATE TABLE `customers` (
  `customer_id` text,
  `customer_unique_id` text,
  `customer_zip_code_prefix` bigint DEFAULT NULL,
  `customer_city` text,
  `customer_state` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

--------------------------------------------------

CREATE TABLE `geolocation` (
  `geolocation_zip_code_prefix` text,
  `geolocation_lat` double DEFAULT NULL,
  `geolocation_lng` double DEFAULT NULL,
  `geolocation_city` text,
  `geolocation_state` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

--------------------------------------------------

CREATE TABLE `order_items` (
  `order_id` text,
  `order_item_id` int DEFAULT NULL,
  `product_id` text,
  `seller_id` text,
  `shipping_limit_date` datetime DEFAULT NULL,
  `price` double DEFAULT NULL,
  `freight_value` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

--------------------------------------------------

CREATE TABLE `order_payments` (
  `order_id` text,
  `payment_sequential` int DEFAULT NULL,
  `payment_type` text,
  `payment_installments` int DEFAULT NULL,
  `payment_value` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

--------------------------------------------------

CREATE TABLE `order_reviews` (
  `review_id` text,
  `order_id` text,
  `review_score` bigint DEFAULT NULL,
  `review_comment_title` text,
  `review_comment_message` text,
  `review_text_combined` text,
  `review_text_english` text,
  `predicted_sentiment` text,
  `sentiment_confidence` double DEFAULT NULL,
  `is_aligned` text,
  `review_creation_date` text,
  `review_answer_timestamp` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

--------------------------------------------------

CREATE TABLE `orders` (
  `order_id` varchar(100) NOT NULL,
  `customer_id` varchar(100) DEFAULT NULL,
  `order_status` varchar(50) DEFAULT NULL,
  `order_purchase_timestamp` datetime DEFAULT NULL,
  `order_approved_at` datetime DEFAULT NULL,
  `order_delivered_carrier_date` datetime DEFAULT NULL,
  `order_delivered_customer_date` datetime DEFAULT NULL,
  `order_estimated_delivery_date` datetime DEFAULT NULL,
  PRIMARY KEY (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

--------------------------------------------------

CREATE TABLE `product_category` (
  `product_category_name` text,
  `product_category_name_english` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

--------------------------------------------------

CREATE TABLE `products` (
  `product_id` text,
  `product_category_name` text,
  `product_name_lenght` int DEFAULT NULL,
  `product_description_lenght` int DEFAULT NULL,
  `product_photos_qty` int DEFAULT NULL,
  `product_weight_g` int DEFAULT NULL,
  `product_length_cm` int DEFAULT NULL,
  `product_height_cm` int DEFAULT NULL,
  `product_width_cm` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

--------------------------------------------------

CREATE TABLE `sellers` (
  `seller_id` varchar(100) NOT NULL,
  `seller_zip_code_prefix` varchar(10) DEFAULT NULL,
  `seller_city` varchar(100) DEFAULT NULL,
  `seller_state` varchar(2) DEFAULT NULL,
  PRIMARY KEY (`seller_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

--------------------------------------------------
