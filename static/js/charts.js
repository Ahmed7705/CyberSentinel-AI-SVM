// Placeholder for extending dashboard visualisations.
window.CyberSentinelCharts = {
  initTrendChart: function (canvasId, series) {
    if (typeof Chart === 'undefined') return;
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: series.map((item) => item.label),
        datasets: [
          {
            label: 'Risk Score',
            data: series.map((item) => item.value),
            borderColor: 'rgba(0, 217, 245, 0.8)',
            tension: 0.35,
            fill: false,
          },
        ],
      },
      options: {
        plugins: { legend: { labels: { color: '#d8fff3' } } },
        scales: {
          x: { ticks: { color: '#9dffe4' } },
          y: { ticks: { color: '#9dffe4' } },
        },
      },
    });
  },
};
