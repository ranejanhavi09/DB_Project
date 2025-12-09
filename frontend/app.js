// API Base URL
const API_BASE_URL = 'http://localhost:5001/api';

// DOM Elements
const customerSelect = document.getElementById('customerSelect');
const loadCustomerBtn = document.getElementById('loadCustomerBtn');
const getRecommendationsBtn = document.getElementById('getRecommendationsBtn');
const customerInfo = document.getElementById('customerInfo');
const recommendations = document.getElementById('recommendations');
const loadingIndicator = document.getElementById('loadingIndicator');
const stats = document.getElementById('stats');

let currentCustomerId = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadCustomers();
    loadStats();
    
    loadCustomerBtn.addEventListener('click', handleLoadCustomer);
    getRecommendationsBtn.addEventListener('click', handleGetRecommendations);
});

// Load customers list
async function loadCustomers() {
    try {
        const response = await fetch(`${API_BASE_URL}/customers`);
        const data = await response.json();
        
        if (data.success) {
            customerSelect.innerHTML = '<option value="">Select a customer...</option>';
            data.customers.forEach(customer => {
                const option = document.createElement('option');
                option.value = customer.customer_unique_id;
                option.textContent = `${customer.customer_unique_id} - ${customer.city || 'Unknown'}, ${customer.state || 'Unknown'} (${customer.total_orders || 0} orders)`;
                customerSelect.appendChild(option);
            });
        } else {
            showError('Failed to load customers');
        }
    } catch (error) {
        console.error('Error loading customers:', error);
        showError('Error connecting to API. Make sure the backend server is running.');
    }
}

// Load customer information
async function handleLoadCustomer() {
    const customerId = customerSelect.value;
    if (!customerId) {
        alert('Please select a customer');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/customers/${customerId}`);
        const data = await response.json();
        
        if (data.success) {
            currentCustomerId = customerId;
            displayCustomerInfo(data.customer);
            getRecommendationsBtn.disabled = false;
        } else {
            showError(data.error || 'Failed to load customer');
        }
    } catch (error) {
        console.error('Error loading customer:', error);
        showError('Error loading customer information');
    }
}

// Display customer information
function displayCustomerInfo(customer) {
    customerInfo.classList.remove('hidden');
    customerInfo.innerHTML = `
        <h3>Customer Information</h3>
        <p><strong>ID:</strong> ${customer.customer_unique_id}</p>
        <p><strong>Location:</strong> ${customer.city || 'Unknown'}, ${customer.state || 'Unknown'}</p>
        <p><strong>Total Orders:</strong> ${customer.order_count || customer.total_orders || 0}</p>
        <p><strong>Products Purchased:</strong> ${customer.product_count || 0}</p>
        <p><strong>Average Review Score:</strong> ${customer.avg_review_score ? customer.avg_review_score.toFixed(2) : 'N/A'}</p>
        ${customer.first_order_date ? `<p><strong>First Order:</strong> ${new Date(customer.first_order_date).toLocaleDateString()}</p>` : ''}
        ${customer.last_order_date ? `<p><strong>Last Order:</strong> ${new Date(customer.last_order_date).toLocaleDateString()}</p>` : ''}
    `;
}

// Get recommendations
async function handleGetRecommendations() {
    if (!currentCustomerId) {
        alert('Please load a customer first');
        return;
    }
    
    const algorithm = document.querySelector('input[name="algorithm"]:checked').value;
    
    loadingIndicator.classList.remove('hidden');
    recommendations.innerHTML = '';
    
    try {
        const response = await fetch(
            `${API_BASE_URL}/customers/${currentCustomerId}/recommendations?algorithm=${algorithm}&limit=20`
        );
        const data = await response.json();
        
        loadingIndicator.classList.add('hidden');
        
        if (data.success) {
            displayRecommendations(data.recommendations, algorithm);
        } else {
            showError(data.error || 'Failed to load recommendations');
        }
    } catch (error) {
        console.error('Error loading recommendations:', error);
        loadingIndicator.classList.add('hidden');
        showError('Error loading recommendations. Make sure the backend server is running.');
    }
}

// Display recommendations
function displayRecommendations(recs, algorithm) {
    if (recs.length === 0) {
        recommendations.innerHTML = '<div class="error">No recommendations found for this customer.</div>';
        return;
    }
    
    recommendations.innerHTML = `
        <div class="success">
            Found ${recs.length} recommendations using ${getAlgorithmName(algorithm)} algorithm
        </div>
    `;
    
    recs.forEach((rec, index) => {
        const card = document.createElement('div');
        card.className = 'recommendation-card';
        
        const rating = rec.avg_rating || 0;
        const ratingClass = rating >= 4 ? 'high' : rating >= 3 ? 'medium' : 'low';
        
        card.innerHTML = `
            <h3>Product #${index + 1}</h3>
            <div class="info-row">
                <span class="info-label">Product ID:</span>
                <span class="info-value">${rec.product_id.substring(0, 20)}...</span>
            </div>
            ${rec.category ? `
            <div class="info-row">
                <span class="info-label">Category:</span>
                <span class="info-value">${rec.category}</span>
            </div>
            ` : ''}
            ${rec.avg_price ? `
            <div class="info-row">
                <span class="info-label">Avg Price:</span>
                <span class="info-value">R$ ${rec.avg_price.toFixed(2)}</span>
            </div>
            ` : ''}
            ${rec.avg_rating ? `
            <div class="info-row">
                <span class="info-label">Rating:</span>
                <span class="info-value">
                    <span class="rating ${ratingClass}">${rec.avg_rating.toFixed(2)} ⭐</span>
                </span>
            </div>
            ` : ''}
            ${rec.total_sales ? `
            <div class="info-row">
                <span class="info-label">Total Sales:</span>
                <span class="info-value">${rec.total_sales}</span>
            </div>
            ` : ''}
            ${rec.review_count !== undefined ? `
            <div class="info-row">
                <span class="info-label">Reviews:</span>
                <span class="info-value">${rec.review_count}</span>
            </div>
            ` : ''}
            ${rec.recommendation_score !== undefined ? `
            <div class="info-row">
                <span class="info-label">Score:</span>
                <span class="info-value">${rec.recommendation_score.toFixed(3)}</span>
            </div>
            ` : ''}
            ${rec.seller_id ? `
            <div class="info-row">
                <span class="info-label">Seller:</span>
                <span class="info-value">${rec.seller_city || 'Unknown'}</span>
            </div>
            ` : ''}
        `;
        
        recommendations.appendChild(card);
    });
}

// Get algorithm display name
function getAlgorithmName(algorithm) {
    const names = {
        'hybrid': 'Hybrid',
        'collaborative': 'Collaborative Filtering',
        'content': 'Content-Based',
        'sentiment': 'Sentiment-Based',
        'seller': 'Seller-Based'
    };
    return names[algorithm] || algorithm;
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        const data = await response.json();
        
        if (data.success && data.stats) {
            displayStats(data.stats);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Display statistics
function displayStats(stats) {
    stats.innerHTML = `
        <div class="stat-card">
            <div class="stat-value">${formatNumber(stats.customer_count)}</div>
            <div class="stat-label">Customers</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${formatNumber(stats.order_count)}</div>
            <div class="stat-label">Orders</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${formatNumber(stats.product_count)}</div>
            <div class="stat-label">Products</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${formatNumber(stats.seller_count)}</div>
            <div class="stat-label">Sellers</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${formatNumber(stats.review_count)}</div>
            <div class="stat-label">Reviews</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${formatNumber(stats.category_count)}</div>
            <div class="stat-label">Categories</div>
        </div>
    `;
}

// Format number with commas
function formatNumber(num) {
    return num ? num.toLocaleString() : '0';
}

// Show error message
function showError(message) {
    recommendations.innerHTML = `<div class="error">${message}</div>`;
}

