"""
FINAL Seller Dashboard with correct column names and queries
"""
from flask import Flask, jsonify, render_template_string
import mysql.connector
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# MySQL Configuration - UPDATE WITH YOUR PASSWORD
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mysql123',  # Your password here
    'database': 'ecom_master'
}

def get_mysql_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)

# ==================== HTML TEMPLATE ====================
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>📊 Seller Analytics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary: #4361ee;
            --secondary: #3a0ca3;
            --success: #4cc9f0;
            --info: #7209b7;
            --warning: #f72585;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .dashboard-container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .dashboard-header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border-left: 5px solid var(--primary);
        }
        
        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s;
            height: 100%;
            border-top: 4px solid var(--primary);
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-card h3 {
            color: #2d3748;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary);
            margin: 10px 0;
        }
        
        .stat-icon {
            font-size: 2.5rem;
            color: var(--primary);
            opacity: 0.8;
            margin-bottom: 15px;
        }
        
        .chart-container {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            height: 100%;
        }
        
        .chart-title {
            color: #2d3748;
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .data-table {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            margin-bottom: 20px;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .data-info {
            background: #e8f4fd;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #4361ee;
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <!-- Header -->
        <div class="dashboard-header">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h1 class="mb-2"><i class="fas fa-chart-line text-primary"></i> Seller Analytics Dashboard</h1>
                    <p class="text-muted mb-0">Real-time insights from 3,095 sellers & $13.5M+ in revenue</p>
                    <div class="data-info">
                        <small><i class="fas fa-database"></i> Connected to: ecom_master | <i class="fas fa-clock"></i> Last updated: <span id="lastUpdated">Loading...</span></small>
                    </div>
                </div>
                <div class="col-md-4 text-end">
                    <button class="btn btn-primary" onclick="loadDashboard()">
                        <i class="fas fa-sync-alt"></i> Refresh Dashboard
                    </button>
                </div>
            </div>
        </div>

        <!-- Stats Overview -->
        <div class="row" id="statsOverview">
            <div class="col-md-3 col-sm-6">
                <div class="stat-card text-center">
                    <div class="stat-icon">
                        <i class="fas fa-store"></i>
                    </div>
                    <h3>Total Sellers</h3>
                    <div class="stat-value" id="totalSellers">...</div>
                    <p class="text-muted mb-0">Active in system</p>
                </div>
            </div>
            <div class="col-md-3 col-sm-6">
                <div class="stat-card text-center">
                    <div class="stat-icon">
                        <i class="fas fa-shopping-cart"></i>
                    </div>
                    <h3>Total Orders</h3>
                    <div class="stat-value" id="totalOrders">...</div>
                    <p class="text-muted mb-0">Completed transactions</p>
                </div>
            </div>
            <div class="col-md-3 col-sm-6">
                <div class="stat-card text-center">
                    <div class="stat-icon">
                        <i class="fas fa-chart-pie"></i>
                    </div>
                    <h3>Total Revenue</h3>
                    <div class="stat-value" id="totalRevenue">...</div>
                    <p class="text-muted mb-0">All-time sales</p>
                </div>
            </div>
            <div class="col-md-3 col-sm-6">
                <div class="stat-card text-center">
                    <div class="stat-icon">
                        <i class="fas fa-users"></i>
                    </div>
                    <h3>Total Customers</h3>
                    <div class="stat-value" id="totalCustomers">...</div>
                    <p class="text-muted mb-0">Registered buyers</p>
                </div>
            </div>
        </div>

        <!-- Charts Row 1 -->
        <div class="row">
            <div class="col-lg-8">
                <div class="chart-container">
                    <div class="chart-title">Monthly Revenue Trend</div>
                    <canvas id="revenueChart" height="300"></canvas>
                </div>
            </div>
            <div class="col-lg-4">
                <div class="chart-container">
                    <div class="chart-title">Order Status Distribution</div>
                    <canvas id="statusChart" height="300"></canvas>
                </div>
            </div>
        </div>

        <!-- Charts Row 2 -->
        <div class="row">
            <div class="col-lg-6">
                <div class="chart-container">
                    <div class="chart-title">Top 10 Product Categories</div>
                    <canvas id="categoryChart" height="250"></canvas>
                </div>
            </div>
            <div class="col-lg-6">
                <div class="chart-container">
                    <div class="chart-title">Price Distribution</div>
                    <canvas id="priceChart" height="250"></canvas>
                </div>
            </div>
        </div>

        <!-- Top Sellers Table -->
        <div class="row">
            <div class="col-12">
                <div class="data-table">
                    <div class="chart-title p-3 mb-0">Top 10 Sellers by Revenue</div>
                    <div class="table-responsive">
                        <table class="table table-hover mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th>Seller ID</th>
                                    <th>Location</th>
                                    <th>Orders</th>
                                    <th>Revenue</th>
                                    <th>Avg Order Value</th>
                                    <th>Performance</th>
                                </tr>
                            </thead>
                            <tbody id="sellersTable">
                                <!-- Filled by JavaScript -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="text-center text-white mt-4">
            <small>Dashboard auto-refreshes every 2 minutes | Data source: MySQL ecom_master database</small>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let charts = {};
        
        // Format currency
        function formatCurrency(value) {
            if (value === null || value === undefined) return '$0.00';
            return '$' + parseFloat(value).toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        }
        
        // Format number
        function formatNumber(num) {
            if (num === null || num === undefined) return '0';
            return parseInt(num).toLocaleString('en-US');
        }
        
        // Update timestamp
        function updateTimestamp() {
            document.getElementById('lastUpdated').textContent = new Date().toLocaleString();
        }
        
        // Load dashboard data
        async function loadDashboard() {
            try {
                console.log('Loading dashboard data...');
                
                // Show loading states
                ['totalSellers', 'totalOrders', 'totalRevenue', 'totalCustomers'].forEach(id => {
                    document.getElementById(id).textContent = '...';
                });
                
                document.getElementById('sellersTable').innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center">
                            <div class="spinner-border spinner-border-sm"></div> Loading data...
                        </td>
                    </tr>
                `;
                
                // Load all data
                const responses = await Promise.all([
                    fetch('/api/dashboard/stats'),
                    fetch('/api/dashboard/revenue-trend'),
                    fetch('/api/dashboard/order-status'),
                    fetch('/api/dashboard/top-categories'),
                    fetch('/api/dashboard/price-distribution'),
                    fetch('/api/dashboard/top-sellers')
                ]);
                
                // Check for errors
                for (let i = 0; i < responses.length; i++) {
                    if (!responses[i].ok) {
                        throw new Error(`API ${i} returned ${responses[i].status}`);
                    }
                }
                
                const [stats, revenue, status, categories, prices, sellers] = await Promise.all(
                    responses.map(r => r.json())
                );
                
                console.log('Data loaded:', { stats, revenue, status, categories, prices, sellers });
                
                // Update stats
                updateStats(stats);
                
                // Update charts
                updateCharts(revenue, status, categories, prices);
                
                // Update sellers table
                updateSellersTable(sellers);
                
                updateTimestamp();
                
                console.log('Dashboard loaded successfully!');
                
            } catch (error) {
                console.error('Error loading dashboard:', error);
                document.getElementById('statsOverview').innerHTML = `
                    <div class="col-12">
                        <div class="alert alert-danger">
                            <h5><i class="fas fa-exclamation-triangle"></i> Error Loading Dashboard</h5>
                            <p>${error.message}</p>
                            <button onclick="loadDashboard()" class="btn btn-danger">
                                <i class="fas fa-sync-alt"></i> Try Again
                            </button>
                        </div>
                    </div>
                `;
            }
        }
        
        function updateStats(stats) {
            document.getElementById('totalSellers').textContent = formatNumber(stats.total_sellers);
            document.getElementById('totalOrders').textContent = formatNumber(stats.total_orders);
            document.getElementById('totalRevenue').textContent = formatCurrency(stats.total_revenue);
            document.getElementById('totalCustomers').textContent = formatNumber(stats.total_customers);
        }
        
        function updateCharts(revenue, status, categories, prices) {
            // Destroy existing charts
            Object.values(charts).forEach(chart => {
                if (chart && typeof chart.destroy === 'function') {
                    chart.destroy();
                }
            });
            
            // Revenue Chart
            const revenueCtx = document.getElementById('revenueChart').getContext('2d');
            charts.revenue = new Chart(revenueCtx, {
                type: 'line',
                data: {
                    labels: revenue.months,
                    datasets: [{
                        label: 'Monthly Revenue',
                        data: revenue.revenue,
                        borderColor: '#4361ee',
                        backgroundColor: 'rgba(67, 97, 238, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: true },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => `Revenue: ${formatCurrency(ctx.raw)}`
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: (value) => formatCurrency(value)
                            }
                        }
                    }
                }
            });
            
            // Status Chart
            const statusCtx = document.getElementById('statusChart').getContext('2d');
            charts.status = new Chart(statusCtx, {
                type: 'doughnut',
                data: {
                    labels: status.labels,
                    datasets: [{
                        data: status.data,
                        backgroundColor: [
                            '#4361ee', '#3a0ca3', '#4cc9f0', 
                            '#7209b7', '#f72585'
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'right' }
                    }
                }
            });
            
            // Category Chart
            const categoryCtx = document.getElementById('categoryChart').getContext('2d');
            charts.category = new Chart(categoryCtx, {
                type: 'bar',
                data: {
                    labels: categories.labels,
                    datasets: [{
                        label: 'Products',
                        data: categories.data,
                        backgroundColor: '#4361ee',
                        borderColor: '#3a0ca3',
                        borderWidth: 1
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: { beginAtZero: true }
                    }
                }
            });
            
            // Price Chart
            const priceCtx = document.getElementById('priceChart').getContext('2d');
            charts.price = new Chart(priceCtx, {
                type: 'pie',
                data: {
                    labels: prices.labels,
                    datasets: [{
                        data: prices.data,
                        backgroundColor: [
                            '#4cc9f0', '#4361ee', '#3a0ca3',
                            '#7209b7', '#f72585'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'right' }
                    }
                }
            });
        }
        
        function updateSellersTable(sellers) {
            let html = '';
            sellers.forEach((seller, index) => {
                const rank = index + 1;
                const rankClass = rank <= 3 ? 'bg-warning text-dark' : '';
                html += `
                    <tr>
                        <td>
                            <span class="badge ${rankClass}">#${rank}</span>
                            ${seller.seller_id.substring(0, 8)}...
                        </td>
                        <td>${seller.seller_city || 'N/A'}, ${seller.seller_state || 'N/A'}</td>
                        <td>${formatNumber(seller.order_count)}</td>
                        <td><strong>${formatCurrency(seller.total_revenue)}</strong></td>
                        <td>${formatCurrency(seller.avg_order_value)}</td>
                        <td>
                            <div class="progress" style="height: 8px;">
                                <div class="progress-bar" style="width: ${Math.min(seller.order_count / 1000 * 100, 100)}%"></div>
                            </div>
                        </td>
                    </tr>
                `;
            });
            document.getElementById('sellersTable').innerHTML = html;
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            loadDashboard();
            // Auto-refresh every 2 minutes
            setInterval(loadDashboard, 120000);
        });
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return HTML_TEMPLATE

# ==================== API ENDPOINTS WITH CORRECT QUERIES ====================

@app.route('/api/dashboard/stats')
def dashboard_stats():
    """Get dashboard overview statistics"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Total sellers
        cursor.execute("SELECT COUNT(*) as count FROM sellers")
        total_sellers = cursor.fetchone()['count']
        
        # Total orders
        cursor.execute("SELECT COUNT(*) as count FROM orders")
        total_orders = cursor.fetchone()['count']
        
        # Total revenue - FIXED: using correct column name 'price' in order_items
        cursor.execute("SELECT COALESCE(SUM(price), 0) as total FROM order_items")
        total_revenue = float(cursor.fetchone()['total'])
        
        # Total customers - FIXED: using correct column name 'customer_unique_id'
        cursor.execute("SELECT COUNT(DISTINCT customer_unique_id) as count FROM customers")
        total_customers = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'total_sellers': total_sellers,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'total_customers': total_customers
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/revenue-trend')
def revenue_trend():
    """Get revenue trend - FIXED with correct column names"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all months with data (not just last 12 months since your data is from 2018)
        cursor.execute("""
            SELECT 
                DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') as month,
                SUM(oi.price) as revenue
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.order_purchase_timestamp IS NOT NULL
            GROUP BY DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m')
            ORDER BY month
        """)
        
        results = cursor.fetchall()
        
        months = []
        revenue = []
        
        for row in results:
            months.append(row['month'])
            revenue.append(float(row['revenue'] or 0))
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'months': months,
            'revenue': revenue
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/order-status')
def order_status():
    """Get order status distribution"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                order_status,
                COUNT(*) as count
            FROM orders
            GROUP BY order_status
            ORDER BY count DESC
        """)
        
        results = cursor.fetchall()
        
        labels = []
        data = []
        
        for row in results:
            labels.append(row['order_status'].title())
            data.append(row['count'])
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'labels': labels,
            'data': data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/top-categories')
def top_categories():
    """Get top product categories - FIXED: using correct column name"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                COALESCE(product_category_name, 'Uncategorized') as category,
                COUNT(*) as product_count
            FROM products
            WHERE product_category_name IS NOT NULL
            AND product_category_name != ''
            GROUP BY product_category_name
            ORDER BY product_count DESC
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        
        labels = []
        data = []
        
        for row in results:
            # Shorten long category names
            label = row['category'][:20] + ('...' if len(row['category']) > 20 else '')
            labels.append(label)
            data.append(row['product_count'])
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'labels': labels,
            'data': data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/price-distribution')
def price_distribution():
    """Get price distribution - FIXED: using correct column name 'price'"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN price <= 10 THEN '0-10'
                    WHEN price <= 50 THEN '11-50'
                    WHEN price <= 100 THEN '51-100'
                    WHEN price <= 200 THEN '101-200'
                    ELSE '200+'
                END as price_range,
                COUNT(*) as product_count
            FROM order_items
            GROUP BY price_range
            ORDER BY 
                CASE price_range
                    WHEN '0-10' THEN 1
                    WHEN '11-50' THEN 2
                    WHEN '51-100' THEN 3
                    WHEN '101-200' THEN 4
                    ELSE 5
                END
        """)
        
        results = cursor.fetchall()
        
        labels = []
        data = []
        
        for row in results:
            labels.append(f"{row['price_range']} ($)")
            data.append(row['product_count'])
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'labels': labels,
            'data': data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/top-sellers')
def top_sellers():
    """Get top sellers - FIXED: using correct column names"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                s.seller_id,
                s.seller_city,
                s.seller_state,
                COUNT(DISTINCT oi.order_id) as order_count,
                SUM(oi.price) as total_revenue,
                AVG(oi.price) as avg_order_value
            FROM sellers s
            JOIN order_items oi ON s.seller_id = oi.seller_id
            GROUP BY s.seller_id, s.seller_city, s.seller_state
            ORDER BY total_revenue DESC
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        
        # Convert decimal to float for JSON
        for row in results:
            row['total_revenue'] = float(row['total_revenue'] or 0)
            row['avg_order_value'] = float(row['avg_order_value'] or 0)
        
        cursor.close()
        conn.close()
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    PORT = 5004  # Different port
    print("🚀 Starting FINAL Seller Dashboard")
    print(f"📊 Dashboard: http://localhost:{PORT}")
    print(f"📋 Data: 3,095 sellers | 99,441 orders | $13.5M revenue")
    print("🔗 Using correct column names from your database")
    app.run(host='0.0.0.0', port=PORT, debug=True)