(function () {
  const vscode = acquireVsCodeApi();

  const generateBtn = document.getElementById('generate-btn');
  const content = document.getElementById('content');

  // Load initial state or set defaults
  updateContent('Welcome to GitPulse. Click generate to start your daily standup.');

  generateBtn.addEventListener('click', () => {
    updateContent('<div class="loader">Analyzing commits...</div>');
    
    // In a real implementation, we'd fetch settings from VS Code config
    // and then call the GitPulse API.
    fetch('http://localhost:8000/summarise', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: 'default', // Placeholder
        repos: [],
        days: 1
      })
    })
    .then(res => res.json())
    .then(data => {
      updateContent(`<div class="summary">${data.summary}</div>`);
    })
    .catch(err => {
      updateContent(`<div class="error">Failed to connect to GitPulse API. Ensure the backend is running.</div>`);
      vscode.postMessage({ type: 'onError', value: err.message });
    });
  });

  function updateContent(html) {
    content.innerHTML = html;
  }

  window.addEventListener('message', event => {
    const message = event.data;
    switch (message.type) {
      case 'refresh':
        generateBtn.click();
        break;
    }
  });
}());
