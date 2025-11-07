(function () {
  const form = document.getElementById('manual-detect-form');
  const resultContainer = document.getElementById('manual-detect-result');
  const config = window.manualDetectConfig || {};

  if (!form || !resultContainer || !config.endpoint) return;

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());
    resultContainer.innerHTML = '<div class="alert alert-info">Submitting for analysis...</div>';

    try {
      const response = await fetch(config.endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (response.status === 401) {
        throw new Error('You must be logged in to run detections.');
      }
      const data = await response.json();
      resultContainer.innerHTML = `
        <div class="alert alert-${data.risk_level === 'critical' ? 'danger' : data.risk_level === 'high' ? 'warning' : 'success'}">
          <strong>Risk Level:</strong> ${data.risk_level.toUpperCase()}<br>
          <strong>Score:</strong> ${(data.risk_score * 100).toFixed(1)}%
          ${data.insight ? `<hr><strong>Insight:</strong> ${data.insight}` : ''}
        </div>`;
    } catch (error) {
      resultContainer.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
    }
  });
})();
