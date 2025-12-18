"""
FINAL Seller Dashboard with Seller Dropdown for Individual Analytics
"""
from flask import Flask, jsonify, render_template_string, request
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
        
        .seller-selector {
            background: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }
        
        .seller-badge {
            background: linear-gradient(45deg, #4361ee, #3a0ca3);
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 8px;
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
        
        .dashboard-title {
            display: flex;
            align-items: center;
            gap: 15px;
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <!-- Header -->
        <div class="dashboard-header">
            <div class="row align-items-center">
                <div class="col-md-6">
                    <div class="dashboard-title">
                        <h1 class="mb-2"><i class="fas fa-chart-line text-primary"></i> Seller Analytics Dashboard</h1>
                        <span id="currentSellerBadge" class="seller-badge" style="display: none;">
                            <i class="fas fa-user-tie"></i> <span id="currentSellerText">All Sellers</span>
                        </span>
                    </div>
                    <p class="text-muted mb-2" id="dashboardSubtitle">Real-time insights from 3,095 sellers & $13.5M+ in revenue</p>
                    <div class="data-info">
                        <small><i class="fas fa-database"></i> Connected to: ecom_master | <i class="fas fa-clock"></i> Last updated: <span id="lastUpdated">Loading...</span></small>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="seller-selector">
                        <div class="row g-3 align-items-center">
                            <div class="col-md-8">
                                <label for="sellerSelect" class="form-label"><strong>Select Seller:</strong></label>
                                <select class="form-select" id="sellerSelect" onchange="onSellerChange()">
                                    <option value="all">📊 All Sellers (Aggregated View)</option>
                                    <option value="" disabled>─────────── Top Sellers ───────────</option>
                                    <!-- Top sellers will be populated here -->
                                </select>
                            </div>
                            <div class="col-md-4 text-end">
                                <button class="btn btn-primary" onclick="loadDashboard()">
                                    <i class="fas fa-sync-alt"></i> Refresh
                                </button>
                                <button class="btn btn-outline-secondary" onclick="resetToAllSellers()">
                                    <i class="fas fa-undo"></i> Reset
                                </button>
                            </div>
                        </div>
                    </div>
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
                    <h3>Total Sellers / Orders</h3>
                    <div class="stat-value" id="totalSellers">...</div>
                    <p class="text-muted mb-0" id="statLabel1">Active sellers</p>
                </div>
            </div>
            <div class="col-md-3 col-sm-6">
                <div class="stat-card text-center">
                    <div class="stat-icon">
                        <i class="fas fa-shopping-cart"></i>
                    </div>
                    <h3>Total Orders / Revenue</h3>
                    <div class="stat-value" id="totalOrders">...</div>
                    <p class="text-muted mb-0" id="statLabel2">Completed orders</p>
                </div>
            </div>
            <div class="col-md-3 col-sm-6">
                <div class="stat-card text-center">
                    <div class="stat-icon">
                        <i class="fas fa-chart-pie"></i>
                    </div>
                    <h3>Total Revenue / Avg Value</h3>
                    <div class="stat-value" id="totalRevenue">...</div>
                    <p class="text-muted mb-0" id="statLabel3">All-time sales</p>
                </div>
            </div>
            <div class="col-md-3 col-sm-6">
                <div class="stat-card text-center">
                    <div class="stat-icon">
                        <i class="fas fa-users"></i>
                    </div>
                    <h3>Total Customers / Products</h3>
                    <div class="stat-value" id="totalCustomers">...</div>
                    <p class="text-muted mb-0" id="statLabel4">Registered buyers</p>
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
                    <div class="chart-title">Top Product Categories</div>
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
                    <div class="chart-title p-3 mb-0" id="tableTitle">Top 10 Sellers by Revenue</div>
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
        let currentSellerId = 'all';
        let sellerOptions = [];
        
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
        
        // Load seller options
        async function loadSellerOptions() {
            try {
                const response = await fetch('/api/sellers/list');
                if (!response.ok) throw new Error('Failed to load sellers');
                const sellers = await response.json();
                
                sellerOptions = sellers;
                const select = document.getElementById('sellerSelect');
                
                // Clear existing options except the first two
                while (select.options.length > 2) {
                    select.remove(2);
                }
                
                // Add top sellers
                sellers.slice(0, 20).forEach(seller => {
                    const option = document.createElement('option');
                    option.value = seller.seller_id;
                    option.textContent = `🏆 ${seller.seller_id.substring(0, 12)}... - ${seller.seller_city || 'Unknown'} (${formatCurrency(seller.total_revenue)})`;
                    select.appendChild(option);
                });
                
                // Add search option
                const searchOption = document.createElement('option');
                searchOption.value = '';
                searchOption.disabled = true;
                searchOption.textContent = '─────────── Search Seller ───────────';
                select.appendChild(searchOption);
                
                // Add search input option
                const searchInputOption = document.createElement('option');
                searchInputOption.value = 'search';
                searchInputOption.textContent = '🔍 Type to search sellers...';
                select.appendChild(searchInputOption);
                
            } catch (error) {
                console.error('Error loading seller options:', error);
            }
        }
        
        // Search sellers
        async function searchSellers(searchTerm) {
            try {
                const response = await fetch(`/api/sellers/search?q=${encodeURIComponent(searchTerm)}`);
                if (!response.ok) throw new Error('Search failed');
                return await response.json();
            } catch (error) {
                console.error('Search error:', error);
                return [];
            }
        }
        
        // Handle seller change
        async function onSellerChange() {
            const select = document.getElementById('sellerSelect');
            const selectedValue = select.value;
            
            if (selectedValue === 'search') {
                // Show search input
                const searchTerm = prompt('Enter seller ID or city to search:');
                if (searchTerm) {
                    const results = await searchSellers(searchTerm);
                    if (results.length > 0) {
                        // Clear and show results
                        while (select.options.length > 2) {
                            select.remove(2);
                        }
                        
                        results.forEach(seller => {
                            const option = document.createElement('option');
                            option.value = seller.seller_id;
                            option.textContent = `${seller.seller_id.substring(0, 12)}... - ${seller.seller_city || 'Unknown'} (${formatCurrency(seller.total_revenue || 0)})`;
                            select.appendChild(option);
                        });
                        
                        select.value = results[0].seller_id;
                        currentSellerId = results[0].seller_id;
                    } else {
                        alert('No sellers found for: ' + searchTerm);
                        select.value = 'all';
                    }
                } else {
                    select.value = 'all';
                }
            } else {
                currentSellerId = selectedValue;
            }
            
            loadDashboard();
        }
        
        // Reset to all sellers
        function resetToAllSellers() {
            document.getElementById('sellerSelect').value = 'all';
            currentSellerId = 'all';
            loadDashboard();
        }
        
        // Load dashboard data
        async function loadDashboard() {
            try {
                console.log('Loading dashboard data for seller:', currentSellerId);
                
                // Update UI based on selection
                const sellerBadge = document.getElementById('currentSellerBadge');
                const sellerText = document.getElementById('currentSellerText');
                const subtitle = document.getElementById('dashboardSubtitle');
                
                if (currentSellerId === 'all') {
                    sellerBadge.style.display = 'none';
                    subtitle.textContent = 'Real-time insights from 3,095 sellers & $13.5M+ in revenue';
                    document.getElementById('tableTitle').textContent = 'Top 10 Sellers by Revenue';
                } else {
                    const selectedOption = document.getElementById('sellerSelect').selectedOptions[0];
                    sellerText.textContent = selectedOption.textContent.substring(0, 30) + '...';
                    sellerBadge.style.display = 'inline-flex';
                    subtitle.textContent = 'Individual seller performance analytics';
                    document.getElementById('tableTitle').textContent = 'Seller Details';
                }
                
                // Update stat labels
                if (currentSellerId === 'all') {
                    document.getElementById('statLabel1').textContent = 'Active sellers';
                    document.getElementById('statLabel2').textContent = 'Completed orders';
                    document.getElementById('statLabel3').textContent = 'All-time sales';
                    document.getElementById('statLabel4').textContent = 'Registered buyers';
                } else {
                    document.getElementById('statLabel1').textContent = 'Total orders';
                    document.getElementById('statLabel2').textContent = 'Total revenue';
                    document.getElementById('statLabel3').textContent = 'Avg order value';
                    document.getElementById('statLabel4').textContent = 'Products sold';
                }
                
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
                
                // Build API URLs with seller parameter
                const sellerParam = currentSellerId === 'all' ? '' : `?seller_id=${currentSellerId}`;
                
                // Load all data
                const responses = await Promise.all([
                    fetch(`/api/dashboard/stats${sellerParam}`),
                    fetch(`/api/dashboard/revenue-trend${sellerParam}`),
                    fetch(`/api/dashboard/order-status${sellerParam}`),
                    fetch(`/api/dashboard/top-categories${sellerParam}`),
                    fetch(`/api/dashboard/price-distribution${sellerParam}`),
                    currentSellerId === 'all' 
                        ? fetch('/api/dashboard/top-sellers')
                        : fetch(`/api/dashboard/seller-details?seller_id=${currentSellerId}`)
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
                updateSellersTable(sellers, currentSellerId);
                
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
            if (currentSellerId === 'all') {
                document.getElementById('totalSellers').textContent = formatNumber(stats.total_sellers);
                document.getElementById('totalOrders').textContent = formatNumber(stats.total_orders);
                document.getElementById('totalRevenue').textContent = formatCurrency(stats.total_revenue);
                document.getElementById('totalCustomers').textContent = formatNumber(stats.total_customers);
            } else {
                document.getElementById('totalSellers').textContent = formatNumber(stats.total_orders);
                document.getElementById('totalOrders').textContent = formatCurrency(stats.total_revenue);
                document.getElementById('totalRevenue').textContent = formatCurrency(stats.avg_order_value);
                document.getElementById('totalCustomers').textContent = formatNumber(stats.total_products);
            }
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
                        label: currentSellerId === 'all' ? 'Monthly Revenue' : 'Seller Monthly Revenue',
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
                type: currentSellerId === 'all' ? 'bar' : 'pie',
                data: {
                    labels: categories.labels,
                    datasets: [{
                        label: currentSellerId === 'all' ? 'Products' : 'Category Distribution',
                        data: categories.data,
                        backgroundColor: currentSellerId === 'all' ? '#4361ee' : [
                            '#4cc9f0', '#4361ee', '#3a0ca3',
                            '#7209b7', '#f72585'
                        ],
                        borderColor: '#3a0ca3',
                        borderWidth: 1
                    }]
                },
                options: {
                    indexAxis: currentSellerId === 'all' ? 'y' : undefined,
                    responsive: true,
                    plugins: {
                        legend: { display: currentSellerId !== 'all', position: 'right' }
                    },
                    scales: currentSellerId === 'all' ? {
                        x: { beginAtZero: true }
                    } : undefined
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
        
        function updateSellersTable(sellers, isIndividual) {
            let html = '';
            
            if (isIndividual === 'all') {
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
            } else {
                // Individual seller view
                if (sellers && sellers.length > 0) {
                    const seller = sellers[0];
                    html = `
                        <tr>
                            <td colspan="2"><strong>Seller ID:</strong><br>${seller.seller_id}</td>
                            <td><strong>Location:</strong><br>${seller.seller_city || 'N/A'}, ${seller.seller_state || 'N/A'}</td>
                            <td><strong>First Order:</strong><br>${seller.first_order_date || 'N/A'}</td>
                            <td><strong>Last Order:</strong><br>${seller.last_order_date || 'N/A'}</td>
                            <td><strong>Active Days:</strong><br>${seller.active_days || 0}</td>
                        </tr>
                        <tr>
                            <td><strong>Total Orders:</strong><br>${formatNumber(seller.order_count)}</td>
                            <td><strong>Total Revenue:</strong><br>${formatCurrency(seller.total_revenue)}</td>
                            <td><strong>Avg Order Value:</strong><br>${formatCurrency(seller.avg_order_value)}</td>
                            <td><strong>Total Products:</strong><br>${formatNumber(seller.total_products)}</td>
                            <td><strong>Unique Customers:</strong><br>${formatNumber(seller.unique_customers)}</td>
                            <td><strong>Avg Rating:</strong><br>${seller.avg_rating ? seller.avg_rating.toFixed(1) + ' ⭐' : 'N/A'}</td>
                        </tr>
                    `;
                } else {
                    html = '<tr><td colspan="6" class="text-center">No data available for this seller</td></tr>';
                }
            }
            
            document.getElementById('sellersTable').innerHTML = html;
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            loadSellerOptions();
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

# ==================== NEW API ENDPOINTS FOR SELLER SELECTION ====================

@app.route('/api/sellers/list')
def sellers_list():
    """Get list of top sellers for dropdown"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                s.seller_id,
                s.seller_city,
                s.seller_state,
                COALESCE(SUM(oi.price), 0) as total_revenue
            FROM sellers s
            LEFT JOIN order_items oi ON s.seller_id = oi.seller_id
            GROUP BY s.seller_id, s.seller_city, s.seller_state
            ORDER BY total_revenue DESC
            LIMIT 50
        """)
        
        results = cursor.fetchall()
        
        # Convert decimal to float
        for row in results:
            row['total_revenue'] = float(row['total_revenue'] or 0)
        
        cursor.close()
        conn.close()
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sellers/search')
def sellers_search():
    """Search sellers by ID or city"""
    try:
        search_term = request.args.get('q', '')
        if not search_term:
            return jsonify([])
        
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                s.seller_id,
                s.seller_city,
                s.seller_state,
                COALESCE(SUM(oi.price), 0) as total_revenue
            FROM sellers s
            LEFT JOIN order_items oi ON s.seller_id = oi.seller_id
            WHERE s.seller_id LIKE %s 
               OR s.seller_city LIKE %s
            GROUP BY s.seller_id, s.seller_city, s.seller_state
            ORDER BY total_revenue DESC
            LIMIT 20
        """, (f'%{search_term}%', f'%{search_term}%'))
        
        results = cursor.fetchall()
        
        # Convert decimal to float
        for row in results:
            row['total_revenue'] = float(row['total_revenue'] or 0)
        
        cursor.close()
        conn.close()
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== UPDATED API ENDPOINTS WITH SELLER FILTER ====================

@app.route('/api/dashboard/stats')
def dashboard_stats():
    """Get dashboard overview statistics with optional seller filter"""
    try:
        seller_id = request.args.get('seller_id')
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        if seller_id:
            # Individual seller stats
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT oi.order_id) as total_orders,
                    COALESCE(SUM(oi.price), 0) as total_revenue,
                    COALESCE(AVG(oi.price), 0) as avg_order_value,
                    COUNT(DISTINCT oi.product_id) as total_products
                FROM order_items oi
                WHERE oi.seller_id = %s
            """, (seller_id,))
            
            result = cursor.fetchone()
            total_orders = result['total_orders']
            total_revenue = float(result['total_revenue'])
            avg_order_value = float(result['avg_order_value'])
            total_products = result['total_products']
            
            return jsonify({
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'avg_order_value': avg_order_value,
                'total_products': total_products
            })
        else:
            # All sellers stats
            cursor.execute("SELECT COUNT(*) as count FROM sellers")
            total_sellers = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM orders")
            total_orders = cursor.fetchone()['count']
            
            cursor.execute("SELECT COALESCE(SUM(price), 0) as total FROM order_items")
            total_revenue = float(cursor.fetchone()['total'])
            
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
    """Get revenue trend with optional seller filter"""
    try:
        seller_id = request.args.get('seller_id')
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        if seller_id:
            query = """
                SELECT 
                    DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') as month,
                    SUM(oi.price) as revenue
                FROM orders o
                JOIN order_items oi ON o.order_id = oi.order_id
                WHERE o.order_purchase_timestamp IS NOT NULL
                  AND oi.seller_id = %s
                GROUP BY DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m')
                ORDER BY month
            """
            cursor.execute(query, (seller_id,))
        else:
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
    """Get order status distribution with optional seller filter"""
    try:
        seller_id = request.args.get('seller_id')
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        if seller_id:
            query = """
                SELECT 
                    o.order_status,
                    COUNT(*) as count
                FROM orders o
                JOIN order_items oi ON o.order_id = oi.order_id
                WHERE oi.seller_id = %s
                GROUP BY o.order_status
                ORDER BY count DESC
            """
            cursor.execute(query, (seller_id,))
        else:
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
    """Get top product categories with optional seller filter"""
    try:
        seller_id = request.args.get('seller_id')
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        if seller_id:
            query = """
                SELECT 
                    COALESCE(p.product_category_name, 'Uncategorized') as category,
                    COUNT(*) as product_count
                FROM products p
                JOIN order_items oi ON p.product_id = oi.product_id
                WHERE oi.seller_id = %s
                GROUP BY p.product_category_name
                ORDER BY product_count DESC
                LIMIT 10
            """
            cursor.execute(query, (seller_id,))
        else:
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
    """Get price distribution with optional seller filter"""
    try:
        seller_id = request.args.get('seller_id')
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        if seller_id:
            query = """
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
                WHERE seller_id = %s
                GROUP BY price_range
                ORDER BY 
                    CASE price_range
                        WHEN '0-10' THEN 1
                        WHEN '11-50' THEN 2
                        WHEN '51-100' THEN 3
                        WHEN '101-200' THEN 4
                        ELSE 5
                    END
            """
            cursor.execute(query, (seller_id,))
        else:
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
    """Get top sellers"""
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

@app.route('/api/dashboard/seller-details')
def seller_details():
    """Get detailed information for a specific seller"""
    try:
        seller_id = request.args.get('seller_id')
        if not seller_id:
            return jsonify({'error': 'Seller ID required'}), 400
        
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                s.seller_id,
                s.seller_city,
                s.seller_state,
                COUNT(DISTINCT oi.order_id) as order_count,
                SUM(oi.price) as total_revenue,
                AVG(oi.price) as avg_order_value,
                COUNT(DISTINCT oi.product_id) as total_products,
                COUNT(DISTINCT o.customer_id) as unique_customers,
                MIN(o.order_purchase_timestamp) as first_order_date,
                MAX(o.order_purchase_timestamp) as last_order_date,
                DATEDIFF(MAX(o.order_purchase_timestamp), MIN(o.order_purchase_timestamp)) as active_days,
                AVG(oi.price) as avg_rating
            FROM sellers s
            JOIN order_items oi ON s.seller_id = oi.seller_id
            JOIN orders o ON oi.order_id = o.order_id
            WHERE s.seller_id = %s
            GROUP BY s.seller_id, s.seller_city, s.seller_state
        """, (seller_id,))
        
        results = cursor.fetchall()
        
        # Convert decimal to float for JSON
        for row in results:
            row['total_revenue'] = float(row['total_revenue'] or 0)
            row['avg_order_value'] = float(row['avg_order_value'] or 0)
            row['avg_rating'] = float(row['avg_rating'] or 0)
        
        cursor.close()
        conn.close()
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    PORT = 5004
    print("🚀 Starting Enhanced Seller Dashboard with Seller Selection")
    print(f"📊 Dashboard: http://localhost:{PORT}")
    print("🎯 Features: Seller dropdown, individual analytics, search functionality")
    print("📋 Toggle between 'All Sellers' view and individual seller performance")
    app.run(host='0.0.0.0', port=PORT, debug=True)