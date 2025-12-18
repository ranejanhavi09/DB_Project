// API Base URL
const API_BASE_URL = 'http://localhost:5001/api';

// DOM Elements
const customerInput = document.getElementById('customerInput');
const loadCustomerBtn = document.getElementById('loadCustomerBtn');
const getRecommendationsBtn = document.getElementById('getRecommendationsBtn');
const customerInfo = document.getElementById('customerInfo');
const recommendations = document.getElementById('recommendations');
const loadingIndicator = document.getElementById('loadingIndicator');
const stats = document.getElementById('stats');

let currentCustomerId = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    
    loadCustomerBtn.addEventListener('click', handleLoadCustomer);
    getRecommendationsBtn.addEventListener('click', handleGetRecommendations);
    
    // Allow Enter key to trigger load customer
    customerInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleLoadCustomer();
        }
    });
});

// Load customer information
async function handleLoadCustomer() {
    const customerId = customerInput.value.trim();
    if (!customerId) {
        alert('Please enter a customer ID');
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
        
        // Generate explanation based on algorithm type
        const explanation = generateExplanation(rec, algorithm);
        
        card.innerHTML = `
            <h3>Product #${index + 1}</h3>
            ${explanation ? `
            <div class="explanation-row">
                <span class="explanation-text">${explanation}</span>
            </div>
            ` : ''}
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
                <span class="info-label">Seller Location:</span>
                <span class="info-value">${rec.seller_id || 'Unknown'}</span>
            </div>
            ` : ''}
        `;
        
        recommendations.appendChild(card);
    });
}

// Generate explanation for why a product is recommended
function generateExplanation(rec, algorithm) {
    if (!rec.explanation_data) {
        return null;
    }
    
    switch (algorithm) {
        case 'collaborative':
            const shopperCount = rec.explanation_data || 0;
            if (shopperCount === 1) {
                return '1 similar shopper also bought this product';
            } else {
                return `${shopperCount} similar shoppers also bought this product`;
            }
            
        case 'content':
            if (rec.explanation_data) {
                const relatedProductId = rec.explanation_data.substring(0, 20) + '...';
                return `Because you also bought product ${relatedProductId}`;
            }
            return null;
            
        case 'sentiment':
            const reviewCount = rec.explanation_data || 0;
            const category = rec.category || 'this category';
            if (reviewCount > 0) {
                return `In category ${category} highly rated by ${reviewCount} ${reviewCount === 1 ? 'person' : 'people'}`;
            }
            return `In category ${category} - recommended based on positive customer sentiment`;
            
        case 'seller':
            const orderCount = rec.explanation_data || 0;
            if (orderCount === 1) {
                return 'From a seller you\'ve ordered from before';
            } else {
                return `From a seller you've ordered from ${orderCount} times`;
            }
            
        default:
            return null;
    }
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

