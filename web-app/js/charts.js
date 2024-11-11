// Real-Time Vehicle Count Chart
const ctxRealTime = document.getElementById('realTimeChart').getContext('2d');
const realTimeChart = new Chart(ctxRealTime, {
    type: 'bar',
    data: {
        labels: ['Cars', 'Trucks', 'Buses'],
        datasets: [{
            label: 'Vehicle Count',
            data: [12, 3, 1], // Placeholder data, replace with real-time data
            backgroundColor: ['rgba(75, 192, 192, 0.6)', 'rgba(153, 102, 255, 0.6)', 'rgba(255, 159, 64, 0.6)']
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: { beginAtZero: true }
        }
    }
});

// Fetch and display historical traffic data
function fetchHistoricalData() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;

    fetch('/historical', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `startDate=${startDate}&endDate=${endDate}`
    })
    .then(response => response.json())
    .then(data => {
        // Update historical chart
        historicalChart.data.labels = data.dates;
        historicalChart.data.datasets[0].data = data.vehicle_counts;
        historicalChart.update();
    })
    .catch(error => console.error('Error fetching historical data:', error));
}

// Historical Traffic Data Chart
const ctxHistorical = document.getElementById('historicalChart').getContext('2d');
const historicalChart = new Chart(ctxHistorical, {
    type: 'line',
    data: {
        labels: [], // Will be updated with historical data
        datasets: [{
            label: 'Vehicle Count',
            data: [], // Will be updated with historical data
            borderColor: 'rgba(75, 192, 192, 1)',
            fill: false
        }]
    },
    options: {
        responsive: true,
        scales: {
            x: { type: 'time', time: { unit: 'day' } },
            y: { beginAtZero: true }
        }
    }
});
