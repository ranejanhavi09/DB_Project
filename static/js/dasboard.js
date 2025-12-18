// Additional JavaScript functionality for seller dashboard

// Export/Print functionality
function exportDashboard() {
    window.print();
}

// Date formatting helper
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Currency formatting
function formatCurrency(amount) {
    if (amount === null || amount === undefined) return 'R$ 0.00';
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(amount);
}

// Number formatting
function formatNumber(num) {
    if (num === null || num === undefined) return '0';
    return new Intl.NumberFormat('en-US').format(num);
}

// Performance score color based on value
function getScoreColor(score) {
    if (score >= 80) return '#28a745'; // Green
    if (score >= 60) return '#ffc107'; // Yellow
    if (score >= 40) return '#fd7e14'; // Orange
    return '#dc3545'; // Red
}

// Initialize tooltips
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize popovers
function initPopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Debounce function for performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initTooltips();
    initPopovers();
});