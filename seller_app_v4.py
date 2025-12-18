"""
Modern Seller Dashboard with Fixed JavaScript Errors
"""
from flask import Flask, jsonify, render_template_string, request
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
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/lucide-static@0.263.0/font/lucide.css">
    <style>
        /* CSS remains exactly the same as before - only updating JavaScript */
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
        
        .seller-selector {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .seller-selector label {
            font-size: 14px;
            font-weight: 500;
            color: var(--gray-700);
            white-space: nowrap;
        }
        
        .seller-dropdown {
            padding: 10px 16px;
            border: 1px solid var(--gray-300);
            border-radius: 12px;
            font-size: 14px;
            font-weight: 500;
            color: var(--gray-900);
            background: white;
            cursor: pointer;
            min-width: 220px;
            transition: all 0.2s;
            appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%236b7280' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 12px center;
            background-size: 16px;
            padding-right: 40px;
        }
        
        .seller-dropdown:hover {
            border-color: var(--gray-400);
        }
        
        .seller-dropdown:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        
        /* Main Content */
        .main-content {
            padding: 32px 0;
        }
        
        /* Stats Cards */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(1, 1fr);
            gap: 20px;
            margin-bottom: 32px;
        }
        
        @media (min-width: 768px) {
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (min-width: 1024px) {
            .stats-grid {
                grid-template-columns: repeat(4, 1fr);
            }
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
        
        .stat-icon {
            width: 24px;
            height: 24px;
            color: white;
        }
        
        .stat-change {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 12px;
            font-weight: 600;
            padding: 4px 8px;
            border-radius: 20px;
        }
        
        .stat-change.positive {
            background-color: #d1fae5;
            color: #065f46;
        }
        
        .stat-change.negative {
            background-color: #fee2e2;
            color: #991b1b;
        }
        
        .stat-change.neutral {
            background-color: #e5e7eb;
            color: #4b5563;
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
            grid-template-columns: repeat(1, 1fr);
            gap: 24px;
            margin-bottom: 32px;
        }
        
        @media (min-width: 1024px) {
            .charts-grid {
                grid-template-columns: repeat(2, 1fr);
            }
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
        
        .chart-canvas-container canvas {
            width: 100% !important;
            height: 100% !important;
            max-height: 320px;
        }
        
        /* Tables Grid */
        .tables-grid {
            display: grid;
            grid-template-columns: repeat(1, 1fr);
            gap: 24px;
        }
        
        @media (min-width: 1024px) {
            .tables-grid {
                grid-template-columns: 1fr 2fr;
            }
        }
        
        .table-container {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
            border: 1px solid var(--gray-200);
            height: 420px;
            display: flex;
            flex-direction: column;
        }
        
        .table-header {
            padding: 20px;
            border-bottom: 1px solid var(--gray-200);
            flex-shrink: 0;
        }
        
        .table-title {
            font-size: 16px;
            font-weight: 600;
            color: var(--gray-900);
            margin: 0;
        }
        
        .table-content {
            flex: 1;
            overflow: hidden;
            position: relative;
        }
        
        .table-scroll-container {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            overflow-y: auto;
        }
        
        .table {
            width: 100%;
            border-collapse: collapse;
            min-width: 500px;
        }
        
        .table thead {
            background-color: var(--gray-50);
            position: sticky;
            top: 0;
            z-index: 10;
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
        
        /* Top Products */
        .products-container {
            padding: 0;
            flex: 1;
            overflow-y: auto;
        }
        
        .product-item {
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 16px 20px;
            border-bottom: 1px solid var(--gray-200);
            transition: background-color 0.2s;
        }
        
        .product-item:hover {
            background-color: var(--gray-50);
        }
        
        .product-item:last-child {
            border-bottom: none;
        }
        
        .product-image {
            width: 48px;
            height: 48px;
            border-radius: 8px;
            background: linear-gradient(135deg, #f3f4f6, #d1d5db);
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        
        .product-info {
            flex: 1;
            min-width: 0;
        }
        
        .product-name {
            font-weight: 500;
            color: var(--gray-900);
            margin-bottom: 4px;
            font-size: 14px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .product-stats {
            font-size: 12px;
            color: var(--gray-500);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .product-revenue {
            font-weight: 600;
            color: var(--gray-900);
        }
        
        /* Status Badges */
        .status-badge {
            display: inline-flex;
            align-items: center;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.02em;
        }
        
        .status-badge.completed {
            background-color: #d1fae5;
            color: #065f46;
        }
        
        .status-badge.processing {
            background-color: #dbeafe;
            color: #1e40af;
        }
        
        .status-badge.pending {
            background-color: #fef3c7;
            color: #92400e;
        }
        
        /* Seller Info Banner */
        .seller-info {
            background: linear-gradient(135deg, #dbeafe, #93c5fd);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 24px;
            border: 1px solid #bfdbfe;
        }
        
        .seller-info.hidden {
            display: none;
        }
        
        .seller-info-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
        }
        
        .seller-info-title {
            font-size: 16px;
            font-weight: 600;
            color: #1e40af;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .seller-info-details {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
        }
        
        @media (min-width: 768px) {
            .seller-info-details {
                grid-template-columns: repeat(4, 1fr);
            }
        }
        
        .seller-detail {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        
        .seller-detail-label {
            font-size: 12px;
            color: #4b5563;
            font-weight: 500;
        }
        
        .seller-detail-value {
            font-size: 14px;
            font-weight: 600;
            color: #1f2937;
        }
        
        /* Buttons */
        .refresh-btn {
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
            white-space: nowrap;
        }
        
        .refresh-btn:hover {
            background: var(--gray-50);
            border-color: var(--gray-400);
        }
        
        .refresh-btn:active {
            transform: scale(0.98);
        }
        
        /* Loading States */
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
        
        /* Footer */
        .footer {
            padding: 20px 0;
            text-align: center;
            color: var(--gray-500);
            font-size: 12px;
            border-top: 1px solid var(--gray-200);
            margin-top: 32px;
        }
        
        .footer p {
            margin: 0;
        }
        
        /* Scrollbar Styling */
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
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--gray-400);
        }
        
        /* Utility Classes */
        .hidden {
            display: none !important;
        }
        
        .visible {
            display: inline-flex !important;
        }
    </style>
</head>
<body>
    <!-- Header -->
    <header class="header">
        <div class="dashboard-container">
            <div class="header-content">
                <div class="header-title">
                    <h1>E-Commerce Analytics</h1>
                    <p>Monitor your sales performance and insights</p>
                </div>
                <div class="seller-selector">
                    <label for="sellerSelect">Select Seller:</label>
                    <select id="sellerSelect" class="seller-dropdown" onchange="onSellerChange()">
                        <option value="all">All Sellers (Aggregated View)</option>
                        <option value="" disabled>─────────── Top Sellers ───────────</option>
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

    <!-- Main Content -->
    <main class="main-content">
        <div class="dashboard-container">
            <!-- Seller Info Banner -->
            <div id="sellerInfo" class="seller-info hidden">
                <div class="seller-info-header">
                    <div class="seller-info-title">
                        <i class="fas fa-user-tie"></i>
                        <span id="sellerName">Seller Details</span>
                    </div>
                    <button class="refresh-btn" onclick="resetToAllSellers()">
                        <i class="fas fa-undo"></i>
                        View All Sellers
                    </button>
                </div>
                <div class="seller-info-details">
                    <div class="seller-detail">
                        <span class="seller-detail-label">Location</span>
                        <span id="sellerLocation" class="seller-detail-value">-</span>
                    </div>
                    <div class="seller-detail">
                        <span class="seller-detail-label">First Order</span>
                        <span id="sellerFirstOrder" class="seller-detail-value">-</span>
                    </div>
                    <div class="seller-detail">
                        <span class="seller-detail-label">Last Order</span>
                        <span id="sellerLastOrder" class="seller-detail-value">-</span>
                    </div>
                    <div class="seller-detail">
                        <span class="seller-detail-label">Active Days</span>
                        <span id="sellerActiveDays" class="seller-detail-value">-</span>
                    </div>
                </div>
            </div>

            <!-- Stats Grid - FIXED: Added proper change indicators -->
            <div class="stats-grid">
                <div class="stat-card" id="revenueCard">
                    <div class="stat-card-header">
                        <div class="stat-icon-container green">
                            <i class="fas fa-dollar-sign stat-icon"></i>
                        </div>
                        <div id="revenueChange" class="stat-change positive hidden">
                            <i class="fas fa-arrow-up"></i>
                            <span>0%</span>
                        </div>
                    </div>
                    <div class="stat-title" id="stat1Title">Total Revenue</div>
                    <div class="stat-value" id="totalRevenue">$0.00</div>
                    <div class="stat-subtitle" id="stat1Subtitle">All-time sales</div>
                </div>
                
                <div class="stat-card" id="ordersCard">
                    <div class="stat-card-header">
                        <div class="stat-icon-container blue">
                            <i class="fas fa-shopping-cart stat-icon"></i>
                        </div>
                        <div id="ordersChange" class="stat-change positive hidden">
                            <i class="fas fa-arrow-up"></i>
                            <span>0%</span>
                        </div>
                    </div>
                    <div class="stat-title" id="stat2Title">Total Orders</div>
                    <div class="stat-value" id="totalOrders">0</div>
                    <div class="stat-subtitle" id="stat2Subtitle">Completed transactions</div>
                </div>
                
                <div class="stat-card" id="customersCard">
                    <div class="stat-card-header">
                        <div class="stat-icon-container purple">
                            <i class="fas fa-users stat-icon"></i>
                        </div>
                        <div id="customersChange" class="stat-change positive hidden">
                            <i class="fas fa-arrow-up"></i>
                            <span>0%</span>
                        </div>
                    </div>
                    <div class="stat-title" id="stat3Title">Total Customers</div>
                    <div class="stat-value" id="totalCustomers">0</div>
                    <div class="stat-subtitle" id="stat3Subtitle">Registered buyers</div>
                </div>
                
                <div class="stat-card" id="avgOrderCard">
                    <div class="stat-card-header">
                        <div class="stat-icon-container orange">
                            <i class="fas fa-chart-line stat-icon"></i>
                        </div>
                        <div id="avgOrderChange" class="stat-change positive hidden">
                            <i class="fas fa-arrow-up"></i>
                            <span>0%</span>
                        </div>
                    </div>
                    <div class="stat-title" id="stat4Title">Average Order Value</div>
                    <div class="stat-value" id="avgOrderValue">$0.00</div>
                    <div class="stat-subtitle" id="stat4Subtitle">Per transaction</div>
                </div>
            </div>

            <!-- Charts Grid -->
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

            <!-- Tables Grid -->
            <div class="tables-grid">
                <div class="table-container">
                    <div class="table-header">
                        <h3 class="table-title" id="productsTitle">Top Product Categories</h3>
                    </div>
                    <div class="table-content">
                        <div class="table-scroll-container">
                            <div id="topProducts">
                                <div class="loading">
                                    <div class="spinner"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="table-container">
                    <div class="table-header">
                        <h3 class="table-title" id="ordersTableTitle">Top Sellers</h3>
                    </div>
                    <div class="table-content">
                        <div class="table-scroll-container">
                            <table class="table">
                                <thead>
                                    <tr id="tableHeaders">
                                        <!-- Headers will be populated dynamically -->
                                    </tr>
                                </thead>
                                <tbody id="dataTable">
                                    <!-- Data will be populated dynamically -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- Footer -->
    <footer class="footer">
        <div class="dashboard-container">
            <p>Dashboard auto-refreshes every 2 minutes | Data source: MySQL ecom_master database</p>
            <p class="mt-2">Last updated: <span id="lastUpdated">Loading...</span></p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        let charts = {};
        let currentSellerId = 'all';
        let sellerOptions = [];
        let previousStats = {};
        
        // Initialize previous stats
        previousStats = {
            revenue: 0,
            orders: 0,
            customers: 0,
            avgOrder: 0
        };
        
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
        
        // Format number with commas
        function formatNumber(num) {
            if (num === null || num === undefined || num === '') return '0';
            const intNum = parseInt(num);
            if (isNaN(intNum)) return '0';
            if (intNum >= 1000000) {
                return (intNum / 1000000).toFixed(1) + 'M';
            } else if (intNum >= 1000) {
                return (intNum / 1000).toFixed(1) + 'K';
            }
            return intNum.toLocaleString('en-US');
        }
        
        // Format date
        function formatDate(dateString) {
            if (!dateString) return '-';
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        }
        
        // Calculate change percentage
        function calculateChange(current, previous) {
            if (!previous || previous === 0) return null;
            const change = ((current - previous) / previous) * 100;
            return Math.round(change * 10) / 10;
        }
        
        // Update change indicator - FIXED VERSION
        function updateChangeIndicator(statId, change) {
            const changeElement = document.getElementById(statId + 'Change');
            
            if (!changeElement) {
                console.error('Change element not found:', statId + 'Change');
                return;
            }
            
            if (change === null || change === undefined) {
                changeElement.classList.add('hidden');
                changeElement.classList.remove('visible');
                return;
            }
            
            changeElement.classList.remove('hidden');
            changeElement.classList.add('visible');
            
            const arrow = changeElement.querySelector('i');
            const text = changeElement.querySelector('span');
            
            // Reset classes
            changeElement.className = 'stat-change';
            
            if (change > 0) {
                changeElement.classList.add('positive');
                if (arrow) arrow.className = 'fas fa-arrow-up';
                if (text) text.textContent = `${Math.abs(change)}%`;
            } else if (change < 0) {
                changeElement.classList.add('negative');
                if (arrow) arrow.className = 'fas fa-arrow-down';
                if (text) text.textContent = `${Math.abs(change)}%`;
            } else {
                changeElement.classList.add('neutral');
                if (arrow) arrow.className = 'fas fa-minus';
                if (text) text.textContent = '0%';
            }
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
                    const city = seller.seller_city || 'Unknown';
                    const revenue = formatCurrency(seller.total_revenue);
                    option.textContent = `${seller.seller_id.substring(0, 10)}... - ${city} (${revenue})`;
                    select.appendChild(option);
                });
                
            } catch (error) {
                console.error('Error loading seller options:', error);
            }
        }
        
        // Handle seller change
        function onSellerChange() {
            const select = document.getElementById('sellerSelect');
            currentSellerId = select.value;
            loadDashboard();
        }
        
        // Reset to all sellers
        function resetToAllSellers() {
            document.getElementById('sellerSelect').value = 'all';
            currentSellerId = 'all';
            loadDashboard();
        }
        
        // Update seller info banner
        function updateSellerInfo(sellerData) {
            const sellerInfo = document.getElementById('sellerInfo');
            if (currentSellerId === 'all') {
                sellerInfo.classList.add('hidden');
                return;
            }
            
            sellerInfo.classList.remove('hidden');
            
            if (sellerData && sellerData.length > 0) {
                const seller = sellerData[0];
                document.getElementById('sellerName').textContent = 
                    `${seller.seller_id.substring(0, 12)}...`;
                document.getElementById('sellerLocation').textContent = 
                    `${seller.seller_city || '-'}, ${seller.seller_state || '-'}`;
                document.getElementById('sellerFirstOrder').textContent = 
                    formatDate(seller.first_order_date);
                document.getElementById('sellerLastOrder').textContent = 
                    formatDate(seller.last_order_date);
                document.getElementById('sellerActiveDays').textContent = 
                    seller.active_days || '0';
            }
        }
        
        // Update stats cards - FIXED VERSION
        function updateStats(stats) {
            console.log('Updating stats with:', stats);
            
            // Get current stats based on view
            let currentStats;
            if (currentSellerId === 'all') {
                currentStats = {
                    revenue: stats.total_revenue || 0,
                    orders: stats.total_orders || 0,
                    customers: stats.total_customers || 0,
                    avgOrder: stats.avg_order_value || 0
                };
            } else {
                currentStats = {
                    revenue: stats.total_revenue || 0,
                    orders: stats.total_orders || 0,
                    customers: stats.total_products || 0, // Using total_products for seller view
                    avgOrder: stats.avg_order_value || 0
                };
            }
            
            // Calculate changes
            const revenueChange = calculateChange(currentStats.revenue, previousStats.revenue);
            const ordersChange = calculateChange(currentStats.orders, previousStats.orders);
            const customersChange = calculateChange(currentStats.customers, previousStats.customers);
            const avgOrderChange = calculateChange(currentStats.avgOrder, previousStats.avgOrder);
            
            // Update change indicators
            updateChangeIndicator('revenue', revenueChange);
            updateChangeIndicator('orders', ordersChange);
            updateChangeIndicator('customers', customersChange);
            updateChangeIndicator('avgOrder', avgOrderChange);
            
            // Update current values
            document.getElementById('totalRevenue').textContent = formatCurrency(currentStats.revenue);
            document.getElementById('totalOrders').textContent = formatNumber(currentStats.orders);
            document.getElementById('totalCustomers').textContent = formatNumber(currentStats.customers);
            document.getElementById('avgOrderValue').textContent = formatCurrency(currentStats.avgOrder);
            
            // Update titles based on view
            if (currentSellerId === 'all') {
                document.getElementById('stat1Title').textContent = 'Total Revenue';
                document.getElementById('stat2Title').textContent = 'Total Orders';
                document.getElementById('stat3Title').textContent = 'Total Customers';
                document.getElementById('stat4Title').textContent = 'Average Order Value';
                
                document.getElementById('stat1Subtitle').textContent = 'All-time sales';
                document.getElementById('stat2Subtitle').textContent = 'Completed transactions';
                document.getElementById('stat3Subtitle').textContent = 'Registered buyers';
                document.getElementById('stat4Subtitle').textContent = 'Per transaction';
            } else {
                document.getElementById('stat1Title').textContent = 'Total Revenue';
                document.getElementById('stat2Title').textContent = 'Total Orders';
                document.getElementById('stat3Title').textContent = 'Unique Products';
                document.getElementById('stat4Title').textContent = 'Avg Order Value';
                
                document.getElementById('stat1Subtitle').textContent = 'Seller revenue';
                document.getElementById('stat2Subtitle').textContent = 'Orders placed';
                document.getElementById('stat3Subtitle').textContent = 'Products sold';
                document.getElementById('stat4Subtitle').textContent = 'Per order';
            }
            
            // Store for next comparison
            previousStats = currentStats;
        }
        
        // Update top products
        function updateTopProducts(categories) {
            const container = document.getElementById('topProducts');
            
            if (currentSellerId === 'all') {
                document.getElementById('productsTitle').textContent = 'Top Product Categories';
                
                if (!categories || !categories.labels || categories.labels.length === 0) {
                    container.innerHTML = '<div class="p-4 text-gray-500 text-center">No category data available</div>';
                    return;
                }
                
                let html = '';
                categories.labels.forEach((label, index) => {
                    const count = categories.data[index] || 0;
                    html += `
                        <div class="product-item">
                            <div class="product-image">
                                <i class="fas fa-tag text-gray-400"></i>
                            </div>
                            <div class="product-info">
                                <div class="product-name">${label}</div>
                                <div class="product-stats">
                                    <span class="product-revenue">${formatNumber(count)} products</span>
                                </div>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;
            } else {
                document.getElementById('productsTitle').textContent = 'Top Categories';
                
                if (!categories || !categories.labels || categories.labels.length === 0) {
                    container.innerHTML = '<div class="p-4 text-gray-500 text-center">No category data available</div>';
                    return;
                }
                
                let html = '';
                categories.labels.forEach((label, index) => {
                    const count = categories.data[index] || 0;
                    html += `
                        <div class="product-item">
                            <div class="product-image">
                                <i class="fas fa-tag text-gray-400"></i>
                            </div>
                            <div class="product-info">
                                <div class="product-name">${label}</div>
                                <div class="product-stats">
                                    <span class="product-revenue">${formatNumber(count)} sales</span>
                                </div>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;
            }
        }
        
        // Update data table
        function updateDataTable(data, isIndividual) {
            const tableBody = document.getElementById('dataTable');
            const tableHeaders = document.getElementById('tableHeaders');
            
            if (isIndividual === 'all') {
                document.getElementById('ordersTableTitle').textContent = 'Top 10 Sellers by Revenue';
                
                tableHeaders.innerHTML = `
                    <th>Seller ID</th>
                    <th>Location</th>
                    <th>Orders</th>
                    <th>Revenue</th>
                    <th>Avg Order</th>
                `;
                
                if (!data || data.length === 0) {
                    tableBody.innerHTML = `
                        <tr>
                            <td colspan="5" class="text-center p-4 text-gray-500">
                                No seller data available
                            </td>
                        </tr>
                    `;
                    return;
                }
                
                let html = '';
                data.forEach((seller, index) => {
                    const rank = index + 1;
                    html += `
                        <tr>
                            <td>
                                <div class="font-semibold text-gray-900">${seller.seller_id.substring(0, 12)}...</div>
                                <div class="text-xs text-gray-500">Rank #${rank}</div>
                            </td>
                            <td>
                                <div class="font-medium">${seller.seller_city || '-'}</div>
                                <div class="text-xs text-gray-500">${seller.seller_state || '-'}</div>
                            </td>
                            <td class="font-semibold">${formatNumber(seller.order_count)}</td>
                            <td class="font-semibold text-green-600">${formatCurrency(seller.total_revenue)}</td>
                            <td>${formatCurrency(seller.avg_order_value)}</td>
                        </tr>
                    `;
                });
                tableBody.innerHTML = html;
            } else {
                document.getElementById('ordersTableTitle').textContent = 'Seller Performance';
                
                tableHeaders.innerHTML = `
                    <th>Metric</th>
                    <th>Value</th>
                    <th>Details</th>
                `;
                
                if (!data || data.length === 0) {
                    tableBody.innerHTML = `
                        <tr>
                            <td colspan="3" class="text-center p-4 text-gray-500">
                                No data available for this seller
                            </td>
                        </tr>
                    `;
                    return;
                }
                
                const seller = data[0];
                const html = `
                    <tr>
                        <td class="font-medium">Total Revenue</td>
                        <td class="font-semibold text-green-600">${formatCurrency(seller.total_revenue)}</td>
                        <td class="text-sm text-gray-500">All-time earnings</td>
                    </tr>
                    <tr>
                        <td class="font-medium">Total Orders</td>
                        <td class="font-semibold">${formatNumber(seller.order_count)}</td>
                        <td class="text-sm text-gray-500">Completed transactions</td>
                    </tr>
                    <tr>
                        <td class="font-medium">Avg Order Value</td>
                        <td class="font-semibold">${formatCurrency(seller.avg_order_value)}</td>
                        <td class="text-sm text-gray-500">Average per order</td>
                    </tr>
                    <tr>
                        <td class="font-medium">Unique Products</td>
                        <td class="font-semibold">${formatNumber(seller.total_products)}</td>
                        <td class="text-sm text-gray-500">Different products sold</td>
                    </tr>
                    <tr>
                        <td class="font-medium">Unique Customers</td>
                        <td class="font-semibold">${formatNumber(seller.unique_customers)}</td>
                        <td class="text-sm text-gray-500">Distinct buyers</td>
                    </tr>
                `;
                tableBody.innerHTML = html;
            }
        }
        
        // Update charts
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
                    labels: revenue.months || [],
                    datasets: [{
                        label: currentSellerId === 'all' ? 'Monthly Revenue' : 'Seller Revenue',
                        data: revenue.revenue || [],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.05)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#3b82f6',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            backgroundColor: 'rgba(255, 255, 255, 0.95)',
                            titleColor: '#1f2937',
                            bodyColor: '#4b5563',
                            borderColor: '#e5e7eb',
                            borderWidth: 1,
                            cornerRadius: 8,
                            padding: 12,
                            callbacks: {
                                label: (ctx) => `Revenue: ${formatCurrency(ctx.raw)}`
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: { color: '#6b7280', font: { size: 11 } }
                        },
                        y: {
                            beginAtZero: true,
                            grid: { color: 'rgba(0, 0, 0, 0.03)' },
                            ticks: { 
                                color: '#6b7280', 
                                font: { size: 11 },
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
                    labels: status.labels || [],
                    datasets: [{
                        data: status.data || [],
                        backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ef4444'],
                        borderWidth: 0,
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '75%',
                    plugins: {
                        legend: { 
                            position: 'right',
                            labels: {
                                padding: 16,
                                usePointStyle: true,
                                font: { size: 12 },
                                color: '#4b5563'
                            }
                        }
                    }
                }
            });
        }
        
        // Load dashboard data
        async function loadDashboard() {
            try {
                console.log('Loading dashboard data for seller:', currentSellerId);
                
                // Show loading states
                ['totalRevenue', 'totalOrders', 'totalCustomers', 'avgOrderValue'].forEach(id => {
                    document.getElementById(id).textContent = '...';
                });
                
                document.getElementById('topProducts').innerHTML = `
                    <div class="loading">
                        <div class="spinner"></div>
                    </div>
                `;
                
                document.getElementById('dataTable').innerHTML = `
                    <tr>
                        <td colspan="5" class="text-center p-4">
                            <div class="spinner" style="margin: 0 auto;"></div>
                        </td>
                    </tr>
                `;
                
                // Build API URLs
                const sellerParam = currentSellerId === 'all' ? '' : `?seller_id=${currentSellerId}`;
                
                // Load all data
                const responses = await Promise.all([
                    fetch(`/api/dashboard/stats${sellerParam}`),
                    fetch(`/api/dashboard/revenue-trend${sellerParam}`),
                    fetch(`/api/dashboard/order-status${sellerParam}`),
                    fetch(`/api/dashboard/top-categories${sellerParam}`),
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
                
                const [stats, revenue, status, categories, tableData] = await Promise.all(
                    responses.map(r => r.json())
                );
                
                console.log('Data loaded:', { stats, revenue, status, categories, tableData });
                
                // Update UI
                updateStats(stats);
                updateCharts(revenue, status, categories, {});
                updateTopProducts(categories);
                updateDataTable(tableData, currentSellerId);
                
                // Update seller info if individual seller
                if (currentSellerId !== 'all') {
                    updateSellerInfo(tableData);
                } else {
                    document.getElementById('sellerInfo').classList.add('hidden');
                }
                
                updateTimestamp();
                
                console.log('Dashboard loaded successfully!');
                
            } catch (error) {
                console.error('Error loading dashboard:', error);
                alert(`Error loading dashboard: ${error.message}`);
            }
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadSellerOptions();
            loadDashboard();
            setInterval(loadDashboard, 120000);
        });
    </script>
</body>
</html>
'''

# ==================== API ENDPOINTS ====================

@app.route('/')
def dashboard():
    return HTML_TEMPLATE

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
            if result:
                total_orders = result['total_orders']
                total_revenue = float(result['total_revenue'])
                avg_order_value = float(result['avg_order_value'])
                total_products = result['total_products']
            else:
                total_orders = 0
                total_revenue = 0.0
                avg_order_value = 0.0
                total_products = 0
            
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
            
            # Get average order value for all sellers
            cursor.execute("SELECT COALESCE(AVG(price), 0) as avg_price FROM order_items")
            avg_order_value = float(cursor.fetchone()['avg_price'])
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'total_sellers': total_sellers,
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'total_customers': total_customers,
                'avg_order_value': avg_order_value
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
                COALESCE(DATEDIFF(MAX(o.order_purchase_timestamp), MIN(o.order_purchase_timestamp)), 0) as active_days
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
        
        cursor.close()
        conn.close()
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    PORT = 5004
    print("🚀 Starting Modern Seller Dashboard")
    print(f"📊 Dashboard: http://localhost:{PORT}")
    print("✅ Fixed JavaScript error when selecting sellers")
    print("🎨 Modern UI with properly sized charts")
    app.run(host='0.0.0.0', port=PORT, debug=True)