// GDP Analytics - Main JavaScript
// ================================

// Global variables
let currentTheme = localStorage.getItem('theme') || 'light';
let charts = {};

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Main initialization function
function initializeApp() {
    console.log('Initializing GDP Analytics Application');
    
    // Apply saved theme
    applyTheme(currentTheme);
    
    // Initialize components
    initializeTooltips();
    initializeCharts();
    initializeFilters();
    initializeDataTables();
    
    // Set up event listeners
    setupEventListeners();
    
    console.log('Application initialized successfully');
}

// Theme Management
// ===============

function toggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    applyTheme(currentTheme);
    localStorage.setItem('theme', currentTheme);
    
    // Update charts with new theme
    updateChartsTheme();
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    
    // Update any theme-specific elements
    const themeIcon = document.querySelector('.theme-toggle i');
    if (themeIcon) {
        themeIcon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
}

// Chart Management
// ===============

function initializeCharts() {
    // Initialize any charts that exist on the page
    const chartContainers = document.querySelectorAll('.chart-container[data-chart]');
    
    chartContainers.forEach(container => {
        const chartType = container.dataset.chart;
        const chartId = container.id;
        
        if (chartId && chartType) {
            loadChart(chartId, chartType);
        }
    });
}

function loadChart(containerId, chartType, data = null, params = {}) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Load data if not provided
    if (!data) {
        fetchChartData(chartType, params)
            .then(data => renderChart(containerId, chartType, data, params))
            .catch(error => showError(container, error));
    } else {
        renderChart(containerId, chartType, data, params);
    }
}

function renderChart(containerId, chartType, data, params = {}) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    try {
        let layout = getChartLayout(chartType, params);
        let plotData = prepareChartData(chartType, data, params);
        
        // Apply theme to layout
        if (currentTheme === 'dark') {
            layout = applyDarkTheme(layout);
        }
        
        // Create the chart
        Plotly.newPlot(containerId, plotData, layout, {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            toImageButtonOptions: {
                format: 'png',
                filename: `gdp_chart_${chartType}`,
                height: 500,
                width: 800,
                scale: 1
            }
        });
        
        // Store chart reference
        charts[containerId] = true;
        
    } catch (error) {
        showError(container, error);
    }
}

function getChartLayout(chartType, params = {}) {
    const metric = params.metric || 'gdp';
    
    // Define metric labels and units
    const metricInfo = {
        'gdp': { label: 'GDP per Capita', unit: 'USD', format: '$' },
        'population': { label: 'Population', unit: 'People', format: '' },
        'life_expectancy': { label: 'Life Expectancy', unit: 'Years', format: '' },
        'infant_mortality': { label: 'Infant Mortality Rate', unit: 'per 1,000 births', format: '' },
        'female': { label: 'Female Population', unit: '%', format: '' },
        'male': { label: 'Male Population', unit: '%', format: '' },
        'internet': { label: 'Internet Penetration', unit: '%', format: '' },
        'hci': { label: 'Human Capital Index', unit: '(0-1 scale)', format: '' },
        'enrollment': { label: 'School Enrollment', unit: '%', format: '' },
        'urban_pop': { label: 'Urban Population', unit: '%', format: '' },
        'migration': { label: 'Net Migration', unit: 'People', format: '' }
    };
    
    const info = metricInfo[metric] || { label: metric, unit: '', format: '' };
    
    const baseLayout = {
        font: { family: 'Segoe UI, Arial, sans-serif', size: 11 },
        margin: { l: 80, r: 30, t: 40, b: 100 },
        paper_bgcolor: 'white',
        plot_bgcolor: 'white',
        showlegend: false,
        hovermode: 'closest'
    };
    
    switch (chartType) {
        case 'bar':
            return {
                ...baseLayout,
                xaxis: { 
                    title: { text: 'Countries', font: { size: 12, color: '#2c3e50' } },
                    tickangle: -45,
                    tickfont: { size: 10 }
                },
                yaxis: { 
                    title: { text: `${info.label} ${info.unit ? '(' + info.unit + ')' : ''}`, font: { size: 12, color: '#2c3e50' } },
                    tickfont: { size: 10 }
                }
            };
        case 'line':
            return {
                ...baseLayout,
                xaxis: { 
                    title: { text: 'Year', font: { size: 12, color: '#2c3e50' } },
                    tickfont: { size: 10 }
                },
                yaxis: { 
                    title: { text: `${info.label} ${info.unit ? '(' + info.unit + ')' : ''}`, font: { size: 12, color: '#2c3e50' } },
                    tickfont: { size: 10 }
                }
            };
        case 'scatter':
            return {
                ...baseLayout,
                xaxis: { 
                    title: { text: 'GDP per Capita (USD)', font: { size: 12, color: '#2c3e50' } },
                    tickfont: { size: 10 }
                },
                yaxis: { 
                    title: { text: 'Life Expectancy (Years)', font: { size: 12, color: '#2c3e50' } },
                    tickfont: { size: 10 }
                }
            };
        case 'histogram':
            return {
                ...baseLayout,
                xaxis: { 
                    title: { text: `${info.label} ${info.unit ? '(' + info.unit + ')' : ''}`, font: { size: 12, color: '#2c3e50' } },
                    tickfont: { size: 10 }
                },
                yaxis: { 
                    title: { text: 'Number of Countries', font: { size: 12, color: '#2c3e50' } },
                    tickfont: { size: 10 }
                }
            };
        default:
            return baseLayout;
    }
}

function prepareChartData(chartType, data, params = {}) {
    if (!data || !Array.isArray(data)) return [];
    
    const metric = params.metric || 'gdp';
    
    // Define value formatters for different metrics
    const formatValue = (value, metric) => {
        if (value === null || value === undefined) return 'N/A';
        
        switch (metric) {
            case 'gdp':
                return `$${(value).toLocaleString()}`;
            case 'population':
            case 'migration':
                return (value).toLocaleString();
            case 'life_expectancy':
                return `${value.toFixed(1)} years`;
            case 'infant_mortality':
                return `${value.toFixed(1)} per 1,000`;
            case 'female':
            case 'male':
            case 'internet':
            case 'enrollment':
            case 'urban_pop':
                return `${value.toFixed(1)}%`;
            case 'hci':
                return value.toFixed(3);
            default:
                return value.toLocaleString();
        }
    };
    
    switch (chartType) {
        case 'bar':
            const values = data.map(d => d[metric] || 0);
            return [{
                x: data.map(d => d.name || d.country_code),
                y: values,
                type: 'bar',
                marker: {
                    color: values.map((v, i) => {
                        const colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'];
                        return colors[i % colors.length];
                    }),
                    opacity: 0.8,
                    line: { width: 0 }
                },
                hovertemplate: '<b>%{x}</b><br>' + 
                    `${metric === 'gdp' ? 'GDP per Capita' : metric.replace('_', ' ')}: ${formatValue('%{y}', metric)}<extra></extra>`
            }];
        
        case 'line':
            const lineValues = data.map(d => d[metric] || d.value || 0);
            return [{
                x: data.map(d => d.year),
                y: lineValues,
                type: 'scatter',
                mode: 'lines+markers',
                line: { color: '#2ecc71', width: 3 },
                marker: { size: 6, color: '#27ae60' },
                hovertemplate: '<b>Year %{x}</b><br>' + 
                    `Value: ${formatValue('%{y}', metric)}<extra></extra>`
            }];
        
        case 'scatter':
            return [{
                x: data.map(d => d.gdp_per_capita || d.gdp || 0),
                y: data.map(d => d.life_expectancy || 0),
                mode: 'markers',
                type: 'scatter',
                marker: {
                    size: 10,
                    color: '#3498db',
                    opacity: 0.7,
                    line: { width: 1, color: '#2980b9' }
                },
                text: data.map(d => d.name || d.country_code),
                hovertemplate: '<b>%{text}</b><br>GDP per Capita: $%{x:,.0f}<br>Life Expectancy: %{y:.1f} years<extra></extra>'
            }];
        
        case 'histogram':
            const histValues = data.map(d => d[metric] || d.value || 0);
            return [{
                x: histValues,
                type: 'histogram',
                nbinsx: Math.min(20, Math.sqrt(histValues.length)),
                marker: {
                    color: '#e74c3c',
                    opacity: 0.7,
                    line: { width: 1, color: '#c0392b' }
                },
                hovertemplate: 'Range: %{x}<br>Countries: %{y}<extra></extra>'
            }];
        
        default:
            return [];
    }
}

function applyDarkTheme(layout) {
    return {
        ...layout,
        paper_bgcolor: '#2d3748',
        plot_bgcolor: '#2d3748',
        font: { ...layout.font, color: '#f8f9fa' },
        xaxis: { ...layout.xaxis, gridcolor: '#4a5568', zerolinecolor: '#4a5568' },
        yaxis: { ...layout.yaxis, gridcolor: '#4a5568', zerolinecolor: '#4a5568' }
    };
}

function updateChartsTheme() {
    // Update all existing charts with new theme
    Object.keys(charts).forEach(chartId => {
        const container = document.getElementById(chartId);
        if (container && container.dataset.chart) {
            // Re-render chart with new theme
            const chartType = container.dataset.chart;
            // You would need to store chart data to re-render
            // For now, just update the layout
            const update = currentTheme === 'dark' ? 
                applyDarkTheme({}) : 
                { paper_bgcolor: 'white', plot_bgcolor: 'white', font: { color: '#333' } };
            
            Plotly.relayout(chartId, update);
        }
    });
}

// Data Fetching
// ============

async function fetchChartData(chartType, params = {}) {
    try {
        let url = `/api/chart-data/${chartType}`;
        
        // Add query parameters
        const queryParams = new URLSearchParams();
        for (const [key, value] of Object.entries(params)) {
            if (Array.isArray(value)) {
                // Handle arrays by adding multiple parameters with the same name
                value.forEach(item => queryParams.append(key, item));
            } else {
                queryParams.append(key, value);
            }
        }
        
        if (queryParams.toString()) {
            url += `?${queryParams.toString()}`;
        }
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching chart data:', error);
        throw error;
    }
}

async function fetchData(endpoint) {
    try {
        const response = await fetch(endpoint);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching data:', error);
        throw error;
    }
}

// UI Utilities
// ===========

function showLoading(container) {
    container.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner"></i>
            <p>Loading chart...</p>
        </div>
    `;
}

function showError(container, error) {
    container.innerHTML = `
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>
            <strong>Error loading chart:</strong> ${error.message || 'Unknown error'}
        </div>
    `;
}

function showSuccess(message) {
    showAlert(message, 'success');
}

function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container') || document.body;
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

// Form Utilities
// =============

function initializeFilters() {
    const filterForms = document.querySelectorAll('.filter-form');
    
    filterForms.forEach(form => {
        form.addEventListener('submit', handleFilterSubmit);
        
        // Auto-submit on input change
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('change', () => {
                if (input.dataset.autoSubmit !== 'false') {
                    form.submit();
                }
            });
        });
    });
}

function handleFilterSubmit(event) {
    const form = event.target;
    const formData = new FormData(form);
    const params = new URLSearchParams(formData);
    
    // Update URL with new parameters
    const newUrl = `${window.location.pathname}?${params.toString()}`;
    window.location.href = newUrl;
}

// Data Table Utilities
// ===================

function initializeDataTables() {
    const tables = document.querySelectorAll('.data-table');
    
    tables.forEach(table => {
        // Add sorting functionality
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => sortTable(table, header));
        });
        
        // Add row hover effects
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            row.addEventListener('click', handleRowClick);
        });
    });
}

function sortTable(table, header) {
    const columnIndex = Array.from(header.parentNode.children).indexOf(header);
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    const isAscending = header.dataset.sortDirection !== 'asc';
    header.dataset.sortDirection = isAscending ? 'asc' : 'desc';
    
    rows.sort((a, b) => {
        const aValue = a.children[columnIndex].textContent.trim();
        const bValue = b.children[columnIndex].textContent.trim();
        
        // Try to parse as numbers
        const aNum = parseFloat(aValue.replace(/[^0-9.-]/g, ''));
        const bNum = parseFloat(bValue.replace(/[^0-9.-]/g, ''));
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAscending ? aNum - bNum : bNum - aNum;
        }
        
        // String comparison
        return isAscending ? 
            aValue.localeCompare(bValue) : 
            bValue.localeCompare(aValue);
    });
    
    // Re-append sorted rows
    rows.forEach(row => tbody.appendChild(row));
    
    // Update sort indicators
    table.querySelectorAll('th').forEach(th => th.classList.remove('sort-asc', 'sort-desc'));
    header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
}

function handleRowClick(event) {
    const row = event.currentTarget;
    const countryCode = row.dataset.countryCode;
    
    if (countryCode) {
        window.location.href = `/country/${countryCode}`;
    }
}

// General Event Listeners
// ======================

function setupEventListeners() {
    // Theme toggle
    const themeToggle = document.querySelector('[onclick="toggleTheme()"]');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Chart export buttons
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('export-chart')) {
            const chartId = event.target.dataset.chartId;
            exportChart(chartId);
        }
    });
    
    // Country search
    const countrySearch = document.getElementById('country-search');
    if (countrySearch) {
        countrySearch.addEventListener('input', debounce(handleCountrySearch, 300));
    }
}

function initializeTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Utility Functions
// ================

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

function formatNumber(value) {
    if (typeof value !== 'number') return value;
    
    if (value >= 1000000000) {
        return (value / 1000000000).toFixed(1) + 'B';
    } else if (value >= 1000000) {
        return (value / 1000000).toFixed(1) + 'M';
    } else if (value >= 1000) {
        return (value / 1000).toFixed(1) + 'K';
    }
    
    return value.toFixed(2);
}

function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

function exportChart(chartId) {
    if (charts[chartId] && window.Plotly) {
        Plotly.downloadImage(chartId, {
            format: 'png',
            width: 1200,
            height: 800,
            filename: `gdp_chart_${chartId}`
        });
    }
}

// Search functionality
function handleCountrySearch(event) {
    const query = event.target.value.toLowerCase();
    const countryOptions = document.querySelectorAll('.country-option');
    
    countryOptions.forEach(option => {
        const countryName = option.textContent.toLowerCase();
        option.style.display = countryName.includes(query) ? 'block' : 'none';
    });
}

// Global error handler
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    
    if (!event.error.message.includes('Script error')) {
        showAlert('An unexpected error occurred. Please try again.', 'danger');
    }
});

// Export functions for global use
window.GDPAnalytics = {
    toggleTheme,
    loadChart,
    fetchData,
    showAlert,
    formatNumber,
    formatCurrency,
    exportChart
};