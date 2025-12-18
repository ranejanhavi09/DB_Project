# Olist Recommendation Engine


- A **graph-database-powered recommendation engine** using **Neo4j**
- A **Seller Analytics Dashboard** backed by **MySQL**, designed to provide sellers with actionable insights

This project demonstrates the use of **both relational and graph databases** to solve real-world e-commerce problems.


## 🚀 Project Overview


### 1️⃣ Recommendation Engine (Neo4j)

The recommendation engine models customers, products, sellers, orders, categories, and reviews as a **graph** to efficiently capture complex relationships and deliver personalized recommendations.

### 2️⃣ Seller Dashboard (MySQL)

The seller dashboard is built using a **MySQL relational database** and provides sellers with insights such as:

- Sales performance
- Order trends
- Product analytics
- Revenue metrics

📌 **Primary dashboard implementation:**  
`seller_app_v4.py`

## ✨ Features

### Recommendation Engine (Neo4j)
- Graph Database: Neo4j for efficient relationship queries
- Multiple Recommendation Algorithms:
  - Hybrid (combines multiple signals)
  - Collaborative Filtering (similar customers)
  - Content-Based (category preferences)
  - Sentiment-Based (positive reviews)
  - Seller-Based (preferred sellers)
- REST API built with Flask
- Modern web UI for exploring recommendations

### Seller Dashboard (MySQL)
- MySQL database integration using MySQL Workbench connection
- Seller-level analytics and KPIs
- Stored procedures and DDL scripts
- Flask-based dashboard backend
- Modular versioning (`seller_app_v2` → `seller_app_v6`)


## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Graph Database:** Neo4j
- **Relational Database:** MySQL
- **Frontend:** HTML, CSS, JavaScript
- **APIs:** REST
- **Data Processing:** Python, SQL
- **Tools:** Neo4j Desktop, MySQL Workbench

---

## 📦 Prerequisites

- Python 3.8+
- Neo4j Database (Community Edition or Desktop)
- MySQL Server
- MySQL Workbench
- Node.js (optional, for frontend development)

## Installation

### 1. Install Neo4j

**Option A: Neo4j Desktop (Recommended)**
1. Download from [neo4j.com/download](https://neo4j.com/download/)
2. Install and create a new database
3. Start the database
4. Note your connection details (URI, username, password)

**Option B: Neo4j Community Edition**
```bash
# Using Docker
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy the example environment file and update with your Neo4j credentials:

```bash
cp .env.example .env
```

Edit `.env` and update:
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
```

## Data Loading

Load the CSV datasets into Neo4j:

```bash
python data_loader.py
```

This will:
1. Create indexes for performance
2. Load all nodes (Customers, Products, Orders, Sellers, Reviews, Categories)
3. Create relationships between nodes
4. Compute aggregated metrics

**Note**: This process may take 10-30 minutes depending on your system.

## Running the Application

### Start the Backend API

```bash
python app.py
```

The API will start on `http://localhost:5000`

### Access the Frontend

Open `frontend/index.html` in your web browser, or serve it with a simple HTTP server:

```bash
# Python
cd frontend
python -m http.server 8000

# Node.js
cd frontend
npx http-server -p 8000
```

Then open `http://localhost:8000` in your browser.

## API Endpoints

### Health Check
```
GET /api/health
```

### Customers
```
GET /api/customers
GET /api/customers/<customer_unique_id>
```

### Recommendations
```
GET /api/customers/<customer_unique_id>/recommendations?algorithm=hybrid&limit=20
```

**Algorithm options**: `hybrid`, `collaborative`, `content`, `sentiment`, `seller`

### Products
```
GET /api/products/<product_id>
```

### Statistics
```
GET /api/stats
GET /api/categories
```



### 2. Install MySql

**Option A: MySQL Workbench (Recommended)**
1. Install and create a new database
2. Start the database
3. Note your connection details (URI, username, password)


### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy the example environment file and update with your MySQL credentials:

```bash
cp .env.example .env
```

Edit `.env` and update:
```
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=  # <-- ADD YOUR PASSWORD HERE
MYSQL_DATABASE= # <-- Changed to 'com_master'
MYSQL_PORT=3306
MYSQL_POOL_SIZE=5
MYSQL_POOL_NAME=seller_dashboard_pool
```

### 4. Create Database Schema
Run the DDL script to create all required tables:
```
mysql -u root -p < database_ddl.sql
```

### 5. Load Stored Procedures
Load analytics and reporting stored procedures:
```
mysql -u root -p < stored_procedures.sql
```

### 6. Test MySQL Connection
Validate the database connection:
```
python test_mysql_connection.py
```

▶️ Step 7: Run Seller Dashboard Application
```
python seller_app_v4.py
```
## Project Structure


```
DB_Project/
├── pycache/ # Python cache files
├── .git/ # Git repository
├── .env # Environment variables (local)
├── .env.example # Environment variable template
├── .gitignore # Git ignore rules
├── app.py # Flask API for Neo4j recommendation engine
├── recommendation_engine.py # Core recommendation algorithms
├── database.py # Neo4j database connection
├── data_loader.py # Loads CSV data into Neo4j
├── config.py # Neo4j configuration
├── config-sql.py # MySQL configuration for Seller Dashboard
├── requirements.txt # Python dependencies
│
├── Datasets/ # Olist CSV datasets
│
├── frontend/ # Recommendation Engine UI
│ ├── index.html
│ ├── styles.css
│ └── app.js
│
├── static/ # Static assets (CSS/JS/images)
├── templates/ # Flask HTML templates
│
├── routes/ # Flask route definitions
├── services/ # Business logic services
├── repositories/ # Database access layer
│
├── db/ # Database-related utilities
│
├── database_ddl.sql # MySQL schema definition
├── stored_procedures.sql # MySQL stored procedures
├── ddl.txt # Generated DDL snapshot
│
├── test_mysql_connection.py # MySQL connectivity test
├── test_seller_dashboard.py # Seller dashboard tests
│
├── seller_app.py # Initial seller dashboard version
├── seller_app_v2.py # Seller dashboard (v2)
├── seller_app_v3.py # Seller dashboard (v3)
├── seller_app_v4.py # ⭐ Primary seller dashboard implementation
├── seller_app_v5.py # Enhanced seller dashboard
├── seller_app_v6.py # Latest experimental version
│
├── check_tables.py # MySQL table validation script
├── check_columns.py # MySQL column validation script
├── debug_data.py # Data debugging utilities
├── get_ddl.py # Auto DDL extraction script
│
├── order_reviews_preprocessing.ipynb # Review sentiment preprocessing
│
├── README.md # Project documentation
├── QUICKSTART.md # Quick setup guide
├── DATASET_SCHEMA_DOCUMENTATION.md
├── GRAPH_DB_SCHEMA.md
```

## Usage Guide

1. **Load Data**: Run `python data_loader.py` to import all datasets
2. **Start API**: Run `python app.py` to start the backend
3. **Open UI**: Open `frontend/index.html` in your browser
4. **Select Customer**: Choose a customer from the dropdown
5. **Choose Algorithm**: Select a recommendation algorithm
6. **Get Recommendations**: Click "Get Recommendations" to see results

## Recommendation Algorithms Explained

### Hybrid (Default)
Combines category preferences, sentiment scores, and seller preferences with weighted scoring.

### Collaborative Filtering
Finds customers with similar purchase patterns and recommends products they bought.

### Content-Based
Recommends products in categories the customer has purchased from before.

### Sentiment-Based
Filters recommendations to only include products with positive sentiment and high ratings.

### Seller-Based
Recommends products from sellers the customer has purchased from previously.

## Troubleshooting

### Connection Issues
- Verify Neo4j is running: `neo4j status`
- Check `.env` file has correct credentials
- Test connection: `cypher-shell -u neo4j -p password`

### Data Loading Errors
- Ensure all CSV files are in the `Datasets/` folder
- Check file permissions
- Verify Neo4j has enough memory allocated

### API Errors
- Check Flask is running on port 5000
- Verify CORS is enabled for frontend
- Check browser console for errors

## Performance Optimization

- Indexes are created automatically during data loading
- For large datasets, consider increasing Neo4j heap memory
- Use connection pooling for production deployments
- Consider caching frequently accessed recommendations

## Future Enhancements

- Real-time recommendation updates
- Machine learning model integration
- A/B testing framework
- User feedback collection
- Advanced filtering options
- Export recommendations to CSV/JSON

## License

This project is for educational purposes. The Olist dataset is available under the [CC0: Public Domain](https://creativecommons.org/publicdomain/zero/1.0/) license.

## References

- [Neo4j Documentation](https://neo4j.com/docs/)
- [Olist Dataset on Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/data)
- [Flask Documentation](https://flask.palletsprojects.com/)

## Support

For issues or questions, please check:
1. Neo4j logs: `neo4j.log`
2. Flask console output
3. Browser developer console

