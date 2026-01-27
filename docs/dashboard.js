// ===== Configuration =====
const INITIAL_CAPITAL = 50000;
const DATA_PATH = '../data/portfolio_state.json';

// ===== Global State =====
let portfolioData = null;
let equityChart = null;
let winLossChart = null;

// ===== Initialize Dashboard =====
async function initDashboard() {
    try {
        updateStatus('Loading...', 'loading');

        // Load portfolio data
        await loadPortfolioData();

        // Update all sections
        updateSummaryCards();
        updateCharts();
        updatePositionsTable();
        updateTradesTable();
        updateSystemInfo();

        updateStatus('Live', 'success');
    } catch (error) {
        console.error('Dashboard initialization error:', error);
        updateStatus('Error', 'error');
        showError('Failed to load portfolio data. Make sure portfolio_state.json exists.');
    }
}

// ===== Load Portfolio Data =====
async function loadPortfolioData() {
    try {
        const response = await fetch(DATA_PATH);
        if (!response.ok) {
            throw new Error('Failed to fetch portfolio data');
        }
        portfolioData = await response.json();
        console.log('Portfolio data loaded:', portfolioData);
    } catch (error) {
        console.error('Error loading portfolio data:', error);
        // Use mock data for development
        portfolioData = createMockData();
    }
}

// ===== Create Mock Data (for development/testing) =====
function createMockData() {
    return {
        timestamp: Date.now() / 1000,
        cash_balance: 45000,
        portfolio: {
            'NVDA': 50,
            'TSLA': 30,
            'AAPL': 100
        },
        orders: [
            {
                order_id: 'abc123',
                symbol: 'NVDA',
                action: 'BUY',
                quantity: 50,
                filled_price: 140.50,
                status: 'FILLED',
                timestamp: Date.now() / 1000 - 86400
            },
            {
                order_id: 'def456',
                symbol: 'TSLA',
                action: 'BUY',
                quantity: 30,
                filled_price: 250.00,
                status: 'FILLED',
                timestamp: Date.now() / 1000 - 172800
            }
        ]
    };
}

// ===== Update Summary Cards =====
function updateSummaryCards() {
    const cashBalance = portfolioData.cash_balance || 0;
    const portfolioValue = calculatePortfolioValue();
    const totalValue = cashBalance + portfolioValue;
    const totalReturn = ((totalValue - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100;
    const activePositions = Object.keys(portfolioData.portfolio || {}).length;

    document.getElementById('cashBalance').textContent = formatCurrency(cashBalance);
    document.getElementById('portfolioValue').textContent = formatCurrency(totalValue);

    const returnElement = document.getElementById('totalReturn');
    returnElement.textContent = formatPercent(totalReturn);
    returnElement.className = 'card-value ' + (totalReturn >= 0 ? 'positive' : 'negative');

    document.getElementById('activePositions').textContent = activePositions;
}

// ===== Calculate Portfolio Value =====
function calculatePortfolioValue() {
    // In real implementation, we'd fetch current prices
    // For now, estimate from order history
    let value = 0;
    const portfolio = portfolioData.portfolio || {};
    const orders = portfolioData.orders || [];

    for (const [symbol, quantity] of Object.entries(portfolio)) {
        // Find last buy price for this symbol
        const lastOrder = orders.reverse().find(o => o.symbol === symbol && o.action === 'BUY');
        const estimatedPrice = lastOrder ? lastOrder.filled_price : 100;
        value += quantity * estimatedPrice;
    }

    return value;
}

// ===== Update Charts =====
function updateCharts() {
    createEquityChart();
    createWinLossChart();
}

// ===== Create Equity Chart =====
function createEquityChart() {
    const ctx = document.getElementById('equityChart').getContext('2d');

    // Generate equity curve from orders
    const equityCurve = generateEquityCurve();

    if (equityChart) {
        equityChart.destroy();
    }

    equityChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: equityCurve.labels,
            datasets: [{
                label: 'Portfolio Value',
                data: equityCurve.values,
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        color: '#94a3b8',
                        callback: function (value) {
                            return '$' + value.toLocaleString();
                        }
                    },
                    grid: {
                        color: '#334155'
                    }
                },
                x: {
                    ticks: {
                        color: '#94a3b8'
                    },
                    grid: {
                        color: '#334155'
                    }
                }
            }
        }
    });
}

// ===== Generate Equity Curve =====
function generateEquityCurve() {
    const orders = portfolioData.orders || [];
    let equity = INITIAL_CAPITAL;
    const labels = ['Start'];
    const values = [INITIAL_CAPITAL];

    orders.forEach((order, index) => {
        if (order.action === 'BUY') {
            equity -= order.quantity * order.filled_price;
        } else if (order.action === 'SELL') {
            equity += order.quantity * order.filled_price;
        }

        labels.push(`Trade ${index + 1}`);
        values.push(equity);
    });

    // Add current value
    labels.push('Now');
    values.push(portfolioData.cash_balance + calculatePortfolioValue());

    return { labels, values };
}

// ===== Create Win/Loss Chart =====
function createWinLossChart() {
    const ctx = document.getElementById('winLossChart').getContext('2d');

    const { wins, losses } = calculateWinLoss();

    if (winLossChart) {
        winLossChart.destroy();
    }

    winLossChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Wins', 'Losses', 'Pending'],
            datasets: [{
                data: [wins, losses, Object.keys(portfolioData.portfolio || {}).length],
                backgroundColor: [
                    '#10b981',
                    '#ef4444',
                    '#f59e0b'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#94a3b8',
                        padding: 15
                    }
                }
            }
        }
    });
}

// ===== Calculate Win/Loss =====
function calculateWinLoss() {
    const orders = portfolioData.orders || [];
    let wins = 0;
    let losses = 0;

    // Group orders by symbol to calculate P&L
    const trades = {};
    orders.forEach(order => {
        if (!trades[order.symbol]) {
            trades[order.symbol] = [];
        }
        trades[order.symbol].push(order);
    });

    // Simple win/loss calculation (buy then sell)
    Object.values(trades).forEach(symbolOrders => {
        for (let i = 0; i < symbolOrders.length - 1; i += 2) {
            if (symbolOrders[i].action === 'BUY' && symbolOrders[i + 1]?.action === 'SELL') {
                const pnl = (symbolOrders[i + 1].filled_price - symbolOrders[i].filled_price) * symbolOrders[i].quantity;
                if (pnl > 0) wins++;
                else losses++;
            }
        }
    });

    return { wins, losses };
}

// ===== Update Positions Table =====
function updatePositionsTable() {
    const tbody = document.getElementById('positionsBody');
    const portfolio = portfolioData.portfolio || {};

    if (Object.keys(portfolio).length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No positions yet</td></tr>';
        return;
    }

    tbody.innerHTML = '';

    for (const [symbol, quantity] of Object.entries(portfolio)) {
        const orders = portfolioData.orders || [];
        const buyOrder = orders.reverse().find(o => o.symbol === symbol && o.action === 'BUY');
        const avgPrice = buyOrder ? buyOrder.filled_price : 0;
        const currentPrice = avgPrice * 1.05; // Mock 5% gain
        const pnl = (currentPrice - avgPrice) * quantity;
        const pnlPercent = ((currentPrice - avgPrice) / avgPrice) * 100;

        const row = `
            <tr>
                <td><strong>${symbol}</strong></td>
                <td>${quantity}</td>
                <td>${formatCurrency(avgPrice)}</td>
                <td>${formatCurrency(currentPrice)}</td>
                <td class="${pnl >= 0 ? 'positive' : 'negative'}">${formatCurrency(pnl)}</td>
                <td class="${pnlPercent >= 0 ? 'positive' : 'negative'}">${formatPercent(pnlPercent)}</td>
            </tr>
        `;
        tbody.innerHTML += row;
    }
}

// ===== Update Trades Table =====
function updateTradesTable() {
    const tbody = document.getElementById('tradesBody');
    const orders = (portfolioData.orders || []).slice(-10).reverse(); // Last 10 trades

    if (orders.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No trades yet</td></tr>';
        return;
    }

    tbody.innerHTML = '';

    orders.forEach(order => {
        const date = new Date(order.timestamp * 1000).toLocaleString();
        const typeClass = order.action === 'BUY' ? 'trade-buy' : 'trade-sell';
        const statusClass = order.status === 'FILLED' ? 'status-filled' : 'status-pending';

        const row = `
            <tr>
                <td>${date}</td>
                <td><strong>${order.symbol}</strong></td>
                <td class="${typeClass}">${order.action}</td>
                <td>${order.quantity}</td>
                <td>${formatCurrency(order.filled_price || 0)}</td>
                <td><span class="${statusClass}">${order.status}</span></td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

// ===== Update System Info =====
function updateSystemInfo() {
    const lastUpdate = new Date(portfolioData.timestamp * 1000);
    document.getElementById('lastUpdate').textContent = lastUpdate.toLocaleString();

    // Calculate next run (based on schedule: 21:35, 23:05, 00:35, 02:05, 03:35 Thailand time)
    const nextRun = calculateNextRun();
    document.getElementById('nextRun').textContent = nextRun;

    const totalTrades = (portfolioData.orders || []).length;
    document.getElementById('totalTrades').textContent = totalTrades;
}

// ===== Calculate Next Run =====
function calculateNextRun() {
    const now = new Date();
    const schedules = [
        { h: 21, m: 35 },
        { h: 23, m: 5 },
        { h: 0, m: 35 },
        { h: 2, m: 5 },
        { h: 3, m: 35 }
    ];

    for (const schedule of schedules) {
        const nextRun = new Date();
        nextRun.setHours(schedule.h, schedule.m, 0, 0);

        if (nextRun > now) {
            return nextRun.toLocaleTimeString();
        }
    }

    // If all today's runs passed, show first run tomorrow
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(schedules[0].h, schedules[0].m, 0, 0);
    return tomorrow.toLocaleString();
}

// ===== Update Status Badge =====
function updateStatus(text, type) {
    const badge = document.getElementById('statusBadge');
    const statusText = document.getElementById('statusText');
    statusText.textContent = text;

    badge.className = 'status-badge';
    if (type === 'error') {
        badge.style.background = 'rgba(239, 68, 68, 0.1)';
        badge.style.borderColor = '#ef4444';
    }
}

// ===== Utility Functions =====
function formatCurrency(value) {
    return '$' + value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatPercent(value) {
    return (value >= 0 ? '+' : '') + value.toFixed(2) + '%';
}

function showError(message) {
    console.error(message);
    // Could add a toast notification here
}

// ===== Auto Refresh =====
function startAutoRefresh() {
    // Refresh every 30 seconds
    setInterval(() => {
        console.log('Auto-refreshing dashboard...');
        initDashboard();
    }, 30000);
}

// ===== Initialize on Load =====
document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
    startAutoRefresh();
});
