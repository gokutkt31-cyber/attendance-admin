// Dashboard Charts and Calendar Heatmap Visualizations using Chart.js and Custom JS rendering

document.addEventListener('DOMContentLoaded', () => {
    // 1. Render Admin/HR Chart.js Graphs
    renderAdminCharts();
    
    // 2. Render Employee Attendance Calendar Heatmap
    renderCalendarHeatmap();
});

function renderAdminCharts() {
    const trendCtx = document.getElementById('attendanceTrendChart');
    const deptCtx = document.getElementById('deptDistributionChart');
    
    // Check if on Admin/HR dashboard
    if (!trendCtx) return;
    
    // Retrieve dataset variables passed from templates via data attributes
    const trendDataRaw = trendCtx.getAttribute('data-trends');
    const deptDataRaw = deptCtx.getAttribute('data-departments');
    
    if (!trendDataRaw) return;
    
    try {
        const trends = JSON.parse(trendDataRaw);
        
        // 1. Line/Bar Chart - Attendance Trend (Last 7 Days)
        const labels = trends.map(t => t.day);
        const dataValues = trends.map(t => t.present);
        
        new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Present Employees',
                    data: dataValues,
                    borderColor: '#6366f1', // primary light HSL fallback
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 3,
                    pointBackgroundColor: '#6366f1',
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: {
                            color: 'var(--text-secondary)',
                            precision: 0
                        }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: 'var(--text-secondary)' }
                    }
                }
            }
        });
        
        // 2. Doughnut Chart - Department Distributions
        if (deptCtx && deptDataRaw) {
            const depts = JSON.parse(deptDataRaw);
            const deptLabels = depts.map(d => d.name);
            const deptCounts = depts.map(d => d.count);
            
            new Chart(deptCtx, {
                type: 'doughnut',
                data: {
                    labels: deptLabels,
                    datasets: [{
                        data: deptCounts,
                        backgroundColor: [
                            '#6366f1', // Primary Indigo
                            '#a855f7', // Purple
                            '#06b6d4', // Cyan
                            '#10b981', // Success Emerald
                            '#f59e0b', // Warning Amber
                            '#ec4899'  // Pink
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: 'var(--text-secondary)',
                                font: { family: 'Plus Jakarta Sans', size: 11 }
                            }
                        }
                    }
                }
            });
        }
    } catch (e) {
        console.error("Chart loading error:", e);
    }
}

function renderCalendarHeatmap() {
    const calendarEl = document.getElementById('heatmap-calendar');
    if (!calendarEl) return;
    
    const historyDataRaw = calendarEl.getAttribute('data-history');
    if (!historyDataRaw) return;
    
    try {
        const history = JSON.parse(historyDataRaw);
        
        // Parse date states mapping
        const logsMap = {};
        history.forEach(item => {
            logsMap[item.date] = item;
        });
        
        // Build current month calendar
        const today = new Date();
        const year = today.getFullYear();
        const month = today.getMonth(); // 0-11
        
        // First day of current month
        const firstDay = new Date(year, month, 1);
        const startDayIndex = firstDay.getDay(); // 0 = Sun, 1 = Mon ...
        
        // Total days in month
        const totalDays = new Date(year, month + 1, 0).getDate();
        
        // Render headers (Sun - Sat)
        const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        let html = '';
        weekDays.forEach(day => {
            html += `<div class="text-center font-bold text-muted small py-1" style="font-family: var(--font-heading)">${day}</div>`;
        });
        
        // Render blank spaces for offset start days
        for (let i = 0; i < startDayIndex; i++) {
            html += `<div class="calendar-day opacity-25" style="cursor: default"></div>`;
        }
        
        // Render days
        for (let d = 1; d <= totalDays; d++) {
            const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
            const log = logsMap[dateStr];
            
            let extraClass = '';
            let detailsAttr = `data-bs-toggle="tooltip" title="No logs found for ${dateStr}"`;
            
            if (log) {
                const status = log.status.toLowerCase();
                if (status === 'present') extraClass = 'present';
                else if (status === 'absent') extraClass = 'absent';
                else if (status === 'late') extraClass = 'late';
                else if (status === 'leave') extraClass = 'leave';
                else if (status === 'half day') extraClass = 'half-day';
                
                detailsAttr = `data-bs-toggle="tooltip" data-bs-html="true" title="<b>${log.status}</b><br>Check-In: ${log.check_in}<br>Check-Out: ${log.check_out}"`;
            }
            
            html += `
                <div class="calendar-day ${extraClass}" ${detailsAttr}>
                    <span>${d}</span>
                </div>
            `;
        }
        
        calendarEl.innerHTML = html;
        
        // Initialize bootstrap tooltips if bootstrap available
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    } catch (err) {
        console.error("Heatmap loading error:", err);
    }
}
