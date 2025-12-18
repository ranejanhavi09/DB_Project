"""
Modern E-Commerce Analytics Dashboard with Admin & Seller Views
"""
from flask import Flask, jsonify, render_template, request, redirect, url_for
import mysql.connector
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# MySQL Configuration
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mysql123',
    'database': 'ecom_master'
}

def get_mysql_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)

# ==================== LANDING PAGE ====================
@app.route('/')
def landing():
    """Landing page with options for admin or seller dashboard"""
    return render_template('landing.html')

# ==================== ADMIN DASHBOARD ====================
@app.route('/admin')
def admin_dashboard():
    """Admin dashboard with aggregated views"""
    return render_template('admin_dashboard.html')

# ==================== SELLER DASHBOARD ====================
@app.route('/seller')
def seller_dashboard():
    """Seller dashboard with dropdown to select seller"""
    return render_template('seller_dashboard.html')

# ==================== HTML TEMPLATES ====================

# Landing Page Template
LANDING_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>📊 E-Commerce Analytics Platform</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary: #3b82f6;
            --primary-light: #60a5fa;
            --primary-dark: #2563eb;
            --secondary: #8b5cf6;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --gray-50: #f9fafb;
            --gray-100: #f3f4f6;
            --gray-900: #111827;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .landing-container {
            max-width: 1000px;
            width: 100%;
            animation: fadeIn 0.8s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .header {
            text-align: center;
            margin-bottom: 50px;
        }
        
        .logo {
            font-size: 48px;
            color: white;
            margin-bottom: 20px;
        }
        
        .title {
            font-size: 48px;
            font-weight: 800;
            color: white;
            margin-bottom: 10px;
            line-height: 1.2;
        }
        
        .subtitle {
            font-size: 20px;
            color: rgba(255, 255, 255, 0.9);
            font-weight: 300;
            margin-bottom: 40px;
        }
        
        .dashboard-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }
        
        .dashboard-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }
        
        .dashboard-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.2);
        }
        
        .card-icon {
            font-size: 48px;
            margin-bottom: 20px;
            height: 80px;
            width: 80px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            margin: 0 auto 25px;
        }
        
        .admin-card .card-icon {
            background: linear-gradient(135deg, #3b82f6, #60a5fa);
            color: white;
        }
        
        .seller-card .card-icon {
            background: linear-gradient(135deg, #8b5cf6, #a78bfa);
            color: white;
        }
        
        .card-title {
            font-size: 28px;
            font-weight: 700;
            color: var(--gray-900);
            margin-bottom: 15px;
        }
        
        .card-description {
            font-size: 16px;
            color: #6b7280;
            line-height: 1.6;
            margin-bottom: 30px;
        }
        
        .btn-dashboard {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            padding: 15px 30px;
            font-size: 16px;
            font-weight: 600;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            width: 100%;
        }
        
        .btn-admin {
            background: linear-gradient(135deg, #3b82f6, #2563eb);
            color: white;
        }
        
        .btn-admin:hover {
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            transform: scale(1.05);
        }
        
        .btn-seller {
            background: linear-gradient(135deg, #8b5cf6, #7c3aed);
            color: white;
        }
        
        .btn-seller:hover {
            background: linear-gradient(135deg, #7c3aed, #6d28d9);
            transform: scale(1.05);
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 60px;
            padding: 30px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        
        .feature {
            text-align: center;
            padding: 20px;
        }
        
        .feature-icon {
            font-size: 24px;
            color: white;
            margin-bottom: 15px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 50px;
            height: 50px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 50%;
        }
        
        .feature-text {
            color: white;
            font-size: 14px;
            font-weight: 500;
        }
        
        .footer {
            text-align: center;
            margin-top: 60px;
            color: rgba(255, 255, 255, 0.7);
            font-size: 14px;
        }
        
        @media (max-width: 768px) {
            .title { font-size: 36px; }
            .subtitle { font-size: 18px; }
            .dashboard-cards { grid-template-columns: 1fr; }
            .card-title { font-size: 24px; }
        }
    </style>
</head>
<body>
    <div class="landing-container">
        <div class="header">
            <div class="logo">
                <i class="fas fa-chart-line"></i>
            </div>
            <h1 class="title">E-Commerce Analytics Platform</h1>
            <p class="subtitle">Advanced insights for Brazilian e-commerce marketplace</p>
        </div>
        
        <div class="dashboard-cards">
            <div class="dashboard-card admin-card">
                <div class="card-icon">
                    <i class="fas fa-users-cog"></i>
                </div>
                <h2 class="card-title">Admin Dashboard</h2>
                <p class="card-description">
                    Comprehensive platform analytics, customer insights, geographic distribution, 
                    and product performance across all sellers.
                </p>
                <a href="/admin" class="btn-dashboard btn-admin">
                    <i class="fas fa-tachometer-alt"></i>
                    Enter Admin Dashboard
                </a>
            </div>
            
            <div class="dashboard-card seller-card">
                <div class="card-icon">
                    <i class="fas fa-user-tie"></i>
                </div>
                <h2 class="card-title">Seller Dashboard</h2>
                <p class="card-description">
                    Personalized analytics for individual sellers with performance metrics, 
                    product insights, and customer behavior analysis.
                </p>
                <a href="/seller" class="btn-dashboard btn-seller">
                    <i class="fas fa-chart-bar"></i>
                    Enter Seller Dashboard
                </a>
            </div>
        </div>
        
        <div class="features">
            <div class="feature">
                <div class="feature-icon">
                    <i class="fas fa-map-marker-alt"></i>
                </div>
                <div class="feature-text">Geographic Analysis</div>
            </div>
            <div class="feature">
                <div class="feature-icon">
                    <i class="fas fa-shopping-bag"></i>
                </div>
                <div class="feature-text">Product Performance</div>
            </div>
            <div class="feature">
                <div class="feature-icon">
                    <i class="fas fa-chart-pie"></i>
                </div>
                <div class="feature-text">Revenue Analytics</div>
            </div>
            <div class="feature">
                <div class="feature-icon">
                    <i class="fas fa-star"></i>
                </div>
                <div class="feature-text">Customer Satisfaction</div>
            </div>
        </div>
        
        <div class="footer">
            <p>Powered by MySQL | Real-time Analytics Dashboard</p>
            <p>© 2024 Brazilian E-Commerce Analytics Platform</p>
        </div>
    </div>
</body>
</html>
'''

# Admin Dashboard Template
ADMIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>📊 Admin Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary: #3b82f6;
            --primary-light: #60a5fa;
            --primary-dark: #2563eb;
            --secondary: #8b5cf6;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --info: #06b6d4;
            --gray-50: #f9fafb;
            --gray-100: #f3f4f6;
            --gray-200: #e5e7eb;
            --gray-300: #d1d5db;
            --gray-400: #9ca3af;
            --gray-500: #6b7280;
            --gray-600: #4b5563;
            --gray-700: #374151;
            --gray-800: #1f2937;
            --gray-900: #111827;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background-color: var(--gray-50);
            color: var(--gray-900);
            min-height: 100vh;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        
        .dashboard-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 24px;
        }
        
        /* Header */
        .header {
            background: white;
            border-bottom: 1px solid var(--gray-200);
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(8px);
            background: rgba(255, 255, 255, 0.95);
        }
        
        .header-content {
            padding: 20px 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .header-left {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .back-btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 16px;
            background: white;
            border: 1px solid var(--gray-300);
            border-radius: 12px;
            font-size: 14px;
            font-weight: 500;
            color: var(--gray-700);
            cursor: pointer;
            transition: all 0.2s;
            text-decoration: none;
        }
        
        .back-btn:hover {
            background: var(--gray-50);
            border-color: var(--gray-400);
        }
        
        .header-title h1 {
            font-size: 24px;
            font-weight: 700;
            color: var(--gray-900);
            margin: 0;
            line-height: 1.2;
        }
        
        .header-title p {
            font-size: 14px;
            color: var(--gray-600);
            margin-top: 4px;
            line-height: 1.4;
        }
        
        /* Navigation */
        .nav-tabs {
            display: flex;
            gap: 2px;
            background: var(--gray-100);
            padding: 4px;
            border-radius: 12px;
            margin: 20px 0 30px 0;
        }
        
        .nav-tab {
            flex: 1;
            padding: 12px 20px;
            border: none;
            background: transparent;
            font-size: 14px;
            font-weight: 600;
            color: var(--gray-600);
            cursor: pointer;
            text-align: center;
            border-radius: 8px;
            transition: all 0.2s;
        }
        
        .nav-tab:hover {
            color: var(--gray-900);
            background: var(--gray-200);
        }
        
        .nav-tab.active {
            background: white;
            color: var(--primary);
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        /* Tab Content */
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
            animation: fadeIn 0.3s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 32px;
        }
        
        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
            border: 1px solid var(--gray-200);
            transition: transform 0.2s, box-shadow 0.2s;
            height: 140px;
            display: flex;
            flex-direction: column;
        }
        
        .stat-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }
        
        .stat-card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
        }
        
        .stat-icon-container {
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .stat-icon-container.green { 
            background: linear-gradient(135deg, #d1fae5, #10b981);
            box-shadow: 0 2px 4px rgba(16, 185, 129, 0.1);
        }
        .stat-icon-container.blue { 
            background: linear-gradient(135deg, #dbeafe, #3b82f6);
            box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1);
        }
        .stat-icon-container.purple { 
            background: linear-gradient(135deg, #ede9fe, #8b5cf6);
            box-shadow: 0 2px 4px rgba(139, 92, 246, 0.1);
        }
        .stat-icon-container.orange { 
            background: linear-gradient(135deg, #ffedd5, #f59e0b);
            box-shadow: 0 2px 4px rgba(245, 158, 11, 0.1);
        }
        .stat-icon-container.red { 
            background: linear-gradient(135deg, #fee2e2, #ef4444);
            box-shadow: 0 2px 4px rgba(239, 68, 68, 0.1);
        }
        .stat-icon-container.teal { 
            background: linear-gradient(135deg, #cffafe, #06b6d4);
            box-shadow: 0 2px 4px rgba(6, 182, 212, 0.1);
        }
        
        .stat-icon {
            width: 24px;
            height: 24px;
            color: white;
        }
        
        .stat-title {
            font-size: 14px;
            font-weight: 500;
            color: var(--gray-600);
            margin-bottom: 8px;
            letter-spacing: 0.01em;
        }
        
        .stat-value {
            font-size: 28px;
            font-weight: 700;
            color: var(--gray-900);
            margin-bottom: 4px;
            line-height: 1.2;
        }
        
        .stat-subtitle {
            font-size: 12px;
            color: var(--gray-500);
            line-height: 1.4;
        }
        
        /* Charts Grid */
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 24px;
            margin-bottom: 32px;
        }
        
        .chart-container {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
            border: 1px solid var(--gray-200);
            height: 400px;
            display: flex;
            flex-direction: column;
        }
        
        .chart-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 24px;
        }
        
        .chart-title {
            font-size: 16px;
            font-weight: 600;
            color: var(--gray-900);
        }
        
        .chart-canvas-container {
            flex: 1;
            position: relative;
            min-height: 0;
        }
        
        /* Tables */
        .table-container {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
            border: 1px solid var(--gray-200);
            margin-bottom: 24px;
        }
        
        .table-header {
            padding: 20px;
            border-bottom: 1px solid var(--gray-200);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .table-title {
            font-size: 16px;
            font-weight: 600;
            color: var(--gray-900);
            margin: 0;
        }
        
        .table-content {
            overflow-x: auto;
        }
        
        .table {
            width: 100%;
            border-collapse: collapse;
            min-width: 800px;
        }
        
        .table thead {
            background-color: var(--gray-50);
        }
        
        .table th {
            padding: 12px 20px;
            text-align: left;
            font-size: 12px;
            font-weight: 600;
            color: var(--gray-600);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 1px solid var(--gray-200);
            white-space: nowrap;
        }
        
        .table td {
            padding: 16px 20px;
            border-bottom: 1px solid var(--gray-200);
            font-size: 14px;
            color: var(--gray-700);
            vertical-align: middle;
        }
        
        .table tr:last-child td {
            border-bottom: none;
        }
        
        .table tr:hover {
            background-color: var(--gray-50);
        }
        
        /* Map Container */
        .map-container {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
            border: 1px solid var(--gray-200);
            height: 500px;
            margin-bottom: 24px;
        }
        
        /* Footer */
        .footer {
            padding: 20px 0;
            text-align: center;
            color: var(--gray-500);
            font-size: 12px;
            border-top: 1px solid var(--gray-200);
            margin-top: 32px;
        }
        
        /* Loading */
        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px;
            color: var(--gray-500);
        }
        
        .spinner {
            width: 32px;
            height: 32px;
            border: 3px solid var(--gray-200);
            border-top-color: var(--primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--gray-100);
            border-radius: 3px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--gray-300);
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <!-- Header -->
    <header class="header">
        <div class="dashboard-container">
            <div class="header-content">
                <div class="header-left">
                    <a href="/" class="back-btn">
                        <i class="fas fa-arrow-left"></i>
                        Back to Home
                    </a>
                    <div class="header-title">
                        <h1>Admin Dashboard</h1>
                        <p>Comprehensive platform analytics and insights</p>
                    </div>
                </div>
                <div class="header-right">
                    <button class="refresh-btn" onclick="loadCurrentTab()">
                        <i class="fas fa-sync-alt"></i>
                        Refresh
                    </button>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
        <div class="dashboard-container">
            <!-- Navigation Tabs -->
            <div class="nav-tabs">
                <button class="nav-tab active" onclick="showTab('overview')">Overview</button>
                <button class="nav-tab" onclick="showTab('customers')">Customers</button>
                <button class="nav-tab" onclick="showTab('geographic')">Geographic</button>
                <button class="nav-tab" onclick="showTab('products')">Products</button>
                <button class="nav-tab" onclick="showTab('sellers')">Sellers</button>
            </div>

            <!-- Overview Tab -->
            <div id="overviewTab" class="tab-content active">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div class="stat-icon-container green">
                                <i class="fas fa-dollar-sign stat-icon"></i>
                            </div>
                        </div>
                        <div class="stat-title">Total Platform Revenue</div>
                        <div class="stat-value" id="totalRevenue">$0.00</div>
                        <div class="stat-subtitle">All-time sales across all sellers</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div class="stat-icon-container blue">
                                <i class="fas fa-shopping-cart stat-icon"></i>
                            </div>
                        </div>
                        <div class="stat-title">Total Orders</div>
                        <div class="stat-value" id="totalOrders">0</div>
                        <div class="stat-subtitle">Completed transactions</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div class="stat-icon-container purple">
                                <i class="fas fa-users stat-icon"></i>
                            </div>
                        </div>
                        <div class="stat-title">Total Customers</div>
                        <div class="stat-value" id="totalCustomers">0</div>
                        <div class="stat-subtitle">Registered buyers</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div class="stat-icon-container orange">
                                <i class="fas fa-store stat-icon"></i>
                            </div>
                        </div>
                        <div class="stat-title">Active Sellers</div>
                        <div class="stat-value" id="totalSellers">0</div>
                        <div class="stat-subtitle">Sellers with orders</div>
                    </div>
                </div>

                <div class="charts-grid">
                    <div class="chart-container">
                        <div class="chart-header">
                            <div class="chart-title">Monthly Revenue Trend</div>
                        </div>
                        <div class="chart-canvas-container">
                            <canvas id="revenueChart"></canvas>
                        </div>
                    </div>
                    
                    <div class="chart-container">
                        <div class="chart-header">
                            <div class="chart-title">Order Status Distribution</div>
                        </div>
                        <div class="chart-canvas-container">
                            <canvas id="statusChart"></canvas>
                        </div>
                    </div>
                </div>

                <div class="table-container">
                    <div class="table-header">
                        <h3 class="table-title">Top 10 Sellers by Revenue</h3>
                    </div>
                    <div class="table-content">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Rank</th>
                                    <th>Seller ID</th>
                                    <th>Location</th>
                                    <th>Orders</th>
                                    <th>Revenue</th>
                                    <th>Avg Order</th>
                                </tr>
                            </thead>
                            <tbody id="topSellersTable">
                                <!-- Populated by JavaScript -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Customers Tab -->
            <div id="customersTab" class="tab-content">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div class="stat-icon-container green">
                                <i class="fas fa-chart-line stat-icon"></i>
                            </div>
                        </div>
                        <div class="stat-title">Avg Customer Lifetime Value</div>
                        <div class="stat-value" id="avgLTV">$0.00</div>
                        <div class="stat-subtitle">Average per customer</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div class="stat-icon-container blue">
                                <i class="fas fa-redo stat-icon"></i>
                            </div>
                        </div>
                        <div class="stat-title">Repeat Purchase Rate</div>
                        <div class="stat-value" id="repeatRate">0%</div>
                        <div class="stat-subtitle">Customers with >1 purchase</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div class="stat-icon-container purple">
                                <i class="fas fa-star stat-icon"></i>
                            </div>
                        </div>
                        <div class="stat-title">Avg Review Score</div>
                        <div class="stat-value" id="avgReview">0.0</div>
                        <div class="stat-subtitle">Out of 5 stars</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div class="stat-icon-container orange">
                                <i class="fas fa-user-plus stat-icon"></i>
                            </div>
                        </div>
                        <div class="stat-title">New Customers (30 days)</div>
                        <div class="stat-value" id="newCustomers">0</div>
                        <div class="stat-subtitle">Recently registered</div>
                    </div>
                </div>

                <div class="charts-grid">
                    <div class="chart-container">
                        <div class="chart-header">
                            <div class="chart-title">Customer Segmentation by LTV</div>
                        </div>
                        <div class="chart-canvas-container">
                            <canvas id="customerSegmentationChart"></canvas>
                        </div>
                    </div>
                    
                    <div class="chart-container">
                        <div class="chart-header">
                            <div class="chart-title">Repeat Purchase Analysis</div>
                        </div>
                        <div class="chart-canvas-container">
                            <canvas id="repeatPurchaseChart"></canvas>
                        </div>
                    </div>
                </div>

                <div class="table-container">
                    <div class="table-header">
                        <h3 class="table-title">Top 20 Customers by Lifetime Value</h3>
                    </div>
                    <div class="table-content">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Rank</th>
                                    <th>Customer ID</th>
                                    <th>Location</th>
                                    <th>Total Orders</th>
                                    <th>Lifetime Value</th>
                                    <th>Avg Review</th>
                                </tr>
                            </thead>
                            <tbody id="topCustomersTable">
                                <!-- Populated by JavaScript -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Geographic Tab -->
            <div id="geographicTab" class="tab-content">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div class="stat-icon-container green">
                                <i class="fas fa-map-marked-alt stat-icon"></i>
                            </div>
                        </div>
                        <div class="stat-title">States Served</div>
                        <div class="stat-value" id="statesServed">0</div>
                        <div class="stat-subtitle">Brazilian states</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div class="stat-icon-container blue">
                                <i class="fas fa-city stat-icon"></i>
                            </div>
                        </div>
                        <div class="stat-title">Cities Served</div>
                        <div class="stat-value" id="citiesServed">0</div>
                        <div class="stat-subtitle">Across Brazil</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div class="stat-icon-container purple">
                                <i class="fas fa-users stat-icon"></i>
                            </div>
                        </div>
                        <div class="stat-title">Top State by Orders</div>
                        <div class="stat-value" id="topState">-</div>
                        <div class="stat-subtitle">Highest order volume</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div class="stat-icon-container orange">
                                <i class="fas fa-star stat-icon"></i>
                            </div>
                        </div>
                        <div class="stat-title">Top State by Satisfaction</div>
                        <div class="stat-value" id="topStateSatisfaction">-</div>
                        <div class="stat-subtitle">Highest review score</div>
                    </div>
                </div>

                <div class="charts-grid">
                    <div class="chart-container">
                        <div class="chart-header">
                            <div class="chart-title">Customer Distribution by State</div>
                        </div>
                        <div class="chart-canvas-container">
                            <canvas id="stateDistributionChart"></canvas>
                        </div>
                    </div>
                    
                    <div class="chart-container">
                        <div class="chart-header">
                            <div class="chart-title">Revenue by State</div>
                        </div>
                        <div class="chart-canvas-container">
                            <canvas id="stateRevenueChart"></canvas>
                        </div>
                    </div>
                </div>

                <div class="table-container">
                    <div class="table-header">
                        <h3 class="table-title">Top 10 Cities by Order Volume</h3>
                    </div>
                    <div class="table-content">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Rank</th>
                                    <th>City</th>
                                    <th>State</th>
                                    <th>Total Orders</th>
                                    <th>Revenue</th>
                                    <th>Avg Satisfaction</th>
                                </tr>
                            </thead>
                            <tbody id="topCitiesTable">
                                <!-- Populated by JavaScript -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Products Tab -->
            <div id="productsTab" class="tab-content">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div class="stat-icon-container green">
                                <i class="fas fa-tags stat-icon"></i>
                            </div>
                        </div>
                        <div class="stat-title">Product Categories</div>
                        <div class="stat-value" id="totalCategories">0</div>
                        <div class="stat-subtitle">Unique categories</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div class="stat-icon-container blue">
                                <i class="fas fa-box-open stat-icon"></i>
                            </div>
                        </div>
                        <div class="stat-title">Total Products</div>
                        <div class="stat-value" id="totalProducts">0</div>
                        <div class="stat-subtitle">In catalog</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div class="stat-icon-container purple">
                                <i class="fas fa-shipping-fast stat-icon"></i>
                            </div>
                        </div>
                        <div class="stat-title">Avg Delivery Days</div>
                        <div class="stat-value" id="avgDeliveryDays">0.0</div>
                        <div class="stat-subtitle">Across all products</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div class="stat-icon-container orange">
                                <i class="fas fa-truck-loading stat-icon"></i>
                            </div>
                        </div>
                        <div class="stat-title">Avg Freight Cost</div>
                        <div class="stat-value" id="avgFreight">$0.00</div>
                        <div class="stat-subtitle">Shipping cost average</div>
                    </div>
                </div>

                <div class="charts-grid">
                    <div class="chart-container">
                        <div class="chart-header">
                            <div class="chart-title">Revenue by Product Category</div>
                        </div>
                        <div class="chart-canvas-container">
                            <canvas id="categoryRevenueChart"></canvas>
                        </div>
                    </div>
                    
                    <div class="chart-container">
                        <div class="chart-header">
                            <div class="chart-title">Product Review Quality by Category</div>
                        </div>
                        <div class="chart-canvas-container">
                            <canvas id="categoryReviewChart"></canvas>
                        </div>
                    </div>
                </div>

                <div class="table-container">
                    <div class="table-header">
                        <h3 class="table-title">Top 10 Best-Selling Products</h3>
                    </div>
                    <div class="table-content">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Rank</th>
                                    <th>Product ID</th>
                                    <th>Category</th>
                                    <th>Units Sold</th>
                                    <th>Revenue</th>
                                    <th>Avg Rating</th>
                                </tr>
                            </thead>
                            <tbody id="topProductsTable">
                                <!-- Populated by JavaScript -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Sellers Tab -->
            <div id="sellersTab" class="tab-content">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div class="stat-icon-container green">
                                <i class="fas fa-chart-bar stat-icon"></i>
                            </div>
                        </div>
                        <div class="stat-title">Avg Seller Rating</div>
                        <div class="stat-value" id="avgSellerRating">0.0</div>
                        <div class="stat-subtitle">Out of 5 stars</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div class="stat-icon-container blue">
                                <i class="fas fa-truck stat-icon"></i>
                            </div>
                        </div>
                        <div class="stat-title">Avg Delivery Performance</div>
                        <div class="stat-value" id="avgDeliveryPerformance">0%</div>
                        <div class="stat-subtitle">On-time delivery rate</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div class="stat-icon-container purple">
                                <i class="fas fa-globe-americas stat-icon"></i>
                            </div>
                        </div>
                        <div class="stat-title">Avg States Served</div>
                        <div class="stat-value" id="avgStatesServed">0.0</div>
                        <div class="stat-subtitle">Per seller</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-card-header">
                            <div class="stat-icon-container orange">
                                <i class="fas fa-layer-group stat-icon"></i>
                            </div>
                        </div>
                        <div class="stat-title">Avg Categories per Seller</div>
                        <div class="stat-value" id="avgCategoriesPerSeller">0.0</div>
                        <div class="stat-subtitle">Product diversification</div>
                    </div>
                </div>

                <div class="charts-grid">
                    <div class="chart-container">
                        <div class="chart-header">
                            <div class="chart-title">Seller Performance Distribution</div>
                        </div>
                        <div class="chart-canvas-container">
                            <canvas id="sellerPerformanceChart"></canvas>
                        </div>
                    </div>
                    
                    <div class="chart-container">
                        <div class="chart-header">
                            <div class="chart-title">Seller Geographic Coverage</div>
                        </div>
                        <div class="chart-canvas-container">
                            <canvas id="sellerCoverageChart"></canvas>
                        </div>
                    </div>
                </div>

                <div class="table-container">
                    <div class="table-header">
                        <h3 class="table-title">Seller Diversification Analysis</h3>
                    </div>
                    <div class="table-content">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Seller ID</th>
                                    <th>Location</th>
                                    <th>Categories</th>
                                    <th>Products</th>
                                    <th>States Served</th>
                                    <th>Diversification Level</th>
                                </tr>
                            </thead>
                            <tbody id="sellerDiversificationTable">
                                <!-- Populated by JavaScript -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- Footer -->
    <footer class="footer">
        <div class="dashboard-container">
            <p>Admin Dashboard | Data source: MySQL ecom_master database</p>
            <p class="mt-2">Last updated: <span id="lastUpdated">Loading...</span></p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        let currentTab = 'overview';
        let charts = {};
        
        // Formatting functions
        function formatCurrency(value) {
            if (!value) return '$0.00';
            const num = parseFloat(value);
            if (isNaN(num)) return '$0.00';
            if (num >= 1000000) return '$' + (num / 1000000).toFixed(1) + 'M';
            if (num >= 1000) return '$' + (num / 1000).toFixed(1) + 'K';
            return '$' + num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }
        
        function formatNumber(num) {
            if (!num) return '0';
            const intNum = parseInt(num);
            if (isNaN(intNum)) return '0';
            if (intNum >= 1000000) return (intNum / 1000000).toFixed(1) + 'M';
            if (intNum >= 1000) return (intNum / 1000).toFixed(1) + 'K';
            return intNum.toLocaleString('en-US');
        }
        
        // Tab management
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.nav-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName + 'Tab').classList.add('active');
            document.querySelector(`.nav-tab[onclick="showTab('${tabName}')"]`).classList.add('active');
            
            currentTab = tabName;
            loadCurrentTab();
        }
        
        function loadCurrentTab() {
            switch(currentTab) {
                case 'overview':
                    loadOverview();
                    break;
                case 'customers':
                    loadCustomers();
                    break;
                case 'geographic':
                    loadGeographic();
                    break;
                case 'products':
                    loadProducts();
                    break;
                case 'sellers':
                    loadSellers();
                    break;
            }
            updateTimestamp();
        }
        
        // Load data for each tab
        async function loadOverview() {
            try {
                const [stats, revenue, status, sellers] = await Promise.all([
                    fetch('/api/admin/stats').then(r => r.json()),
                    fetch('/api/admin/revenue-trend').then(r => r.json()),
                    fetch('/api/admin/order-status').then(r => r.json()),
                    fetch('/api/admin/top-sellers').then(r => r.json())
                ]);
                
                // Update stats
                document.getElementById('totalRevenue').textContent = formatCurrency(stats.total_revenue);
                document.getElementById('totalOrders').textContent = formatNumber(stats.total_orders);
                document.getElementById('totalCustomers').textContent = formatNumber(stats.total_customers);
                document.getElementById('totalSellers').textContent = formatNumber(stats.total_sellers);
                
                // Update charts
                updateRevenueChart(revenue);
                updateStatusChart(status);
                
                // Update table
                updateTopSellersTable(sellers);
                
            } catch (error) {
                console.error('Error loading overview:', error);
            }
        }
        
        async function loadCustomers() {
            try {
                const [ltv, repeat, customers] = await Promise.all([
                    fetch('/api/admin/customer-ltv').then(r => r.json()),
                    fetch('/api/admin/repeat-purchase').then(r => r.json()),
                    fetch('/api/admin/top-customers').then(r => r.json())
                ]);
                
                // Update stats
                document.getElementById('avgLTV').textContent = formatCurrency(ltv.avg_lifetime_value);
                document.getElementById('repeatRate').textContent = ltv.repeat_purchase_rate + '%';
                document.getElementById('avgReview').textContent = ltv.avg_review_score.toFixed(1);
                document.getElementById('newCustomers').textContent = formatNumber(ltv.new_customers);
                
                // Update charts
                updateCustomerSegmentationChart(ltv);
                updateRepeatPurchaseChart(repeat);
                
                // Update table
                updateTopCustomersTable(customers);
                
            } catch (error) {
                console.error('Error loading customers:', error);
            }
        }
        
        async function loadGeographic() {
            try {
                const [distribution, topCities] = await Promise.all([
                    fetch('/api/admin/geographic-distribution').then(r => r.json()),
                    fetch('/api/admin/top-cities').then(r => r.json())
                ]);
                
                // Update stats
                document.getElementById('statesServed').textContent = distribution.states_count;
                document.getElementById('citiesServed').textContent = distribution.cities_count;
                document.getElementById('topState').textContent = distribution.top_state || '-';
                document.getElementById('topStateSatisfaction').textContent = distribution.top_state_satisfaction || '-';
                
                // Update charts
                updateStateDistributionChart(distribution);
                updateStateRevenueChart(distribution);
                
                // Update table
                updateTopCitiesTable(topCities);
                
            } catch (error) {
                console.error('Error loading geographic:', error);
            }
        }
        
        async function loadProducts() {
            try {
                const [categories, topProducts] = await Promise.all([
                    fetch('/api/admin/product-categories').then(r => r.json()),
                    fetch('/api/admin/top-products').then(r => r.json())
                ]);
                
                // Update stats
                document.getElementById('totalCategories').textContent = categories.categories_count;
                document.getElementById('totalProducts').textContent = formatNumber(categories.products_count);
                document.getElementById('avgDeliveryDays').textContent = categories.avg_delivery_days.toFixed(1);
                document.getElementById('avgFreight').textContent = formatCurrency(categories.avg_freight_cost);
                
                // Update charts
                updateCategoryRevenueChart(categories);
                updateCategoryReviewChart(categories);
                
                // Update table
                updateTopProductsTable(topProducts);
                
            } catch (error) {
                console.error('Error loading products:', error);
            }
        }
        
        async function loadSellers() {
            try {
                const [performance, diversification] = await Promise.all([
                    fetch('/api/admin/seller-performance').then(r => r.json()),
                    fetch('/api/admin/seller-diversification').then(r => r.json())
                ]);
                
                // Update stats
                document.getElementById('avgSellerRating').textContent = performance.avg_rating.toFixed(1);
                document.getElementById('avgDeliveryPerformance').textContent = performance.on_time_rate + '%';
                document.getElementById('avgStatesServed').textContent = performance.avg_states_served.toFixed(1);
                document.getElementById('avgCategoriesPerSeller').textContent = performance.avg_categories.toFixed(1);
                
                // Update charts
                updateSellerPerformanceChart(performance);
                updateSellerCoverageChart(performance);
                
                // Update table
                updateSellerDiversificationTable(diversification);
                
            } catch (error) {
                console.error('Error loading sellers:', error);
            }
        }
        
        // Chart update functions
        function updateRevenueChart(data) {
            if (charts.revenue) charts.revenue.destroy();
            
            const ctx = document.getElementById('revenueChart').getContext('2d');
            charts.revenue = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.months || [],
                    datasets: [{
                        label: 'Monthly Revenue',
                        data: data.revenue || [],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.05)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        }
        
        function updateStatusChart(data) {
            if (charts.status) charts.status.destroy();
            
            const ctx = document.getElementById('statusChart').getContext('2d');
            charts.status = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.labels || [],
                    datasets: [{
                        data: data.data || [],
                        backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ef4444']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '75%',
                    plugins: { legend: { position: 'right' } }
                }
            });
        }
        
        // Table update functions
        function updateTopSellersTable(sellers) {
            const tbody = document.getElementById('topSellersTable');
            let html = '';
            
            sellers.slice(0, 10).forEach((seller, index) => {
                html += `
                    <tr>
                        <td>${index + 1}</td>
                        <td>${seller.seller_id.substring(0, 12)}...</td>
                        <td>${seller.seller_city || '-'}, ${seller.seller_state || '-'}</td>
                        <td>${formatNumber(seller.order_count)}</td>
                        <td>${formatCurrency(seller.total_revenue)}</td>
                        <td>${formatCurrency(seller.avg_order_value)}</td>
                    </tr>
                `;
            });
            
            tbody.innerHTML = html || '<tr><td colspan="6" class="text-center">No data available</td></tr>';
        }
        
        // Add similar functions for other tables and charts...
        
        function updateTimestamp() {
            document.getElementById('lastUpdated').textContent = new Date().toLocaleString();
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadCurrentTab();
        });
    </script>
</body>
</html>
'''

# Seller Dashboard Template (using your original template with modifications)
SELLER_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>📊 Seller Analytics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        /* Keep all your original CSS styles */
        :root {
            --primary: #3b82f6;
            --primary-light: #60a5fa;
            --primary-dark: #2563eb;
            --secondary: #8b5cf6;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --info: #06b6d4;
            --gray-50: #f9fafb;
            --gray-100: #f3f4f6;
            --gray-200: #e5e7eb;
            --gray-300: #d1d5db;
            --gray-400: #9ca3af;
            --gray-500: #6b7280;
            --gray-600: #4b5563;
            --gray-700: #374151;
            --gray-800: #1f2937;
            --gray-900: #111827;
        }
        
        /* All your original CSS here - keeping it as is */
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background-color: var(--gray-50);
            color: var(--gray-900);
            min-height: 100vh;
        }
        
        .dashboard-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 24px;
        }
        
        /* Add back button */
        .back-btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 16px;
            background: white;
            border: 1px solid var(--gray-300);
            border-radius: 12px;
            font-size: 14px;
            font-weight: 500;
            color: var(--gray-700);
            cursor: pointer;
            transition: all 0.2s;
            text-decoration: none;
            margin-right: 20px;
        }
        
        .back-btn:hover {
            background: var(--gray-50);
            border-color: var(--gray-400);
        }
        
        /* Rest of your original CSS */
        .header-content {
            padding: 20px 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .header-left {
            display: flex;
            align-items: center;
        }
        
        /* ... all other CSS styles from your original dashboard ... */
        
    </style>
</head>
<body>
    <!-- Header -->
    <header class="header">
        <div class="dashboard-container">
            <div class="header-content">
                <div class="header-left">
                    <a href="/" class="back-btn">
                        <i class="fas fa-arrow-left"></i>
                        Back to Home
                    </a>
                    <div class="header-title">
                        <h1>Seller Analytics Dashboard</h1>
                        <p>Monitor your sales performance and insights</p>
                    </div>
                </div>
                <div class="seller-selector">
                    <label for="sellerSelect">Select Seller:</label>
                    <select id="sellerSelect" class="seller-dropdown" onchange="onSellerChange()">
                        <option value="">-- Select a Seller --</option>
                        <!-- Top sellers will be populated here -->
                    </select>
                    <button class="refresh-btn" onclick="loadDashboard()">
                        <i class="fas fa-sync-alt"></i>
                        Refresh
                    </button>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Content - Using your original dashboard structure -->
    <main class="main-content">
        <div class="dashboard-container">
            <!-- Seller Info Banner -->
            <div id="sellerInfo" class="seller-info hidden">
                <!-- Your original seller info banner -->
            </div>

            <!-- Stats Grid -->
            <div class="stats-grid">
                <!-- Your original stats cards -->
            </div>

            <!-- Charts Grid -->
            <div class="charts-grid">
                <!-- Your original charts -->
            </div>

            <!-- Tables Grid -->
            <div class="tables-grid">
                <!-- Your original tables -->
            </div>
        </div>
    </main>

    <!-- Footer -->
    <footer class="footer">
        <div class="dashboard-container">
            <p>Seller Dashboard | Data source: MySQL ecom_master database</p>
            <p class="mt-2">Last updated: <span id="lastUpdated">Loading...</span></p>
        </div>
    </footer>

    <script>
        // Your original JavaScript with modifications to use stored procedures
        let currentSellerId = '';
        let sellerOptions = [];
        
        // Format currency
        function formatCurrency(value) {
            if (value === null || value === undefined || value === '') return '$0.00';
            const num = parseFloat(value);
            if (isNaN(num)) return '$0.00';
            if (num >= 1000000) {
                return '$' + (num / 1000000).toFixed(1) + 'M';
            } else if (num >= 1000) {
                return '$' + (num / 1000).toFixed(1) + 'K';
            }
            return '$' + num.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        }
        
        // Load seller options using stored procedure
        async function loadSellerOptions() {
            try {
                const response = await fetch('/api/sellers/top');
                if (!response.ok) throw new Error('Failed to load sellers');
                const sellers = await response.json();
                
                sellerOptions = sellers;
                const select = document.getElementById('sellerSelect');
                
                // Clear existing options except the first one
                select.innerHTML = '<option value="">-- Select a Seller --</option>';
                
                // Add top sellers
                sellers.forEach(seller => {
                    const option = document.createElement('option');
                    option.value = seller.seller_id;
                    const city = seller.seller_city || 'Unknown';
                    const revenue = formatCurrency(seller.total_revenue);
                    option.textContent = `${seller.seller_id.substring(0, 10)}... - ${city} (${revenue})`;
                    select.appendChild(option);
                });
                
            } catch (error) {
                console.error('Error loading seller options:', error);
            }
        }
        
        // Load dashboard data using stored procedures
        async function loadDashboard() {
            if (!currentSellerId) {
                alert('Please select a seller first');
                return;
            }
            
            try {
                // Call various stored procedures for seller data
                const [overview, revenue, products, delivery, reviews] = await Promise.all([
                    fetch(`/api/seller/overview?seller_id=${currentSellerId}`).then(r => r.json()),
                    fetch(`/api/seller/revenue-trend?seller_id=${currentSellerId}`).then(r => r.json()),
                    fetch(`/api/seller/products?seller_id=${currentSellerId}`).then(r => r.json()),
                    fetch(`/api/seller/delivery?seller_id=${currentSellerId}`).then(r => r.json()),
                    fetch(`/api/seller/reviews?seller_id=${currentSellerId}`).then(r => r.json())
                ]);
                
                // Update UI with data from stored procedures
                updateSellerInfo(overview);
                updateCharts(revenue, products, delivery, reviews);
                updateTables(overview, products);
                
                updateTimestamp();
                
            } catch (error) {
                console.error('Error loading dashboard:', error);
                alert(`Error loading dashboard: ${error.message}`);
            }
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadSellerOptions();
        });
    </script>
</body>
</html>
'''

# ==================== API ENDPOINTS ====================

# Admin Dashboard Endpoints
@app.route('/api/admin/stats')
def admin_stats():
    """Get admin overview statistics"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Use existing stored procedures
        cursor.execute("CALL sp_get_customer_geographic_distribution('2017-01-01', '2018-12-31')")
        geo_data = cursor.fetchall()
        
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT seller_id) as total_sellers,
                COUNT(DISTINCT customer_unique_id) as total_customers,
                COUNT(DISTINCT order_id) as total_orders,
                COALESCE(SUM(price), 0) as total_revenue
            FROM (
                SELECT oi.seller_id, c.customer_unique_id, o.order_id, oi.price
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.order_id
                JOIN customers c ON o.customer_id = c.customer_id
                WHERE o.order_status = 'delivered'
            ) t
        """)
        stats = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'total_sellers': stats['total_sellers'] if stats else 0,
            'total_customers': stats['total_customers'] if stats else 0,
            'total_orders': stats['total_orders'] if stats else 0,
            'total_revenue': float(stats['total_revenue']) if stats else 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/revenue-trend')
def admin_revenue_trend():
    """Get platform revenue trend"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
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

@app.route('/api/admin/order-status')
def admin_order_status():
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

@app.route('/api/admin/top-sellers')
def admin_top_sellers():
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
            WHERE oi.order_id IN (SELECT order_id FROM orders WHERE order_status = 'delivered')
            GROUP BY s.seller_id, s.seller_city, s.seller_state
            ORDER BY total_revenue DESC
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        
        for row in results:
            row['total_revenue'] = float(row['total_revenue'] or 0)
            row['avg_order_value'] = float(row['avg_order_value'] or 0)
        
        cursor.close()
        conn.close()
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Customer analytics endpoints using stored procedures
@app.route('/api/admin/customer-ltv')
def admin_customer_ltv():
    """Get customer lifetime value analysis"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Using stored procedure
        cursor.callproc('sp_get_customer_lifetime_value_analysis', ['2017-01-01', '2018-12-31'])
        for result in cursor.stored_results():
            ltv_data = result.fetchall()
            break
        
        cursor.execute("""
            SELECT 
                ROUND(AVG(lifetime_value), 2) as avg_lifetime_value,
                ROUND(AVG(avg_review_score), 2) as avg_review_score,
                COUNT(CASE WHEN total_orders > 1 THEN 1 END) * 100.0 / COUNT(*) as repeat_purchase_rate,
                COUNT(CASE WHEN first_purchase >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 END) as new_customers
            FROM (
                SELECT 
                    c.customer_unique_id,
                    COUNT(DISTINCT o.order_id) as total_orders,
                    SUM(oi.price) as lifetime_value,
                    AVG(r.review_score) as avg_review_score,
                    MIN(o.order_purchase_timestamp) as first_purchase
                FROM customers c
                JOIN orders o ON c.customer_id = o.customer_id
                JOIN order_items oi ON o.order_id = oi.order_id
                LEFT JOIN order_reviews r ON o.order_id = r.order_id
                WHERE o.order_status = 'delivered'
                GROUP BY c.customer_unique_id
            ) t
        """)
        
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'avg_lifetime_value': float(result['avg_lifetime_value']) if result else 0,
            'avg_review_score': float(result['avg_review_score']) if result else 0,
            'repeat_purchase_rate': round(float(result['repeat_purchase_rate']) if result else 0, 1),
            'new_customers': result['new_customers'] if result else 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/top-customers')
def admin_top_customers():
    """Get top customers"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                c.customer_unique_id,
                c.customer_city,
                c.customer_state,
                COUNT(DISTINCT o.order_id) as total_orders,
                SUM(oi.price) as lifetime_value,
                AVG(r.review_score) as avg_review_score
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            JOIN order_items oi ON o.order_id = oi.order_id
            LEFT JOIN order_reviews r ON o.order_id = r.order_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_unique_id, c.customer_city, c.customer_state
            ORDER BY lifetime_value DESC
            LIMIT 20
        """)
        
        results = cursor.fetchall()
        
        for row in results:
            row['lifetime_value'] = float(row['lifetime_value'] or 0)
            row['avg_review_score'] = float(row['avg_review_score'] or 0)
        
        cursor.close()
        conn.close()
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Geographic analytics endpoints
@app.route('/api/admin/geographic-distribution')
def admin_geographic_distribution():
    """Get geographic distribution"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Using stored procedure
        cursor.callproc('sp_get_customer_geographic_distribution', ['2017-01-01', '2018-12-31'])
        for result in cursor.stored_results():
            geo_data = result.fetchall()
            break
        
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT customer_state) as states_count,
                COUNT(DISTINCT customer_city) as cities_count,
                (SELECT customer_state FROM (
                    SELECT customer_state, COUNT(*) as cnt
                    FROM customers
                    GROUP BY customer_state
                    ORDER BY cnt DESC
                    LIMIT 1
                ) t) as top_state,
                (SELECT customer_state FROM (
                    SELECT c.customer_state, AVG(r.review_score) as avg_score
                    FROM customers c
                    JOIN orders o ON c.customer_id = o.customer_id
                    JOIN order_reviews r ON o.order_id = r.order_id
                    GROUP BY c.customer_state
                    HAVING COUNT(r.review_id) >= 10
                    ORDER BY avg_score DESC
                    LIMIT 1
                ) t) as top_state_satisfaction
            FROM customers
        """)
        
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'states_count': result['states_count'] if result else 0,
            'cities_count': result['cities_count'] if result else 0,
            'top_state': result['top_state'] if result else None,
            'top_state_satisfaction': result['top_state_satisfaction'] if result else None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/top-cities')
def admin_top_cities():
    """Get top cities"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                c.customer_city,
                c.customer_state,
                COUNT(DISTINCT o.order_id) as total_orders,
                SUM(oi.price) as total_revenue,
                AVG(r.review_score) as avg_satisfaction
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            JOIN order_items oi ON o.order_id = oi.order_id
            LEFT JOIN order_reviews r ON o.order_id = r.order_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_city, c.customer_state
            HAVING total_orders >= 10
            ORDER BY total_orders DESC
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        
        for row in results:
            row['total_revenue'] = float(row['total_revenue'] or 0)
            row['avg_satisfaction'] = float(row['avg_satisfaction'] or 0)
        
        cursor.close()
        conn.close()
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Seller Dashboard Endpoints using stored procedures
@app.route('/api/seller/overview')
def seller_overview():
    """Get seller overview using stored procedure"""
    try:
        seller_id = request.args.get('seller_id')
        if not seller_id:
            return jsonify({'error': 'Seller ID required'}), 400
        
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Call stored procedure
        cursor.callproc('sp_get_seller_overview', [
            seller_id,
            '2017-01-01 00:00:00',
            '2018-12-31 23:59:59'
        ])
        
        results = []
        for result in cursor.stored_results():
            results = result.fetchall()
            break
        
        cursor.close()
        conn.close()
        
        if results:
            result = results[0]
            return jsonify({
                'seller_id': result['seller_id'],
                'seller_city': result['seller_city'],
                'seller_state': result['seller_state'],
                'total_orders': result['total_orders'],
                'total_revenue': float(result['total_revenue'] or 0),
                'avg_order_value': float(result['avg_item_price'] or 0),
                'unique_products': result['unique_products_sold'],
                'unique_customers': result['unique_customers'],
                'avg_review_score': float(result['avg_review_score'] or 0),
                'states_served': result['states_served']
            })
        else:
            return jsonify({
                'seller_id': seller_id,
                'total_orders': 0,
                'total_revenue': 0,
                'avg_order_value': 0,
                'unique_products': 0,
                'unique_customers': 0,
                'avg_review_score': 0,
                'states_served': 0
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/seller/revenue-trend')
def seller_revenue_trend():
    """Get seller revenue trend using stored procedure"""
    try:
        seller_id = request.args.get('seller_id')
        if not seller_id:
            return jsonify({'error': 'Seller ID required'}), 400
        
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.callproc('sp_get_seller_revenue_trends', [
            seller_id,
            '2017-01-01 00:00:00',
            '2018-12-31 23:59:59',
            'monthly'
        ])
        
        results = []
        for result in cursor.stored_results():
            results = result.fetchall()
            break
        
        cursor.close()
        conn.close()
        
        months = []
        revenue = []
        
        for row in results:
            months.append(row['period'])
            revenue.append(float(row['revenue'] or 0))
        
        return jsonify({
            'months': months,
            'revenue': revenue
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add more endpoints for other stored procedures...

if __name__ == '__main__':
    PORT = 5004
    print("🚀 Starting Enhanced E-Commerce Analytics Platform")
    print(f"🌐 Landing Page: http://localhost:{PORT}")
    print(f"👑 Admin Dashboard: http://localhost:{PORT}/admin")
    print(f"👨‍💼 Seller Dashboard: http://localhost:{PORT}/seller")
    print("✅ Using stored procedures for optimized queries")
    app.run(host='0.0.0.0', port=PORT, debug=True)