(function () {
  const trigger = document.getElementById('generate-report-btn');
  const table = document.getElementById('report-table');
  if (!trigger || !table) return;

  trigger.addEventListener('click', () => {
    const html = `<!DOCTYPE html><html><head><meta charset="utf-8"><title>CyberSentinel Report</title>
    <style>
      body { font-family: Arial, sans-serif; background: #0b1118; color: #e5fef7; padding: 2rem; }
      table { width: 100%; border-collapse: collapse; margin-top: 1.5rem; }
      th, td { border: 1px solid rgba(61,245,198,0.25); padding: 0.75rem; }
      th { background: rgba(0,245,160,0.1); }
    </style></head><body>
    <h1>CyberSentinel Alert Report</h1>
    <p>Generated: ${new Date().toISOString()}</p>
    ${table.outerHTML}
    </body></html>`;

    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'cybersentinel-report.html';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  });
})();
