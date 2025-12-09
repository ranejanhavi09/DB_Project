# Olist Recommendation Engine

A graph database-powered recommendation system for the Olist Brazilian E-Commerce dataset. This project uses Neo4j to store customer, order, product, and review data, and provides multiple recommendation algorithms through a web interface.

## Features

- **Graph Database**: Neo4j for efficient relationship queries
- **Multiple Recommendation Algorithms**:
  - Hybrid (combines multiple signals)
  - Collaborative Filtering (similar customers)
  - Content-Based (category preferences)
  - Sentiment-Based (positive reviews)
  - Seller-Based (preferred sellers)
- **Web UI**: Modern, responsive interface for exploring recommendations
- **REST API**: Flask backend with comprehensive endpoints

## Prerequisites

- Python 3.8+
- Neo4j Database (Community Edition or Desktop)
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

## Project Structure

```
DB_Project/
├── Datasets/                    # CSV data files
├── frontend/                    # Web UI
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── config.py                    # Configuration
├── database.py                  # Neo4j connection
├── data_loader.py               # Data import script
├── recommendation_engine.py      # Recommendation algorithms
├── app.py                       # Flask API
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── README.md                    # This file
├── DATASET_SCHEMA_DOCUMENTATION.md
└── GRAPH_DB_SCHEMA.md          # Graph schema documentation
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

