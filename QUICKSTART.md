# Quick Start Guide

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] Neo4j installed and running
- [ ] All CSV files in `Datasets/` folder

## Step-by-Step Setup

### 1. Install Neo4j

**Windows/Mac (Neo4j Desktop):**
- Download from https://neo4j.com/download/
- Install and create a new database
- Start the database
- Note: Default password is usually `neo4j` (change on first login)

**Linux/Docker:**
```bash
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

```bash
# Copy example file
cp .env.example .env

# Edit .env and update Neo4j credentials
# NEO4J_URI=bolt://localhost:7687
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=your_password
```

### 4. Load Data into Neo4j

```bash
python data_loader.py
```

**Expected time:** 10-30 minutes depending on system

**What it does:**
- Creates indexes
- Loads ~99K customers
- Loads ~99K orders
- Loads ~33K products
- Loads ~3K sellers
- Loads ~48K reviews
- Creates all relationships
- Computes aggregated metrics

### 5. Start the API Server

```bash
python app.py
```

You should see:
```
Starting Flask server on port 5000
Neo4j URI: bolt://localhost:7687
 * Running on http://0.0.0.0:5000
```

### 6. Open the Frontend

**Option 1: Direct file**
- Open `frontend/index.html` in your browser
- Note: CORS may require serving via HTTP server

**Option 2: HTTP Server**
```bash
cd frontend
python -m http.server 8000
# Then open http://localhost:8000
```

## Testing the Setup

### Test API Connection

```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### Test Recommendations

1. Open the frontend UI
2. Select a customer from dropdown
3. Click "Load Customer"
4. Select an algorithm
5. Click "Get Recommendations"

## Common Issues

### "Connection refused" error
- Check Neo4j is running: `neo4j status`
- Verify credentials in `.env`
- Check firewall settings

### "Module not found" error
- Run: `pip install -r requirements.txt`
- Check Python version: `python --version`

### Data loading fails
- Check CSV files exist in `Datasets/` folder
- Verify file permissions
- Check Neo4j has enough memory

### Frontend can't connect to API
- Verify API is running on port 5000
- Check browser console for CORS errors
- Try accessing API directly: `http://localhost:5000/api/health`

## Next Steps

- Explore different recommendation algorithms
- Check database statistics
- Review customer purchase patterns
- Analyze product categories

## Getting Help

1. Check `README.md` for detailed documentation
2. Review `GRAPH_DB_SCHEMA.md` for schema details
3. Check Neo4j logs for database errors
4. Review Flask console output for API errors

