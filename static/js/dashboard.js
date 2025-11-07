(function () {
  const config = window.dashboardBootstrap || {};
  const trainBtn = document.getElementById('manual-train-btn');
  const timeline = document.getElementById('notification-feed');

  async function refreshNotifications() {
    if (!config.notificationsEndpoint || !timeline) return;
    try {
      const response = await fetch(config.notificationsEndpoint);
      if (!response.ok) throw new Error('Request failed');
      const data = await response.json();
      timeline.innerHTML = '';
      data.forEach((item) => {
        const li = document.createElement('li');
        li.innerHTML = `<strong>${item.event_type || item.event || 'event'}</strong><br><small class="text-muted">${item.timestamp}</small>`;
        timeline.appendChild(li);
      });
    } catch (error) {
      console.error('Notification refresh failed', error);
    }
  }

  async function retrainModels() {
    if (!config.alertsEndpoint) return;
    trainBtn.disabled = true;
    trainBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Training';
    try {
      const response = await fetch('/ai/train', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ limit: 500 })
      });
      if (!response.ok) throw new Error('Training failed');
      trainBtn.innerHTML = '<i class="fa-solid fa-check"></i> Models Updated';
    } catch (error) {
      console.error(error);
      trainBtn.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Retry';
    } finally {
      setTimeout(() => {
        trainBtn.innerHTML = '<i class="fa-solid fa-robot"></i> Retrain AI Models';
        trainBtn.disabled = false;
      }, 4000);
    }
  }

  function renderActivityChart() {
    if (typeof Chart === 'undefined') return;
    const canvas = document.getElementById('activityChart');
    if (!canvas) return;
    const labels = [];
    const counts = [];
    (config.activityStats || []).forEach((row) => {
      labels.push(row.event_type || row.activity_type);
      counts.push(row.total || row.count || 0);
    });
    if (!labels.length) {
      labels.push('No Data');
      counts.push(0);
    }
    new Chart(canvas, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Events',
          data: counts,
          backgroundColor: 'rgba(61, 245, 198, 0.6)',
          borderColor: 'rgba(61, 245, 198, 1)',
          borderWidth: 1,
        }],
      },
      options: {
        responsive: true,
        scales: {
          x: { ticks: { color: '#9dffe4' } },
          y: { ticks: { color: '#9dffe4' }, beginAtZero: true },
        },
        plugins: {
          legend: { labels: { color: '#e5fef7' } },
        },
      },
    });
  }

  if (trainBtn) {
    trainBtn.addEventListener('click', retrainModels);
  }

  renderActivityChart();
  refreshNotifications();
  setInterval(refreshNotifications, 60000);
})();
